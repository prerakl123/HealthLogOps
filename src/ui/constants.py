"""
Constants and configuration values for HealthLogOps UI.

This module contains color schemes, icon mappings, and activity suggestions
used throughout the application's user interface.

Color Palette:
    - Primary: Teal (#009688)
    - Primary Dark: #00796B
    - Primary Light: #B2DFDB
    - Accent: Amber (#FFC107)
    - Background: #F5F7FA
    - Surface: #FFFFFF
"""

from typing import Final

# =============================================================================
# TYPE ALIASES
# =============================================================================

ColorTuple = tuple[float, float, float, float]
"""RGBA color represented as a tuple of four floats (0.0 to 1.0)."""


# =============================================================================
# CATEGORY COLOR SCHEMES
# =============================================================================

CATEGORY_COLORS: Final[dict[str, ColorTuple]] = {
    "Strength Training": (0.91, 0.30, 0.24, 1),    # Red
    "Cardio": (0.20, 0.66, 0.33, 1),               # Green
    "Meal": (1.0, 0.60, 0.0, 1),                   # Orange
    "Sleep": (0.40, 0.23, 0.72, 1),                # Purple
    "Water Intake": (0.13, 0.59, 0.95, 1),         # Blue
    "Weight Log": (0.0, 0.59, 0.53, 1),            # Teal
    "default": (0.5, 0.5, 0.55, 1)                 # Gray
}
"""
Primary accent colors for each health tracking category.

These vibrant colors are used for category indicators, icons, and accent elements
to provide quick visual identification of different activity types.
"""

CATEGORY_COLORS_LIGHT: Final[dict[str, ColorTuple]] = {
    "Strength Training": (1.0, 0.90, 0.88, 1),     # Light Red
    "Cardio": (0.88, 0.96, 0.90, 1),               # Light Green
    "Meal": (1.0, 0.94, 0.85, 1),                  # Light Orange
    "Sleep": (0.93, 0.90, 0.98, 1),                # Light Purple
    "Water Intake": (0.88, 0.95, 1.0, 1),          # Light Blue
    "Weight Log": (0.88, 0.96, 0.95, 1),           # Light Teal
    "default": (0.94, 0.94, 0.95, 1)               # Light Gray
}
"""
Light background colors for metric pills and badges.

These pastel versions of the category colors are used as backgrounds
for metric displays to maintain visual hierarchy while reducing contrast.
"""


# =============================================================================
# ICON MAPPINGS
# =============================================================================

CATEGORY_ICONS: Final[dict[str, str]] = {
    "Strength Training": "weight-lifter",
    "Cardio": "run-fast",
    "Meal": "food-apple",
    "Sleep": "sleep",
    "Water Intake": "cup-water",
    "Weight Log": "scale-bathroom",
    "default": "checkbox-marked-circle-outline"
}
"""
Material Design icon names for each health tracking category.

These icons are displayed alongside category names and in log cards
to provide quick visual identification.
"""

METRIC_ICONS: Final[dict[str, str]] = {
    "sets": "numeric",
    "reps": "repeat",
    "weight": "weight",
    "weight_kg": "weight",
    "duration": "timer-outline",
    "duration_min": "timer-outline",
    "distance": "map-marker-distance",
    "distance_km": "map-marker-distance",
    "calories": "fire",
    "protein": "food-steak",
    "protein_g": "food-steak",
    "carbs": "bread-slice",
    "carbs_g": "bread-slice",
    "fat": "water",
    "fat_g": "water",
    "hours": "clock-outline",
    "quality": "star",
    "quality_1_10": "star",
    "glasses": "cup-water",
    "avg_heart_rate": "heart-pulse",
    "incline": "angle-acute",
    "incline_percent": "angle-acute",
    "speed": "speedometer",
    "speed_kmh": "speedometer",
    "custom": "tag-outline",
    "default": "circle-small"
}
"""
Material Design icon names for different metric fields.

These icons are displayed in metric pills within log cards to provide
visual context for the type of data being displayed.
"""


# =============================================================================
# ACTIVITY SUGGESTIONS
# =============================================================================

ACTIVITY_SUGGESTIONS: Final[dict[str, list[str]]] = {
    "Strength Training": [
        "Bench Press", "Squats", "Deadlift", "Bicep Curls", "Shoulder Press",
        "Lat Pulldown", "Leg Press", "Tricep Dips", "Pull-ups", "Push-ups",
        "Lunges", "Plank", "Cable Rows", "Chest Fly", "Leg Curls"
    ],
    "Cardio": [
        "Morning Run", "Evening Jog", "HIIT Workout", "Cycling", "Swimming",
        "Jump Rope", "Treadmill", "Treadmill Walk", "Elliptical", "Stair Climber", "Rowing",
        "Sprint Intervals", "Dancing", "Aerobics", "Walking", "Hiking"
    ],
    "Meal": [
        "Breakfast", "Lunch", "Dinner", "Snack", "Pre-workout Meal",
        "Post-workout Meal", "Protein Shake", "Smoothie", "Salad", "Fruits"
    ],
    "Sleep": [
        "Night Sleep", "Power Nap", "Afternoon Nap", "Recovery Sleep"
    ],
    "Water Intake": [
        "Morning Hydration", "Post-workout", "Evening", "With Meals", "Afternoon"
    ],
    "Weight Log": [
        "Morning Weight", "Evening Weight", "Weekly Check", "Monthly Check"
    ],
    "Daily Steps": [
        "Daily Total", "Morning Walk", "Evening Walk", "Office Commute", "Weekend Hike"
    ]
}
"""
Predefined activity suggestions for each category.

These suggestions appear in the activity name field dropdown to help users
quickly select common activities without typing. The suggestions are
context-sensitive based on the selected category.
"""


# =============================================================================
# UI CONFIGURATION
# =============================================================================

DEFAULT_ANIMATION_DURATION: Final[float] = 0.2
"""Default duration in seconds for UI animations."""

DROPDOWN_MAX_HEIGHT: Final[int] = 250
"""Maximum height in density-independent pixels for dropdown menus."""

SUGGESTION_MAX_HEIGHT: Final[int] = 250
"""Maximum height in density-independent pixels for suggestion dropdowns."""

MAX_VISIBLE_SUGGESTIONS: Final[int] = 5
"""Maximum number of suggestions to display at once."""

MAX_VISIBLE_METRICS: Final[int] = 4
"""Maximum number of metric pills to display on a log card."""
