"""
Activity suggestion field components for HealthLogOps.

This module provides text input fields with autocomplete functionality
that suggests activities based on the selected category.

Classes:
    SuggestionItem: Individual suggestion item in the dropdown.
    SuggestionPopup: Popup container for suggestion items.
    ActivitySuggestionField: Text field with category-aware suggestions.

Example:
    >>> field = ActivitySuggestionField()
    >>> field.set_category("Cardio")
    >>> # Now typing will show relevant cardio suggestions
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
from kivymd.uix.textfield import MDTextField

from ui.constants import (
    ACTIVITY_SUGGESTIONS,
    MAX_VISIBLE_SUGGESTIONS,
    SUGGESTION_MAX_HEIGHT,
)


class SuggestionItem(ButtonBehavior, MDBoxLayout):
    """
    A single suggestion item with subtle hover effect.

    Displays a suggestion text with an icon and provides visual
    feedback when pressed.

    Attributes:
        text: The suggestion text to display.

    Args:
        text: The text to display for this suggestion.
        on_select: Callback function invoked when the suggestion is selected.
            The callback receives the suggestion text as its argument.
        **kwargs: Additional keyword arguments passed to MDBoxLayout.

    Example:
        >>> item = SuggestionItem(
        ...     text="Morning Run",
        ...     on_select=lambda val: print(f"Selected: {val}")
        ... )
    """

    text = StringProperty("")
    """The suggestion text displayed in this item."""

    def __init__(
        self,
        text: str = "",
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> None:
        """
        Initialize a SuggestionItem.

        :param text: The text to display for this suggestion.
        :param on_select: Callback function invoked when selected.
        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)
        self.text = text
        self.on_select_callback = on_select

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(44)
        self.padding = [dp(12), dp(8), dp(12), dp(8)]

        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(6)]
            )

        self.bind(pos=self._update_bg, size=self._update_bg)

        # Suggestion icon
        icon = MDIcon(
            icon="arrow-top-left",
            theme_icon_color="Custom",
            icon_color=(0.6, 0.6, 0.65, 1),
            pos_hint={"center_y": 0.5},
            size_hint_x=None,
            width=dp(20),
            font_size=dp(18)
        )
        self.add_widget(icon)

        # Text
        label = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.35, 1),
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
        self._bg_color.rgba = (0, 0.59, 0.53, 0.08)

    def on_release(self) -> None:
        """
        Handle release event and trigger selection callback.

        Resets the visual state and invokes the on_select callback
        if one was provided during initialization.
        """
        self._bg_color.rgba = (0, 0, 0, 0)
        if self.on_select_callback:
            self.on_select_callback(self.text)


