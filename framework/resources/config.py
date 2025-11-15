"""
Configuration module for loading environment variables and providing config access.
"""

import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv


class Config:
    """Configuration management class that loads and provides access to environment variables."""

    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration by loading environment variables.

        Args:
            env_file: Path to .env file (default: ".env")
        """
        self.env_file = env_file
        self._load_env()
        self._config = self._build_config()

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path(self.env_file)

        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded configuration from: {env_path.absolute()}")
        else:
            print(f"Warning: {env_path.absolute()} not found. Using .env.example or defaults.")
            # Try to load from .env.example if .env doesn't exist
            example_path = Path(".env.example")
            if example_path.exists():
                load_dotenv(example_path)
                print(f"Loaded configuration from: {example_path.absolute()}")

    def _build_config(self) -> Dict[str, Any]:
        """
        Build configuration dictionary from environment variables.

        Returns:
            Configuration dictionary
        """
        return {
            # Application Under Test
            'base_url': os.getenv('BASE_URL', 'http://www.automationpractice.pl/index.php'),
            'app_timeout': int(os.getenv('APP_TIMEOUT', '10')),

            # Browser Configuration
            'browser': os.getenv('BROWSER', 'chrome').lower(),
            'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
            'window_size': os.getenv('WINDOW_SIZE', '1920x1080'),

            # Test Execution
            'implicit_wait': int(os.getenv('IMPLICIT_WAIT', '10')),
            'explicit_wait': int(os.getenv('EXPLICIT_WAIT', '20')),
            'page_load_timeout': int(os.getenv('PAGE_LOAD_TIMEOUT', '30')),

            # Reporting & Logging
            'log_level': os.getenv('LOG_LEVEL', 'INFO').upper(),
            'screenshots_on_failure': os.getenv('SCREENSHOTS_ON_FAILURE', 'true').lower() == 'true',
            'screenshot_dir': os.getenv('SCREENSHOT_DIR', 'screenshots'),
            'report_dir': os.getenv('REPORT_DIR', '_reports'),
            'log_dir': os.getenv('LOG_DIR', 'logs'),

            # Test Data
            'test_data_dir': os.getenv('TEST_DATA_DIR', 'framework/resources/data'),
            'user_data_file': os.getenv('USER_DATA_FILE', 'users.json'),

            # Environment
            'environment': os.getenv('ENVIRONMENT', 'production').lower(),

            # Optional: Selenium Grid
            'use_grid': os.getenv('USE_GRID', 'false').lower() == 'true',
            'grid_url': os.getenv('GRID_URL', 'http://localhost:4444/wd/hub'),
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()

    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value using dictionary-style access.

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            KeyError: If key not found
        """
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """
        Check if configuration key exists.

        Args:
            key: Configuration key

        Returns:
            True if key exists, False otherwise
        """
        return key in self._config

    def __repr__(self) -> str:
        """String representation of Config object."""
        return f"Config(env_file='{self.env_file}', keys={list(self._config.keys())})"
