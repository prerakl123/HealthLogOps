"""
Log card components for HealthLogOps.

This module provides the visual components for displaying health log
entries as styled cards with category colors, icons, and metric badges.

Classes:
    - MetricPill: A small badge displaying a single metric value.
    - OverflowPill: A pill showing "+n" for additional metrics.
    - LogCard: A complete card component for displaying a log entry.

Example:
    >>> log_data = {
    ...     "activity_name": "Morning Run",
    ...     "category_name": "Cardio",
    ...     "timestamp": datetime.now(),
    ...     "metrics": {"duration_min": 30, "distance_km": 5.0}
    ... }
    >>> card = LogCard(log_data=log_data)
"""

from typing import Any, Callable, Optional

from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.menu import MDDropdownMenu

from ui.constants import (
    CATEGORY_COLORS,
    CATEGORY_COLORS_LIGHT,
    CATEGORY_ICONS,
    METRIC_ICONS,
    ColorTuple,
)


class MetricPill(MDBoxLayout):
    """
    A styled pill/tag showing a metric value with an icon.

    Displays a small rounded badge with a category-appropriate color,
    an icon representing the metric type, and the metric value.
    Pills never truncate text - they display the full value.

    Attributes:
        pill_width: The calculated width of the pill.

    Args:
        metric_key: The name/key of the metric (e.g., "duration_min").
        metric_value: The value to display.
        color: The primary accent color (RGBA tuple).
        light_color: The light background color (RGBA tuple).
        **kwargs: Additional keyword arguments passed to MDBoxLayout.
    """

    pill_width = NumericProperty(0)
    """The calculated width of this pill."""

    def __init__(
        self,
        metric_key: str,
        metric_value: Any,
        color: ColorTuple,
        light_color: ColorTuple,
        **kwargs
    ) -> None:
        """
        Initialize a MetricPill.

        :param metric_key: The name/key of the metric for icon lookup.
        :param metric_value: The value to display in the pill.
        :param color: Primary accent color as RGBA tuple.
        :param light_color: Light background color as RGBA tuple.
        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.height = dp(24)
        self.padding = [dp(6), dp(2), dp(6), dp(2)]
        self.spacing = dp(16)

        # Calculate width based on value length
        value_str = str(metric_value)
        self.width = dp(48) + len(value_str) * dp(5)
        self.pill_width = self.width

        # Get icon for this metric
        icon_name = METRIC_ICONS.get(
            metric_key.lower(),
            METRIC_ICONS.get("default")
        )

        # Draw background with border
        with self.canvas.before:
            # Light background fill
            Color(*light_color)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            # Border
            Color(*color)
            self._border = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        # Draw inner rectangle for border effect
        with self.canvas.before:
            Color(*light_color)
            self._inner = RoundedRectangle(
                pos=(self.x + dp(1), self.y + dp(1)),
                size=(self.width - dp(2), self.height - dp(2)),
                radius=[dp(12)]
            )

        self.bind(pos=self._update_graphics, size=self._update_graphics)

        # Icon wrapper for proper size control
        icon_wrapper = MDBoxLayout(
            size_hint=(None, None),
            size=(dp(12), dp(16)),
            pos_hint={"center_y": 0.5}
        )
        icon = MDIcon(
            icon=icon_name,
            theme_icon_color="Custom",
            icon_color=color,
            font_size="11sp",
            size=(dp(8), dp(12)),
            pos_hint={"center_x": 0.75, "center_y": 0.5},
            halign="center",
            valign="center"
        )
        icon_wrapper.add_widget(icon)
        self.add_widget(icon_wrapper)

        # Value label
        value_label = MDLabel(
            text=value_str,
            font_style="Label",
            role="small",
            theme_text_color="Custom",
            text_color=color,
            bold=True,
            halign="left",
            valign="center",
            size_hint_x=None,
            width=len(value_str) * dp(6.5)
        )
        self.add_widget(value_label)

    def _update_graphics(self, *args) -> None:
        """Update the pill graphics when position or size changes."""
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.pos = self.pos
        self._border.size = self.size
        self._inner.pos = (self.x + dp(1), self.y + dp(1))
        self._inner.size = (self.width - dp(2), self.height - dp(2))


class OverflowPill(MDBoxLayout):
    """
    A pill showing "+n" to indicate additional metrics not displayed.

    Args:
        count: The number of additional metrics.
        color: The primary accent color (RGBA tuple).
        light_color: The light background color (RGBA tuple).
        **kwargs: Additional keyword arguments passed to MDBoxLayout.
    """

    pill_width = NumericProperty(0)
    """The calculated width of this pill."""

    def __init__(
        self,
        count: int,
        color: ColorTuple,
        light_color: ColorTuple,
        **kwargs
    ) -> None:
        """
        Initialize an OverflowPill.

        :param count: Number of additional hidden metrics.
        :param color: Primary accent color as RGBA tuple.
        :param light_color: Light background color as RGBA tuple.
        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.height = dp(24)
        self.padding = [dp(6), dp(2), dp(6), dp(2)]

        text = f"+{count}"
        self.width = dp(24) + len(text) * dp(4)
        self.pill_width = self.width

        # Draw background with border
        with self.canvas.before:
            Color(*light_color)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            Color(*color)
            self._border = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            Color(*light_color)
            self._inner = RoundedRectangle(
                pos=(self.x + dp(1), self.y + dp(1)),
                size=(self.width - dp(2), self.height - dp(2)),
                radius=[dp(12)]
            )

        self.bind(pos=self._update_graphics, size=self._update_graphics)

        # Label - NO shorten
        label = MDLabel(
            text=text,
            font_style="Label",
            role="small",
            theme_text_color="Custom",
            text_color=color,
            bold=True,
            halign="center",
            valign="center"
        )
        self.add_widget(label)

    def _update_graphics(self, *args) -> None:
        """Update the pill graphics when position or size changes."""
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.pos = self.pos
        self._border.size = self.size
        self._inner.pos = (self.x + dp(1), self.y + dp(1))
        self._inner.size = (self.width - dp(2), self.height - dp(2))


