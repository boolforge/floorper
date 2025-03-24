# Floorper Detailed Refactoring Plan

## Project Overview
Floorper (Floorp + Import + Merger) is a universal browser profile migration tool designed to migrate profiles from various browsers to Floorp. The project currently consists of three main components:
- **browsermigrator**: Handles browser detection and profile migration
- **floorpizer**: Provides migration functionality with CLI and GUI interfaces
- **floorper**: Core functionality that needs to be expanded

## Current Architecture Analysis
The current codebase has several issues that need to be addressed:
1. Duplicate functionality between browsermigrator and floorpizer
2. Inconsistent naming conventions and coding styles
3. Multiple implementations of similar interfaces (TUI, GUI)
4. Lack of unified error handling and logging
5. Incomplete integration of components

## Refactoring Goals
1. Unify browsermigrator and floorpizer into a single coherent floorper package
2. Implement three consistent interfaces: GUI (PyQt6), TUI (Textual), and CLI
3. Enhance browser detection to support exotic and retro browsers
4. Add backup restoration functionality
5. Improve code quality, readability, and maintainability
6. Optimize performance and resource usage
7. Enhance cross-platform compatibility
8. Improve documentation

## Detailed Implementation Plan

### 1. Code Structure Reorganization
```
floorper/
├── floorper/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── browser_detector.py
│   │   ├── profile_migrator.py
│   │   ├── backup_manager.py
│   │   └── constants.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── tui.py
│   │   └── gui.py
│   ├── browsers/
│   │   ├── __init__.py
│   │   ├── firefox_based.py
│   │   ├── chromium_based.py
│   │   ├── exotic.py
│   │   └── retro.py
│   └── utils/
│       ├── __init__.py
│       ├── file_operations.py
│       ├── database_operations.py
│       └── platform_utils.py
├── bin/
│   ├── floorper-cli
│   ├── floorper-tui
│   └── floorper-gui
├── tests/
│   ├── test_browser_detector.py
│   ├── test_profile_migrator.py
│   ├── test_backup_manager.py
│   └── test_interfaces.py
├── docs/
│   ├── api/
│   ├── user_guide/
│   └── developer_guide/
├── setup.py
├── requirements.txt
└── README.md
```

### 2. Core Module Refactoring

#### 2.1 Browser Detector
- Consolidate browser detection logic from both browsermigrator and floorpizer
- Implement platform-specific detection strategies
- Add support for exotic and retro browsers
- Improve detection reliability with multiple fallback methods
- Implement browser profile analysis

#### 2.2 Profile Migrator
- Unify migration logic from both components
- Implement smart merging strategies
- Add support for all data types (bookmarks, history, passwords, cookies, extensions, preferences, sessions)
- Implement progress reporting and cancellation
- Add validation and error recovery

#### 2.3 Backup Manager
- Implement backup creation before migration
- Add backup restoration functionality
- Support incremental backups
- Implement backup verification

### 3. Interface Development

#### 3.1 Command Line Interface (CLI)
- Implement comprehensive command-line options
- Support batch processing and scripting
- Add verbose output modes
- Implement progress indicators

#### 3.2 Text User Interface (TUI)
- Implement modern TUI using Textual library
- Create consistent navigation and interaction patterns
- Add visual elements like progress bars, tables, and panels
- Support keyboard shortcuts and mouse interaction

#### 3.3 Graphical User Interface (GUI)
- Enhance existing PyQt6 implementation
- Implement consistent design language
- Add advanced features like drag-and-drop
- Improve responsiveness and feedback

### 4. Browser Support Enhancement

#### 4.1 Firefox-based Browsers
- Improve support for Firefox derivatives (LibreWolf, Waterfox, Pale Moon, etc.)
- Add support for legacy Firefox versions
- Implement specialized handlers for Firefox-specific data formats

#### 4.2 Chromium-based Browsers
- Enhance support for Chromium derivatives (Chrome, Edge, Brave, Opera, etc.)
- Add support for legacy Chromium versions
- Implement specialized handlers for Chromium-specific data formats

#### 4.3 Exotic Browsers
- Add support for less common browsers (qutebrowser, Dillo, NetSurf, etc.)
- Implement specialized detection and migration strategies

#### 4.4 Text-based and Retro Browsers
- Add support for text-based browsers (ELinks, Links, Lynx, w3m)
- Implement support for historical browsers found in backups
- Create specialized handlers for non-standard data formats

### 5. Cross-platform Compatibility

#### 5.1 Windows Support
- Enhance registry-based detection
- Improve path handling for Windows-specific locations
- Add support for Windows-specific browsers

#### 5.2 macOS Support
- Improve detection in macOS-specific locations
- Add support for macOS-specific browsers
- Enhance handling of macOS security restrictions

#### 5.3 Linux Support
- Improve detection across various Linux distributions
- Add support for Linux-specific browsers
- Enhance XDG compliance

#### 5.4 Other Platforms
- Add support for Haiku
- Add support for OS/2
- Implement fallback strategies for unknown platforms

### 6. Performance Optimization

#### 6.1 Memory Usage
- Reduce memory footprint during migration
- Implement streaming for large data sets
- Optimize data structures

#### 6.2 Processing Speed
- Implement parallel processing where applicable
- Optimize database operations
- Add caching for frequently accessed data

#### 6.3 Startup Time
- Implement lazy loading
- Optimize import structure
- Reduce initialization overhead

### 7. Documentation Enhancement

#### 7.1 User Documentation
- Update installation instructions
- Create comprehensive user guides for all interfaces
- Add troubleshooting section
- Document supported browsers and data types

#### 7.2 Developer Documentation
- Document architecture and design decisions
- Create API reference
- Add contribution guidelines
- Document testing procedures

#### 7.3 Code Documentation
- Improve inline documentation
- Add type hints
- Create architecture diagrams
- Document browser-specific implementations

## Implementation Timeline

### Phase 1: Core Refactoring
- Consolidate browser detection
- Unify profile migration
- Implement backup manager
- Remove duplicate code

### Phase 2: Interface Development
- Implement CLI enhancements
- Develop modern TUI with Textual
- Enhance PyQt6 GUI

### Phase 3: Browser Support
- Enhance Firefox-based browser support
- Improve Chromium-based browser support
- Add exotic browser support
- Implement text-based and retro browser support

### Phase 4: Testing and Optimization
- Implement comprehensive tests
- Optimize performance
- Enhance cross-platform compatibility
- Fix bugs and edge cases

### Phase 5: Documentation and Finalization
- Update all documentation
- Create architecture diagrams
- Final code review
- Release preparation

## Conclusion
This refactoring plan aims to transform Floorper into a unified, robust, and user-friendly tool for browser profile migration. By consolidating the existing components, enhancing browser support, and improving the user interfaces, Floorper will provide a comprehensive solution for migrating profiles to Floorp from a wide range of browsers across multiple platforms.
