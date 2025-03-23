# Floorpizer & BrowserMigrator

A powerful suite of tools to migrate profiles between browsers including Floorp.

## Features

### Floorpizer (Original)
- Migrate profiles from multiple browsers to Floorp
- Support for Firefox, Chrome, Edge, Opera, Brave, Vivaldi, LibreWolf, Waterfox, Pale Moon, and Basilisk
- Graphical user interface for easy profile management
- Profile optimization and cleaning tools
- Profile merging capabilities
- Automatic browser detection

### BrowserMigrator (New PyQt6 Version)
- Universal browser profile migration between any supported browsers
- Modern, responsive UI with PyQt6
- Enhanced browser detection with reliable fallback mechanisms
- Visual profile cards with detailed information
- Consistent browser selection that prevents "no browsers selected" errors
- Improved error handling and logging
- Screenshot capability for testing
- Support for 15+ browsers including Firefox, Chrome, Edge, Brave, Vivaldi, Opera GX, and more

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

Run the original Floorpizer:
```bash
python floorpizer.py
```

Run the new BrowserMigrator:
```bash
python run_browser_migrator.py
```

Or use command line with the original tool:
```bash
floorpizer --source <source_profile> --target <target_profile> --browser <browser_type>
```

## License

MIT License