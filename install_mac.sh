#!/bin/bash

# AutoEdit Pro - One-Click Mac Installer
set -e

echo "======================================="
echo "   AutoEdit Pro Mac Installer          "
echo "======================================="

# Set up paths
ROOT_DIR="$(pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
CEP_DIR="$HOME/Library/Application Support/Adobe/CEP/extensions/com.autoeditpro.extension"

echo "-> [1/4] Setting up Python environment..."
cd "$BACKEND_DIR"
# Create a temporary venv to keep user's system clean during build
python3 -m venv build_venv
source build_venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "-> [2/4] Compiling AI Backend (This may take a few minutes)..."
# Compile as a single file (--onefile) to make it portable and clean
pyinstaller --noconfirm --onefile --console --name "AutoEditPro_Daemon" \
  --add-data "modules:modules" \
  --hidden-import "whisper" \
  --hidden-import "pyannote.audio" \
  main.py > /dev/null 2>&1

echo "-> [3/4] Bundling Application..."
# Create a bin folder in frontend to hold the backend daemon
mkdir -p "$FRONTEND_DIR/bin"
cp "dist/AutoEditPro_Daemon" "$FRONTEND_DIR/bin/"

# Clean up build artifacts
rm -rf build_venv build dist AutoEditPro_Daemon.spec
cd "$ROOT_DIR"

echo "-> [4/4] Installing Adobe Extension..."
# Remove old installation if exists
rm -rf "$CEP_DIR"
mkdir -p "$CEP_DIR"

# Copy the bundled frontend (which now includes the backend executable)
cp -R "$FRONTEND_DIR"/* "$CEP_DIR/"

# Enable PlayerDebugMode for CC2019 through CC2024
for i in {9..16}; do
    defaults write com.adobe.CSXS.$i PlayerDebugMode 1
done

echo "======================================="
echo "   Installation Complete!              "
echo "======================================="
echo "The backend daemon is now bundled inside the extension."
echo "You can now open Adobe Premiere Pro."
echo "Go to Window > Extensions > AutoEdit Pro."
echo "The backend server will start automatically!"
