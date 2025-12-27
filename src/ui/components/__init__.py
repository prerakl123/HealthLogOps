"""
UI Components package for HealthLogOps.

This package contains reusable UI components organized into logical modules:

Modules:
    - dropdown: Styled dropdown menu components
    - suggestion_field: Text field with autocomplete suggestions
    - form_builder: Dynamic form generation from templates
    - log_card: Log entry card display components
    - empty_state: Empty state placeholder widgets

All components follow Material Design 3 guidelines and use the
KivyMD framework for consistent styling across the application.
"""

from ui.components.dropdown import StyledDropdown, DropdownItem
from ui.components.suggestion_field import ActivitySuggestionField, SuggestionItem
from ui.components.form_builder import DynamicFormBuilder, KeyValueField
from ui.components.log_card import LogCard, MetricPill, OverflowPill, SwipeableLogCard
from ui.components.empty_state import EmptyStateWidget
from ui.components.date_group import DateGroup, DateGroupHeader, NoActivityLabel

__all__ = [
    # Dropdown components
    "StyledDropdown",
    "DropdownItem",

    # Suggestion field components
    "ActivitySuggestionField",
    "SuggestionItem",

    # Form builder components
    "DynamicFormBuilder",
    "KeyValueField",

    # Log card components
    "LogCard",
    "MetricPill",
    "OverflowPill",
    "SwipeableLogCard",

    # Empty state components
    "EmptyStateWidget",

    # Date group components
    "DateGroup",
    "DateGroupHeader",
    "NoActivityLabel",
]
