"""
Date group components for HealthLogOps.

This module provides collapsible date-based grouping for log entries,
allowing users to organize and view activities by date.

Classes:
    DateGroupHeader: Collapsible header for a group of logs by date.
    DateGroup: Container widget for grouped log entries.
    NoActivityLabel: Label shown when no activities exist for a date.
"""

from datetime import date, timedelta
from typing import Any, Callable, Optional

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon, MDLabel


def format_date_header(log_date: date) -> str:
    """
    Format a date for display in the group header.

    :param log_date: The date to format.
    :returns: Formatted date string (e.g., "Today", "Yesterday", "Dec 25, 2025").
    """
    today = date.today()

    if log_date == today:
        return "Today"
    elif log_date == today.replace(day=today.day - 1) if today.day > 1 else today:
        # Handle yesterday more carefully
        yesterday = today - timedelta(days=1)
        if log_date == yesterday:
            return "Yesterday"

    # Format as "Dec 25, 2025"
    return log_date.strftime("%b %d, %Y")


class DateGroupHeader(MDBoxLayout):
    """
    A collapsible header for a date group of log entries.

    Displays the date and a count of activities, with a chevron
    that rotates to indicate expanded/collapsed state.

    Attributes:
        date_text: The formatted date string to display.
        count: Number of activities for this date.
        is_expanded: Whether the group is currently expanded.

    Args:
        date_text: The formatted date string.
        count: Number of activities.
        is_expanded: Initial expanded state.
        on_toggle: Callback when header is tapped.
        **kwargs: Additional keyword arguments.
    """

    date_text = StringProperty("")
    is_expanded = BooleanProperty(True)

    def __init__(
        self,
        date_text: str,
        count: int,
        is_expanded: bool = True,
        on_toggle: Optional[Callable[[bool], None]] = None,
        **kwargs
    ) -> None:
        """
        Initialize a DateGroupHeader.

        :param date_text: The formatted date string.
        :param count: Number of activities for this date.
        :param is_expanded: Initial expanded state.
        :param on_toggle: Callback when header is tapped.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.date_text = date_text
        self.is_expanded = is_expanded
        self.on_toggle_callback = on_toggle
        self._count = count

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(40)
        self.padding = [dp(4), dp(8), dp(12), dp(8)]
        self.spacing = dp(8)

        # Get theme colors
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        is_dark = app.is_dark_mode() if app and hasattr(app, 'is_dark_mode') else False

        bg_color = (0.2, 0.2, 0.22, 1) if is_dark else (0.94, 0.95, 0.96, 1)
        text_primary = (0.9, 0.9, 0.92, 1) if is_dark else (0.25, 0.25, 0.3, 1)
        text_secondary = (0.65, 0.65, 0.7, 1) if is_dark else (0.5, 0.5, 0.55, 1)
        icon_color = (0.55, 0.55, 0.6, 1) if is_dark else (0.4, 0.4, 0.45, 1)

        # Background
        with self.canvas.before:
            Color(*bg_color)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Chevron icon
        self.chevron = MDIcon(
            icon="chevron-down" if is_expanded else "chevron-right",
            theme_icon_color="Custom",
            icon_color=icon_color,
            size_hint_x=None,
            width=dp(24),
            pos_hint={"center_y": 0.5}
        )
        self.add_widget(self.chevron)

        # Date label
        date_label = MDLabel(
            text=date_text,
            font_style="Title",
            role="small",
            bold=True,
            theme_text_color="Custom",
            text_color=text_primary,
            pos_hint={"center_y": 0.5}
        )
        self.add_widget(date_label)

        # Spacer
        self.add_widget(MDBoxLayout(size_hint_x=1))

        # Count badge
        count_text = f"{count} {'activity' if count == 1 else 'activities'}"
        count_label = MDLabel(
            text=count_text,
            font_style="Label",
            role="small",
            theme_text_color="Custom",
            text_color=text_secondary,
            size_hint_x=None,
            width=dp(80),
            halign="right",
            pos_hint={"center_y": 0.5}
        )
        self.add_widget(count_label)

    def _update_bg(self, *args) -> None:
        """Update background position and size."""
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_touch_down(self, touch) -> bool:
        """Handle touch to toggle expanded state."""
        if self.collide_point(*touch.pos):
            self.is_expanded = not self.is_expanded
            self.chevron.icon = "chevron-down" if self.is_expanded else "chevron-right"

            if self.on_toggle_callback:
                self.on_toggle_callback(self.is_expanded)
            return True
        return super().on_touch_down(touch)


class NoActivityLabel(MDBoxLayout):
    """
    A label displayed when no activities exist for a date.

    Args:
        **kwargs: Additional keyword arguments.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize a NoActivityLabel."""
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(40)
        self.padding = [dp(16), dp(8)]

        label = MDLabel(
            text="No activity logged.",
            font_style="Body",
            role="medium",
            theme_text_color="Custom",
            text_color=(0.55, 0.55, 0.6, 1),
            halign="center",
            valign="center"
        )
        self.add_widget(label)


class DateGroup(MDBoxLayout):
    """
    A container widget for grouped log entries by date.

    Contains a collapsible header and a container for log cards.
    When collapsed, the log cards are hidden.

    Attributes:
        log_date: The date for this group.
        is_expanded: Whether the group is currently expanded.
        view_mode: Display mode for log cards ('compact', 'balanced', 'detailed').

    Args:
        log_date: The date for this group.
        logs: List of log dictionaries for this date.
        is_expanded: Initial expanded state.
        view_mode: Display mode for log cards.
        **kwargs: Additional keyword arguments.
    """

    is_expanded = BooleanProperty(True)

    def __init__(
        self,
        log_date: date,
        logs: list[dict[str, Any]],
        is_expanded: bool = True,
        view_mode: str = "balanced",
        **kwargs
    ) -> None:
        """
        Initialize a DateGroup.

        :param log_date: The date for this group.
        :param logs: List of log dictionaries for this date.
        :param is_expanded: Initial expanded state.
        :param view_mode: Display mode for log cards.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self.log_date = log_date
        self.logs = logs
        self.is_expanded = is_expanded
        self.view_mode = view_mode

        self.orientation = "vertical"
        self.size_hint_y = None
        self.spacing = dp(6)
        self.padding = [0, 0, 0, dp(4)]

        # Bind height to children
        self.bind(minimum_height=self.setter('height'))

        # Create header
        date_text = format_date_header(log_date)
        self.header = DateGroupHeader(
            date_text=date_text,
            count=len(logs),
            is_expanded=is_expanded,
            on_toggle=self._on_toggle
        )
        self.add_widget(self.header)

        # Create cards container
        self.cards_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
            padding=[0, dp(4), 0, 0]
        )
        self.cards_container.bind(minimum_height=self.cards_container.setter('height'))

        # Populate cards
        self._populate_cards()

        self.add_widget(self.cards_container)

        # Set initial visibility
        if not is_expanded:
            self.cards_container.height = 0
            self.cards_container.opacity = 0

    def _populate_cards(self) -> None:
        """Populate the cards container with log cards."""
        from ui.components.log_card import LogCard

        self.cards_container.clear_widgets()

        if not self.logs:
            self.cards_container.add_widget(NoActivityLabel())
        else:
            for log in self.logs:
                card = LogCard(log_data=log, view_mode=self.view_mode)
                self.cards_container.add_widget(card)

    def _on_toggle(self, is_expanded: bool) -> None:
        """Handle header toggle."""
        self.is_expanded = is_expanded

        if is_expanded:
            # Expand
            self.cards_container.opacity = 1
            self.cards_container.height = self.cards_container.minimum_height
        else:
            # Collapse
            self.cards_container.opacity = 0
            self.cards_container.height = 0
