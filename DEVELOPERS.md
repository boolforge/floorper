# Floorper Developer Documentation

This comprehensive technical documentation is intended for developers who want to understand, modify, or contribute to the Floorper project. It covers the software architecture, data formats, transformation processes, and development guidelines.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Structure](#module-structure)
3. [Data Formats](#data-formats)
4. [Browser Profile Structure](#browser-profile-structure)
5. [Migration Process](#migration-process)
6. [Cross-Platform Implementation](#cross-platform-implementation)
7. [GUI Implementation](#gui-implementation)
8. [Testing Framework](#testing-framework)
9. [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

Floorper follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Browser        │────▶│  Profile        │────▶│  Target         │
│  Detection      │     │  Migration      │     │  Integration    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                       ▲
        │                       │                       │
        │                       │                       │
        │                       │                       │
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                       User Interface                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Browser Detection**: Identifies installed browsers and their profiles
2. **Profile Migration**: Extracts and transforms profile data
3. **Target Integration**: Integrates transformed data into Floorp
4. **User Interface**: Provides interaction through GUI or CLI

## Module Structure

The codebase is organized into the following key modules:

### browsermigrator/
- `browser_detector.py`: Detects installed browsers and their profiles
- `profile_migrator.py`: Handles extraction and migration of profile data
- `constants.py`: Defines constants, paths, and browser information
- `exotic_browser_handler.py`: Specialized handling for non-mainstream browsers
- `main_window_improved.py`: PyQt6 GUI implementation
- `profile_card.py`: UI component for displaying profile information

### floorpizer/
- `floorpizer.py`: Core integration with Floorp
- `qt_gui.py`: Legacy Qt GUI implementation
- `browser_detection.py`: Legacy browser detection
- `profile_migration.py`: Legacy profile migration
- `utils.py`: Utility functions

### Root Level
- `run_floorper_qt.py`: Main entry point for PyQt6 GUI
- `run_browser_migrator.py`: Legacy entry point
- `run_qt_floorpizer.py`: Legacy Qt GUI entry point

## Data Formats

### Browser Profile Data

Browser profile data is represented as structured dictionaries:

```python
profile = {
    "name": "Profile Name",
    "path": "/path/to/profile",
    "browser_type": "firefox",
    "stats": {
        "bookmarks": 120,
        "history": 1500,
        "cookies": 300,
        "passwords": 25,
        "tabs": 8,
        "windows": 2,
        "extensions": 15,
        "certificates": 5,
        "forms": 30,
        "permissions": 40
    }
}
```

### Migration Configuration

Migration settings are represented as:

```python
migration_config = {
    "source_profile": profile,
    "target_profile": target_profile,
    "data_types": ["bookmarks", "history", "passwords", "cookies"],
    "options": {
        "merge_strategy": "smart",  # "smart", "overwrite", "append"
        "backup": True,
        "deduplicate": True
    }
}
```

## Browser Profile Structure

### Firefox-based Browsers

Firefox and its derivatives store profile data in a directory structure:

```
profile_directory/
├── places.sqlite       # Bookmarks and history
├── cookies.sqlite      # Cookies
├── key4.db             # Passwords
├── logins.json         # Additional login data
├── cert9.db            # Certificates
├── permissions.sqlite  # Site permissions
├── extensions/         # Installed extensions
├── sessionstore.jsonlz4 # Session data
└── prefs.js            # Preferences
```

Key files and their formats:
- `places.sqlite`: SQLite database with tables for bookmarks and history
- `cookies.sqlite`: SQLite database with cookie information
- `key4.db`: SQLite database with encrypted password data
- `sessionstore.jsonlz4`: Mozilla-specific compressed JSON format

### Chrome-based Browsers

Chrome and its derivatives use a different structure:

```
profile_directory/
├── Bookmarks           # JSON file with bookmarks
├── History             # SQLite database with history
├── Cookies             # SQLite database with cookies
├── Login Data          # SQLite database with passwords
├── Preferences         # JSON file with preferences
├── Extensions/         # Directory with extensions
└── Sessions/           # Directory with session data
```

Key files and their formats:
- `Bookmarks`: JSON file with a hierarchical bookmark structure
- `History`: SQLite database with tables for visits and URLs
- `Login Data`: SQLite database with encrypted password data
- `Preferences`: JSON file with user preferences

### Text-based Browsers

Text-based browsers typically use simpler formats:

```
profile_directory/
├── bookmarks.html      # HTML file with bookmarks (w3m)
├── bookmarks           # Text file with bookmarks (ELinks)
├── history             # Text file with history (w3m)
├── globhist            # Text file with history (ELinks)
└── cookies             # Text file with cookies
```

## Migration Process

The migration process follows these steps:

1. **Detection**: Identify source and target browser profiles
2. **Extraction**: Read data from source profile
3. **Transformation**: Convert data to target format
4. **Deduplication**: Remove duplicate entries (optional)
5. **Integration**: Write transformed data to target profile
6. **Verification**: Validate successful migration

### Data Transformation Algorithms

#### Bookmark Transformation

For converting between different bookmark formats:

```python
def transform_bookmarks(source_bookmarks, source_type, target_type):
    """
    Transform bookmarks from source format to target format.
    
    Args:
        source_bookmarks: Source bookmarks data
        source_type: Source browser type ('firefox', 'chrome', etc.)
        target_type: Target browser type ('firefox', 'chrome', etc.)
        
    Returns:
        Transformed bookmarks in target format
    """
    if source_type == 'firefox' and target_type == 'firefox':
        # Direct copy for same family
        return copy.deepcopy(source_bookmarks)
    
    if source_type == 'firefox' and target_type == 'chrome':
        # Convert Firefox bookmarks to Chrome format
        return _firefox_to_chrome_bookmarks(source_bookmarks)
    
    if source_type == 'chrome' and target_type == 'firefox':
        # Convert Chrome bookmarks to Firefox format
        return _chrome_to_firefox_bookmarks(source_bookmarks)
    
    # For other combinations, use intermediate format
    intermediate = _to_intermediate_format(source_bookmarks, source_type)
    return _from_intermediate_format(intermediate, target_type)
```

#### History Transformation

Similar approach for history data:

```python
def transform_history(source_history, source_type, target_type):
    """
    Transform history from source format to target format.
    
    Args:
        source_history: Source history data
        source_type: Source browser type ('firefox', 'chrome', etc.)
        target_type: Target browser type ('firefox', 'chrome', etc.)
        
    Returns:
        Transformed history in target format
    """
    # Similar implementation as bookmark transformation
    # with specific handling for history data structures
```

### Deduplication Algorithm

For removing duplicate bookmarks:

```python
def deduplicate_bookmarks(bookmarks, strategy='url'):
    """
    Remove duplicate bookmarks.
    
    Args:
        bookmarks: List of bookmarks
        strategy: Deduplication strategy ('url', 'title', 'both')
        
    Returns:
        Deduplicated bookmarks
    """
    seen = set()
    result = []
    
    for bookmark in bookmarks:
        key = None
        
        if strategy == 'url':
            key = bookmark['url']
        elif strategy == 'title':
            key = bookmark['title']
        elif strategy == 'both':
            key = f"{bookmark['url']}|{bookmark['title']}"
        
        if key not in seen:
            seen.add(key)
            result.append(bookmark)
    
    return result
```

## Cross-Platform Implementation

Floorper supports multiple platforms through platform-specific code paths:

### Platform Detection

```python
def get_platform():
    """
    Detect the current platform.
    
    Returns:
        String identifying the platform ('windows', 'macos', 'linux', etc.)
    """
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "haiku1":
        return "haiku"
    elif sys.platform == "os2emx":
        return "os2"
    else:
        return "other"
```

### Platform-Specific Path Handling

```python
def get_profile_paths(browser_id):
    """
    Get profile paths for a browser on the current platform.
    
    Args:
        browser_id: Browser identifier
        
    Returns:
        List of possible profile paths
    """
    platform = get_platform()
    paths = []
    
    # Get browser info
    browser_info = BROWSERS.get(browser_id, {})
    
    # Get paths for current platform
    for path_template in browser_info.get("profile_paths", []):
        expanded_path = expand_path(path_template)
        
        # Filter paths by platform
        if platform == "windows" and "AppData" in expanded_path:
            paths.append(expanded_path)
        elif platform == "linux" and ("~/.config" in path_template or "~/.mozilla" in path_template):
            paths.append(expanded_path)
        elif platform == "macos" and "Library/Application Support" in expanded_path:
            paths.append(expanded_path)
        # Additional platform checks...
    
    return paths
```

### Registry Access (Windows)

```python
def get_registry_info(browser_id):
    """
    Get browser information from Windows registry.
    
    Args:
        browser_id: Browser identifier
        
    Returns:
        Dictionary with registry information
    """
    if get_platform() != "windows":
        return {}
    
    result = {}
    
    try:
        import winreg
        
        # Get registry paths for browser
        browser_info = BROWSERS.get(browser_id, {})
        registry_paths = browser_info.get("registry_paths", [])
        
        for reg_path in registry_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    # Read values
                    # ...
            except WindowsError:
                # Try current user
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        # Read values
                        # ...
                except WindowsError:
                    continue
    except ImportError:
        # winreg not available
        pass
    
    return result
```

## GUI Implementation

The PyQt6 GUI is implemented using a component-based architecture:

### Main Window

The main window (`FloorperWindow`) serves as the container for all UI components and manages the application flow.

### Profile Card

The `ProfileCard` component displays information about a browser profile and provides interaction options.

### Worker Threads

Background operations use Qt's worker thread mechanism:

```python
class MigrationWorker(QObject):
    """Worker for performing migration in a background thread."""
    
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, migration_config):
        super().__init__()
        self.migration_config = migration_config
        
    def run(self):
        """Perform the migration process."""
        try:
            # Migration steps...
            self.log.emit("Starting migration...")
            
            # Report progress
            self.progress.emit(25)
            
            # More steps...
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
```

### Theme Support

The application supports light and dark themes through Qt stylesheets:

```python
def apply_theme(app, theme="light"):
    """
    Apply theme to application.
    
    Args:
        app: QApplication instance
        theme: Theme name ('light' or 'dark')
    """
    if theme == "dark":
        app.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #2D2D30;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            /* More style rules... */
        """)
    else:
        app.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #F0F0F0;
                color: #000000;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            /* More style rules... */
        """)
```

## Testing Framework

Floorper uses a comprehensive testing approach:

### Unit Tests

Unit tests focus on individual components:

```python
def test_browser_detection():
    """Test browser detection functionality."""
    detector = BrowserDetector()
    browsers = detector.detect_browsers()
    
    # Assertions
    assert isinstance(browsers, list)
    assert len(browsers) > 0
    
    # More specific tests...
```

### Integration Tests

Integration tests verify component interactions:

```python
def test_profile_migration():
    """Test profile migration process."""
    # Setup test profiles
    source_profile = create_test_profile("firefox")
    target_profile = create_test_profile("floorp")
    
    # Perform migration
    migrator = ProfileMigrator()
    result = migrator.migrate(source_profile, target_profile)
    
    # Verify results
    assert result.success
    assert os.path.exists(os.path.join(target_profile["path"], "places.sqlite"))
    # More assertions...
```

### System Tests

System tests validate the entire application:

```python
def test_end_to_end_migration():
    """Test end-to-end migration process."""
    # Setup test environment
    setup_test_environment()
    
    # Run application with test parameters
    result = run_application([
        "--source", "firefox",
        "--target", "/path/to/test/floorp/profile",
        "--data-types", "bookmarks,history"
    ])
    
    # Verify results
    assert result.exit_code == 0
    # More assertions...
```

## Contributing Guidelines

### Code Style

Floorper follows PEP 8 with these additional guidelines:

- Maximum line length: 100 characters
- Docstrings: Google style
- Import order: standard library, third-party, local
- Class organization: constants, class variables, `__init__`, public methods, private methods

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Ensure all tests pass
5. Submit pull request with detailed description

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes
- `refactor`: Code restructuring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Example:
```
feat: Add support for Lynx browser

Implement detection and migration for Lynx text-based browser.
This includes bookmark and history migration.

Closes #123
```

## Performance Considerations

### Memory Optimization

For handling large profiles:

```python
def process_large_history(history_db_path, target_db_path):
    """
    Process large history database with minimal memory usage.
    
    Args:
        history_db_path: Path to source history database
        target_db_path: Path to target history database
    """
    # Connect to databases
    source_conn = sqlite3.connect(f"file:{history_db_path}?mode=ro", uri=True)
    target_conn = sqlite3.connect(target_db_path)
    
    # Process in batches
    batch_size = 1000
    offset = 0
    
    while True:
        # Read batch
        source_cursor = source_conn.cursor()
        source_cursor.execute(
            "SELECT url, title, last_visit_date FROM moz_places LIMIT ? OFFSET ?",
            (batch_size, offset)
        )
        batch = source_cursor.fetchall()
        
        if not batch:
            break
        
        # Process batch
        target_cursor = target_conn.cursor()
        target_conn.executemany(
            "INSERT OR IGNORE INTO moz_places (url, title, last_visit_date) VALUES (?, ?, ?)",
            batch
        )
        target_conn.commit()
        
        # Move to next batch
        offset += batch_size
    
    # Close connections
    source_conn.close()
    target_conn.close()
```

### Parallel Processing

For improved performance:

```python
def migrate_profile_parallel(source_profile, target_profile, data_types):
    """
    Migrate profile data using parallel processing.
    
    Args:
        source_profile: Source profile information
        target_profile: Target profile information
        data_types: List of data types to migrate
    """
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit migration tasks
        futures = []
        
        for data_type in data_types:
            future = executor.submit(
                migrate_data_type,
                source_profile,
                target_profile,
                data_type
            )
            futures.append((data_type, future))
        
        # Process results
        results = {}
        for data_type, future in futures:
            try:
                results[data_type] = future.result()
            except Exception as e:
                results[data_type] = {"success": False, "error": str(e)}
    
    return results
```

## Security Considerations

### Password Handling

Secure handling of sensitive data:

```python
def migrate_passwords(source_profile, target_profile):
    """
    Migrate passwords securely.
    
    Args:
        source_profile: Source profile information
        target_profile: Target profile information
    """
    # Import encryption libraries
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    
    # Extract encrypted data
    # ...
    
    # Decrypt using appropriate method for source browser
    # ...
    
    # Re-encrypt for target browser
    # ...
    
    # Securely delete temporary decrypted data
    # ...
```

### Data Protection

Ensuring data integrity:

```python
def backup_profile(profile_path):
    """
    Create backup of profile before modification.
    
    Args:
        profile_path: Path to profile
        
    Returns:
        Path to backup
    """
    import datetime
    import shutil
    
    # Create timestamped backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{profile_path}_backup_{timestamp}"
    
    # Create backup
    shutil.copytree(profile_path, backup_path)
    
    return backup_path
```

This documentation provides a comprehensive overview of the Floorper project from a technical perspective. Developers should refer to the actual code for the most up-to-date implementation details.
