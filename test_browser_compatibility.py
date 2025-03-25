#!/usr/bin/env python3
"""
Browser Profile Compatibility Test for Floorper

This script tests Floorper's compatibility with the simulated browser profiles.
"""

import os
import sys
import json
import shutil
from pathlib import Path
import traceback
from typing import Dict, Any
import logging
import pytest
from unittest.mock import patch, MagicMock

# Add the floorper directory to the path
sys.path.append(os.path.abspath('.'))

# Import Floorper modules
from floorper.core.browser_detector import BrowserDetector
from floorper.core.profile_migrator import ProfileMigrator

@pytest.fixture(autouse=True)
def setup_test_directories(tmp_path):
    """Fixture para crear estructura de directorios de prueba"""
    test_profiles = tmp_path / "test_profiles"
    test_profiles.mkdir()
    
    # Crear perfiles de prueba básicos
    (test_profiles / "firefox").mkdir()
    (test_profiles / "chrome").mkdir()
    
    # Configurar paths globales
    global TEST_PROFILES_DIR, TEST_RESULTS_DIR
    TEST_PROFILES_DIR = test_profiles
    TEST_RESULTS_DIR = tmp_path / "test_results"
    TEST_RESULTS_DIR.mkdir()

# Mejorar el sistema de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_profile_dir(tmp_path):
    # Configurar ambiente de prueba aislado
    profile_dir = tmp_path / "test_profiles"
    profile_dir.mkdir()
    return profile_dir

def test_detection_with_mock():
    """Prueba con mock de sistema de archivos"""
    with patch("pathlib.Path.iterdir") as mock_iterdir:
        mock_iterdir.return_value = [MagicMock(is_dir=lambda: True, name="firefox")]
        
        detector = BrowserDetector()
        results = detector.detect_all_profiles()
        
        assert "firefox" in results
        assert results["firefox"]["version"] == "100.0"

def test_browser_detection() -> Dict[str, Any]:
    """Test mejorado con manejo de errores y tipos"""
    logger.info("Iniciando detección de navegadores...")
    
    detector = BrowserDetector()
    results = {}
    
    try:
        for browser_dir in TEST_PROFILES_DIR.iterdir():
            if not browser_dir.is_dir():
                continue
                
            browser_name = browser_dir.name
            logger.debug(f"Probando detección de: {browser_name}")
            
            try:
                detected = detector.detect_browser_profile(str(browser_dir))
                results[browser_name] = {
                    "detected": detected is not None,
                    "detected_name": detected.name if detected else None,
                    "detected_version": detected.version if detected else None,
                    "profile_path": str(browser_dir)
                }
                
            except Exception as e:
                logger.error(f"Error detectando {browser_name}: {str(e)}")
                results[browser_name] = {
                    "error": str(e),
                    "stack_trace": traceback.format_exc()
                }
    
    except Exception as e:
        logger.critical(f"Fallo catastrófico en detección: {str(e)}")
        raise
    
    return results

def test_profile_migration():
    """Test profile migration functionality with simulated profiles."""
    print("\nTesting profile migration...")
    
    migrator = ProfileMigrator()
    results = {}
    
    # Create a target directory for migrations
    target_dir = TEST_RESULTS_DIR / "migrations"
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(exist_ok=True)
    
    for browser_dir in TEST_PROFILES_DIR.iterdir():
        if not browser_dir.is_dir():
            continue
            
        browser_name = browser_dir.name
        print(f"  Testing migration of {browser_name}...")
        
        # Create a target directory for this browser
        browser_target = target_dir / browser_name
        browser_target.mkdir(exist_ok=True)
        
        # Test migration
        try:
            success = migrator.migrate_profile(
                str(browser_dir),
                str(browser_target),
                browser_name
            )
            
            results[browser_name] = {
                "migration_success": success,
                "source_path": str(browser_dir),
                "target_path": str(browser_target)
            }
            
            print(f"    {'✓ Migrated' if success else '✗ Migration failed'}")
            
        except Exception as e:
            results[browser_name] = {
                "migration_success": False,
                "error": str(e),
                "source_path": str(browser_dir),
                "target_path": str(browser_target)
            }
            
            print(f"    ✗ Error: {e}")
    
    # Save results
    with open(TEST_RESULTS_DIR / "migration_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

def generate_report(detection_results, migration_results):
    """Generate a comprehensive test report."""
    print("\nGenerating test report...")
    
    report = {
        "summary": {
            "total_browsers_tested": len(detection_results),
            "detection_success_count": sum(1 for r in detection_results.values() if r["detected"]),
            "migration_success_count": sum(1 for r in migration_results.values() if r.get("migration_success", False))
        },
        "detection_results": detection_results,
        "migration_results": migration_results
    }
    
    # Calculate success rates
    report["summary"]["detection_success_rate"] = (
        report["summary"]["detection_success_count"] / report["summary"]["total_browsers_tested"] * 100
    )
    report["summary"]["migration_success_rate"] = (
        report["summary"]["migration_success_count"] / report["summary"]["total_browsers_tested"] * 100
    )
    
    # Save detailed report
    with open(TEST_RESULTS_DIR / "test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Generate human-readable report
    with open(TEST_RESULTS_DIR / "test_report.md", "w") as f:
        f.write("# Floorper Browser Compatibility Test Report\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- Total browsers tested: {report['summary']['total_browsers_tested']}\n")
        f.write(f"- Detection success rate: {report['summary']['detection_success_rate']:.1f}%\n")
        f.write(f"- Migration success rate: {report['summary']['migration_success_rate']:.1f}%\n\n")
        
        f.write("## Detailed Results\n\n")
        f.write("| Browser | Detection | Migration |\n")
        f.write("|---------|-----------|----------|\n")
        
        for browser in sorted(detection_results.keys()):
            detection = "✓" if detection_results[browser]["detected"] else "✗"
            migration = "✓" if migration_results[browser].get("migration_success", False) else "✗"
            f.write(f"| {browser} | {detection} | {migration} |\n")
    
    print(f"  Report generated at {TEST_RESULTS_DIR / 'test_report.md'}")
    return report

if __name__ == "__main__":
    print("Starting browser compatibility tests...")
    
    # Run tests
    detection_results = test_browser_detection()
    migration_results = test_profile_migration()
    
    # Generate report
    report = generate_report(detection_results, migration_results)
    
    # Print summary
    print("\nTest Summary:")
    print(f"  Total browsers tested: {report['summary']['total_browsers_tested']}")
    print(f"  Detection success rate: {report['summary']['detection_success_rate']:.1f}%")
    print(f"  Migration success rate: {report['summary']['migration_success_rate']:.1f}%")
    
    print("\nCompatibility testing completed!")
