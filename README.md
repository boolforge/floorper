[![PyPI Version](https://img.shields.io/pypi/v/floorper)](https://pypi.org/project/floorper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI Status](https://github.com/boolforge/floorper/actions/workflows/tests.yml/badge.svg)](https://github.com/boolforge/floorper/actions)

# Floorper

Floorper is a comprehensive browser profile migration and management tool that allows users to detect, backup, restore, and migrate profiles between different browsers.

## Features

- **Multi-browser Support**: Detect and migrate profiles from various browsers, including exotic and retro browsers
- **Multiple Interfaces**: Choose between GUI (PyQt6), TUI (Textual), or CLI interfaces
- **Profile Migration**: Migrate bookmarks, history, cookies, passwords, and other data between browsers
- **Backup & Restore**: Create and manage backups of browser profiles
- **Performance Optimized**: Utilizes caching and parallel processing for efficient operations
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.8 or higher
- PyQt6 (for GUI interface)
- Textual (for TUI interface)

### Install from PyPI

```bash
pip install floorper
```

### Install from Source

```bash
git clone https://github.com/boolforge/floorper.git
cd floorper
pip install -e .
```

## Usage

### Graphical User Interface (GUI)

```bash
floorper --gui
```

### Text User Interface (TUI)

```bash
floorper
# or
floorper --tui
```

### Command Line Interface (CLI)

List all detected browser profiles:
```bash
floorper --cli list
```

Migrate from one browser profile to another:
```bash
floorper --cli migrate --source "/path/to/source/profile" --target "/path/to/target/profile"
```

Create a backup of a profile:
```bash
floorper --cli backup create --profile "/path/to/profile" --browser firefox
```

Restore a backup:
```bash
floorper --cli backup restore --backup "/path/to/backup.zip" --target "/path/to/restore/directory"
```

## Supported Browsers

Floorper supports a wide range of browsers, including:

### Standard Browsers
- Firefox
- Chrome
- Edge
- Safari
- Opera
- Brave
- Vivaldi

### Firefox-based Browsers
- Floorp
- Waterfox
- LibreWolf
- Pale Moon
- Basilisk

### Chromium-based Browsers
- Chromium
- Brave
- Vivaldi
- Opera
- Edge

### Exotic and Retro Browsers
- SeaMonkey
- K-Meleon
- Otter Browser
- Dooble
- Midori
- Falkon
- Qutebrowser
- Netscape Navigator
- Internet Explorer
- Lynx
- Links
- w3m

## Architecture

Floorper is organized into several modules:

- **Core**: Contains the main functionality for browser detection, profile migration, and backup management
- **Interfaces**: Provides GUI, TUI, and CLI interfaces
- **Utils**: Contains utility functions and performance optimizations
- **Browsers**: Contains browser-specific detection and migration logic

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
