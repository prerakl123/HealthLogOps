"""
Activity suggestion field components for HealthLogOps.

This module provides text input fields with autocomplete functionality
that suggests activities based on the selected category.

Classes:
    SuggestionItem: Individual suggestion item in the dropdown.
    ActivitySuggestionField: Text field with category-aware suggestions.

Example:
    >>> field = ActivitySuggestionField()
    >>> field.set_category("Cardio")
    >>> # Now typing will show relevant cardio suggestions
"""

from typing import Callable, Optional

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.textfield import MDTextField

from ui.constants import (
    ACTIVITY_SUGGESTIONS,
    DEFAULT_ANIMATION_DURATION,
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
            Color(0, 0, 0, 0)
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
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0.59, 0.53, 0.08)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(6)]
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
                radius=[dp(6)]
            )
        if self.on_select_callback:
            self.on_select_callback(self.text)


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
        self.dropdown_container: Optional[MDBoxLayout] = None

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
        if self.is_dropdown_open and self.dropdown_container:
            self._update_filtered_suggestions(value)

    def _on_focus_change(self, instance, focused: bool) -> None:
        """
        Handle focus changes to show/hide suggestions.

        Shows the suggestions dropdown when the field gains focus
        and hides it when focus is lost.

        :param instance: The text field instance.
        :param focused: Whether the field is now focused.
        """
        if focused and self.suggestions:
            Clock.schedule_once(lambda dt: self._show_suggestions(), 0.1)
        else:
            Clock.schedule_once(lambda dt: self._hide_suggestions(), 0.2)

    def _show_suggestions(self) -> None:
        """
        Show the suggestions dropdown with animation.

        Creates the dropdown container, populates it with filtered
        suggestions, and animates it into view.
        """
        if self.is_dropdown_open or not self.suggestions:
            return

        self.is_dropdown_open = True

        self.dropdown_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=0,
            padding=[dp(4), dp(4)],
            spacing=dp(2),
            opacity=0
        )

        # Background
        with self.dropdown_container.canvas.before:
            Color(0, 0, 0, 0.03)
            self._sug_shadow = RoundedRectangle(
                pos=self.dropdown_container.pos,
                size=self.dropdown_container.size,
                radius=[dp(10)]
            )
            Color(1, 1, 1, 1)
            self._sug_bg = RoundedRectangle(
                pos=self.dropdown_container.pos,
                size=self.dropdown_container.size,
                radius=[dp(10)]
            )
            Color(0.92, 0.93, 0.94, 1)
            self._sug_border = RoundedRectangle(
                pos=self.dropdown_container.pos,
                size=self.dropdown_container.size,
                radius=[dp(10)]
            )
            Color(1, 1, 1, 1)
            self._sug_inner = RoundedRectangle(
                pos=(self.dropdown_container.x + dp(1), self.dropdown_container.y + dp(1)),
                size=(self.dropdown_container.width - dp(2), self.dropdown_container.height - dp(2)),
                radius=[dp(9)]
            )

        self.dropdown_container.bind(
            pos=self._update_suggestion_graphics,
            size=self._update_suggestion_graphics
        )

        self._populate_suggestions(self.text_field.text)
        self.add_widget(self.dropdown_container)

        # Animate
        filtered_count = len(self._get_filtered_suggestions(self.text_field.text))
        target_height = min(filtered_count * dp(44) + dp(8), dp(SUGGESTION_MAX_HEIGHT))
        if target_height > dp(8):
            anim = Animation(
                height=target_height,
                opacity=1,
                duration=DEFAULT_ANIMATION_DURATION,
                t='out_cubic'
            )
            anim.start(self.dropdown_container)
            self.height = dp(52) + target_height + dp(8)

    def _hide_suggestions(self) -> None:
        """
        Hide the suggestions dropdown with animation.

        Animates the dropdown out of view and removes it from
        the widget tree.
        """
        if not self.is_dropdown_open or not self.dropdown_container:
            return

        self.is_dropdown_open = False

        anim = Animation(height=0, opacity=0, duration=0.15, t='out_cubic')
        anim.bind(on_complete=self._remove_suggestions)
        anim.start(self.dropdown_container)
        self.height = dp(52)

    def _remove_suggestions(self, *args) -> None:
        """
        Remove the suggestions container from the widget tree.

        Called as a callback after the hide animation completes.
        """
        if self.dropdown_container and self.dropdown_container.parent:
            self.remove_widget(self.dropdown_container)
            self.dropdown_container = None

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
        if not self.dropdown_container:
            return

        self.dropdown_container.clear_widgets()
        filtered = self._get_filtered_suggestions(filter_text)

        for suggestion in filtered:
            item = SuggestionItem(
                text=suggestion,
                on_select=self._on_suggestion_selected
            )
            self.dropdown_container.add_widget(item)

    def _update_filtered_suggestions(self, filter_text: str) -> None:
        """
        Update the displayed suggestions when input text changes.

        Re-populates the dropdown and adjusts its height based on
        the number of matching suggestions.

        :param filter_text: The new filter text.
        """
        if not self.dropdown_container:
            return

        self._populate_suggestions(filter_text)
        filtered = self._get_filtered_suggestions(filter_text)
        target_height = min(len(filtered) * dp(44) + dp(8), dp(SUGGESTION_MAX_HEIGHT))

        if target_height > dp(8):
            self.dropdown_container.height = target_height
            self.height = dp(52) + target_height + dp(8)
        else:
            self._hide_suggestions()

    def _update_suggestion_graphics(self, instance, value) -> None:
        """
        Update suggestion container graphics when position/size changes.

        :param instance: The widget instance that triggered the update.
        :param value: The new position or size value.
        """
        if hasattr(self, '_sug_shadow'):
            self._sug_shadow.pos = (instance.x + dp(1), instance.y - dp(1))
            self._sug_shadow.size = instance.size
            self._sug_bg.pos = instance.pos
            self._sug_bg.size = instance.size
            self._sug_border.pos = instance.pos
            self._sug_border.size = instance.size
            self._sug_inner.pos = (instance.x + dp(1), instance.y + dp(1))
            self._sug_inner.size = (instance.width - dp(2), instance.height - dp(2))

    def _on_suggestion_selected(self, value: str) -> None:
        """
        Handle suggestion selection from the dropdown.

        Sets the text field value to the selected suggestion,
        hides the dropdown, and removes focus from the field.

        :param value: The selected suggestion text.
        """
        self.text_field.text = value
        self._hide_suggestions()
        self.text_field.focus = False
