#!/bin/bash
# Install requirements
pip install -r requirements.txt

# Compile main.py into a standalone executable using PyInstaller
# --onefile creates a single executable file
# --name specifies the output executable name
# --add-data allows including the modules directory if needed (depending on how PyInstaller resolves imports)
# Note: Deep learning models (like Whisper, pyannote) might require extra PyInstaller hooks or --add-data arguments for weights.

pyinstaller --noconfirm --onedir --console --name "AutoEditPro_Daemon" \
  --add-data "modules:modules" \
  --hidden-import "whisper" \
  --hidden-import "pyannote.audio" \
  main.py

echo "Build complete. Check the 'dist' directory."