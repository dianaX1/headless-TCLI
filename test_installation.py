#!/usr/bin/env python3
"""
Test script to verify the Headless Telegram Client installation.
This script checks all dependencies and components without requiring API credentials.
"""

import sys
import os
import importlib
from pathlib import Path

def print_header():
    print("+--------------------------------------------------------------+")
    print("|                 INSTALLATION TEST SCRIPT                    |")
    print("|                Headless Telegram Client                     |")
    print("+--------------------------------------------------------------+")
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   [X] ERROR: Python 3.8+ required")
        return False
    else:
        print("   [V] Python version OK")
        return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\nChecking dependencies...")
    
    dependencies = [
        ("tdjson", "TDLib JSON interface"),
        ("fastapi", "Web framework"),
        ("uvicorn", "ASGI server"),
        ("websockets", "WebSocket support"),
        ("jinja2", "Template engine"),
    ]
    
    all_ok = True
    for module, description in dependencies:
        try:
            importlib.import_module(module)
            print(f"   [V] {module} - {description}")
        except ImportError:
            print(f"   [X] {module} - {description} (MISSING)")
            all_ok = False
    
    return all_ok

def check_project_files():
    """Check if all project files are present."""
    print("\nChecking project files...")
    
    required_files = [
        ("A113/main.py", "CLI entry point"),
        ("A113/web_server.py", "Web server"),
        ("A113/tdlib_client.py", "TDLib client wrapper"),
        ("A113/auth.py", "Authentication handler"),
        ("A113/message_handler.py", "Message processing"),
        ("A113/requirements.txt", "Dependencies list"),
        ("A113/templates/index.html", "Web interface template"),
    ]
    
    all_ok = True
    for file_path, description in required_files:
        if Path(file_path).exists():
            print(f"   [V] {file_path} - {description}")
        else:
            print(f"   [X] {file_path} - {description} (MISSING)")
            all_ok = False
    
    return all_ok

def check_directories():
    """Check if required directories exist or can be created."""
    print("\nChecking directories...")
    
    directories = [
        ("templates", "HTML templates"),
        ("static", "Static files"),
        ("tdlib", "TDLib data (will be created)"),
    ]
    
    all_ok = True
    for dir_path, description in directories:
        path = Path(dir_path)
        if path.exists():
            print(f"   [V] {dir_path}/ - {description}")
        else:
            try:
                path.mkdir(exist_ok=True)
                print(f"   [V] {dir_path}/ - {description} (created)")
            except Exception as e:
                print(f"   [X] {dir_path}/ - {description} (cannot create: {e})")
                all_ok = False
    
    return all_ok

def test_imports():
    """Test importing project modules."""
    print("\nTesting project imports...")
    
    modules = [
        ("tdlib_client", "TDLibClient"),
        ("auth", "authenticate"),
        ("message_handler", "listen_for_messages"),
        ("web_server", "app"),
    ]
    
    all_ok = True
    for module, component in modules:
        try:
            mod = importlib.import_module(module)
            if hasattr(mod, component.split('.')[0]):
                print(f"   [V] {module}.{component}")
            else:
                print(f"   [!] {module}.{component} (component not found)")
        except Exception as e:
            print(f"   [X] {module}.{component} (import error: {e})")
            all_ok = False
    
    return all_ok

def test_tdjson():
    """Test TDLib JSON interface."""
    print("\nTesting TDLib interface...")
    
    try:
        import tdjson
        
        # Test basic TDLib functions
        client_id = tdjson.td_create_client_id()
        print(f"   [V] TDLib client creation (ID: {client_id})")
        
        # Test execute function
        result = tdjson.td_execute('{"@type": "getOption", "name": "version"}')
        if result:
            print("   [V] TDLib execute function")
        else:
            print("   [!] TDLib execute function (no result)")
        
        return True
        
    except Exception as e:
        print(f"   [X] TDLib interface error: {e}")
        return False

def print_summary(results):
    """Print test summary."""
    print("\n" + "="*64)
    print("INSTALLATION TEST SUMMARY")
    print("="*64)
    
    test_names = [
        "Python Version",
        "Dependencies",
        "Project Files", 
        "Directories",
        "Module Imports",
        "TDLib Interface"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "[V] PASS" if result else "[X] FAIL"
        print(f"{name:<20} {status}")
    
    print("-" * 64)
    print(f"OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nALL TESTS PASSED!")
        print("Your installation is ready to use.")
        print("\nNext steps:")
        print("1. Get your API credentials from https://my.telegram.org")
        print("2. Run: python web_server.py")
        print("3. Open http://127.0.0.1:8000 in your browser")
    else:
        print(f"\n{total - passed} TESTS FAILED!")
        print("Please fix the issues above before using the client.")
        print("\nCommon solutions:")
        print("- Run: pip install -r requirements.txt")
        print("- Check Python installation and PATH")
        print("- Verify all project files are present")

def main():
    """Run all installation tests."""
    print_header()
    
    results = [
        check_python_version(),
        check_dependencies(),
        check_project_files(),
        check_directories(),
        test_imports(),
        test_tdjson(),
    ]
    
    print_summary(results)
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)