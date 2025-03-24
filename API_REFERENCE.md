# API Reference

This document provides a comprehensive reference for Floorper's Application Programming Interface (API), detailing classes, methods, and interfaces for developers who want to extend or integrate with Floorper.

## Table of Contents

1. [Core API](#core-api)
2. [Browser Detection API](#browser-detection-api)
3. [Profile Migration API](#profile-migration-api)
4. [Target Integration API](#target-integration-api)
5. [Platform Services API](#platform-services-api)
6. [User Interface API](#user-interface-api)
7. [Utility API](#utility-api)

## Core API

The Core API provides the central functionality of Floorper.

### FloorperController

The main controller class that coordinates the migration process.

```python
class FloorperController:
    """
    Main controller for the Floorper application.
    
    This class coordinates the browser detection, profile migration,
    and target integration processes.
    """
    
    def __init__(self, config=None):
        """
        Initialize the controller.
        
        Args:
            config (dict, optional): Configuration dictionary.
        """
        pass
    
    def detect_browsers(self):
        """
        Detect installed browsers.
        
        Returns:
            list: List of detected browsers.
        """
        pass
    
    def get_browser_profiles(self, browser_id):
        """
        Get profiles for a specific browser.
        
        Args:
            browser_id (str): Browser identifier.
            
        Returns:
            list: List of profiles for the specified browser.
        """
        pass
    
    def migrate_profile(self, source_profile, target_profile, data_types=None, options=None):
        """
        Migrate a source profile to a target profile.
        
        Args:
            source_profile (dict): Source profile information.
            target_profile (dict): Target profile information.
            data_types (list, optional): Data types to migrate.
            options (dict, optional): Migration options.
            
        Returns:
            dict: Migration results.
        """
        pass
    
    def get_migration_status(self, migration_id):
        """
        Get status of a migration process.
        
        Args:
            migration_id (str): Migration identifier.
            
        Returns:
            dict: Migration status.
        """
        pass
    
    def cancel_migration(self, migration_id):
        """
        Cancel a migration process.
        
        Args:
            migration_id (str): Migration identifier.
            
        Returns:
            bool: True if cancelled successfully.
        """
        pass
    
    def register_observer(self, observer):
        """
        Register an observer for migration events.
        
        Args:
            observer (MigrationObserver): Observer to register.
        """
        pass
    
    def unregister_observer(self, observer):
        """
        Unregister an observer.
        
        Args:
            observer (MigrationObserver): Observer to unregister.
        """
        pass
```

### MigrationObserver

Interface for observing migration events.

```python
class MigrationObserver:
    """
    Observer interface for migration events.
    """
    
    def update(self, event, data):
        """
        Update method called when an event occurs.
        
        Args:
            event (str): Event name.
            data (dict): Event data.
        """
        pass
```

### MigrationResult

Class representing the result of a migration operation.

```python
class MigrationResult:
    """
    Result of a migration operation.
    """
    
    def __init__(self, success, message=None, details=None):
        """
        Initialize the migration result.
        
        Args:
            success (bool): Whether the migration was successful.
            message (str, optional): Result message.
            details (dict, optional): Detailed results.
        """
        self.success = success
        self.message = message
        self.details = details or {}
    
    def is_successful(self):
        """
        Check if the migration was successful.
        
        Returns:
            bool: True if successful.
        """
        return self.success
    
    def get_message(self):
        """
        Get the result message.
        
        Returns:
            str: Result message.
        """
        return self.message
    
    def get_details(self):
        """
        Get detailed results.
        
        Returns:
            dict: Detailed results.
        """
        return self.details
```

## Browser Detection API

The Browser Detection API provides functionality for detecting browsers and their profiles.

### BrowserDetector

Class for detecting installed browsers.

```python
class BrowserDetector:
    """
    Detects installed browsers and their profiles.
    """
    
    def __init__(self, platform_utils=None):
        """
        Initialize the browser detector.
        
        Args:
            platform_utils (PlatformUtils, optional): Platform utilities.
        """
        pass
    
    def detect_browsers(self):
        """
        Detect installed browsers.
        
        Returns:
            list: List of detected browsers.
        """
        pass
    
    def get_browser_info(self, browser_id):
        """
        Get information about a specific browser.
        
        Args:
            browser_id (str): Browser identifier.
            
        Returns:
            dict: Browser information.
        """
        pass
    
    def detect_profiles(self, browser_id):
        """
        Detect profiles for a specific browser.
        
        Args:
            browser_id (str): Browser identifier.
            
        Returns:
            list: List of detected profiles.
        """
        pass
    
    def get_profile_info(self, browser_id, profile_path):
        """
        Get information about a specific profile.
        
        Args:
            browser_id (str): Browser identifier.
            profile_path (str): Profile path.
            
        Returns:
            dict: Profile information.
        """
        pass
    
    def register_browser_handler(self, browser_id, handler):
        """
        Register a custom browser handler.
        
        Args:
            browser_id (str): Browser identifier.
            handler (BrowserHandler): Browser handler.
        """
        pass
```

### BrowserHandler

Interface for browser-specific handlers.

```python
class BrowserHandler:
    """
    Interface for browser-specific handlers.
    """
    
    def get_browser_info(self):
        """
        Get information about the browser.
        
        Returns:
            dict: Browser information.
        """
        pass
    
    def detect_profiles(self):
        """
        Detect profiles for the browser.
        
        Returns:
            list: List of detected profiles.
        """
        pass
    
    def get_profile_info(self, profile_path):
        """
        Get information about a specific profile.
        
        Args:
            profile_path (str): Profile path.
            
        Returns:
            dict: Profile information.
        """
        pass
    
    def extract_data(self, profile_path, data_type):
        """
        Extract data from a profile.
        
        Args:
            profile_path (str): Profile path.
            data_type (str): Data type to extract.
            
        Returns:
            object: Extracted data.
        """
        pass
```

### ExoticBrowserHandler

Handler for exotic and text-based browsers.

```python
class ExoticBrowserHandler(BrowserHandler):
    """
    Handler for exotic and text-based browsers.
    """
    
    def __init__(self, browser_id):
        """
        Initialize the exotic browser handler.
        
        Args:
            browser_id (str): Browser identifier.
        """
        pass
    
    # Implements BrowserHandler interface
```

## Profile Migration API

The Profile Migration API provides functionality for migrating browser profiles.

### ProfileMigrator

Class for migrating browser profiles.

```python
class ProfileMigrator:
    """
    Migrates browser profiles.
    """
    
    def __init__(self, browser_detector=None, data_converter=None):
        """
        Initialize the profile migrator.
        
        Args:
            browser_detector (BrowserDetector, optional): Browser detector.
            data_converter (DataConverter, optional): Data converter.
        """
        pass
    
    def migrate(self, source_profile, target_profile, data_types=None, options=None):
        """
        Migrate a source profile to a target profile.
        
        Args:
            source_profile (dict): Source profile information.
            target_profile (dict): Target profile information.
            data_types (list, optional): Data types to migrate.
            options (dict, optional): Migration options.
            
        Returns:
            MigrationResult: Migration result.
        """
        pass
    
    def extract_data(self, profile, data_type):
        """
        Extract data from a profile.
        
        Args:
            profile (dict): Profile information.
            data_type (str): Data type to extract.
            
        Returns:
            object: Extracted data.
        """
        pass
    
    def transform_data(self, data, source_type, target_type, data_type):
        """
        Transform data from source format to target format.
        
        Args:
            data (object): Data to transform.
            source_type (str): Source browser type.
            target_type (str): Target browser type.
            data_type (str): Data type.
            
        Returns:
            object: Transformed data.
        """
        pass
    
    def integrate_data(self, data, target_profile, data_type, options=None):
        """
        Integrate data into a target profile.
        
        Args:
            data (object): Data to integrate.
            target_profile (dict): Target profile information.
            data_type (str): Data type.
            options (dict, optional): Integration options.
            
        Returns:
            bool: True if successful.
        """
        pass
    
    def register_data_handler(self, data_type, handler):
        """
        Register a custom data handler.
        
        Args:
            data_type (str): Data type.
            handler (DataHandler): Data handler.
        """
        pass
```

### DataConverter

Class for converting data between different formats.

```python
class DataConverter:
    """
    Converts data between different formats.
    """
    
    def convert(self, data, source_format, target_format, data_type):
        """
        Convert data from source format to target format.
        
        Args:
            data (object): Data to convert.
            source_format (str): Source format.
            target_format (str): Target format.
            data_type (str): Data type.
            
        Returns:
            object: Converted data.
        """
        pass
    
    def register_converter(self, source_format, target_format, data_type, converter):
        """
        Register a custom converter.
        
        Args:
            source_format (str): Source format.
            target_format (str): Target format.
            data_type (str): Data type.
            converter (Converter): Converter function or object.
        """
        pass
```

### MergeStrategy

Interface for merge strategies.

```python
class MergeStrategy:
    """
    Interface for merge strategies.
    """
    
    def merge(self, source_data, target_data, data_type):
        """
        Merge source data into target data.
        
        Args:
            source_data (object): Source data.
            target_data (object): Target data.
            data_type (str): Data type.
            
        Returns:
            object: Merged data.
        """
        pass
```

## Target Integration API

The Target Integration API provides functionality for integrating data into the target browser.

### TargetIntegrator

Class for integrating data into the target browser.

```python
class TargetIntegrator:
    """
    Integrates data into the target browser.
    """
    
    def __init__(self, browser_detector=None):
        """
        Initialize the target integrator.
        
        Args:
            browser_detector (BrowserDetector, optional): Browser detector.
        """
        pass
    
    def integrate(self, data, target_profile, data_type, options=None):
        """
        Integrate data into a target profile.
        
        Args:
            data (object): Data to integrate.
            target_profile (dict): Target profile information.
            data_type (str): Data type.
            options (dict, optional): Integration options.
            
        Returns:
            bool: True if successful.
        """
        pass
    
    def backup_profile(self, profile_path):
        """
        Create a backup of a profile.
        
        Args:
            profile_path (str): Profile path.
            
        Returns:
            str: Backup path.
        """
        pass
    
    def restore_profile(self, backup_path, profile_path):
        """
        Restore a profile from a backup.
        
        Args:
            backup_path (str): Backup path.
            profile_path (str): Profile path.
            
        Returns:
            bool: True if successful.
        """
        pass
    
    def verify_integration(self, target_profile, data_type):
        """
        Verify integration of data into a target profile.
        
        Args:
            target_profile (dict): Target profile information.
            data_type (str): Data type.
            
        Returns:
            bool: True if verified.
        """
        pass
```

## Platform Services API

The Platform Services API provides platform-specific functionality.

### PlatformUtils

Class for platform-specific utilities.

```python
class PlatformUtils:
    """
    Platform-specific utilities.
    """
    
    @staticmethod
    def get_platform():
        """
        Get the current platform.
        
        Returns:
            str: Platform identifier.
        """
        pass
    
    @staticmethod
    def expand_path(path_template):
        """
        Expand a path template.
        
        Args:
            path_template (str): Path template.
            
        Returns:
            str: Expanded path.
        """
        pass
    
    @staticmethod
    def get_registry_value(key_path, value_name):
        """
        Get a registry value (Windows only).
        
        Args:
            key_path (str): Registry key path.
            value_name (str): Value name.
            
        Returns:
            object: Registry value.
        """
        pass
    
    @staticmethod
    def get_user_data_dir():
        """
        Get the user data directory.
        
        Returns:
            str: User data directory.
        """
        pass
    
    @staticmethod
    def get_app_data_dir():
        """
        Get the application data directory.
        
        Returns:
            str: Application data directory.
        """
        pass
    
    @staticmethod
    def create_directory(path):
        """
        Create a directory.
        
        Args:
            path (str): Directory path.
            
        Returns:
            bool: True if successful.
        """
        pass
    
    @staticmethod
    def copy_file(source, destination):
        """
        Copy a file.
        
        Args:
            source (str): Source path.
            destination (str): Destination path.
            
        Returns:
            bool: True if successful.
        """
        pass
    
    @staticmethod
    def secure_delete(path):
        """
        Securely delete a file.
        
        Args:
            path (str): File path.
            
        Returns:
            bool: True if successful.
        """
        pass
```

### SecurityManager

Class for security-related functionality.

```python
class SecurityManager:
    """
    Security-related functionality.
    """
    
    def __init__(self, platform_utils=None):
        """
        Initialize the security manager.
        
        Args:
            platform_utils (PlatformUtils, optional): Platform utilities.
        """
        pass
    
    def encrypt_data(self, data, key=None):
        """
        Encrypt data.
        
        Args:
            data (bytes): Data to encrypt.
            key (bytes, optional): Encryption key.
            
        Returns:
            bytes: Encrypted data.
        """
        pass
    
    def decrypt_data(self, data, key=None):
        """
        Decrypt data.
        
        Args:
            data (bytes): Data to decrypt.
            key (bytes, optional): Decryption key.
            
        Returns:
            bytes: Decrypted data.
        """
        pass
    
    def hash_data(self, data, salt=None):
        """
        Hash data.
        
        Args:
            data (bytes): Data to hash.
            salt (bytes, optional): Salt.
            
        Returns:
            bytes: Hashed data.
        """
        pass
    
    def verify_hash(self, data, hash_value, salt=None):
        """
        Verify a hash.
        
        Args:
            data (bytes): Data to verify.
            hash_value (bytes): Hash value.
            salt (bytes, optional): Salt.
            
        Returns:
            bool: True if verified.
        """
        pass
    
    def generate_key(self):
        """
        Generate an encryption key.
        
        Returns:
            bytes: Encryption key.
        """
        pass
    
    def secure_random(self, length):
        """
        Generate secure random bytes.
        
        Args:
            length (int): Length of random bytes.
            
        Returns:
            bytes: Random bytes.
        """
        pass
```

## User Interface API

The User Interface API provides functionality for the user interfaces.

### FloorperGUI

Class for the graphical user interface.

```python
class FloorperGUI:
    """
    Graphical user interface.
    """
    
    def __init__(self, controller=None):
        """
        Initialize the GUI.
        
        Args:
            controller (FloorperController, optional): Controller.
        """
        pass
    
    def run(self):
        """
        Run the GUI.
        """
        pass
    
    def show_main_window(self):
        """
        Show the main window.
        """
        pass
    
    def show_browser_selection(self):
        """
        Show the browser selection dialog.
        """
        pass
    
    def show_profile_selection(self, browser_id):
        """
        Show the profile selection dialog.
        
        Args:
            browser_id (str): Browser identifier.
        """
        pass
    
    def show_options_dialog(self):
        """
        Show the options dialog.
        """
        pass
    
    def show_progress_dialog(self, migration_id):
        """
        Show the progress dialog.
        
        Args:
            migration_id (str): Migration identifier.
        """
        pass
    
    def show_result_dialog(self, result):
        """
        Show the result dialog.
        
        Args:
            result (MigrationResult): Migration result.
        """
        pass
```

### FloorperTUI

Class for the text-based user interface.

```python
class FloorperTUI:
    """
    Text-based user interface.
    """
    
    def __init__(self, controller=None):
        """
        Initialize the TUI.
        
        Args:
            controller (FloorperController, optional): Controller.
        """
        pass
    
    def run(self):
        """
        Run the TUI.
        """
        pass
    
    def show_main_screen(self):
        """
        Show the main screen.
        """
        pass
    
    def show_browser_selection(self):
        """
        Show the browser selection screen.
        """
        pass
    
    def show_profile_selection(self, browser_id):
        """
        Show the profile selection screen.
        
        Args:
            browser_id (str): Browser identifier.
        """
        pass
    
    def show_options_screen(self):
        """
        Show the options screen.
        """
        pass
    
    def show_progress_screen(self, migration_id):
        """
        Show the progress screen.
        
        Args:
            migration_id (str): Migration identifier.
        """
        pass
    
    def show_result_screen(self, result):
        """
        Show the result screen.
        
        Args:
            result (MigrationResult): Migration result.
        """
        pass
```

### FloorperCLI

Class for the command-line interface.

```python
class FloorperCLI:
    """
    Command-line interface.
    """
    
    def __init__(self, controller=None):
        """
        Initialize the CLI.
        
        Args:
            controller (FloorperController, optional): Controller.
        """
        pass
    
    def run(self, args=None):
        """
        Run the CLI.
        
        Args:
            args (list, optional): Command-line arguments.
            
        Returns:
            int: Exit code.
        """
        pass
    
    def parse_args(self, args=None):
        """
        Parse command-line arguments.
        
        Args:
            args (list, optional): Command-line arguments.
            
        Returns:
            argparse.Namespace: Parsed arguments.
        """
        pass
    
    def execute_command(self, args):
        """
        Execute a command.
        
        Args:
            args (argparse.Namespace): Parsed arguments.
            
        Returns:
            int: Exit code.
        """
        pass
    
    def show_progress(self, migration_id):
        """
        Show migration progress.
        
        Args:
            migration_id (str): Migration identifier.
        """
        pass
    
    def show_result(self, result):
        """
        Show migration result.
        
        Args:
            result (MigrationResult): Migration result.
        """
        pass
```

## Utility API

The Utility API provides various utility functions.

### Logger

Class for logging.

```python
class Logger:
    """
    Logging functionality.
    """
    
    def __init__(self, log_file=None, log_level=None):
        """
        Initialize the logger.
        
        Args:
            log_file (str, optional): Log file path.
            log_level (int, optional): Log level.
        """
        pass
    
    def debug(self, message):
        """
        Log a debug message.
        
        Args:
            message (str): Message to log.
        """
        pass
    
    def info(self, message):
        """
        Log an info message.
        
        Args:
            message (str): Message to log.
        """
        pass
    
    def warning(self, message):
        """
        Log a warning message.
        
        Args:
            message (str): Message to log.
        """
        pass
    
    def error(self, message):
        """
        Log an error message.
        
        Args:
            message (str): Message to log.
        """
        pass
    
    def critical(self, message):
        """
        Log a critical message.
        
        Args:
            message (str): Message to log.
        """
        pass
    
    def set_log_level(self, log_level):
        """
        Set the log level.
        
        Args:
            log_level (int): Log level.
        """
        pass
    
    def set_log_file(self, log_file):
        """
        Set the log file.
        
        Args:
            log_file (str): Log file path.
        """
        pass
```

### ConfigManager

Class for managing configuration.

```python
class ConfigManager:
    """
    Configuration management.
    """
    
    def __init__(self, config_file=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str, optional): Configuration file path.
        """
        pass
    
    def load_config(self, config_file=None):
        """
        Load configuration from a file.
        
        Args:
            config_file (str, optional): Configuration file path.
            
        Returns:
            dict: Configuration.
        """
        pass
    
    def save_config(self, config, config_file=None):
        """
        Save configuration to a file.
        
        Args:
            config (dict): Configuration.
            config_file (str, optional): Configuration file path.
            
        Returns:
            bool: True if successful.
        """
        pass
    
    def get_config(self):
        """
        Get the current configuration.
        
        Returns:
            dict: Configuration.
        """
        pass
    
    def set_config(self, config):
        """
        Set the current configuration.
        
        Args:
            config (dict): Configuration.
        """
        pass
    
    def get_value(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key (str): Configuration key.
            default (object, optional): Default value.
            
        Returns:
            object: Configuration value.
        """
        pass
    
    def set_value(self, key, value):
        """
        Set a configuration value.
        
        Args:
            key (str): Configuration key.
            value (object): Configuration value.
        """
        pass
```

This API reference provides a comprehensive overview of Floorper's programming interface. For more detailed information about implementation details, refer to the source code and developer documentation.
