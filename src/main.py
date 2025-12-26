"""
HealthLogOps - Pythonic Health Activity Tracker.

This is the main application entry point using KivyMD framework.
A beautifully designed health tracking app with Material Design 3.

The application provides:
    - Health activity logging across multiple categories
    - Dynamic form templates for different activity types
    - Beautiful Material Design 3 user interface
    - Dark/Light theme support
    - SQLite database for persistent storage

Usage:
    Run directly to start the application::

        python main.py

    Or import and run programmatically::

        from main import main
        main()

Classes:
    HealthLogOpsApp: The main MDApp subclass.

Functions:
    main: Application entry point function.
"""

import sys
from pathlib import Path
from typing import Optional

# Ensure the src directory is in the path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp

from database import DatabaseManager
from ui.screens import HomeScreen, AddLogScreen, EditLogScreen, SettingsScreen


# Set window size for desktop testing (will be ignored on Android)
Window.size = (400, 720)


class HealthLogOpsApp(MDApp):
    """
    Main application class for HealthLogOps.

    A modern, beautifully designed health activity tracker featuring:
        - Material Design 3 styling
        - Teal/Cyan primary theme with Amber accents
        - Smooth screen transitions
        - Dark mode support
        - Persistent SQLite storage

    Attributes:
        db_manager: The database manager instance for data persistence.
        screen_manager: The screen manager controlling navigation.

    Example:
        >>> app = HealthLogOpsApp()
        >>> app.run()
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the HealthLogOpsApp.

        :param kwargs: Additional keyword arguments passed to MDApp.
        """
        super().__init__(**kwargs)
        self.db_manager: Optional[DatabaseManager] = None
        self.screen_manager: Optional[ScreenManager] = None

    def build(self) -> ScreenManager:
        """
        Build the application UI.

        Initializes the theme, loads the KV file, sets up the database,
        and creates all application screens.

        :returns: The root ScreenManager widget containing all screens.
        """
        # ========== THEME CONFIGURATION ==========
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"

        # Set dynamic color if available (Material You)
        try:
            self.theme_cls.dynamic_color = True
        except AttributeError:
            pass  # Not available in all KivyMD versions

        # ========== LOAD KV FILE ==========
        kv_path = Path(__file__).parent / "ui" / "healthlogops.kv"
        Builder.load_file(str(kv_path))

        # ========== INITIALIZE DATABASE ==========
        self._init_database()

        # ========== CREATE SCREEN MANAGER ==========
        self.screen_manager = ScreenManager(
            transition=SlideTransition(duration=0.25)
        )

        # Create and configure screens
        home_screen = HomeScreen(name="home")
        home_screen.db_manager = self.db_manager

        add_log_screen = AddLogScreen(name="add_log")
        add_log_screen.db_manager = self.db_manager

        edit_log_screen = EditLogScreen(name="edit_log")
        edit_log_screen.db_manager = self.db_manager

        settings_screen = SettingsScreen(name="settings")
        settings_screen.db_manager = self.db_manager

        # Add screens to manager
        self.screen_manager.add_widget(home_screen)
        self.screen_manager.add_widget(add_log_screen)
        self.screen_manager.add_widget(edit_log_screen)
        self.screen_manager.add_widget(settings_screen)

        return self.screen_manager

    def _init_database(self) -> None:
        """
        Initialize the database connection and seed default data.

        Determines the appropriate database path based on platform
        (uses user_data_dir on mobile, home directory on desktop),
        creates the database, and seeds default categories.
        """
        # Determine database path based on platform
        if hasattr(self, "user_data_dir"):
            db_dir = Path(self.user_data_dir)
        else:
            db_dir = Path.home() / ".healthlogops"

        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "health_tracker.db"

        print(f"[HealthLogOps] Database: {db_path.as_posix()}")

        self.db_manager = DatabaseManager(db_path)
        self.db_manager.seed_default_categories()

    # ========== NAVIGATION METHODS ==========

    def switch_to_add_log(self) -> None:
        """
        Navigate to the Add Log screen.

        Uses a slide-left animation for forward navigation.
        """
        if self.screen_manager:
            self.screen_manager.transition.direction = "left"
            self.screen_manager.current = "add_log"

    def switch_to_edit_log(self, log_id: int) -> None:
        """
        Navigate to the Edit Log screen.

        :param log_id: The ID of the log to edit.
        """
        if self.screen_manager:
            edit_screen = self.screen_manager.get_screen("edit_log")
            if edit_screen:
                edit_screen.load_log(log_id)
                self.screen_manager.transition.direction = "left"
                self.screen_manager.current = "edit_log"

    def go_back(self) -> None:
        """
        Navigate back to the Home screen.

        Uses a slide-right animation for backward navigation
        and refreshes the home screen logs.
        """
        if self.screen_manager:
            self.screen_manager.transition.direction = "right"
            self.screen_manager.current = "home"

            # Refresh home screen logs
            home = self.screen_manager.get_screen("home")
            if home:
                home.refresh_logs()

    def open_settings(self) -> None:
        """
        Navigate to the Settings screen.

        Uses a slide-left animation for forward navigation.
        """
        if self.screen_manager:
            self.screen_manager.transition.direction = "left"
            self.screen_manager.current = "settings"

    # ========== THEME METHODS ==========

    def toggle_theme(self, is_dark: bool) -> None:
        """
        Toggle between light and dark theme.

        Updates the theme style and adjusts background colors
        for all screens to match the selected theme.

        :param is_dark: True for dark theme, False for light theme.
        """
        self.theme_cls.theme_style = "Dark" if is_dark else "Light"

        # Store theme preference
        self._is_dark_mode = is_dark

        # Update background colors for screens
        bg_color = (0.12, 0.12, 0.14, 1) if is_dark else (0.96, 0.97, 0.98, 1)

        for screen_name in ["home", "add_log", "edit_log", "settings"]:
            screen = self.screen_manager.get_screen(screen_name)
            if screen:
                screen.md_bg_color = bg_color

        # Refresh home screen to apply theme to cards
        home = self.screen_manager.get_screen("home")
        if home:
            home.refresh_logs()

    def is_dark_mode(self) -> bool:
        """Check if dark mode is currently enabled."""
        return getattr(self, '_is_dark_mode', False)

    # ========== LIFECYCLE METHODS ==========

    def on_start(self) -> None:
        """
        Called when the application starts.

        Logs application start for debugging purposes.
        """
        print("[HealthLogOps] Application started")

    def on_stop(self) -> None:
        """
        Called when the application stops.

        Logs application stop for debugging purposes.
        """
        print("[HealthLogOps] Application stopped")

    def on_pause(self) -> bool:
        """
        Called when the app is paused (Android).

        :returns: True to allow the app to pause.
        """
        return True

    def on_resume(self) -> None:
        """
        Called when the app resumes from pause (Android).

        Can be used to refresh data after resuming.
        """
        pass


def main() -> None:
    """
    Application entry point.

    Creates and runs the HealthLogOpsApp instance.

    Example:
        >>> main()  # Starts the application
    """
    HealthLogOpsApp().run()


if __name__ == "__main__":
    main()
