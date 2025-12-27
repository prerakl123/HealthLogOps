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

from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
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
            Color(0, 0, 0, 0)
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
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0.59, 0.53, 0.15)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )

    def on_release(self) -> None:
        """
        Handle release event and trigger selection callback.

        Resets the visual state and invokes the on_select callback
        if one was provided during initialization.
        """
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
        if self.on_select_callback:
            self.on_select_callback(self.text)


class StyledDropdown(MDBoxLayout):
    """
    A beautifully styled dropdown menu with smooth animations.

    Replaces the default Kivy Spinner with a modern dropdown that features:
    - Animated open/close transitions
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
        """
        Initialize a StyledDropdown.

        :param on_select: Callback function invoked when a selection is made.
        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)
        self.on_select_callback = on_select
        self.dropdown_container: Optional[MDBoxLayout] = None
        self._dropdown_anim: Optional[Animation] = None

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

        # Make clickable
        button_box.bind(on_touch_down=self._on_button_touch)

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
        if instance.collide_point(*touch.pos):
            self.toggle_dropdown()
            return True
        return False

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
        Open the dropdown with a fade-in animation.

        Creates the dropdown container, populates it with items,
        and animates it into view. Does nothing if already open
        or if there are no values to display.
        """
        if self.is_open or not self.values:
            return

        self.is_open = True

        # Change chevron icon
        self.chevron.icon = "chevron-up"

        # Remove any existing dropdown container first
        if self.dropdown_container and self.dropdown_container.parent:
            self.remove_widget(self.dropdown_container)
            self.dropdown_container = None

        # Create dropdown container
        self.dropdown_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=0,
            padding=[dp(4), dp(4)],
            spacing=dp(2),
            opacity=0
        )

        # Background with shadow
        with self.dropdown_container.canvas.before:
            # Soft shadow
            Color(0, 0, 0, 0.04)
            self._drop_shadow = RoundedRectangle(
                pos=(self.dropdown_container.x + dp(2), self.dropdown_container.y - dp(2)),
                size=self.dropdown_container.size,
                radius=[dp(12)]
            )
            # White background
            Color(1, 1, 1, 1)
            self._drop_bg = RoundedRectangle(
                pos=self.dropdown_container.pos,
                size=self.dropdown_container.size,
                radius=[dp(12)]
            )
            # Subtle border
            Color(0.92, 0.93, 0.94, 1)
            self._drop_border = RoundedRectangle(
                pos=self.dropdown_container.pos,
                size=self.dropdown_container.size,
                radius=[dp(12)]
            )
            Color(1, 1, 1, 1)
            self._drop_inner = RoundedRectangle(
                pos=(self.dropdown_container.x + dp(1), self.dropdown_container.y + dp(1)),
                size=(self.dropdown_container.width - dp(2), self.dropdown_container.height - dp(2)),
                radius=[dp(11)]
            )

        self.dropdown_container.bind(
            pos=self._update_dropdown_graphics,
            size=self._update_dropdown_graphics
        )

        # Add items
        for value in self.values:
            icon = CATEGORY_ICONS.get(value, CATEGORY_ICONS.get("default"))
            item = DropdownItem(
                text=value,
                icon=icon,
                on_select=self._on_item_selected
            )
            self.dropdown_container.add_widget(item)

        self.add_widget(self.dropdown_container)

        # Calculate target height
        target_height = min(len(self.values) * dp(48) + dp(8), dp(250))

        # Animate open
        anim = Animation(height=target_height, opacity=1, duration=0.2, t='out_cubic')
        anim.start(self.dropdown_container)

        # Update parent height
        self.height = dp(52) + target_height + dp(8)

    def close_dropdown(self) -> None:
        """
        Close the dropdown with a fade-out animation.

        Animates the dropdown container out of view and removes it
        from the widget tree. Does nothing if already closed.
        """
        if not self.is_open or not self.dropdown_container:
            return

        self.is_open = False

        # Change chevron icon back
        self.chevron.icon = "chevron-down"

        # Animate close
        anim = Animation(height=0, opacity=0, duration=0.15, t='out_cubic')
        anim.bind(on_complete=self._remove_dropdown)
        anim.start(self.dropdown_container)

        # Reset height
        self.height = dp(52)

    def _remove_dropdown(self, *args) -> None:
        """
        Remove the dropdown container from the widget tree.

        Called as a callback after the close animation completes.
        """
        if self.dropdown_container and self.dropdown_container.parent:
            self.remove_widget(self.dropdown_container)
            self.dropdown_container = None

    def _update_dropdown_graphics(self, instance, value) -> None:
        """
        Update dropdown container graphics when position/size changes.

        :param instance: The widget instance that triggered the update.
        :param value: The new position or size value.
        """
        if hasattr(self, '_drop_shadow'):
            self._drop_shadow.pos = (instance.x + dp(2), instance.y - dp(2))
            self._drop_shadow.size = instance.size
            self._drop_bg.pos = instance.pos
            self._drop_bg.size = instance.size
            self._drop_border.pos = instance.pos
            self._drop_border.size = instance.size
            self._drop_inner.pos = (instance.x + dp(1), instance.y + dp(1))
            self._drop_inner.size = (instance.width - dp(2), instance.height - dp(2))

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
