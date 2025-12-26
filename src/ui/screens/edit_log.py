"""
Edit Log screen for HealthLogOps.

This module contains the EditLogScreen class, which provides a form
interface for users to edit or delete existing health log entries.

Classes:
    EditLogScreen: Form screen for editing/deleting log entries.
"""

from typing import Any, Optional

from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText

from ui.components import DynamicFormBuilder, KeyValueField
from database import DatabaseManager


class EditLogScreen(MDScreen):
    """
    Screen for editing existing health log entries.

    Provides a form interface pre-populated with the log's existing data,
    allowing users to modify or delete the entry.

    Features:
        - Pre-populated form with existing log data
        - Category display (read-only)
        - Activity name editing
        - Dynamic metric fields editing
        - Notes section editing
        - Delete functionality with confirmation

    Attributes:
        log_id: The ID of the log being edited.
        category_label: Label showing the category name.
        activity_field: The activity name input field.
        notes_field: The optional notes text field.
        form_container: Container for dynamic form fields.
        db_manager: Reference to the database manager instance.
    """

    log_id = NumericProperty(0)
    """The ID of the log being edited."""

    category_label = ObjectProperty(None)
    """Label showing the category name (read-only)."""

    activity_field = ObjectProperty(None)
    """The activity name input field."""

    notes_field = ObjectProperty(None)
    """The optional notes text field."""

    form_container = ObjectProperty(None)
    """Container widget for dynamic form fields."""

    def __init__(self, **kwargs) -> None:
        """
        Initialize the EditLogScreen.

        :param kwargs: Additional keyword arguments passed to MDScreen.
        """
        super().__init__(**kwargs)
        self.db_manager: Optional[DatabaseManager] = None
        self.current_fields: dict[str, KeyValueField] = {}
        self.custom_fields: list[KeyValueField] = []
        self.current_template: dict[str, str] = {}
        self.log_data: Optional[dict[str, Any]] = None
        self._delete_dialog: Optional[MDDialog] = None
        self._custom_field_counter: int = 0

    def load_log(self, log_id: int) -> None:
        """
        Load a log entry for editing.

        :param log_id: The ID of the log to edit.
        """
        if not self.db_manager:
            return

        self.log_id = log_id
        self.log_data = self.db_manager.get_log(log_id)
        self.custom_fields.clear()
        self._custom_field_counter = 0

        if not self.log_data:
            return

        # Get category info
        category = self.db_manager.get_category(self.log_data["category_id"])
        if not category:
            return

        # Set category label
        if self.category_label:
            self.category_label.text = category["name"]

        # Set activity name
        if self.activity_field:
            self.activity_field.text = self.log_data.get("activity_name", "")

        # Set notes
        if self.notes_field:
            self.notes_field.text = self.log_data.get("notes", "") or ""

        # Build form with existing values
        self.current_template = category.get("template", {})
        existing_metrics = self.log_data.get("metrics", {})

        if self.form_container:
            self.form_container.clear_widgets()
            self.current_fields = DynamicFormBuilder.build_form(
                template=self.current_template,
                container=self.form_container,
                initial_values=existing_metrics
            )

            # Load custom fields (metrics not in template)
            for key, value in existing_metrics.items():
                if key not in self.current_template:
                    self._custom_field_counter += 1
                    custom_field = DynamicFormBuilder.create_custom_field(
                        container=self.form_container,
                        field_name=key.replace("_", " ").title(),
                        field_type="str"
                    )
                    custom_field.value_field.text = str(value)
                    # Store the original key for later extraction
                    custom_field._original_key = key
                    self.custom_fields.append(custom_field)

    def add_custom_field(self) -> None:
        """
        Add a custom field to the form.

        Creates a new removable field with a default name and
        string type. Shows a snackbar confirmation to the user.
        """
        if not self.form_container:
            return

        self._custom_field_counter += 1
        field_name = f"Custom {self._custom_field_counter}"

        custom_field = DynamicFormBuilder.create_custom_field(
            container=self.form_container,
            field_name=field_name,
            field_type="str"
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
        Save the edited log entry.

        :returns: True if save was successful, False otherwise.
        """
        if not self.db_manager or not self.log_data:
            return False

        # Get activity name
        activity_name = ""
        if self.activity_field:
            activity_name = self.activity_field.text.strip()
        if not activity_name:
            activity_name = self.log_data.get("activity_name", "Activity")

        # Extract metrics
        metrics = DynamicFormBuilder.extract_values(
            fields=self.current_fields,
            template=self.current_template
        )

        # Add custom field values
        for custom_field in self.custom_fields:
            if custom_field.parent:  # Only if not removed
                # Get the field name from the editable key field or fall back to field_name
                if hasattr(custom_field, 'key_field') and custom_field.key_field:
                    field_name = custom_field.key_field.text.strip().lower().replace(" ", "_")
                else:
                    field_name = custom_field.field_name.lower().replace(" ", "_")
                if not field_name:
                    field_name = "custom"
                raw_value = custom_field.get_value()
                # Try to convert to number if possible
                try:
                    if '.' in raw_value:
                        metrics[field_name] = float(raw_value)
                    else:
                        metrics[field_name] = int(raw_value)
                except (ValueError, TypeError):
                    metrics[field_name] = raw_value

        # Get notes
        notes = self.notes_field.text.strip() if self.notes_field else None

        # Update in database
        try:
            self.db_manager.update_log(
                log_id=self.log_id,
                activity_name=activity_name,
                metrics=metrics,
                notes=notes if notes else None
            )
            MDSnackbar(
                MDSnackbarText(text="Log updated successfully"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()
            return True
        except Exception as e:
            print(f"Error updating log: {e}")
            MDSnackbar(
                MDSnackbarText(text="Failed to update log"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()
            return False

    def confirm_delete(self) -> None:
        """Show confirmation dialog before deleting the log."""
        self._delete_dialog = MDDialog(
            MDDialogHeadlineText(text="Delete Log?"),
            MDDialogSupportingText(
                text="This action cannot be undone. Are you sure you want to delete this log entry?"
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self._delete_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Delete"),
                    style="text",
                    theme_text_color="Custom",
                    text_color=(0.91, 0.30, 0.24, 1),
                    on_release=lambda x: self._do_delete()
                ),
                spacing="8dp",
            ),
        )
        self._delete_dialog.open()

    def _do_delete(self) -> None:
        """Actually delete the log after confirmation."""
        if self._delete_dialog:
            self._delete_dialog.dismiss()

        if not self.db_manager:
            return

        try:
            if self.db_manager.delete_log(self.log_id):
                MDSnackbar(
                    MDSnackbarText(text="Log deleted"),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.9,
                ).open()
                # Go back to home
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                if app:
                    app.go_back()
        except Exception as e:
            print(f"Error deleting log: {e}")
            MDSnackbar(
                MDSnackbarText(text="Failed to delete log"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()
