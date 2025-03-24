# Architecture Overview

This document provides a detailed description of Floorper's architecture, design patterns, and system components.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Diagram](#component-diagram)
3. [Data Flow](#data-flow)
4. [Design Patterns](#design-patterns)
5. [Interface Architecture](#interface-architecture)
6. [Cross-Platform Design](#cross-platform-design)
7. [Security Architecture](#security-architecture)

## System Architecture

Floorper follows a modular, layered architecture that separates concerns and promotes maintainability:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                     User Interfaces                         │
│                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐  │
│  │             │      │             │      │             │  │
│  │     GUI     │      │     TUI     │      │     CLI     │  │
│  │  (PyQt6)    │      │   (Rich)    │      │ (argparse)  │  │
│  │             │      │             │      │             │  │
│  └─────────────┘      └─────────────┘      └─────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    Application Core                         │
│                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐  │
│  │             │      │             │      │             │  │
│  │   Browser   │      │   Profile   │      │   Target    │  │
│  │  Detection  │◄────▶│  Migration  │◄────▶│ Integration │  │
│  │             │      │             │      │             │  │
│  └─────────────┘      └─────────────┘      └─────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    Platform Services                        │
│                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐  │
│  │             │      │             │      │             │  │
│  │    File     │      │   System    │      │  Security   │  │
│  │   Access    │      │  Detection  │      │  Services   │  │
│  │             │      │             │      │             │  │
│  └─────────────┘      └─────────────┘      └─────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Architectural Layers

1. **User Interfaces Layer**
   - Responsible for user interaction
   - Implements GUI, TUI, and CLI interfaces
   - Handles user input and output formatting
   - Maintains separation from business logic

2. **Application Core Layer**
   - Contains the core business logic
   - Implements browser detection, profile migration, and target integration
   - Maintains platform independence
   - Provides services to the UI layer

3. **Platform Services Layer**
   - Handles platform-specific operations
   - Provides file system access, system detection, and security services
   - Abstracts platform differences
   - Enables cross-platform compatibility

## Component Diagram

The following diagram shows the main components and their relationships:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  FloorperGUI    │     │  FloorperTUI    │     │  FloorperCLI    │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                      FloorperController                         │
│                                                                 │
└────────┬────────────────────────┬───────────────────────┬───────┘
         │                        │                       │
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│ BrowserDetector │     │ ProfileMigrator │     │ TargetIntegrator│
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  PlatformUtils  │     │  DataConverter  │     │ SecurityManager │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Components

1. **FloorperGUI / FloorperTUI / FloorperCLI**
   - Interface-specific implementations
   - Handle user interaction and display
   - Communicate with controller

2. **FloorperController**
   - Central coordinator
   - Manages workflow between components
   - Handles error conditions
   - Provides logging and reporting

3. **BrowserDetector**
   - Detects installed browsers
   - Identifies browser profiles
   - Extracts profile metadata
   - Supports multiple platforms

4. **ProfileMigrator**
   - Extracts data from source profiles
   - Transforms data between formats
   - Handles deduplication
   - Manages migration process

5. **TargetIntegrator**
   - Integrates transformed data into Floorp
   - Ensures data integrity
   - Handles conflicts
   - Verifies successful integration

6. **PlatformUtils**
   - Provides platform-specific utilities
   - Handles file system operations
   - Manages registry access (Windows)
   - Detects system configuration

7. **DataConverter**
   - Converts between data formats
   - Implements transformation algorithms
   - Handles format-specific quirks
   - Ensures data integrity

8. **SecurityManager**
   - Manages secure access to sensitive data
   - Handles encryption/decryption
   - Manages permissions
   - Ensures secure operations

## Data Flow

The data flow through the system follows this sequence:

1. **User Input**
   - User selects source browser, target profile, and options
   - Interface captures and validates input

2. **Browser Detection**
   - System detects installed browsers
   - Identifies available profiles
   - Extracts profile metadata

3. **Profile Selection**
   - User selects specific source profile
   - System validates profile accessibility

4. **Data Extraction**
   - System extracts data from source profile
   - Reads bookmarks, history, passwords, etc.
   - Validates data integrity

5. **Data Transformation**
   - Converts data to target format
   - Applies transformation rules
   - Performs deduplication if requested

6. **Target Integration**
   - Creates backup of target profile (if enabled)
   - Integrates transformed data into target
   - Resolves conflicts using selected strategy

7. **Verification**
   - Verifies successful integration
   - Validates data integrity
   - Reports results to user

8. **Cleanup**
   - Removes temporary files
   - Securely deletes sensitive data
   - Finalizes operation

## Design Patterns

Floorper implements several design patterns to promote maintainability and extensibility:

### Model-View-Controller (MVC)

The application follows the MVC pattern:
- **Model**: Browser profiles, migration data, configuration
- **View**: GUI, TUI, and CLI interfaces
- **Controller**: FloorperController and component controllers

### Factory Method

Used for creating browser-specific handlers:

```python
class BrowserHandlerFactory:
    @staticmethod
    def create_handler(browser_type):
        if browser_type == "firefox":
            return FirefoxHandler()
        elif browser_type == "chrome":
            return ChromeHandler()
        elif browser_type == "edge":
            return EdgeHandler()
        # More handlers...
        else:
            return GenericHandler()
```

### Strategy Pattern

Used for implementing different merge strategies:

```python
class MergeStrategy:
    def merge(self, source_data, target_data):
        pass

class SmartMergeStrategy(MergeStrategy):
    def merge(self, source_data, target_data):
        # Smart merge implementation
        pass

class OverwriteMergeStrategy(MergeStrategy):
    def merge(self, source_data, target_data):
        # Overwrite implementation
        pass

class AppendMergeStrategy(MergeStrategy):
    def merge(self, source_data, target_data):
        # Append implementation
        pass
```

### Observer Pattern

Used for progress reporting and logging:

```python
class MigrationObserver:
    def update(self, event, data):
        pass

class LoggingObserver(MigrationObserver):
    def update(self, event, data):
        # Log the event
        pass

class ProgressObserver(MigrationObserver):
    def update(self, event, data):
        # Update progress display
        pass
```

### Adapter Pattern

Used for handling different browser data formats:

```python
class BookmarkAdapter:
    def adapt(self, source_format, target_format, data):
        pass

class ChromeToFirefoxBookmarkAdapter(BookmarkAdapter):
    def adapt(self, source_format, target_format, data):
        # Convert Chrome bookmarks to Firefox format
        pass
```

## Interface Architecture

### GUI Architecture

The GUI is built using PyQt6 and follows a component-based architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      MainWindow                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                 │                 │
     ┌───────────┘                 └───────────┐
     │                                         │
     ▼                                         ▼
┌─────────────────┐                   ┌─────────────────┐
│                 │                   │                 │
│  BrowserPanel   │                   │  OptionsPanel   │
│                 │                   │                 │
└─────────────────┘                   └─────────────────┘
     │                                         │
     │                                         │
     ▼                                         ▼
┌─────────────────┐                   ┌─────────────────┐
│                 │                   │                 │
│  ProfileCard    │                   │  DataTypeSelector│
│                 │                   │                 │
└─────────────────┘                   └─────────────────┘
                                                │
                                                │
                                                ▼
                                      ┌─────────────────┐
                                      │                 │
                                      │ MergeStrategySelector│
                                      │                 │
                                      └─────────────────┘
```

### TUI Architecture

The TUI is built using the Rich library and follows a similar component-based approach:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                        TUIApp                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                 │                 │
     ┌───────────┘                 └───────────┐
     │                                         │
     ▼                                         ▼
┌─────────────────┐                   ┌─────────────────┐
│                 │                   │                 │
│  BrowserPanel   │                   │  OptionsPanel   │
│                 │                   │                 │
└─────────────────┘                   └─────────────────┘
     │                                         │
     │                                         │
     ▼                                         ▼
┌─────────────────┐                   ┌─────────────────┐
│                 │                   │                 │
│  ProfileList    │                   │  DataTypeList   │
│                 │                   │                 │
└─────────────────┘                   └─────────────────┘
                 │                                │
                 └────────────┬───────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │                 │
                    │    LogPanel     │
                    │                 │
                    └─────────────────┘
```

### CLI Architecture

The CLI is built using argparse and follows a command-pattern architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      CLIParser                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                     CommandHandler                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                 │                  │
         │                 │                  │
         ▼                 ▼                  ▼
┌─────────────────┐┌─────────────────┐┌─────────────────┐
│                 ││                 ││                 │
│  MigrateCommand ││  ListCommand    ││  ConfigCommand  │
│                 ││                 ││                 │
└─────────────────┘└─────────────────┘└─────────────────┘
```

## Cross-Platform Design

Floorper's cross-platform architecture uses several strategies to ensure compatibility:

### Platform Abstraction Layer

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                  Platform-Independent Code                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                   Platform Abstraction Layer                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                 │                  │               │
         │                 │                  │               │
         ▼                 ▼                  ▼               ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐  ┌─────────────┐
│             │    │             │    │             │  │             │
│  Windows    │    │  macOS      │    │  Linux      │  │  Other OS   │
│  Impl       │    │  Impl       │    │  Impl       │  │  Impl       │
│             │    │             │    │             │  │             │
└─────────────┘    └─────────────┘    └─────────────┘  └─────────────┘
```

### Platform Detection

```python
def get_platform():
    """Detect the current platform."""
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

### Platform-Specific Implementations

```python
class PathProvider:
    @staticmethod
    def get_browser_paths(browser_id):
        platform = get_platform()
        
        if platform == "windows":
            return WindowsPathProvider.get_browser_paths(browser_id)
        elif platform == "macos":
            return MacOSPathProvider.get_browser_paths(browser_id)
        elif platform == "linux":
            return LinuxPathProvider.get_browser_paths(browser_id)
        elif platform == "haiku":
            return HaikuPathProvider.get_browser_paths(browser_id)
        elif platform == "os2":
            return OS2PathProvider.get_browser_paths(browser_id)
        else:
            return GenericPathProvider.get_browser_paths(browser_id)
```

## Security Architecture

Floorper implements several security measures:

### Secure Data Handling

- Sensitive data is kept in memory only as long as necessary
- Temporary files are securely deleted after use
- Passwords are never stored in plaintext

### Encryption

- Uses platform-specific encryption APIs when available
- Implements secure encryption for password handling
- Supports master password for accessing encrypted data

### Permission Management

- Checks for necessary permissions before accessing files
- Provides clear error messages for permission issues
- Suggests elevation when necessary

### Backup System

- Creates automatic backups before modifying profiles
- Implements verification to ensure backup integrity
- Provides restore functionality for recovery

This architecture document provides a high-level overview of Floorper's design. For more detailed information about specific components, refer to the API Reference and Developer Documentation.
