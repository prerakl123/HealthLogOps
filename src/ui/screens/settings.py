"""
About screen for HealthLogOps.

This module contains the SettingsScreen class (kept for backwards compatibility),
which now serves as an About screen showing application information.

Classes:
    SettingsScreen: Application about/info screen.

Example:
    >>> about_screen = SettingsScreen(name="settings")
"""

from typing import Optional

from kivymd.uix.screen import MDScreen

from database import DatabaseManager


class SettingsScreen(MDScreen):
    """
    About screen for application information.

    Displays version info, app description, and credits.
    Note: Settings options like theme toggle and view mode are now
    accessible from the home screen's three-dot menu and eye icon.

    Attributes:
        db_manager: Reference to the database manager instance.

    Args:
        **kwargs: Additional keyword arguments passed to MDScreen.

    Example:
        >>> about = SettingsScreen(name="settings")
        >>> about.db_manager = DatabaseManager("health.db")
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the SettingsScreen (About Screen).

        :param kwargs: Additional keyword arguments passed to MDScreen.
        """
        super().__init__(**kwargs)
        self.db_manager: Optional[DatabaseManager] = None

    def on_enter(self) -> None:
        """
        Called when the screen is displayed.

        Can be used to update dynamic content if needed.
        """
        pass
