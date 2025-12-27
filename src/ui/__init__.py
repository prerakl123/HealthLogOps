"""
UI Package for HealthLogOps.

This package contains all user interface components organized into
logical subpackages for better maintainability.

Subpackages:
    - components: Reusable UI widgets (dropdown, log cards, forms, etc.)
    - screens: Application screens (home, add_log, settings)
    - constants: Color schemes, icons, and configuration values

The package provides convenient re-exports of commonly used classes
to maintain backward compatibility and simplify imports.

Example:
    >>> from ui import HomeScreen, AddLogScreen, LogCard
    >>> from ui.constants import CATEGORY_COLORS
"""

# Import from screens subpackage
from ui.screens import HomeScreen, AddLogScreen, EditLogScreen, SettingsScreen

# Import from components subpackage
from ui.components import (
    DynamicFormBuilder,
    LogCard,
    KeyValueField,
    EmptyStateWidget,
    MetricPill,
    OverflowPill,
    SwipeableLogCard,
    StyledDropdown,
    DropdownItem,
    ActivitySuggestionField,
    SuggestionItem,
    DateGroup,
    DateGroupHeader,
    NoActivityLabel,
)

# Import constants
from ui.constants import (
    ACTIVITY_SUGGESTIONS,
    CATEGORY_COLORS,
    CATEGORY_COLORS_LIGHT,
    CATEGORY_ICONS,
    METRIC_ICONS,
)

__all__ = [
    # Screens
    "HomeScreen",
    "AddLogScreen",
    "EditLogScreen",
    "SettingsScreen",

    # Components - Dropdown
    "StyledDropdown",
    "DropdownItem",

    # Components - Suggestion Field
    "ActivitySuggestionField",
    "SuggestionItem",

    # Components - Form Builder
    "DynamicFormBuilder",
    "KeyValueField",

    # Components - Log Card
    "LogCard",
    "MetricPill",
    "OverflowPill",
    "SwipeableLogCard",

    # Components - Empty State
    "EmptyStateWidget",

    # Components - Date Group
    "DateGroup",
    "DateGroupHeader",
    "NoActivityLabel",

    # Constants
    "ACTIVITY_SUGGESTIONS",
    "CATEGORY_COLORS",
    "CATEGORY_COLORS_LIGHT",
    "CATEGORY_ICONS",
    "METRIC_ICONS",
]
