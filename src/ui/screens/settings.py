"""
Settings screen for HealthLogOps.

This module contains the SettingsScreen class, which provides
application configuration options including theme selection,
view mode selection, and category management.

Classes:
    SettingsScreen: Application settings and preferences screen.

Example:
    >>> settings_screen = SettingsScreen(name="settings")
    >>> settings_screen.db_manager = database_manager
"""

from typing import Optional

from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.divider import MDDivider
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from database import DatabaseManager


class SettingsScreen(MDScreen):
    """
    Settings screen for app configuration.

    Provides options for customizing the application including
    theme toggle, view mode selection, category management,
    and about information.

    Features:
        - Theme toggle (Light/Dark mode)
        - View mode selection (Compact/Balanced/Detailed)
        - Category management
        - About section with version info

    Attributes:
        db_manager: Reference to the database manager instance.

    Args:
        **kwargs: Additional keyword arguments passed to MDScreen.

    Example:
        >>> settings = SettingsScreen(name="settings")
        >>> settings.db_manager = DatabaseManager("health.db")
        >>> # User can toggle dark mode, etc.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the SettingsScreen.

        :param kwargs: Additional keyword arguments passed to MDScreen.
        """
        super().__init__(**kwargs)
        self.db_manager: Optional[DatabaseManager] = None
        self._view_mode_dialog: Optional[MDDialog] = None
        self._categories_dialog: Optional[MDDialog] = None

    def on_enter(self) -> None:
        """
        Called when the screen is displayed.

        Synchronizes the dark mode switch with the current
        application theme.
        """
        self._sync_theme_switch()

    def _sync_theme_switch(self) -> None:
        """
        Sync the dark mode switch state with current theme.

        Ensures the switch reflects the actual theme state when
        the settings screen is opened.
        """
        dark_switch = self.ids.get("dark_mode_switch")
        if dark_switch:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            dark_switch.active = app.theme_cls.theme_style == "Dark"

    def open_view_mode_dialog(self) -> None:
        """Open dialog to select view mode."""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        home_screen = app.screen_manager.get_screen("home") if app else None
        current_mode = home_screen.view_mode if home_screen else "balanced"

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            adaptive_height=True,
            padding=[0, dp(8), 0, dp(8)]
        )

        modes = [
            ("compact", "view-compact", "Compact", "Shows only activity name and time"),
            ("balanced", "view-dashboard", "Balanced", "Shows activity, time, and key metrics"),
            ("detailed", "view-agenda", "Detailed", "Shows all info including notes"),
        ]

        for mode_id, icon, title, subtitle in modes:
            item = MDListItem(
                MDListItemLeadingIcon(icon=icon),
                MDListItemHeadlineText(text=title),
                on_release=lambda x, m=mode_id: self._select_view_mode(m)
            )
            if mode_id == current_mode:
                item.md_bg_color = (0, 0.59, 0.53, 0.1)
            content.add_widget(item)

        self._view_mode_dialog = MDDialog(
            MDDialogHeadlineText(text="View Mode"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self._view_mode_dialog.dismiss()
                ),
                spacing="8dp",
            ),
        )
        self._view_mode_dialog.open()

    def _select_view_mode(self, mode: str) -> None:
        """Handle view mode selection."""
        if self._view_mode_dialog:
            self._view_mode_dialog.dismiss()

        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if app:
            home_screen = app.screen_manager.get_screen("home")
            if home_screen:
                home_screen.set_view_mode(mode)
                MDSnackbar(
                    MDSnackbarText(text=f"View mode set to {mode.title()}"),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.9,
                ).open()

    def open_categories_dialog(self) -> None:
        """Open dialog to manage categories."""
        if not self.db_manager:
            return

        categories = self.db_manager.get_all_categories()

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            adaptive_height=True,
            padding=[0, dp(8), 0, dp(8)]
        )

        if not categories:
            from kivymd.uix.label import MDLabel
            content.add_widget(MDLabel(
                text="No categories available",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.5, 0.5, 0.55, 1)
            ))
        else:
            for cat in categories:
                item = MDListItem(
                    MDListItemLeadingIcon(icon=cat.get("icon", "folder")),
                    MDListItemHeadlineText(text=cat["name"]),
                )
                content.add_widget(item)
                content.add_widget(MDDivider())

        self._categories_dialog = MDDialog(
            MDDialogHeadlineText(text="Categories"),
            MDDialogSupportingText(
                text="These are the available activity categories. Custom category management coming soon!"
            ),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Close"),
                    style="text",
                    on_release=lambda x: self._categories_dialog.dismiss()
                ),
                spacing="8dp",
            ),
        )
        self._categories_dialog.open()
