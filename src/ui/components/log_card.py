"""
Log card components for HealthLogOps.

This module provides the visual components for displaying health log
entries as styled cards with category colors, icons, and metric badges.

Classes:
    - MetricPill: A small badge displaying a single metric value.
    - OverflowPill: A pill showing "+n" for additional metrics.
    - LogCard: A complete card component for displaying a log entry.
    - SwipeableLogCard: A wrapper that adds swipe-to-edit/delete gestures.

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

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon, MDLabel
from kivy.uix.widget import Widget as KivyWidget

# Try to import plyer for vibration (optional)
try:
    from plyer import vibrator

    HAS_VIBRATOR = True
except ImportError:
    HAS_VIBRATOR = False

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

        # Card styling
        self.orientation = "horizontal"
        self.size_hint_y = None

        # Adjust height based on view mode
        if view_mode == "compact":
            self.height = dp(40)
        elif view_mode == "detailed":
            self.height = dp(120)
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
                radius=[dp(0)]
            )
            Color(*card_bg)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(0)]
            )
            Color(*self.accent_color)
            self._accent = RoundedRectangle(
                pos=self.pos,
                size=(dp(5), self.height),
                radius=[dp(0)]
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

        # Main content container - adjust padding based on view mode
        if self.view_mode == "compact":
            content_padding = [dp(12), dp(10), dp(6), dp(6)]
        elif self.view_mode == "detailed":
            content_padding = [dp(12), dp(10), dp(10), dp(10)]
        else:
            content_padding = [dp(12), dp(8), dp(10), dp(8)]

        content = MDBoxLayout(
            orientation="horizontal",
            padding=content_padding,
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

            def update_icon_bg_pos(instance, value):
                if self._icon_bg:
                    self._icon_bg.pos = value

            def update_icon_bg_size(instance, value):
                if self._icon_bg:
                    self._icon_bg.size = value

            icon_container.bind(pos=update_icon_bg_pos, size=update_icon_bg_size)

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

        # Right side: Text content - adjust spacing based on view mode
        if self.view_mode == "compact":
            text_spacing = dp(0)
            text_padding = [0, 0, 0, 0]
        elif self.view_mode == "detailed":
            text_spacing = dp(8)
            text_padding = [0, dp(2), 0, dp(2)]
        else:
            text_spacing = dp(4)
            text_padding = [0, dp(4), 0, dp(4)]

        text_container = MDBoxLayout(
            orientation="vertical",
            spacing=text_spacing,
            padding=text_padding
        )

        # Top row: Activity name + Time + Menu
        top_row_height = dp(20) if self.view_mode == "compact" else dp(22)
        top_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=top_row_height,
            spacing=dp(4) if self.view_mode == "compact" else dp(8),
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
            width=dp(50) if self.view_mode == "compact" else dp(55),
            halign="right",
            valign="center"
        )
        top_row.add_widget(time_label)

        text_container.add_widget(top_row)

        # Metrics row - will be populated dynamically (hide in compact mode)
        if self.view_mode != "compact":
            metrics_height = dp(28) if self.view_mode == "detailed" else dp(24)
            metrics_padding_top = dp(4) if self.view_mode == "detailed" else dp(2)
            self._metrics_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=metrics_height,
                spacing=dp(4),
                padding=[0, metrics_padding_top, 0, dp(2)]
            )
            self._metrics_row.bind(width=lambda *args: Clock.schedule_once(
                self._update_metrics_display
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
                    height=dp(22),
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


class SwipeableLogCard(KivyWidget):
    """
    A wrapper that adds Gmail-style swipe gestures to LogCard.

    Features:
        - Swipe right (15-20% of screen width) to edit
        - Swipe left (15-20% of screen width) to delete
        - Visual feedback with colored background and icons during swipe
        - Haptic feedback when threshold is reached
        - Snap-back animation when released without completing swipe

    The action only triggers when:
        1. User has swiped past the threshold (15-20% screen width)
        2. Haptic vibration has occurred
        3. User has lifted their finger

    Args:
        log_data: Dictionary containing log entry information.
        view_mode: Display mode ('compact', 'balanced', 'detailed').
        **kwargs: Additional keyword arguments passed to Widget.
    """

    # Swipe threshold as percentage of screen width
    SWIPE_THRESHOLD = 0.175  # 17.5% of screen width

    # Track the current card offset for animation
    card_offset = NumericProperty(0)

    def __init__(
            self,
            log_data: dict[str, Any],
            view_mode: str = "balanced",
            **kwargs
    ) -> None:
        """
        Initialize a SwipeableLogCard.

        :param log_data: Dictionary containing log entry information.
        :param view_mode: Display mode ('compact', 'balanced', 'detailed').
        :param kwargs: Additional keyword arguments passed to Widget.
        """
        super().__init__(**kwargs)

        self.log_data = log_data
        self.view_mode = view_mode

        # Set size
        self.size_hint_y = None

        # Adjust height based on view mode
        if view_mode == "compact":
            self.height = dp(40)
        elif view_mode == "detailed":
            self.height = dp(120)
        else:
            self.height = dp(80)

        # Swipe tracking state
        self._touch_start_x = 0
        self._touch_start_y = 0
        self._is_swiping = False
        self._swipe_direction = None  # 'left' or 'right'
        self._threshold_reached = False
        self._vibrated = False
        self._current_touch = None

        # Get theme colors
        app = MDApp.get_running_app()
        is_dark = app.is_dark_mode() if app and hasattr(app, 'is_dark_mode') else False

        # Colors for swipe backgrounds
        self._edit_color = (0.13, 0.59, 0.95, 1)  # Blue for edit
        self._delete_color = (0.91, 0.30, 0.24, 1)  # Red for delete
        self._bg_color = (0.18, 0.18, 0.20, 1) if is_dark else (0.96, 0.97, 0.98, 1)

        # Build the structure
        self._build_swipeable_structure()

        # Bind card_offset to update the card position
        self.bind(card_offset=self._on_card_offset_change)
        self.bind(pos=self._on_layout_change, size=self._on_layout_change)

    def _build_swipeable_structure(self) -> None:
        """Build the swipeable card structure with background actions."""
        # Draw background and action areas directly on self's canvas
        with self.canvas.before:
            # Background
            Color(*self._bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])

            # Left action area (edit - blue)
            Color(*self._edit_color)
            self._left_rect = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[dp(12), 0, 0, dp(12)])

            # Right action area (delete - red)
            Color(*self._delete_color)
            self._right_rect = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[0, dp(12), dp(12), 0])

        # Edit icon (left side, shown on right swipe)
        self._edit_icon = MDIcon(
            icon="pencil",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
            font_size="24sp",
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            opacity=0
        )

        # Delete icon (right side, shown on left swipe)
        self._delete_icon = MDIcon(
            icon="delete",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
            font_size="24sp",
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            opacity=0
        )

        # Card content (the actual LogCard) - NO size_hint so we control it manually
        self._card = LogCard(
            log_data=self.log_data,
            view_mode=self.view_mode,
            size_hint=(None, None)
        )

        # Add widgets - order matters for z-index (last added is on top)
        self.add_widget(self._edit_icon)
        self.add_widget(self._delete_icon)
        self.add_widget(self._card)

        # Schedule initial layout
        Clock.schedule_once(self._initial_layout, 0)

    def _initial_layout(self, dt) -> None:
        """Set up initial positions after the widget is laid out."""
        self._on_layout_change()

    def _on_layout_change(self, *args) -> None:
        """Update all element positions when layout changes."""
        if not hasattr(self, '_card'):
            return

        # Update background
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

        # Set card size to match self
        self._card.size = self.size

        # Position card at current offset
        self._card.pos = (self.x + self.card_offset, self.y)

        # Position edit icon on the left, vertically centered
        self._edit_icon.center_y = self.center_y
        self._edit_icon.x = self.x + dp(16)

        # Position delete icon on the right, vertically centered
        self._delete_icon.center_y = self.center_y
        self._delete_icon.x = self.right - dp(16) - self._delete_icon.width

        # Update action area rectangles
        self._update_action_areas()

    def _update_action_areas(self) -> None:
        """Update the visible action areas based on card offset."""
        offset = self.card_offset

        if offset > 0:
            # Swiping right - show edit (left side)
            self._left_rect.pos = (self.x, self.y)
            self._left_rect.size = (min(offset + dp(12), self.width), self.height)
            self._right_rect.size = (0, self.height)
        elif offset < 0:
            # Swiping left - show delete (right side)
            abs_offset = abs(offset)
            self._right_rect.pos = (self.right - abs_offset - dp(12), self.y)
            self._right_rect.size = (min(abs_offset + dp(12), self.width), self.height)
            self._left_rect.size = (0, self.height)
        else:
            # No swipe - hide action areas
            self._left_rect.size = (0, self.height)
            self._right_rect.size = (0, self.height)

    def _on_card_offset_change(self, instance, value) -> None:
        """Handle card offset changes for animation."""
        if not hasattr(self, '_card'):
            return

        # Move the card
        self._card.x = self.x + value

        # Update action area backgrounds
        self._update_action_areas()

        # Update icon opacity based on swipe progress
        threshold_px = Window.width * self.SWIPE_THRESHOLD
        if value > 0:
            progress = min(abs(value) / threshold_px, 1.0)
            self._edit_icon.opacity = progress
            self._delete_icon.opacity = 0
        elif value < 0:
            progress = min(abs(value) / threshold_px, 1.0)
            self._delete_icon.opacity = progress
            self._edit_icon.opacity = 0
        else:
            self._edit_icon.opacity = 0
            self._delete_icon.opacity = 0

    def on_touch_down(self, touch) -> bool:
        """Handle touch down event."""
        if self.collide_point(*touch.pos):
            self._touch_start_x = touch.x
            self._touch_start_y = touch.y
            self._is_swiping = False
            self._swipe_direction = None
            self._threshold_reached = False
            self._vibrated = False
            self._current_touch = touch
            self._card_start_x = self._card.x
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch) -> bool:
        """Handle touch move event for swipe detection."""
        if touch.grab_current is not self:
            return super().on_touch_move(touch)

        dx = touch.x - self._touch_start_x
        dy = touch.y - self._touch_start_y

        # Check if this is a horizontal swipe (not vertical scroll)
        if not self._is_swiping:
            if abs(dx) > dp(10) and abs(dx) > abs(dy) * 1.5:
                self._is_swiping = True
                self._swipe_direction = 'right' if dx > 0 else 'left'
            elif abs(dy) > dp(10):
                # This is a vertical scroll, not our swipe
                touch.ungrab(self)
                return super().on_touch_move(touch)

        if self._is_swiping:
            threshold_px = Window.width * self.SWIPE_THRESHOLD
            max_swipe = threshold_px * 1.2  # Allow slight over-swipe

            if self._swipe_direction == 'right' and dx > 0:
                # Swiping right - show edit action
                self.card_offset = min(dx, max_swipe)

                # Check threshold
                if dx >= threshold_px and not self._threshold_reached:
                    self._threshold_reached = True
                    self._vibrate()
                elif dx < threshold_px:
                    self._threshold_reached = False

            elif self._swipe_direction == 'left' and dx < 0:
                # Swiping left - show delete action
                self.card_offset = max(dx, -max_swipe)

                # Check threshold
                if abs(dx) >= threshold_px and not self._threshold_reached:
                    self._threshold_reached = True
                    self._vibrate()
                elif abs(dx) < threshold_px:
                    self._threshold_reached = False

            return True

        return super().on_touch_move(touch)

    def on_touch_up(self, touch) -> bool:
        """Handle touch up event - trigger action if threshold was reached."""
        if touch.grab_current is not self:
            return super().on_touch_up(touch)

        touch.ungrab(self)

        if self._is_swiping and self._threshold_reached:
            # All conditions met: swiped past threshold + vibrated + finger lifted
            if self._swipe_direction == 'right':
                # Animate card off then trigger edit
                self._animate_complete_swipe('right', self._trigger_edit)
            elif self._swipe_direction == 'left':
                # Animate card off then trigger delete
                self._animate_complete_swipe('left', self._trigger_delete)
        else:
            # Snap back to original position
            self._animate_snap_back()

        self._is_swiping = False
        self._swipe_direction = None
        self._current_touch = None

        return True

    def _vibrate(self) -> None:
        """Trigger haptic feedback."""
        if not self._vibrated:
            self._vibrated = True
            if HAS_VIBRATOR:
                try:
                    vibrator.vibrate(0.02)  # 20ms vibration
                except Exception:
                    pass  # Vibration not available

    def _animate_snap_back(self) -> None:
        """Animate the card back to its original position."""
        anim = Animation(card_offset=0, duration=0.2, t='out_cubic')
        anim.start(self)

    def _animate_complete_swipe(self, direction: str, callback: Callable) -> None:
        """Animate the card completing the swipe, then call callback."""
        if direction == 'right':
            target = self.width
        else:
            target = -self.width

        anim = Animation(card_offset=target, duration=0.15, t='out_cubic')

        def on_complete(*args):
            # Reset position
            self.card_offset = 0
            # Then trigger action
            Clock.schedule_once(lambda dt: callback(), 0.05)

        anim.bind(on_complete=on_complete)
        anim.start(self)

    def _trigger_edit(self) -> None:
        """Trigger the edit action."""
        log_id = self.log_data.get("id")
        if log_id:
            app = MDApp.get_running_app()
            if app and hasattr(app, 'switch_to_edit_log'):
                app.switch_to_edit_log(log_id)

    def _trigger_delete(self) -> None:
        """Trigger the delete action with confirmation dialog."""
        log_id = self.log_data.get("id")
        if log_id:
            app = MDApp.get_running_app()
            if app and hasattr(app, 'confirm_delete_log'):
                app.confirm_delete_log(log_id)