class SuggestionPopup(ModalView):
    """
    A styled suggestion popup that appears below the text field.

    Uses ModalView for proper overlay handling with transparent background.
    """

    max_height = NumericProperty(dp(SUGGESTION_MAX_HEIGHT))
    """Maximum height of the suggestion popup."""

    def __init__(self, attached_widget=None, **kwargs):
        # Set ModalView properties before super().__init__
        kwargs.setdefault('background', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('overlay_color', (0, 0, 0, 0))
        kwargs.setdefault('auto_dismiss', False)  # We handle dismiss manually for text fields
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
            Color(0, 0, 0, 0.06)
            self._shadow = RoundedRectangle(radius=[dp(0), dp(0), dp(10), dp(10)])
            Color(1, 1, 1, 1)
            self._bg = RoundedRectangle(radius=[dp(0), dp(0), dp(10), dp(10)])
            Color(0.90, 0.91, 0.92, 1)
            self._border = RoundedRectangle(radius=[dp(0), dp(0), dp(10), dp(10)])
            Color(1, 1, 1, 1)
            self._inner = RoundedRectangle(radius=[dp(0), dp(0), dp(10), dp(10)])

        self.wrapper.bind(pos=self._update_wrapper_graphics, size=self._update_wrapper_graphics)
        self.wrapper.add_widget(self.scroll_view)
        super().add_widget(self.wrapper)

    def _update_wrapper_graphics(self, instance, value):
        """Update background graphics when position/size changes."""
        self._shadow.pos = (instance.x + dp(1), instance.y - dp(1))
        self._shadow.size = instance.size
        self._bg.pos = instance.pos
        self._bg.size = instance.size
        self._border.pos = instance.pos
        self._border.size = instance.size
        self._inner.pos = (instance.x + dp(1), instance.y + dp(1))
        self._inner.size = (instance.width - dp(2), instance.height - dp(2))

    def _align_center(self, *args):
        """Override ModalView's centering behavior to use custom positioning."""
        # Do nothing - we handle positioning ourselves in update_position_and_size
        pass

    def update_position_and_size(self):
        """Update position and size based on content and attached widget."""
        if self._attached_widget:
            # Get position in window coordinates
            pos = self._attached_widget.to_window(0, 0)

            # Calculate content height
            content_height = self.container.height + dp(8)
            target_height = min(content_height, self.max_height)

            # Set size
            self.width = self._attached_widget.width
            self.height = target_height

            # Position below the widget
            self.x = dp(32)
            self.y = pos[1] + target_height + (self._attached_widget.height / 2) - dp(4)

    def open(self, *args, **kwargs):
        """Open the popup and position it below the attached widget."""
        # Position before opening
        self.update_position_and_size()
        super().open(*args, **kwargs)
        # Re-position after open to ensure layout is correct
        Clock.schedule_once(lambda dt: self.update_position_and_size(), 0)

    def on_open(self):
        """Ensure positioning after ModalView opens."""
        self.update_position_and_size()

    def add_item(self, item):
        """Add a suggestion item to the container."""
        self.container.add_widget(item)

    def clear_items(self):
        """Clear all items from the popup."""
        self.container.clear_widgets()


class ActivitySuggestionField(MDBoxLayout):
    """
    A text field with dropdown suggestions based on selected category.

    Shows relevant activity suggestions when focused, filtered by
    the current input text. Suggestions are category-specific and
    help users quickly select common activities.

    Attributes:
        text: The current text value of the input field.
        category: The currently selected activity category.
        suggestions: List of available suggestions for the current category.
        is_dropdown_open: Whether the suggestions dropdown is visible.

    Args:
        **kwargs: Additional keyword arguments passed to MDBoxLayout.

    Example:
        >>> field = ActivitySuggestionField()
        >>> field.set_category("Strength Training")
        >>> # Suggestions like "Bench Press", "Squats" will appear
    """

    text = StringProperty("")
    """The current text value of the input field."""

    category = StringProperty("")
    """The currently selected activity category for filtering suggestions."""

    suggestions = ListProperty([])
    """List of available suggestions for the current category."""

    is_dropdown_open = BooleanProperty(False)
    """Whether the suggestions dropdown is currently visible."""

    def __init__(self, **kwargs) -> None:
        """
        Initialize an ActivitySuggestionField.

        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)
        self._dropdown: Optional[SuggestionPopup] = None
        self._show_scheduled = None
        self._hide_scheduled = None

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(52)
        self.spacing = dp(4)

        # Text field
        self.text_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(52)
        )
        self.text_field.hint_text = "e.g., Morning Run, Bench Press"
        self.text_field.bind(text=self._on_text_change)
        self.text_field.bind(focus=self._on_focus_change)
        self.add_widget(self.text_field)

        # Bind text property
        self.bind(text=lambda inst, val: setattr(self.text_field, 'text', val))
        self.text_field.bind(text=lambda inst, val: setattr(self, 'text', val))

    def set_category(self, category: str) -> None:
        """
        Update suggestions based on the selected category.

        Retrieves the predefined suggestions for the given category
        and updates the internal suggestions list.

        :param category: The category name to load suggestions for.
        """
        self.category = category
        self.suggestions = ACTIVITY_SUGGESTIONS.get(category, [])

    def _on_text_change(self, instance, value: str) -> None:
        """
        Handle text changes and filter suggestions accordingly.

        Called when the user types in the text field. Updates the
        displayed suggestions to match the current input.

        :param instance: The text field instance.
        :param value: The new text value.
        """
        if self.is_dropdown_open and self._dropdown:
            self._update_filtered_suggestions(value)

    def _on_focus_change(self, instance, focused: bool) -> None:
        """
        Handle focus changes to show/hide suggestions.

        Shows the suggestions dropdown when the field gains focus
        and hides it when focus is lost.

        :param instance: The text field instance.
        :param focused: Whether the field is now focused.
        """
        # Cancel any pending schedules
        if self._show_scheduled:
            Clock.unschedule(self._show_scheduled)
            self._show_scheduled = None
        if self._hide_scheduled:
            Clock.unschedule(self._hide_scheduled)
            self._hide_scheduled = None

        if focused and self.suggestions:
            self._show_scheduled = Clock.schedule_once(lambda dt: self._show_suggestions(), 0.1)
        else:
            self._hide_scheduled = Clock.schedule_once(lambda dt: self._hide_suggestions(), 0.15)

    def _show_suggestions(self) -> None:
        """
        Show the suggestions dropdown.
        """
        if self.is_dropdown_open or not self.suggestions:
            return

        # Get filtered suggestions
        filtered = self._get_filtered_suggestions(self.text_field.text)
        if not filtered:
            return

        self.is_dropdown_open = True

        # Create popup
        self._dropdown = SuggestionPopup(attached_widget=self.text_field)
        self._dropdown.bind(on_dismiss=self._on_dropdown_dismiss)

        # Populate with suggestions
        self._populate_suggestions(self.text_field.text)

        # Open dropdown
        self._dropdown.open()

    def _hide_suggestions(self) -> None:
        """
        Hide the suggestions dropdown.
        """
        if not self.is_dropdown_open or not self._dropdown:
            return

        self._dropdown.dismiss()

    def _on_dropdown_dismiss(self, *args) -> None:
        """
        Handle dropdown dismissal.
        """
        self.is_dropdown_open = False
        self._dropdown = None

    def _get_filtered_suggestions(self, filter_text: str) -> list[str]:
        """
        Get suggestions filtered by the current input text.

        :param filter_text: The text to filter suggestions by.
        :returns: List of matching suggestions, limited to MAX_VISIBLE_SUGGESTIONS.
        """
        if not filter_text:
            return self.suggestions[:MAX_VISIBLE_SUGGESTIONS]
        filter_lower = filter_text.lower()
        return [
            s for s in self.suggestions
            if filter_lower in s.lower()
        ][:MAX_VISIBLE_SUGGESTIONS]

    def _populate_suggestions(self, filter_text: str) -> None:
        """
        Populate the dropdown with filtered suggestion items.

        Clears any existing items and creates new SuggestionItem
        widgets for each matching suggestion.

        :param filter_text: The text to filter suggestions by.
        """
        if not self._dropdown:
            return

        self._dropdown.clear_items()
        filtered = self._get_filtered_suggestions(filter_text)

        for suggestion in filtered:
            item = SuggestionItem(
                text=suggestion,
                on_select=self._on_suggestion_selected
            )
            self._dropdown.add_item(item)

        # Update dropdown position and size
        self._dropdown.update_position_and_size()

    def _update_filtered_suggestions(self, filter_text: str) -> None:
        """
        Update the displayed suggestions when input text changes.

        Re-populates the dropdown and adjusts its height based on
        the number of matching suggestions.

        :param filter_text: The new filter text.
        """
        if not self._dropdown:
            return

        filtered = self._get_filtered_suggestions(filter_text)

        if not filtered:
            self._hide_suggestions()
            return

        self._populate_suggestions(filter_text)

    def _on_suggestion_selected(self, value: str) -> None:
        """
        Handle suggestion selection from the dropdown.

        Sets the text field value to the selected suggestion,
        hides the dropdown, and removes focus from the field.

        :param value: The selected suggestion text.
        """
        self.text_field.text = value
        self._hide_suggestions()
        # Delay unfocus to allow the selection to complete
        Clock.schedule_once(lambda dt: setattr(self.text_field, 'focus', False), 0.1)

    def on_parent(self, instance, parent) -> None:
        """Clean up dropdown when widget is removed from parent."""
        if parent is None and self._dropdown:
            self._dropdown.dismiss()
            self._dropdown = None
