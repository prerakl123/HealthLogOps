"""
Dynamic form builder components for HealthLogOps.

This module provides utilities for generating form fields dynamically
based on JSON templates, enabling flexible data entry for different
activity categories.

Classes:
    KeyValueField: A styled key-value input field.
    DynamicFormBuilder: Factory class for building forms from templates.

Example:
    >>> template = {"sets": "int", "reps": "int", "weight_kg": "float"}
    >>> fields = DynamicFormBuilder.build_form(template, container)
    >>> values = DynamicFormBuilder.extract_values(fields, template)
"""

from typing import Any, Callable, Optional

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField


class KeyValueField(MDBoxLayout):
    """
    A styled key-value input field with label and text input side by side.

    Displays a field name in a colored label container on the left
    and a text input on the right. Optionally includes a remove button
    for custom fields. Custom fields also have an editable key name.

    Attributes:
        field_name: The display name for this field.
        field_type: The data type of this field (int, float, str, text).
        key_field: The editable key name text field (only for custom fields).

    Args:
        field_name: The name to display for this field.
        field_type: The data type hint (int, float, str, text).
        hint_text: Placeholder text for the input field.
        input_filter: Kivy input filter ('int', 'float', or None).
        removable: Whether to show a remove button (also enables editable key).
        **kwargs: Additional keyword arguments passed to MDBoxLayout.

    Example:
        >>> field = KeyValueField(
        ...     field_name="Weight",
        ...     field_type="float",
        ...     hint_text="Enter weight in kg",
        ...     removable=False
        ... )
    """

    field_name = StringProperty("")
    """The display name shown in the key label."""

    field_type = StringProperty("str")
    """The data type of this field (int, float, str, text)."""

    def __init__(
        self,
        field_name: str,
        field_type: str = "str",
        hint_text: str = "Enter value",
        input_filter: Optional[str] = None,
        removable: bool = True,
        **kwargs
    ) -> None:
        """
        Initialize a KeyValueField.

        :param field_name: The name to display for this field.
        :param field_type: The data type hint (int, float, str, text).
        :param hint_text: Placeholder text for the input field.
        :param input_filter: Kivy input filter ('int', 'float', or None).
        :param removable: Whether to show a remove button (also enables editable key).
        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)

        self.field_name = field_name
        self.field_type = field_type
        self.orientation = "horizontal"
        self.spacing = dp(12)
        self.size_hint_y = None
        self.height = dp(56)
        self.key_field = None  # Will be set for custom fields

        if removable:
            # Custom field with editable key name
            self._build_editable_key_field(field_name, hint_text)
        else:
            # Standard field with fixed key label
            self._build_fixed_key_field(field_name, hint_text, input_filter)

    def _build_fixed_key_field(
        self,
        field_name: str,
        hint_text: str,
        input_filter: Optional[str]
    ) -> None:
        """Build a field with a fixed (non-editable) key label."""
        # Key label container
        key_container = MDBoxLayout(
            size_hint_x=0.4,
            padding=[dp(12), dp(8)],
        )
        with key_container.canvas.before:
            Color(0.0, 0.59, 0.53, 0.12)
            self._key_rect = RoundedRectangle(
                pos=key_container.pos,
                size=key_container.size,
                radius=[dp(10)]
            )
        key_container.bind(pos=self._update_key_rect, size=self._update_key_rect)

        key_label = MDLabel(
            text=field_name,
            theme_text_color="Custom",
            text_color=(0.0, 0.49, 0.45, 1),
            bold=True,
            halign="center",
            valign="center",
            shorten=True,
            shorten_from="right",
            text_size=(None, None)
        )
        key_label.bind(
            size=lambda inst, val: setattr(inst, 'text_size', (val[0], None))
        )
        key_container.add_widget(key_label)
        self.add_widget(key_container)

        # Value input field
        self.value_field = MDTextField(
            mode="outlined",
            size_hint_x=0.6,
        )
        self.value_field.hint_text = hint_text
        if input_filter:
            self.value_field.input_filter = input_filter
        self.add_widget(self.value_field)

    def _build_editable_key_field(
        self,
        field_name: str,
        hint_text: str
    ) -> None:
        """Build a custom field with editable key name and no input filter restriction."""
        # Editable key name text field
        self.key_field = MDTextField(
            mode="outlined",
            size_hint_x=0.35,
        )
        self.key_field.hint_text = "Field name"
        self.key_field.text = field_name
        self.add_widget(self.key_field)

        # Value input field (no input filter for custom fields - allow any value)
        self.value_field = MDTextField(
            mode="outlined",
            size_hint_x=0.45,
        )
        self.value_field.hint_text = hint_text
        self.add_widget(self.value_field)

        # Remove button
        remove_btn = MDIconButton(
            icon="close-circle",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.3, 0.3, 0.8),
            pos_hint={"center_y": 0.5},
            on_release=lambda x: self._remove_self()
        )
        self.add_widget(remove_btn)

    def _update_key_rect(self, instance, value) -> None:
        """
        Update the key label background when position/size changes.

        :param instance: The widget instance that triggered the update.
        :param value: The new position or size value.
        """
        self._key_rect.pos = instance.pos
        self._key_rect.size = instance.size

    def _remove_self(self) -> None:
        """
        Remove this field from its parent container.

        Called when the remove button is pressed on removable fields.
        """
        if self.parent:
            self.parent.remove_widget(self)

    def get_value(self) -> str:
        """
        Get the current value from the input field.

        :returns: The text value entered in the field.
        """
        return self.value_field.text

    def clear(self) -> None:
        """
        Clear the input field value.

        Resets the text field to an empty string.
        """
        self.value_field.text = ""

    def bind_change(self, callback: Callable[[str, str], None]) -> None:
        """
        Bind a callback to text changes in this field.

        :param callback: Function called when text changes.
            Receives field_name and new_value as arguments.
        """
        self.value_field.bind(
            text=lambda inst, val: callback(self.field_name, val)
        )


class DynamicFormBuilder:
    """
    Factory class for dynamically generating form fields from templates.

    Provides static methods for creating, populating, and extracting
    values from dynamic forms based on JSON template definitions.

    The template format uses field names as keys and type strings as values:
        - "int": Integer input with numeric filter
        - "float": Decimal input with numeric filter
        - "str" or "text": Free-text input

    Example:
        >>> template = {"sets": "int", "reps": "int", "weight_kg": "float"}
        >>> container = MDBoxLayout(orientation="vertical")
        >>> fields = DynamicFormBuilder.build_form(template, container)
        >>>
        >>> # Later, extract values:
        >>> values = DynamicFormBuilder.extract_values(fields, template)
        >>> # {'sets': 3, 'reps': 10, 'weight_kg': 50.0}
    """

    TYPE_CONFIG: dict[str, dict[str, Any]] = {
        "int": {"input_filter": "int", "hint_text": "Number", "default": "0"},
        "float": {"input_filter": "float", "hint_text": "Decimal", "default": "0.0"},
        "str": {"input_filter": None, "hint_text": "Text", "default": ""},
        "text": {"input_filter": None, "hint_text": "Text", "default": ""}
    }
    """
    Configuration for different field types.
    
    Maps type names to their input filter, hint text, and default value.
    """

    @classmethod
    def build_form(
        cls,
        template: dict[str, str],
        container: BoxLayout | MDBoxLayout,
        on_change_callback: Optional[Callable[[str, str], None]] = None,
        initial_values: Optional[dict[str, Any]] = None
    ) -> dict[str, KeyValueField]:
        """
        Build form fields from a template and add them to a container.

        Creates KeyValueField widgets for each field defined in the template
        and adds them to the specified container widget.

        :param template: Dictionary mapping field names to type strings.
        :param container: The BoxLayout to add fields to.
        :param on_change_callback: Optional callback for value changes.
            Called with (field_name, new_value) when any field changes.
        :param initial_values: Optional dictionary of initial field values.
        :returns: Dictionary mapping field names to their KeyValueField widgets.

        :raises TypeError: If template is not a dictionary.

        Example:
            >>> template = {"calories": "int", "protein_g": "float"}
            >>> fields = DynamicFormBuilder.build_form(template, container)
        """
        fields: dict[str, KeyValueField] = {}
        for field_name, field_type in template.items():
            field_widget = cls._create_field(
                field_name=field_name,
                field_type=field_type,
                on_change_callback=on_change_callback,
                removable=False
            )
            # Set initial value if provided
            if initial_values and field_name in initial_values:
                field_widget.value_field.text = str(initial_values[field_name])
            container.add_widget(field_widget)
            fields[field_name] = field_widget
        return fields

    @classmethod
    def _create_field(
        cls,
        field_name: str,
        field_type: str,
        on_change_callback: Optional[Callable[[str, str], None]] = None,
        removable: bool = True
    ) -> KeyValueField:
        """
        Create a single KeyValueField based on field configuration.

        :param field_name: The name to display for this field.
        :param field_type: The data type (int, float, str, text).
        :param on_change_callback: Optional callback for value changes.
        :param removable: Whether to include a remove button (custom field).
        :returns: A configured KeyValueField widget.
        """
        config = cls.TYPE_CONFIG.get(field_type.lower(), cls.TYPE_CONFIG["str"])
        display_name = field_name.replace("_", " ").title()

        # Custom fields (removable=True) don't use input_filter to allow any value type
        field_widget = KeyValueField(
            field_name=display_name,
            field_type=field_type,
            hint_text="Enter value" if removable else config["hint_text"],
            input_filter=None if removable else config["input_filter"],
            removable=removable
        )
        if on_change_callback:
            field_widget.bind_change(on_change_callback)
        return field_widget

    @classmethod
    def create_custom_field(
        cls,
        container: BoxLayout | MDBoxLayout,
        field_name: str = "Custom Field",
        field_type: str = "str"
    ) -> KeyValueField:
        """
        Create and add a removable custom field to a container.

        Useful for allowing users to add their own fields beyond
        the template definition.

        :param container: The BoxLayout to add the field to.
        :param field_name: The name for the custom field.
        :param field_type: The data type (int, float, str, text).
        :returns: The created KeyValueField widget.

        Example:
            >>> custom = DynamicFormBuilder.create_custom_field(
            ...     container,
            ...     field_name="Notes",
            ...     field_type="text"
            ... )
        """
        field_widget = cls._create_field(
            field_name=field_name,
            field_type=field_type,
            removable=True
        )
        container.add_widget(field_widget)
        return field_widget

    @classmethod
    def extract_values(
        cls,
        fields: dict[str, KeyValueField],
        template: dict[str, str]
    ) -> dict[str, Any]:
        """
        Extract and convert values from form fields.

        Reads the text values from each field and converts them
        to the appropriate Python type based on the template.

        :param fields: Dictionary of field_name to KeyValueField mappings.
        :param template: The original template with type definitions.
        :returns: Dictionary of field names to converted values.

        Example:
            >>> values = DynamicFormBuilder.extract_values(fields, template)
            >>> # {'sets': 3, 'reps': 10, 'weight_kg': 50.0}
        """
        values: dict[str, Any] = {}
        for field_name, field_widget in fields.items():
            raw_value = field_widget.get_value().strip()
            field_type = template.get(field_name, "str").lower()
            try:
                if field_type == "int":
                    values[field_name] = int(raw_value) if raw_value else 0
                elif field_type == "float":
                    values[field_name] = float(raw_value) if raw_value else 0.0
                else:
                    values[field_name] = raw_value
            except ValueError:
                values[field_name] = 0 if field_type in ("int", "float") else raw_value
        return values

    @classmethod
    def clear_form(cls, fields: dict[str, KeyValueField]) -> None:
        """
        Clear all values in a set of form fields.

        Resets each field to an empty string.

        :param fields: Dictionary of field_name to KeyValueField mappings.
        """
        for field_widget in fields.values():
            field_widget.clear()
