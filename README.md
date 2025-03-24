# Floorper - Universal Browser Profile Migration Tool for Floorp

![Floorper Logo](docs/images/floorper_logo.png)

Floorper is a comprehensive tool designed specifically for migrating browser profiles from various browsers to Floorp. It supports a wide range of browsers, including mainstream browsers, exotic browsers, and even text-based browsers.

## Features

- **Universal Browser Support**: Migrate profiles from Firefox, Chrome, Edge, Brave, Opera, and many more browsers to Floorp
- **Cross-Platform Compatibility**: Works on Windows, macOS, Linux, Haiku, and OS/2
- **Three Interface Options**: 
  - Modern PyQt6 GUI for desktop users
  - Advanced TUI (Text User Interface) for terminal environments
  - Powerful CLI for scripting and automation
- **Comprehensive Migration**: Transfers bookmarks, history, passwords, cookies, extensions, and more
- **Smart Merging**: Intelligently merges content without overwriting existing Floorp data
- **Exotic Browser Support**: Includes support for text-based browsers like ELinks, w3m, and Lynx
- **Robust Error Handling**: Ensures reliable migration even with incomplete or corrupted profiles

## Installation

### Prerequisites

- Python 3.7 or higher
- PyQt6 (for GUI version)
- Rich (for TUI version)

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

### GUI Mode

Launch the graphical interface:

```bash
floorper-gui
```

Or run directly from the source:

```bash
python run_floorper_qt.py
```

### TUI Mode

Launch the text-based interface:

```bash
floorper-tui
```

Or run directly from the source:

```bash
python run_floorper_tui.py
```

### Command Line Mode

For advanced users and automation:

```bash
floorper --source firefox --target /path/to/floorp/profile --data-types bookmarks,history,passwords
```

Additional CLI options:
```
--list-browsers     List all detected browsers
--list-profiles     List all detected profiles
--merge-strategy    Specify merge strategy (smart, overwrite, append)
--backup            Create backup before migration
--verbose           Enable verbose output
--quiet             Suppress all output except errors
```

## Supported Browsers

### Mainstream Browsers
- Mozilla Firefox
- Google Chrome
- Microsoft Edge
- Brave
- Opera
- Vivaldi
- Safari

### Firefox-based Browsers
- Floorp
- LibreWolf
- Waterfox
- Pale Moon
- Basilisk
- SeaMonkey
- Tor Browser

### Chromium-based Browsers
- Chromium
- Opera GX
- Yandex Browser
- SRWare Iron
- Slimjet
- Epic Privacy Browser

### Other Browsers
- GNOME Web (Epiphany)
- Midori
- Konqueror
- Falkon
- Otter Browser
- qutebrowser
- Dillo
- NetSurf

### Text-based Browsers
- ELinks
- Links
- Lynx
- w3m

## Screenshots

![Main Window](docs/images/main_window.png)
![Browser Selection](docs/images/browser_selection.png)
![Migration Process](docs/images/migration_process.png)
![TUI Interface](docs/images/tui_interface.png)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The Floorp team for their excellent browser
- All the browser developers whose work makes the web accessible
- Contributors to the various open-source libraries used in this project

## Related Projects

- [Firefox Session Merger](https://github.com/james-cube/firefox-session-merger)
- [Firefox Bookmarks Deduplicator](https://github.com/james-cube/firefox-bookmarks-deduplicator)
- [Firefox Bookmarks Merger](https://github.com/james-cube/firefox-bookmarks-merger)
- [Firefox History Merger](https://github.com/crazy-max/firefox-history-merger)
