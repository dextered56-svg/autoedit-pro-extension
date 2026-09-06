// Initialize Adobe CSInterface
let csInterface;
try {
    csInterface = new CSInterface();
} catch (e) {
    // Mock CSInterface if not available (for testing outside Premiere)
    class MockCSInterface {
        evalScript(script, callback) {
            console.log("Mock evalScript called with:", script);
            if (callback) callback("Mock result");
        }
    }
    csInterface = new MockCSInterface();
}
const API_URL = "http://127.0.0.1:8000/api";

function updateStatus(msg) {
    document.getElementById('status').innerText = msg;
}

document.getElementById('btnSilence').addEventListener('click', async () => {
    updateStatus("Requesting active sequence path...");

    csInterface.evalScript("getActiveMediaFilePath()", async (filepath) => {
        if (!filepath) {
            updateStatus("Error: No media found in active sequence.");
            return;
        }

        const noiseFloor = document.getElementById('noiseFloor').value;
        const minSilence = document.getElementById('minSilence').value;

        updateStatus(`Processing silence removal on ${filepath}...`);
        try {
            const response = await fetch(`${API_URL}/detect_silence`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filepath: filepath,
                    noise_floor: parseInt(noiseFloor),
                    min_silence_len: parseInt(minSilence)
                })
            });
            const data = await response.json();

            if (data.error) {
                updateStatus("Backend Error: " + data.error);
                return;
            }

            // Pass JSON cuts to ExtendScript
            const cutsJson = JSON.stringify(data.cuts);
            updateStatus(`Found ${data.cuts.length} cuts. Applying to timeline...`);

            // Base64 encode JSON to avoid injection/escaping issues in ExtendScript
            const cutsB64 = btoa(unescape(encodeURIComponent(cutsJson)));
            const script = `applyCuts('${cutsB64}')`;
            csInterface.evalScript(script, (res) => {
                updateStatus(res || "Silence removal complete.");
            });

        } catch (err) {
            updateStatus("Error: Backend not reachable.");
            console.error(err);
        }
    });
});

// Similar implementations for other buttons...
document.getElementById('btnVisual').addEventListener('click', async () => {
    updateStatus("Requesting active sequence path...");
    csInterface.evalScript("getActiveMediaFilePath()", async (filepath) => {
        if (!filepath) {
            updateStatus("Error: No media found.");
            return;
        }

        updateStatus("Processing visual automation in backend...");
        try {
            const response = await fetch(`${API_URL}/visual_automation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filepath: filepath,
                    scale_percent: 150
                })
            });
            const data = await response.json();

            if (data.error) {
                updateStatus("Backend Error: " + data.error);
                return;
            }

            const keyframesJson = JSON.stringify(data.keyframes);
            updateStatus("Applying transforms...");

            const kfB64 = btoa(unescape(encodeURIComponent(keyframesJson)));
            csInterface.evalScript(`applyVisuals('${kfB64}')`, (res) => {
                updateStatus(res || "Visual auto-zoom complete.");
            });
        } catch (err) {
            updateStatus("Error: Backend not reachable.");
        }
    });
});

document.getElementById('btnMulticam').addEventListener('click', async () => {
    updateStatus("Requesting active sequence path for Multi-Cam...");
    csInterface.evalScript("getActiveMediaFilePath()", async (filepath) => {
        if (!filepath) {
            updateStatus("Error: No media found.");
            return;
        }

        updateStatus("Processing multicam diarization in backend...");
        try {
            const response = await fetch(`${API_URL}/multicam_switch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filepath: filepath,
                    num_speakers: null // Let pyannote auto-detect
                })
            });
            const data = await response.json();

            if (data.error) {
                updateStatus("Backend Error: " + data.error);
                return;
            }

            const segmentsJson = JSON.stringify(data.speaker_segments);
            updateStatus("Applying multicam cuts...");

            const segB64 = btoa(unescape(encodeURIComponent(segmentsJson)));
            csInterface.evalScript(`applyMulticam('${segB64}')`, (res) => {
                updateStatus(res || "Multi-Cam switch complete.");
            });
        } catch (err) {
            updateStatus("Error: Backend not reachable.");
        }
    });
});

document.getElementById('btnCaptions').addEventListener('click', async () => {
    updateStatus("Requesting active sequence path for Captions...");
    csInterface.evalScript("getActiveMediaFilePath()", async (filepath) => {
        if (!filepath) {
            updateStatus("Error: No media found.");
            return;
        }

        updateStatus("Processing captions and chapters in backend...");
        try {
            const response = await fetch(`${API_URL}/captions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filepath: filepath,
                    filter_profanity: true
                })
            });
            const data = await response.json();

            if (data.error) {
                updateStatus("Backend Error: " + data.error);
                return;
            }

            const captionsJson = JSON.stringify({
                captions: data.captions,
                chapters: data.chapters
            });
            updateStatus("Applying captions to timeline...");

            const capB64 = btoa(unescape(encodeURIComponent(captionsJson)));
            csInterface.evalScript(`applyCaptions('${capB64}')`, (res) => {
                updateStatus(res || "Auto-Captions complete.");
            });
        } catch (err) {
            updateStatus("Error: Backend not reachable.");
        }
    });
});