class LogCard(MDBoxLayout):
    """
    A beautifully styled card component for displaying a health log entry.

    Features a category-colored accent strip on the left, a centered
    category icon, activity name, time (top right), and metric pills
    that automatically show "+n" for overflow.

    Attributes:
        log_data: The log entry data dictionary.
        on_tap_callback: Optional callback for card tap events.
        accent_color: The category's primary color.
        light_color: The category's light background color.
        category_icon: The Material Design icon for the category.

    Args:
        log_data: Dictionary containing log entry information.
            Expected keys: activity_name, category_name, timestamp, metrics
        on_tap_callback: Optional function called when card is tapped.
        view_mode: Display mode ('compact', 'balanced', 'detailed').
        **kwargs: Additional keyword arguments passed to MDBoxLayout.
    """

    def __init__(
        self,
        log_data: dict[str, Any],
        on_tap_callback: Optional[Callable[[int], None]] = None,
        view_mode: str = "balanced",
        **kwargs
    ) -> None:
        """
        Initialize a LogCard.

        :param log_data: Dictionary containing log entry information.
        :param on_tap_callback: Optional function called when card is tapped.
        :param view_mode: Display mode ('compact', 'balanced', 'detailed').
        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)
        self.log_data = log_data
        self.on_tap_callback = on_tap_callback
        self.view_mode = view_mode
        self._metrics_row = None
        self._all_metrics = list(log_data.get("metrics", {}).items())
        self._menu = None  # Context menu reference

        # Card styling
        self.orientation = "horizontal"
        self.size_hint_y = None

        # Adjust height based on view mode
        if view_mode == "compact":
            self.height = dp(36)
        elif view_mode == "detailed":
            self.height = dp(110)
        else:
            self.height = dp(80)

        self.padding = 0
        self.spacing = 0

        # Get category color
        category_name = log_data.get("category_name", "default")
        self.accent_color: ColorTuple = CATEGORY_COLORS.get(
            category_name,
            CATEGORY_COLORS["default"]
        )
        self.light_color: ColorTuple = CATEGORY_COLORS_LIGHT.get(
            category_name,
            CATEGORY_COLORS_LIGHT["default"]
        )
        self.category_icon: str = CATEGORY_ICONS.get(
            category_name,
            CATEGORY_ICONS["default"]
        )

        # Get theme colors
        app = MDApp.get_running_app()
        is_dark = app.is_dark_mode() if app and hasattr(app, 'is_dark_mode') else False

        card_bg = (0.18, 0.18, 0.20, 1) if is_dark else (1, 1, 1, 1)
        shadow_color = (0, 0, 0, 0.08) if is_dark else (0, 0, 0, 0.03)

        # Draw card background with shadow
        with self.canvas.before:
            Color(*shadow_color)
            self._shadow = RoundedRectangle(
                pos=(self.x + dp(1), self.y - dp(1)),
                size=self.size,
                radius=[dp(12)]
            )
            Color(*card_bg)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            Color(*self.accent_color)
            self._accent = RoundedRectangle(
                pos=self.pos,
                size=(dp(5), self.height),
                radius=[dp(12), 0, 0, dp(12)]
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._build_card()

        # Schedule metrics layout after widget is ready
        Clock.schedule_once(self._update_metrics_display, 0)


    def _update_canvas(self, *args) -> None:
        """Update the card background graphics when position or size changes."""
        self._shadow.pos = (self.x + dp(1), self.y - dp(1))
        self._shadow.size = self.size
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._accent.pos = self.pos
        self._accent.size = (dp(5), self.height)

    def _build_card(self) -> None:
        """Build the internal structure of the card."""
        # Get theme colors
        app = MDApp.get_running_app()
        is_dark = app.is_dark_mode() if app and hasattr(app, 'is_dark_mode') else False

        text_primary = (0.9, 0.9, 0.92, 1) if is_dark else (0.15, 0.15, 0.2, 1)
        text_secondary = (0.65, 0.65, 0.7, 1) if is_dark else (0.55, 0.55, 0.6, 1)

        # Initialize icon bg reference
        self._icon_bg = None

        # Main content container
        content = MDBoxLayout(
            orientation="horizontal",
            padding=[dp(12), dp(8), dp(10), dp(8)],
            spacing=dp(10)
        )

        # Left side: Icon container (hide in compact mode)
        if self.view_mode != "compact":
            icon_container = MDBoxLayout(
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                pos_hint={"center_y": 0.5}
            )
            with icon_container.canvas.before:
                Color(*self.accent_color[:3], 0.10)
                self._icon_bg = RoundedRectangle(
                    pos=icon_container.pos,
                    size=icon_container.size,
                    radius=[dp(10)]
                )
            icon_container.bind(
                pos=lambda i, v: setattr(self._icon_bg, 'pos', v),
                size=lambda i, v: setattr(self._icon_bg, 'size', v)
            )

            # Center the icon within container using an inner layout
            icon_wrapper = MDBoxLayout(
                size_hint=(1, 1),
                padding=[dp(8), 0, 0, 0]  # Left padding to shift icon right
            )
            icon = MDIcon(
                icon=self.category_icon,
                theme_icon_color="Custom",
                icon_color=self.accent_color,
                pos_hint={"center_y": 0.5},
                halign="center",
                valign="center"
            )
            icon_wrapper.add_widget(icon)
            icon_container.add_widget(icon_wrapper)
            content.add_widget(icon_container)

        # Right side: Text content
        text_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=[0, dp(4), 0, dp(4)]
        )

        # Top row: Activity name + Time + Menu
        top_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(22),
            spacing=dp(8)
        )

        # Activity name - allow natural sizing, no forced shorten
        activity_label = MDLabel(
            text=self.log_data.get("activity_name", "Unknown"),
            font_style="Title",
            role="small",
            bold=True,
            theme_text_color="Custom",
            text_color=text_primary,
            size_hint_x=1,
            halign="left",
            valign="center"
        )
        top_row.add_widget(activity_label)

        # Time only (top right, grey) - no date
        timestamp = self.log_data.get("timestamp")
        time_str = timestamp.strftime("%I:%M %p").lstrip("0") if timestamp else ""

        time_label = MDLabel(
            text=time_str,
            font_style="Label",
            role="small",
            theme_text_color="Custom",
            text_color=text_secondary,
            size_hint_x=None,
            width=dp(55),
            halign="right",
            valign="center"
        )
        top_row.add_widget(time_label)

        # Triple-dot menu button
        menu_button = MDIconButton(
            icon="dots-vertical",
            theme_icon_color="Custom",
            icon_color=text_secondary,
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={"center_y": 0.5},
            on_release=lambda x: self._show_context_menu(x)
        )
        top_row.add_widget(menu_button)

        text_container.add_widget(top_row)

        # Metrics row - will be populated dynamically (hide in compact mode)
        if self.view_mode != "compact":
            self._metrics_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(24),
                spacing=dp(4),
                padding=[0, dp(2), 0, dp(2)]
            )
            self._metrics_row.bind(width=lambda *args: Clock.schedule_once(
                self._update_metrics_display, 0
            ))
            text_container.add_widget(self._metrics_row)

        # Show notes in detailed mode
        if self.view_mode == "detailed":
            notes = self.log_data.get("notes")
            if notes:
                notes_label = MDLabel(
                    text=notes[:100] + ("..." if len(notes) > 100 else ""),
                    font_style="Label",
                    role="small",
                    theme_text_color="Custom",
                    text_color=text_secondary,
                    size_hint_y=None,
                    height=dp(18),
                    halign="left",
                    valign="center"
                )
                text_container.add_widget(notes_label)

        # Bottom spacer
        text_container.add_widget(MDBoxLayout(size_hint_y=1))

        content.add_widget(text_container)
        self.add_widget(content)

    def _update_metrics_display(self, *args) -> None:
        """Update metrics pills based on available width."""
        if not self._metrics_row or not self._all_metrics:
            return

        self._metrics_row.clear_widgets()

        available_width = self._metrics_row.width - dp(10)  # Some padding
        if available_width <= 0:
            return

        # Calculate which pills fit
        pills_to_show = []
        used_width = 0
        overflow_pill_width = dp(40)  # Approximate width for "+n"

        for key, value in self._all_metrics:
            pill = MetricPill(
                metric_key=key,
                metric_value=value,
                color=self.accent_color,
                light_color=self.light_color
            )
            pill_width = pill.pill_width + dp(4)  # Include spacing

            remaining = len(self._all_metrics) - len(pills_to_show)

            # Check if this pill fits
            if remaining > 1:
                # Need to reserve space for potential overflow pill
                if used_width + pill_width + overflow_pill_width <= available_width:
                    pills_to_show.append(pill)
                    used_width += pill_width
                else:
                    break
            else:
                # Last pill - just check if it fits
                if used_width + pill_width <= available_width:
                    pills_to_show.append(pill)
                    used_width += pill_width
                else:
                    break

        # Add visible pills
        for pill in pills_to_show:
            self._metrics_row.add_widget(pill)

        # Add overflow indicator if needed
        overflow_count = len(self._all_metrics) - len(pills_to_show)
        if overflow_count > 0:
            overflow_pill = OverflowPill(
                count=overflow_count,
                color=self.accent_color,
                light_color=self.light_color
            )
            self._metrics_row.add_widget(overflow_pill)

        # Add flexible spacer
        self._metrics_row.add_widget(MDBoxLayout(size_hint_x=1))

    def _show_context_menu(self, button) -> None:
        """Show context menu with edit and delete options."""
        if self._menu:
            self._menu.dismiss()
            self._menu = None

        menu_items = [
            {
                "text": "Edit",
                "leading_icon": "pencil-outline",
                "on_release": lambda: self._on_menu_edit(),
            },
            {
                "text": "Delete",
                "leading_icon": "delete-outline",
                "on_release": lambda: self._on_menu_delete(),
            },
        ]

        self._menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=3,
        )
        self._menu.open()

    def _on_menu_edit(self) -> None:
        """Handle edit action from context menu."""
        if self._menu:
            self._menu.dismiss()
            self._menu = None

        log_id = self.log_data.get("id")
        if log_id:
            app = MDApp.get_running_app()
            if app and hasattr(app, 'switch_to_edit_log'):
                app.switch_to_edit_log(log_id)

    def _on_menu_delete(self) -> None:
        """Handle delete action from context menu."""
        if self._menu:
            self._menu.dismiss()
            self._menu = None

        log_id = self.log_data.get("id")
        if log_id:
            app = MDApp.get_running_app()
            if app and hasattr(app, 'confirm_delete_log'):
                app.confirm_delete_log(log_id)
