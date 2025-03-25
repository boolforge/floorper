# Installation Guide

This guide provides detailed instructions for installing Floorper on various platforms.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Platform-Specific Instructions](#platform-specific-instructions)
4. [Troubleshooting](#troubleshooting)
5. [Upgrading](#upgrading)
6. [Uninstallation](#uninstallation)

## Prerequisites

Before installing Floorper, ensure your system meets the following requirements:

### General Requirements

- Python 3.7 or higher
- Pip (Python package manager)
- 100MB free disk space
- Internet connection (for installation)

### GUI Mode Requirements

- PyQt6
- Qt6 libraries
- Display server (X11, Wayland, or Windows/macOS equivalent)

### TUI Mode Requirements

- Rich library
- Terminal with 256 color support
- UTF-8 compatible terminal

## Installation Methods

Floorper can be installed using several methods:

### Method 1: Using Pip (Recommended)

The simplest way to install Floorper is using pip:

```bash
pip install floorper
```

For a user-specific installation:

```bash
pip install --user floorper
```

### Method 2: From Source

To install from source:

```bash
git clone https://github.com/boolforge/floorper.git
cd floorper
pip install -e .
```

### Method 3: Using Package Managers

#### Debian/Ubuntu

```bash
sudo apt update
sudo apt install python3-pip
pip3 install floorper
```

#### Fedora

```bash
sudo dnf install python3-pip
pip3 install floorper
```

#### Arch Linux

```bash
sudo pacman -S python-pip
pip install floorper
```

#### macOS (Homebrew)

```bash
brew install python
pip3 install floorper
```

#### Windows (Chocolatey)

```powershell
choco install python
pip install floorper
```

## Platform-Specific Instructions

### Windows

1. Install Python from [python.org](https://python.org) or Microsoft Store
2. Ensure Python is added to PATH during installation
3. Open Command Prompt or PowerShell as administrator
4. Run: `pip install floorper`
5. Launch using:
   - GUI: `floorper-gui`
   - TUI: `floorper-tui`
   - CLI: `floorper --help`

#### Windows-Specific Notes

- For accessing browser profiles, you may need to run Floorper with administrator privileges
- If using Windows Store Python, you may need to use `python -m pip install floorper`
- For portable installation, use: `pip install --target=C:\path\to\folder floorper`

### macOS

1. Install Python using Homebrew: `brew install python`
2. Install Floorper: `pip3 install floorper`
3. Launch using:
   - GUI: `floorper-gui`
   - TUI: `floorper-tui`
   - CLI: `floorper --help`

#### macOS-Specific Notes

- You may need to grant Floorper permission to access browser data in System Preferences > Security & Privacy > Privacy > Full Disk Access
- For Apple Silicon (M1/M2) Macs, ensure you're using Python compiled for ARM architecture
- If using Homebrew Python, you might need to use `python3` instead of `python`

### Linux

#### Debian/Ubuntu

1. Install dependencies: `sudo apt install python3-pip python3-pyqt6 libqt6-dev`
2. Install Floorper: `pip3 install floorper`
3. Launch using:
   - GUI: `floorper-gui`
   - TUI: `floorper-tui`
   - CLI: `floorper --help`

#### Fedora

1. Install dependencies: `sudo dnf install python3-pip python3-qt6`
2. Install Floorper: `pip3 install floorper`
3. Launch using the same commands as above

#### Arch Linux

1. Install dependencies: `sudo pacman -S python-pip python-pyqt6`
2. Install Floorper: `pip install floorper`
3. Launch using the same commands as above

#### Linux-Specific Notes

- For accessing some browser profiles, you may need to run Floorper with sudo
- If you encounter permission issues, check that your user has read access to browser profile directories
- For systems without display server, use the TUI or CLI interface

### Haiku

1. Install Python using HaikuDepot
2. Open Terminal and run: `pip install floorper`
3. Launch using:
   - GUI: `floorper-gui`
   - TUI: `floorper-tui`
   - CLI: `floorper --help`

### OS/2

1. Install Python for OS/2
2. Open command prompt and run: `pip install floorper`
3. Launch using:
   - TUI: `floorper-tui` (recommended for OS/2)
   - CLI: `floorper --help`

## Troubleshooting

### Common Installation Issues

#### "Command not found" after installation

**Problem**: After installing Floorper, the command is not found.

**Solution**:
- Ensure Python scripts directory is in your PATH
- For Windows: `%APPDATA%\Python\Python3x\Scripts`
- For Unix-like systems: `~/.local/bin` or `/usr/local/bin`
- Try using the full path to the executable
- Restart your terminal or command prompt

#### PyQt6 Installation Fails

**Problem**: Error installing PyQt6 dependency.

**Solution**:
- Install Qt6 development libraries for your platform
- For Debian/Ubuntu: `sudo apt install python3-pyqt6 libqt6-dev`
- For Fedora: `sudo dnf install python3-qt6`
- For macOS: `brew install qt@6`
- For Windows: Consider using the binary wheel: `pip install PyQt6-Qt6==6.x.x`

#### Permission Denied Errors

**Problem**: Permission errors during installation.

**Solution**:
- For system-wide installation, use sudo (Linux/macOS) or administrator privileges (Windows)
- For user installation, use `pip install --user floorper`
- Check file permissions in the installation directory

#### Missing Dependencies

**Problem**: Error about missing dependencies.

**Solution**:
- Install required dependencies: `pip install -r requirements.txt`
- For specific dependencies, install them manually: `pip install [dependency-name]`

## Upgrading

To upgrade Floorper to the latest version:

```bash
pip install --upgrade floorper
```

To upgrade to a specific version:

```bash
pip install --upgrade floorper==X.Y.Z
```

## Uninstallation

To remove Floorper from your system:

```bash
pip uninstall floorper
```

This will remove the package but leave configuration files. To completely remove all Floorper data:

### Windows
Delete the directory: `%APPDATA%\floorper`

### macOS and Linux
Delete the directory: `~/.floorper`

## Virtual Environment Installation

For a clean, isolated installation, consider using a virtual environment:

```bash
# Create virtual environment
python -m venv floorper-env

# Activate virtual environment
# On Windows:
floorper-env\Scripts\activate
# On macOS/Linux:
source floorper-env/bin/activate

# Install Floorper
pip install floorper

# Run Floorper
floorper-gui
```

This method prevents conflicts with other Python packages and allows for easy cleanup by simply deleting the virtual environment directory.
