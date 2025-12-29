"""
Home screen for HealthLogOps.

This module contains the HomeScreen class, which serves as the main
dashboard displaying recent health log entries grouped by date,
with filter options for viewing activities.

Classes:
    HomeScreen: The main dashboard screen.

Example:
    >>> home_screen = HomeScreen(name="home")
    >>> home_screen.db_manager = database_manager
"""

from collections import defaultdict
from datetime import datetime, date
from typing import Any, Optional

from database import DatabaseManager
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from ui.components import EmptyStateWidget, DateGroup


class FilterChip(MDBoxLayout):
    """
    A filter chip button for filtering logs by category.

    Attributes:
        text: The filter text.
        is_active: Whether this filter is currently active.
    """

    def __init__(
        self,
        text: str,
        is_active: bool = False,
        on_tap: Optional[callable] = None,
        **kwargs
    ) -> None:
        """
        Initialize a FilterChip.

        :param text: The filter label text.
        :param is_active: Whether the filter is active.
        :param on_tap: Callback when tapped.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self.filter_text = text
        self.is_active = is_active
        self.on_tap_callback = on_tap

        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.height = dp(32)
        self.padding = [dp(12), dp(6), dp(12), dp(6)]

        # Calculate width based on text
        self.width = dp(24) + len(text) * dp(7)

        app = MDApp.get_running_app()
        is_dark = app.is_dark_mode() if app and hasattr(app, 'is_dark_mode') else False

        # Background - adapt for dark mode
        if is_active:
            bg_color = (0, 0.59, 0.53, 1)
            text_color = (1, 1, 1, 1)
        else:
            bg_color = (0.25, 0.25, 0.28, 1) if is_dark else (0.94, 0.95, 0.96, 1)
            text_color = (0.8, 0.8, 0.82, 1) if is_dark else (0.3, 0.3, 0.35, 1)

        with self.canvas.before:
            Color(*bg_color)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(16)]
            )

        self.bind(pos=self._update_bg, size=self._update_bg)

        # Label
        label = MDLabel(
            text=text,
            font_style="Label",
            role="medium",
            theme_text_color="Custom",
            text_color=text_color,
            halign="center",
            valign="center",
            bold=is_active
        )
        self.add_widget(label)

        # Make tappable
        self.bind(on_touch_down=self._on_touch)

    def _update_bg(self, *args) -> None:
        """Update background graphics."""
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _on_touch(self, instance, touch) -> bool:
        """Handle touch event."""
        if self.collide_point(*touch.pos):
            if self.on_tap_callback:
                self.on_tap_callback(self.filter_text)
            return True
        return False


class HomeScreen(MDScreen):
    """
    Home/Dashboard screen showing recent logs grouped by date.

    Displays a scrollable list of health log entries organized by date,
    with collapsible date groups and filter options by category.

    Features:
        - Header with app title and daily stats
        - Filter chips for filtering by activity type
        - Logs grouped by date with collapsible sections
        - Empty state when no logs exist
        - Floating action button for quick add
        - Automatic refresh on screen entry
        - Multiple view modes (compact, balanced, detailed)

    Attributes:
        logs_container: The container widget for date groups.
        filter_container: Container for filter chips.
        db_manager: Reference to the database manager instance.
        active_filter: Currently active category filter (None = all).
        view_mode: Current view mode ('compact', 'balanced', 'detailed').

    Args:
        **kwargs: Additional keyword arguments passed to MDScreen.
    """

    logs_container = ObjectProperty(None)
    """Container widget where date groups are displayed."""

    filter_container = ObjectProperty(None)
    """Container widget for filter chips."""

    active_filter = StringProperty("")
    """Currently active filter category (empty string = all)."""

    view_mode = StringProperty("balanced")
    """Current view mode for log cards."""

    def __init__(self, **kwargs) -> None:
        """
        Initialize the HomeScreen.

        :param kwargs: Additional keyword arguments passed to MDScreen.
        """
        super().__init__(**kwargs)
        self.db_manager: Optional[DatabaseManager] = None
        self.active_filter = ""
        self.view_mode = "balanced"
        self._all_logs: list[dict[str, Any]] = []
        self._cached_categories: set = set()
        self._filters_need_refresh: bool = True
        self._menu: Optional[MDDropdownMenu] = None
        self._view_mode_dialog: Optional[MDDialog] = None
        self._categories_dialog: Optional[MDDialog] = None
        self._about_dialog: Optional[MDDialog] = None
        self._long_press_event: Optional[Clock] = None
        self._long_press_threshold: float = 0.5  # seconds

    def on_enter(self) -> None:
        """
        Called when the screen is displayed.

        Schedules a slight delay before refreshing logs to ensure
        all widgets are properly initialized.
        """
        Clock.schedule_once(lambda dt: self.refresh_logs(), 0.1)

    def refresh_logs(self) -> None:
        """
        Refresh the list of recent logs grouped by date.

        Clears the current log display and repopulates it with
        the latest entries from the database, grouped by date.
        Shows an empty state widget if no logs exist.
        """
        if not self.logs_container or not self.db_manager:
            return

        self.logs_container.clear_widgets()

        # Get all recent logs
        self._all_logs = self.db_manager.get_recent_logs(limit=100)

        # Check if categories changed to avoid unnecessary filter rebuild
        new_categories = set()
        for log in self._all_logs:
            cat = log.get("category_name")
            if cat:
                new_categories.add(cat)

        if new_categories != self._cached_categories:
            self._cached_categories = new_categories
            self._filters_need_refresh = True

        # Refresh filters only if needed
        if self._filters_need_refresh:
            self._refresh_filters()
            self._filters_need_refresh = False

        # Apply filter and display
        self._display_filtered_logs()

        # Update today's count in header
        self._update_today_count()

    def _refresh_filters(self) -> None:
        """Refresh the filter chips based on available categories."""
        if not self.filter_container:
            return

        self.filter_container.clear_widgets()

        # Get unique categories from logs
        categories = set()
        for log in self._all_logs:
            cat = log.get("category_name")
            if cat:
                categories.add(cat)

        # Add "All" filter
        all_chip = FilterChip(
            text="All",
            is_active=(self.active_filter == ""),
            on_tap=self._on_filter_tap
        )
        self.filter_container.add_widget(all_chip)

        # Add category filters
        for category in sorted(categories):
            chip = FilterChip(
                text=category,
                is_active=(self.active_filter == category),
                on_tap=self._on_filter_tap
            )
            self.filter_container.add_widget(chip)

    def _on_filter_tap(self, filter_text: str) -> None:
        """
        Handle filter chip tap.

        :param filter_text: The filter text that was tapped.
        """
        old_filter = self.active_filter

        if filter_text == "All":
            self.active_filter = ""
        else:
            self.active_filter = filter_text

        # Only refresh if filter actually changed
        if old_filter != self.active_filter:
            # Update filter chip styles without full rebuild
            self._update_filter_styles()
            # Refresh displayed logs
            self._display_filtered_logs()

    def _update_filter_styles(self) -> None:
        """Update filter chip active styles without recreating widgets."""
        if not self.filter_container:
            return

        app = MDApp.get_running_app()
        is_dark = app.is_dark_mode() if app and hasattr(app, 'is_dark_mode') else False

        for chip in self.filter_container.children:
            if hasattr(chip, 'filter_text'):
                is_active = (chip.filter_text == "All" and self.active_filter == "") or \
                           (chip.filter_text == self.active_filter)
                chip.is_active = is_active

                # Update colors
                if is_active:
                    bg_color = (0, 0.59, 0.53, 1)
                    text_color = (1, 1, 1, 1)
                else:
                    bg_color = (0.25, 0.25, 0.28, 1) if is_dark else (0.94, 0.95, 0.96, 1)
                    text_color = (0.8, 0.8, 0.82, 1) if is_dark else (0.3, 0.3, 0.35, 1)

                # Update canvas color
                if hasattr(chip, '_bg'):
                    chip.canvas.before.clear()
                    with chip.canvas.before:
                        Color(*bg_color)
                        chip._bg = RoundedRectangle(
                            pos=chip.pos,
                            size=chip.size,
                            radius=[dp(16)]
                        )

                # Update label
                for child in chip.children:
                    if isinstance(child, MDLabel):
                        child.text_color = text_color
                        child.bold = is_active

    def _display_filtered_logs(self) -> None:
        """Display logs filtered by the active filter."""
        if not self.logs_container:
            return

        self.logs_container.clear_widgets()

        # Filter logs
        if self.active_filter:
            filtered_logs = [
                log for log in self._all_logs
                if log.get("category_name") == self.active_filter
            ]
        else:
            filtered_logs = self._all_logs

        if not filtered_logs:
            empty_widget = EmptyStateWidget()
            self.logs_container.add_widget(empty_widget)
            return

        # Group logs by date
        logs_by_date: dict[date, list[dict[str, Any]]] = defaultdict(list)
        for log in filtered_logs:
            timestamp = log.get("timestamp")
            if timestamp:
                log_date = timestamp.date()
                logs_by_date[log_date].append(log)

        # Sort dates descending (newest first)
        sorted_dates = sorted(logs_by_date.keys(), reverse=True)

        # Create date groups
        for log_date in sorted_dates:
            logs = logs_by_date[log_date]
            date_group = DateGroup(
                log_date=log_date,
                logs=logs,
                is_expanded=True,
                view_mode=self.view_mode
            )
            self.logs_container.add_widget(date_group)

    def _update_today_count(self) -> None:
        """
        Update the today's log count displayed in the header.

        Calculates the number of activities logged today and updates
        the corresponding label in the UI.
        """
        if not self.db_manager:
            return

        today = datetime.now().date()
        today_count = sum(
            1 for log in self._all_logs
            if log.get("timestamp") and log["timestamp"].date() == today
        )

        today_label = self.ids.get("today_count_label")
        if today_label:
            if today_count == 0:
                today_label.text = "No activities logged today"
            elif today_count == 1:
                today_label.text = "Today: 1 activity logged"
            else:
                today_label.text = f"Today: {today_count} activities logged"

    def set_view_mode(self, mode: str) -> None:
        """
        Set the view mode for log cards.

        :param mode: View mode ('compact', 'balanced', 'detailed').
        """
        if mode in ("compact", "balanced", "detailed"):
            self.view_mode = mode
            self._display_filtered_logs()
            self._update_view_mode_icon()

    def _update_view_mode_icon(self) -> None:
        """Update the view mode button icon based on current mode."""
        view_button = self.ids.get("view_mode_button")
        if view_button:
            icons = {
                "compact": "eye-outline",
                "balanced": "eye",
                "detailed": "eye-plus"
            }
            view_button.icon = icons.get(self.view_mode, "eye-outline")

    def cycle_view_mode(self) -> None:
        """Cycle through view modes: compact -> balanced -> detailed -> compact."""
        modes = ["compact", "balanced", "detailed"]
        current_idx = modes.index(self.view_mode) if self.view_mode in modes else 0
        next_idx = (current_idx + 1) % len(modes)
        next_mode = modes[next_idx]
        self.set_view_mode(next_mode)
        MDSnackbar(
            MDSnackbarText(text=f"View: {next_mode.title()}"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def on_view_button_touch_down(self, touch) -> None:
        """Handle touch down on view mode button for long press detection."""
        if self._long_press_event:
            self._long_press_event.cancel()
        self._long_press_event = Clock.schedule_once(
            lambda dt: self._on_view_button_long_press(),
            self._long_press_threshold
        )

    def on_view_button_touch_up(self, touch) -> None:
        """Handle touch up on view mode button."""
        if self._long_press_event:
            self._long_press_event.cancel()
            self._long_press_event = None

    def _on_view_button_long_press(self) -> None:
        """Handle long press on view mode button - open view mode dialog."""
        self._long_press_event = None
        self.open_view_mode_dialog()

    def open_view_mode_dialog(self) -> None:
        """Open dialog to select view mode."""
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
            if mode_id == self.view_mode:
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
        """Handle view mode selection from dialog."""
        if self._view_mode_dialog:
            self._view_mode_dialog.dismiss()
        self.set_view_mode(mode)
        MDSnackbar(
            MDSnackbarText(text=f"View mode set to {mode.title()}"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def open_menu(self, button) -> None:
        """Open the three-dot dropdown menu."""
        app = MDApp.get_running_app()
        is_dark = app.is_dark_mode() if app and hasattr(app, 'is_dark_mode') else False

        menu_items = [
            {
                "text": "Dark Mode",
                "leading_icon": "theme-light-dark",
                "trailing_icon": "check" if is_dark else "",
                "on_release": lambda: self._toggle_theme(),
            },
            {
                "text": "Categories",
                "leading_icon": "folder-plus-outline",
                "on_release": lambda: self._open_categories(),
            },
            {
                "text": "About",
                "leading_icon": "information-outline",
                "on_release": lambda: self._open_about(),
            },
        ]

        self._menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
        )
        self._menu.open()

    def _toggle_theme(self) -> None:
        """Toggle between light and dark theme."""
        if self._menu:
            self._menu.dismiss()
        app = MDApp.get_running_app()
        if app:
            is_dark = app.is_dark_mode() if hasattr(app, 'is_dark_mode') else False
            app.toggle_theme(not is_dark)
            mode_name = "Dark" if not is_dark else "Light"
            MDSnackbar(
                MDSnackbarText(text=f"{mode_name} mode enabled"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()

    def _open_categories(self) -> None:
        """Open the categories management dialog."""
        if self._menu:
            self._menu.dismiss()

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
            content.add_widget(MDLabel(
                text="No categories available",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.5, 0.5, 0.55, 1)
            ))
        else:
            from kivymd.uix.divider import MDDivider
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

    def _open_about(self) -> None:
        """Open the about dialog."""
        if self._menu:
            self._menu.dismiss()

        app = MDApp.get_running_app()

        self._about_dialog = MDDialog(
            MDDialogHeadlineText(text="About HealthLogOps"),
            MDDialogSupportingText(
                text="HealthLogOps v0.1.0\n\n"
                     "Your personal health activity tracker.\n\n"
                     "Track your workouts, meals, sleep, water intake, "
                     "weight, and daily steps all in one place.\n\n"
                     "Built with Python and KivyMD."
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Close"),
                    style="text",
                    on_release=lambda x: self._about_dialog.dismiss()
                ),
                spacing="8dp",
            ),
        )
        self._about_dialog.open()
