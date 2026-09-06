# AutoEdit Pro

AutoEdit Pro is a premium AI Video Editing software designed as a two-part system:
1. **Standalone App (Backend)**: A local Python-based server (FastAPI) handling heavy AI processing.
2. **NLE Connector (Frontend)**: An Adobe Premiere Pro CEP extension acting as the UI, communicating with the backend via a REST API.

## Directory Structure
- `backend/`: Python FastAPI app, AI modules, and PyInstaller build script.
- `frontend/`: Adobe CEP extension HTML/JS UI and ExtendScript logic.

## 1. Backend Setup & Compilation

### Requirements
Ensure you have Python 3.8+ installed.
Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Running for Development
Run the FastAPI server directly:
```bash
python main.py
```
Or use uvicorn:
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### Building the Standalone Executable
We use PyInstaller to compile the backend into a standalone executable.
Run the provided script:
```bash
./build.sh
```
The compiled executable will be located in the `backend/dist/` directory.

## 2. Frontend Installation (Adobe Premiere Pro)

### Enable PlayerDebugMode (for unsigned extensions)
To test the extension without signing it, enable PlayerDebugMode:
- **Mac**: `defaults write com.adobe.CSXS.11 PlayerDebugMode 1` (Change `11` to your CSXS version).
- **Windows**: Open `regedit`, navigate to `HKEY_CURRENT_USER\Software\Adobe\CSXS.11`, and add a String value named `PlayerDebugMode` with value `1`.

### Install Extension
Copy or symlink the `frontend` folder into the Premiere Pro extensions directory:
- **Mac**: `/Library/Application Support/Adobe/CEP/extensions/com.autoeditpro.extension`
- **Windows**: `C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\com.autoeditpro.extension`

## 3. Testing the Bridge

1. **Open Premiere Pro**: Create a project and add a sequence with some media.
2. **Open the Extension**: Go to `Window > Extensions > AutoEdit Pro`.
    - Note: The extension will automatically spawn the AI backend daemon in the background using Node.js when opened. You will see the status change to "AI Backend Ready".
3. **Test an Action**: Click "Remove Silence" in the panel.
   - The frontend (`main.js`) will send a REST request to `http://127.0.0.1:8000/api/detect_silence`.
   - The backend processes the dummy data and returns JSON with cut timecodes in seconds.
   - The frontend receives this JSON and calls `applyCuts()` in `host.jsx`.
   - `host.jsx` converts seconds to Premiere ticks (1 sec = 254016000000 ticks) and logs the ripple delete action in the ExtendScript console (ESTK or VSCode Debugger).

## Timecode Synchronization Note
The python backend calculates timestamps in seconds (float). The Premiere frontend uses `TICKS_PER_SECOND = 254016000000` to convert these seconds into exact ticks for the sequence in and out points, avoiding frame rate rounding errors.
