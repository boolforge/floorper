"""
Utility functions for Floorpizer.
Contains common operations and helper functions.
"""

import os
import sys
import json
import logging
import hashlib
import sqlite3
import tempfile
import subprocess
import platform
import locale
import winreg
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from contextlib import contextmanager
import lz4.block
import time

from .config import (
    CHUNK_SIZE,
    BUFFER_SIZE,
    HASH_ALGORITHM,
    MAX_RETRIES,
    RETRY_DELAY,
    TIMEOUT
)

logger = logging.getLogger(__name__)

class FileOperationError(Exception):
    """Base exception for file operations."""
    pass

class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class CompressionError(Exception):
    """Base exception for compression operations."""
    pass

def setup_logging(log_file: str, log_level: int = logging.INFO) -> None:
    """Configure logging with file and console handlers."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )

@contextmanager
def safe_file_operation(file_path: Union[str, Path], mode: str = 'r'):
    """Context manager for safe file operations with retries."""
    file_path = Path(file_path)
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            with open(file_path, mode, encoding='utf-8' if 'b' not in mode else None) as f:
                yield f
            return
        except (IOError, OSError) as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(RETRY_DELAY)
    
    raise FileOperationError(f"Failed to operate on file {file_path} after {MAX_RETRIES} attempts: {last_error}")

@contextmanager
def safe_db_connection(db_path: Union[str, Path]):
    """Context manager for safe database operations."""
    db_path = Path(db_path)
    conn = None
    
    try:
        conn = sqlite3.connect(db_path, timeout=TIMEOUT)
        yield conn
    except sqlite3.Error as e:
        raise DatabaseError(f"Database operation failed: {e}")
    finally:
        if conn:
            conn.close()

def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """Calculate SHA-256 hash of a file."""
    file_path = Path(file_path)
    sha256_hash = hashlib.new(HASH_ALGORITHM)
    
    with safe_file_operation(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(BUFFER_SIZE), b''):
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()

def decompress_lz4(data: bytes) -> bytes:
    """Decompress LZ4 data."""
    try:
        if data[:8] != b"mozLz40\0":
            raise CompressionError("Invalid LZ4 file format")
        return lz4.block.decompress(data[8:])
    except Exception as e:
        raise CompressionError(f"Decompression failed: {e}")

def compress_lz4(data: bytes) -> bytes:
    """Compress data using LZ4."""
    try:
        compressed = lz4.block.compress(data)
        return b"mozLz40\0" + compressed
    except Exception as e:
        raise CompressionError(f"Compression failed: {e}")

def get_system_info() -> Dict[str, str]:
    """Get system information."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "encoding": locale.getpreferredencoding()
    }

def get_registry_value(key_path, value_name=None):
    """
    Get a registry value from the specified key path and value name.
    Returns None if the key or value doesn't exist.
    
    Args:
        key_path (str): The registry key path.
        value_name (str, optional): The name of the value to retrieve. If None, checks if the key exists.
        
    Returns:
        The value if found, or None if not found.
    """
    try:
        import winreg
        parts = key_path.split('\\')
        hive_map = {
            'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
            'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
            'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
            'HKEY_USERS': winreg.HKEY_USERS,
            'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
            'HKCR': winreg.HKEY_CLASSES_ROOT,
            'HKCU': winreg.HKEY_CURRENT_USER,
            'HKLM': winreg.HKEY_LOCAL_MACHINE,
            'HKU': winreg.HKEY_USERS,
            'HKCC': winreg.HKEY_CURRENT_CONFIG,
            'SOFTWARE': winreg.HKEY_LOCAL_MACHINE
        }
        
        # If no hive specified, assume HKLM
        if parts[0] in hive_map:
            hive = hive_map[parts[0]]
            subkey = '\\'.join(parts[1:])
        else:
            hive = winreg.HKEY_LOCAL_MACHINE
            subkey = key_path
            
        try:
            key = winreg.OpenKey(hive, subkey)
            if value_name is None:
                # Just checking if the key exists
                winreg.CloseKey(key)
                return True
            else:
                value, _ = winreg.QueryValueEx(key, value_name)
                winreg.CloseKey(key)
                return value
        except (WindowsError, FileNotFoundError):
            return None
            
    except ImportError:
        logger.warning("winreg module not available (non-Windows OS)")
        return None

def run_command(command: List[str], timeout: int = TIMEOUT) -> str:
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        result.check_returncode()
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Command timed out after {timeout} seconds")

def create_temp_dir() -> Path:
    """Create a temporary directory."""
    return Path(tempfile.mkdtemp())

def format_size(size_bytes: int) -> str:
    """Format size in bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Get detailed information about a file."""
    file_path = Path(file_path)
    stat = file_path.stat()
    
    return {
        "name": file_path.name,
        "size": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "accessed": datetime.fromtimestamp(stat.st_atime),
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "extension": file_path.suffix,
        "hash": calculate_file_hash(file_path) if file_path.is_file() else None
    }

def verify_json_file(file_path: Union[str, Path]) -> bool:
    """Verify that a JSON file is valid."""
    try:
        with safe_file_operation(file_path) as f:
            json.load(f)
        return True
    except json.JSONDecodeError:
        return False

def verify_sqlite_db(file_path: Union[str, Path]) -> bool:
    """Verify that a SQLite database is valid."""
    try:
        with safe_db_connection(file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return True
    except sqlite3.Error:
        return False 