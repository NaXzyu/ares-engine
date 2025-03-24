"""
Configuration system for Ares Engine.
This module provides tools to read, write and manage engine configuration settings.
"""

import os
import sys
import shutil
from pathlib import Path

def _get_platform_config_dir():
    platform = sys.platform
    # Remove hardcoded app_name - we'll get this from project_config later
    # Use a generic name for the initial setup, will be replaced by actual product_name
    config_base = "AresEngine"

    if platform.startswith("win"):
        platform_name = "Windows"
        try:
            base_path = Path(os.environ.get('LOCALAPPDATA'))
        except (KeyError, TypeError):
            base_path = Path.home() / "AppData" / "Local"
        return base_path / config_base / "Saved" / "Config" / platform_name
    elif platform.startswith("darwin"):
        platform_name = "MacOS"
        return Path.home() / "Library" / "Application Support" / config_base / "Saved" / "Config" / platform_name
    else:
        platform_name = "Linux"
        try:
            import appdirs
            return Path(appdirs.user_data_dir("ares-engine", config_base)) / "Saved" / "Config" / platform_name
        except ImportError:
            return Path.home() / ".local" / "share" / "ares-engine" / "Saved" / "Config" / platform_name

USER_CONFIG_DIR = _get_platform_config_dir()
CONFIG_DIR = Path(__file__).resolve().parent
CONFIG_FILES_DIR = Path(__file__).resolve().parent.parent / "ini"  # Updated from "config_files" to "ini"

if "ARES_CONFIG_DIR" in os.environ:
    CONFIG_FILES_DIR = Path(os.environ["ARES_CONFIG_DIR"])
    print(f"Using configuration directory from environment: {CONFIG_FILES_DIR}")

os.makedirs(CONFIG_FILES_DIR, exist_ok=True)
os.makedirs(USER_CONFIG_DIR, exist_ok=True)

from .config import Config, config, get_config

def _import_configs():
    global engine_config, build_config, package_config, project_config
    from .engine_config import EngineConfig
    from .build_config import BuildConfig
    from .package_config import PackageConfig
    from .project_config import ProjectConfig
    
    engine_config = EngineConfig()
    build_config = BuildConfig()
    package_config = PackageConfig()
    project_config = ProjectConfig()
    return engine_config, build_config, package_config, project_config

engine_config = None
build_config = None
package_config = None
project_config = None

def initialize():
    global engine_config, build_config, package_config, project_config
    if engine_config is None or build_config is None or package_config is None or project_config is None:
        engine_config, build_config, package_config, project_config = _import_configs()
    
    _ensure_config_files_exist()
    
    engine_config.load()
    build_config.load()
    package_config.load()
    project_config.load()
    
    print(f"Configuration loaded from {USER_CONFIG_DIR}")
    return True

def save_all():
    global engine_config, build_config, package_config, project_config
    if engine_config is None or build_config is None or package_config is None or project_config is None:
        engine_config, build_config, package_config, project_config = _import_configs()
    
    engine_config.save()
    build_config.save()
    package_config.save()
    project_config.save()
    
    print(f"Configuration saved to {USER_CONFIG_DIR}")
    return True

def _ensure_config_files_exist():
    for config_file in ['engine.ini', 'build.ini', 'package.ini', 'compiler.ini', 'project.ini']:
        source = CONFIG_FILES_DIR / config_file
        destination = USER_CONFIG_DIR / config_file
        
        if source.exists() and not destination.exists():
            shutil.copy2(source, destination)
            print(f"Created default config file: {destination}")

# Define exports
__all__ = [
    # Config objects
    'config', 'get_config', 'engine_config', 'build_config', 'package_config', 'project_config',
    
    # Directory paths
    'USER_CONFIG_DIR', 'CONFIG_DIR', 'CONFIG_FILES_DIR',
    
    # Functions
    'initialize', 'save_all'
]
