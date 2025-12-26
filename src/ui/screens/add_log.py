"""
Add Log screen for HealthLogOps.

This module contains the AddLogScreen class, which provides a form
interface for users to create new health log entries with dynamic
fields based on the selected category.

Classes:
    AddLogScreen: Form screen for creating new log entries.

Example:
    >>> add_screen = AddLogScreen(name="add_log")
    >>> add_screen.db_manager = database_manager
"""

from typing import Any, Optional

from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from ui.components import DynamicFormBuilder, KeyValueField
from database import DatabaseManager


class AddLogScreen(MDScreen):
    """
    Screen for adding new health log entries.

    Provides a form interface with category selection, activity name
    input, dynamic metric fields based on the selected category's
    template, custom field support, and optional notes.

    Features:
        - Category selection with styled dropdown
        - Activity name input with suggestions
        - Dynamic form fields based on category template
        - Add custom fields button
        - Notes section
        - Form validation and submission

    Attributes:
        category_spinner: The category selection dropdown widget.
        activity_field: The activity name input field.
        notes_field: The optional notes text field.
        form_container: Container for dynamic form fields.
        db_manager: Reference to the database manager instance.
        current_fields: Dictionary of current template fields.
        custom_fields: List of user-added custom fields.
        current_template: The current category's field template.
        categories: List of available categories.

    Args:
        **kwargs: Additional keyword arguments passed to MDScreen.

    Example:
        >>> add_log = AddLogScreen(name="add_log")
        >>> add_log.db_manager = DatabaseManager("health.db")
        >>> # User selects category, fills form, and saves
    """

    category_spinner = ObjectProperty(None)
    """The category selection dropdown widget."""

    activity_field = ObjectProperty(None)
    """The activity name input field (supports suggestions)."""

    notes_field = ObjectProperty(None)
    """The optional notes text field."""

    form_container = ObjectProperty(None)
    """Container widget for dynamic form fields."""

    def __init__(self, **kwargs) -> None:
        """
        Initialize the AddLogScreen.

        :param kwargs: Additional keyword arguments passed to MDScreen.
        """
        super().__init__(**kwargs)
        self.db_manager: Optional[DatabaseManager] = None
        self.current_fields: dict[str, KeyValueField] = {}
        self.custom_fields: list[KeyValueField] = []
        self.current_template: dict[str, str] = {}
        self.categories: list[dict[str, Any]] = []
        self._category_map: dict[str, int] = {}
        self._custom_field_counter: int = 0

    def on_enter(self) -> None:
        """
        Called when the screen is displayed.

        Triggers loading of categories into the dropdown.
        """
        self.load_categories()

    def load_categories(self) -> None:
        """
        Load categories into the styled dropdown.

        Fetches all categories from the database and populates
        the category dropdown. Sets up the selection callback
        and selects the first category by default.
        """
        if not self.db_manager or not self.category_spinner:
            return

        self.categories = self.db_manager.get_all_categories()
        self._category_map = {cat["name"]: cat["id"] for cat in self.categories}

        category_names = [cat["name"] for cat in self.categories]
        self.category_spinner.values = category_names

        # Set up the callback for category selection
        self.category_spinner.on_select_callback = self.on_category_selected

        if category_names:
            self.category_spinner.text = category_names[0]
            self.on_category_selected(category_names[0])

    def on_category_selected(self, category_name: str) -> None:
        """
        Handle category selection change.

        Rebuilds the dynamic form based on the selected category's
        template and updates activity name suggestions.

        :param category_name: The name of the selected category.
        """
        if not self.form_container:
            return

        # Clear existing fields
        self.form_container.clear_widgets()
        self.current_fields.clear()
        self.custom_fields.clear()
        self._custom_field_counter = 0

        # Find selected category
        selected_category = next(
            (cat for cat in self.categories if cat["name"] == category_name),
            None
        )

        if not selected_category:
            return

        self.current_template = selected_category.get("template", {})

        # Build dynamic form fields (key-value style)
        self.current_fields = DynamicFormBuilder.build_form(
            template=self.current_template,
            container=self.form_container
        )

        # Update activity field suggestions based on category
        if self.activity_field and hasattr(self.activity_field, 'set_category'):
            self.activity_field.set_category(category_name)

    def add_custom_field(self) -> None:
        """
        Add a custom field to the form.

        Creates a new removable field with a default name and
        float type. Shows a snackbar confirmation to the user.
        """
        if not self.form_container:
            return

        self._custom_field_counter += 1
        field_name = f"Custom {self._custom_field_counter}"

        custom_field = DynamicFormBuilder.create_custom_field(
            container=self.form_container,
            field_name=field_name,
            field_type="float"
        )
        self.custom_fields.append(custom_field)

        # Show feedback
        MDSnackbar(
            MDSnackbarText(text=f"Added custom field: {field_name}"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def save_log(self) -> bool:
        """
        Save the current form as a new log entry.

        Collects all form data including template fields, custom
        fields, and notes, then saves to the database.

        :returns: True if save was successful, False otherwise.

        :raises: None (errors are handled gracefully and logged)
        """
        if not self.db_manager:
            return False

        # Get category ID
        category_name = self.category_spinner.text if self.category_spinner else ""
        category_id = self._category_map.get(category_name)

        if not category_id:
            return False

        # Get activity name (works with both MDTextField and ActivitySuggestionField)
        activity_name = ""
        if self.activity_field:
            if hasattr(self.activity_field, 'text'):
                activity_name = self.activity_field.text.strip()
            elif hasattr(self.activity_field, 'text_field'):
                activity_name = self.activity_field.text_field.text.strip()
        if not activity_name:
            activity_name = category_name

        # Extract metrics from template fields
        metrics = DynamicFormBuilder.extract_values(
            fields=self.current_fields,
            template=self.current_template
        )

        # Add custom field values
        for custom_field in self.custom_fields:
            if custom_field.parent:  # Only if not removed
                field_name = custom_field.field_name.lower().replace(" ", "_")
                try:
                    raw_value = custom_field.get_value()
                    metrics[field_name] = float(raw_value) if raw_value else 0.0
                except ValueError:
                    metrics[field_name] = custom_field.get_value()

        # Get notes
        notes = self.notes_field.text.strip() if self.notes_field else None

        # Save to database
        try:
            self.db_manager.add_log(
                category_id=category_id,
                activity_name=activity_name,
                metrics=metrics,
                notes=notes if notes else None
            )
            self.clear_form()
            return True
        except Exception as e:
            print(f"Error saving log: {e}")
            return False

    def clear_form(self) -> None:
        """
        Clear all form fields.

        Resets the activity name, notes, template fields, and
        removes all custom fields.
        """
        if self.activity_field:
            if hasattr(self.activity_field, 'text'):
                self.activity_field.text = ""
            elif hasattr(self.activity_field, 'text_field'):
                self.activity_field.text_field.text = ""
        if self.notes_field:
            self.notes_field.text = ""

        DynamicFormBuilder.clear_form(self.current_fields)
        self.custom_fields.clear()
