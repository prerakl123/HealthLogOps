"""
Dropdown components for HealthLogOps.

This module provides beautifully styled dropdown menu components that replace
the default Kivy Spinner with a more modern, animated design.

Classes:
    DropdownItem: Individual selectable item within a dropdown.
    StyledDropdown: Complete dropdown menu with animation and styling.

Example:
    >>> dropdown = StyledDropdown(on_select=handle_selection)
    >>> dropdown.values = ["Option 1", "Option 2", "Option 3"]
    >>> dropdown.text = "Select an option"
"""

from typing import Callable, Optional

from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon, MDLabel

from ui.constants import CATEGORY_ICONS


class DropdownItem(ButtonBehavior, MDBoxLayout):
    """
    A single selectable item within a styled dropdown list.

    Provides visual feedback on press/release and executes a callback
    when selected by the user.

    Attributes:
        text: The display text for this dropdown item.
        icon: Optional Material Design icon name to display.
        selected: Whether this item is currently selected.

    Args:
        text: The text to display for this item.
        icon: Optional icon name from Material Design icons.
        on_select: Callback function invoked when the item is selected.
            The callback receives the item's text as its argument.
        **kwargs: Additional keyword arguments passed to MDBoxLayout.

    Example:
        >>> item = DropdownItem(
        ...     text="Strength Training",
        ...     icon="weight-lifter",
        ...     on_select=lambda val: print(f"Selected: {val}")
        ... )
    """

    text = StringProperty("")
    """The display text for this dropdown item."""

    icon = StringProperty("")
    """Optional Material Design icon name to display alongside the text."""

    selected = BooleanProperty(False)
    """Whether this item is currently in a selected state."""

    def __init__(
        self,
        text: str = "",
        icon: str = "",
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> None:
        """
        Initialize a DropdownItem.

        :param text: The text to display for this item.
        :param icon: Optional icon name from Material Design icons.
        :param on_select: Callback function invoked when item is selected.
        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)
        self.text = text
        self.icon = icon
        self.on_select_callback = on_select

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(48)
        self.padding = [dp(16), dp(8), dp(16), dp(8)]
        self.spacing = dp(12)

        # Background for hover effect
        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )

        self.bind(pos=self._update_bg, size=self._update_bg)

        # Icon (if provided)
        if icon:
            icon_widget = MDIcon(
                icon=icon,
                theme_icon_color="Custom",
                icon_color=(0, 0.59, 0.53, 1),
                pos_hint={"center_y": 0.5},
                size_hint_x=None,
                width=dp(24)
            )
            self.add_widget(icon_widget)

        # Text label
        label = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.25, 1),
            pos_hint={"center_y": 0.5},
            shorten=True,
            shorten_from="right"
        )
        self.add_widget(label)

    def _update_bg(self, *args) -> None:
        """
        Update the background rectangle position and size.

        Called automatically when the widget's position or size changes.
        """
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_press(self) -> None:
        """
        Handle press event with visual feedback.

        Changes the background color to indicate the pressed state.
        """
        self._bg_color.rgba = (0, 0.59, 0.53, 0.15)

    def on_release(self) -> None:
        """
        Handle release event and trigger selection callback.

        Resets the visual state and invokes the on_select callback
        if one was provided during initialization.
        """
        self._bg_color.rgba = (0, 0, 0, 0)
        if self.on_select_callback:
            self.on_select_callback(self.text)


class DropdownPopup(ModalView):
    """
    A popup container for dropdown items using ModalView.

    Uses ModalView for proper overlay handling with transparent background,
    allowing clicks outside to dismiss.
    """

    max_height = NumericProperty(dp(250))
    """Maximum height of the dropdown popup."""

    def __init__(self, attached_widget=None, **kwargs):
        # Set ModalView properties before super().__init__
        kwargs.setdefault('background', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('overlay_color', (0, 0, 0, 0))
        kwargs.setdefault('auto_dismiss', True)
        kwargs.setdefault('size_hint', (None, None))

        super().__init__(**kwargs)

        self._attached_widget = attached_widget

        # Container for items
        self.container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(4), dp(4)],
            spacing=dp(2),
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        # ScrollView for items
        self.scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(3),
            bar_color=(0, 0.59, 0.53, 0.4),
        )
        self.scroll_view.add_widget(self.container)

        # Wrapper with background
        self.wrapper = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
        )

        # Add background graphics to wrapper
        with self.wrapper.canvas.before:
            Color(0, 0, 0, 0.08)
            self._shadow = RoundedRectangle(radius=[dp(0), dp(0), dp(12), dp(12)])
            Color(1, 1, 1, 1)
            self._bg = RoundedRectangle(radius=[dp(0), dp(0), dp(12), dp(12)])
            Color(0.90, 0.91, 0.92, 1)
            self._border = RoundedRectangle(radius=[dp(0), dp(0), dp(12), dp(12)])
            Color(1, 1, 1, 1)
            self._inner = RoundedRectangle(radius=[dp(0), dp(0), dp(12), dp(12)])

        self.wrapper.bind(pos=self._update_wrapper_graphics, size=self._update_wrapper_graphics)
        self.wrapper.add_widget(self.scroll_view)
        super().add_widget(self.wrapper)

    def _update_wrapper_graphics(self, instance, value):
        """Update background graphics when position/size changes."""
        self._shadow.pos = (instance.x + dp(2), instance.y - dp(2))
        self._shadow.size = instance.size
        self._bg.pos = instance.pos
        self._bg.size = instance.size
        self._border.pos = instance.pos
        self._border.size = instance.size
        self._inner.pos = (instance.x + dp(1), instance.y + dp(1))
        self._inner.size = (instance.width - dp(2), instance.height - dp(2))

    def _align_center(self, *args):
        """Override ModalView's centering behavior to use custom positioning."""
        # Do nothing - we handle positioning ourselves in _position_popup
        pass

    def _position_popup(self):
        """Position the popup below the attached widget."""
        if self._attached_widget:
            # Get position in window coordinates
            pos = self._attached_widget.to_window(0, 0, initial=False)

            # Calculate content height
            content_height = self.container.height + dp(8)
            target_height = min(content_height, self.max_height)
            print("Content height:", content_height)
            print("Max height:", self.max_height)
            print("pos[1]:", pos[1])
            print("self.height:", self.height)

            # Set size
            self.width = self._attached_widget.width
            self.height = target_height

            # Position below the widget (pos[1] is bottom of widget)
            self.x = dp(32)
            self.y = pos[1] / 2 + target_height
            print("self.y:", self.y)
            print()

    def open(self, *args, **kwargs):
        """Open the dropdown and position it below the attached widget."""
        # Position before opening
        self._position_popup()
        super().open(*args, **kwargs)
        # Re-position after open to ensure layout is correct
        Clock.schedule_once(lambda dt: self._position_popup(), 0)

    def on_open(self):
        """Ensure positioning after ModalView opens."""
        self._position_popup()

    def add_item(self, item):
        """Add a dropdown item to the container."""
        self.container.add_widget(item)

    def clear_items(self):
        """Clear all items from the dropdown."""
        self.container.clear_widgets()


class StyledDropdown(MDBoxLayout):
    """
    A beautifully styled dropdown menu with smooth animations.

    Replaces the default Kivy Spinner with a modern dropdown that features:
    - ModalView-based popup for reliable z-ordering
    - Category-specific icons
    - Clean Material Design styling
    - Touch-friendly interaction

    Attributes:
        text: Currently selected value or placeholder text.
        values: List of selectable options.
        is_open: Whether the dropdown is currently expanded.

    Args:
        on_select: Callback function invoked when a selection is made.
            The callback receives the selected value as its argument.
        **kwargs: Additional keyword arguments passed to MDBoxLayout.

    Example:
        >>> def handle_selection(value):
        ...     print(f"Selected: {value}")
        >>>
        >>> dropdown = StyledDropdown(on_select=handle_selection)
        >>> dropdown.values = ["Option A", "Option B", "Option C"]
        >>> dropdown.text = "Choose one..."
    """

    text = StringProperty("Select...")
    """The currently displayed text (selected value or placeholder)."""

    values = ListProperty([])
    """List of available options to select from."""

    is_open = BooleanProperty(False)
    """Whether the dropdown menu is currently expanded."""

    def __init__(
        self,
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.on_select_callback = on_select
        self._dropdown: Optional[DropdownPopup] = None

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(52)

        # Main button area
        self._build_button()

    def _build_button(self) -> None:
        """
        Build the main dropdown button widget.

        Creates the clickable button area with icon, text label,
        and chevron indicator.
        """
        button_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            padding=[dp(14), 0, dp(10), 0],
            spacing=dp(8)
        )

        # Background
        with button_box.canvas.before:
            Color(0.96, 0.97, 0.98, 1)
            self._btn_bg = RoundedRectangle(
                pos=button_box.pos,
                size=button_box.size,
                radius=[dp(10)]
            )
            Color(0.88, 0.89, 0.91, 1)  # Softer border color
            self._btn_border = RoundedRectangle(
                pos=button_box.pos,
                size=button_box.size,
                radius=[dp(10)]
            )
            Color(0.96, 0.97, 0.98, 1)
            self._btn_inner = RoundedRectangle(
                pos=(button_box.x + dp(1), button_box.y + dp(1)),
                size=(button_box.width - dp(2), button_box.height - dp(2)),
                radius=[dp(9)]
            )

        button_box.bind(pos=self._update_btn_graphics, size=self._update_btn_graphics)

        # Category icon
        self.category_icon = MDIcon(
            icon=CATEGORY_ICONS.get("default"),
            theme_icon_color="Custom",
            icon_color=(0, 0.59, 0.53, 1),
            pos_hint={"center_y": 0.5},
            size_hint_x=None,
            width=dp(24)
        )
        button_box.add_widget(self.category_icon)

        # Text label
        self.text_label = MDLabel(
            text=self.text,
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.25, 1),
            pos_hint={"center_y": 0.5},
            shorten=True,
            shorten_from="right"
        )
        self.bind(text=lambda inst, val: setattr(self.text_label, 'text', val))
        button_box.add_widget(self.text_label)

        # Chevron icon
        self.chevron = MDIcon(
            icon="chevron-down",
            theme_icon_color="Custom",
            icon_color=(0.5, 0.5, 0.55, 1),
            pos_hint={"center_y": 0.5},
            size_hint_x=None,
            width=dp(24)
        )
        button_box.add_widget(self.chevron)

        # Make clickable - using on_touch_up to avoid issues with touch propagation
        button_box.bind(on_touch_up=self._on_button_touch)

        self.button_box = button_box
        self.add_widget(button_box)

    def _update_btn_graphics(self, instance, value) -> None:
        """
        Update button background graphics when position/size changes.

        :param instance: The widget instance that triggered the update.
        :param value: The new position or size value.
        """
        self._btn_bg.pos = instance.pos
        self._btn_bg.size = instance.size
        self._btn_border.pos = instance.pos
        self._btn_border.size = instance.size
        self._btn_inner.pos = (instance.x + dp(1), instance.y + dp(1))
        self._btn_inner.size = (instance.width - dp(2), instance.height - dp(2))

    def _on_button_touch(self, instance, touch) -> bool:
        """
        Handle touch events on the dropdown button.

        :param instance: The widget that received the touch.
        :param touch: The touch event object.
        :returns: True if the touch was handled, False otherwise.
        """
        if instance.collide_point(*touch.pos) and not self.is_open:
            # Schedule the toggle to avoid touch event conflicts
            Clock.schedule_once(lambda dt: self._do_open(), 0)
            return True
        return False

    def _do_open(self) -> None:
        """Actually open the dropdown (called from scheduled callback)."""
        if not self.is_open:
            self.open_dropdown()

    def toggle_dropdown(self) -> None:
        """
        Toggle the dropdown between open and closed states.

        If currently closed, opens the dropdown with animation.
        If currently open, closes the dropdown with animation.
        """
        if self.is_open:
            self.close_dropdown()
        else:
            self.open_dropdown()

    def open_dropdown(self) -> None:
        """
        Open the dropdown with items populated.

        Creates the dropdown popup, populates it with items,
        and opens it below the button. Does nothing if already open
        or if there are no values to display.
        """
        if self.is_open or not self.values:
            return

        self.is_open = True
        self.chevron.icon = "chevron-up"

        # Create dropdown popup
        self._dropdown = DropdownPopup(attached_widget=self.button_box)
        self._dropdown.bind(on_dismiss=self._on_dropdown_dismiss)

        # Add items
        for value in self.values:
            icon = CATEGORY_ICONS.get(value, CATEGORY_ICONS.get("default"))
            item = DropdownItem(
                text=value,
                icon=icon,
                on_select=self._on_item_selected
            )
            self._dropdown.add_item(item)

        # Open dropdown
        self._dropdown.open()

    def close_dropdown(self) -> None:
        """
        Close the dropdown.

        Dismisses the dropdown popup. Does nothing if already closed.
        """
        if not self.is_open or not self._dropdown:
            return

        self._dropdown.dismiss()

    def _on_dropdown_dismiss(self, *args) -> None:
        """
        Handle dropdown dismissal.

        Called when the dropdown is dismissed (closed).
        """
        self.is_open = False
        self.chevron.icon = "chevron-down"
        self._dropdown = None

    def _on_item_selected(self, value: str) -> None:
        """
        Handle item selection from the dropdown.

        Updates the displayed text and icon, closes the dropdown,
        and invokes the on_select callback if provided.

        :param value: The selected item's text value.
        """
        self.text = value

        # Update icon
        self.category_icon.icon = CATEGORY_ICONS.get(value, CATEGORY_ICONS.get("default"))

        self.close_dropdown()

        if self.on_select_callback:
            self.on_select_callback(value)

    def on_parent(self, instance, parent) -> None:
        """Clean up dropdown when widget is removed from parent."""
        if parent is None and self._dropdown:
            self._dropdown.dismiss()
            self._dropdown = None
