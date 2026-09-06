import cv2
import mediapipe as mp

def process(filepath: str, scale_percent: int, center_sensitivity: int):
    try:
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

        cap = cv2.VideoCapture(filepath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate target 9:16 aspect ratio bounds
        target_width = height * (9 / 16)

        keyframes = []
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame every half second to reduce processing time
            if frame_idx % int(fps / 2) == 0:
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(image_rgb)

                time_sec = frame_idx / fps

                if results.detections:
                    # Take the first face
                    detection = results.detections[0]
                    bbox = detection.location_data.relative_bounding_box

                    # Calculate face center
                    face_cx = bbox.xmin + (bbox.width / 2)
                    face_cy = bbox.ymin + (bbox.height / 2)

                    # Normalize for Premiere (0.5, 0.5 is center)
                    # We want to move the anchor point, but Premiere Position is based on sequence resolution
                    # Send normalized coordinates to center the face
                    keyframes.append({
                        "time": time_sec,
                        "x": face_cx,
                        "y": face_cy,
                        "scale": scale_percent
                    })

            frame_idx += 1

        cap.release()
        return {"keyframes": keyframes}
    except Exception as e:
        return {"error": str(e), "keyframes": []}
