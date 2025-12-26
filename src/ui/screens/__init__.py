"""
Screens package for HealthLogOps.

This package contains the main application screens organized into
individual modules for better maintainability.

Modules:
    - home: Home/Dashboard screen with recent activities
    - add_log: Form screen for adding new log entries
    - edit_log: Form screen for editing existing log entries
    - settings: Application settings and preferences

All screens inherit from MDScreen and follow a consistent pattern
for database access and navigation.
"""

from ui.screens.home import HomeScreen
from ui.screens.add_log import AddLogScreen
from ui.screens.edit_log import EditLogScreen
from ui.screens.settings import SettingsScreen

__all__ = [
    "HomeScreen",
    "AddLogScreen",
    "EditLogScreen",
    "SettingsScreen",
]
