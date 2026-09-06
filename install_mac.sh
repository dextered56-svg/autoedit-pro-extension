#!/bin/bash

# AutoEdit Pro - Mac Installer Script

echo "======================================="
echo "   Installing AutoEdit Pro (Mac)       "
echo "======================================="

# 1. Build the Backend
echo "\n[1/3] Building the Python Backend..."
cd backend
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "Compiling via PyInstaller..."
chmod +x build.sh
./build.sh
cd ..

echo "\n[2/3] Installing Adobe CEP Extension..."
# 2. Install the Frontend Extension
CEP_DIR="$HOME/Library/Application Support/Adobe/CEP/extensions/com.autoeditpro.extension"

echo "Creating extension directory at: $CEP_DIR"
mkdir -p "$CEP_DIR"

echo "Copying frontend files..."
cp -R frontend/* "$CEP_DIR/"

# 3. Enable PlayerDebugMode (macOS)
echo "\n[3/3] Enabling PlayerDebugMode for unsigned extensions..."
# Loop through CSXS versions 9 to 16 to ensure compatibility with recent Premiere Pro versions
for i in {9..16}; do
    defaults write com.adobe.CSXS.$i PlayerDebugMode 1
    echo "Enabled for CSXS.$i"
done

echo "======================================="
echo "   Installation Complete!              "
echo "======================================="
echo "To use AutoEdit Pro:"
echo "1. Run the backend daemon: ./backend/dist/AutoEditPro_Daemon"
echo "2. Open Adobe Premiere Pro."
echo "3. Go to Window > Extensions > AutoEdit Pro."
