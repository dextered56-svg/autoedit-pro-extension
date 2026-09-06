import librosa
import numpy as np

def detect(filepath: str, noise_floor: int, min_silence_len: int, padding: int):
    try:
        # Load audio using librosa
        y, sr = librosa.load(filepath, sr=None)

        # Split non-silent intervals
        non_silent_intervals = librosa.effects.split(y, top_db=abs(noise_floor))

        # Convert non-silent intervals to seconds
        non_silent_intervals_sec = librosa.samples_to_time(non_silent_intervals, sr=sr)

        # Calculate total duration
        total_duration = librosa.get_duration(y=y, sr=sr)

        cuts = []
        pad_sec = padding / 1000.0
        min_silence_sec = min_silence_len / 1000.0

        # Find silent regions by inverting non-silent regions
        current_time = 0.0
        for interval in non_silent_intervals_sec:
            start_non_silent = interval[0]
            end_non_silent = interval[1]

            silence_start = current_time
            silence_end = start_non_silent

            if (silence_end - silence_start) >= min_silence_sec:
                cut_in = min(silence_end, silence_start + pad_sec)
                cut_out = max(silence_start, silence_end - pad_sec)

                # If padding doesn't cross over
                if cut_out > cut_in:
                    cuts.append({"in": cut_in, "out": cut_out})

            current_time = end_non_silent

        # Check last chunk
        if total_duration - current_time >= min_silence_sec:
             cut_in = min(total_duration, current_time + pad_sec)
             cut_out = max(current_time, total_duration - pad_sec)
             if cut_out > cut_in:
                 cuts.append({"in": cut_in, "out": cut_out})

        return {"cuts": cuts}
    except Exception as e:
        return {"error": str(e), "cuts": []}
