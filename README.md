# HealthLogOps - Pythonic Health Activity Tracker

A personal, offline-first health tracking application for Android built with Python, Kivy, and KivyMD.

## Features

- **Dynamic Categories**: Create custom health tracking categories with flexible templates
- **Template-Based Logging**: Each category defines its own input fields (reps, weight, duration, etc.)
- **Offline-First**: All data stored locally in SQLite - no internet required
- **Material Design 3**: Clean, modern UI using KivyMD

## Project Structure

```
HealthLogOps/
├── src/
│   ├── main.py              # Application entry point
│   ├── database/
│   │   ├── __init__.py
│   │   └── manager.py       # DatabaseManager class
│   └── ui/
│       ├── __init__.py
│       ├── components.py    # DynamicFormBuilder & reusable components
│       ├── screens.py       # HomeScreen & AddLogScreen
│       └── healthlogops.kv  # Declarative UI definitions
├── buildozer.spec           # Android build configuration
├── pyproject.toml           # Python project configuration
└── README.md
```

## Database Schema

### Categories Table
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| name | TEXT | Category name (e.g., 'Strength Training') |
| icon | TEXT | Material Design icon name |
| template_json | TEXT | JSON defining input fields |

### Health Logs Table
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| category_id | INT | Foreign key to categories |
| activity_name | TEXT | Specific activity name |
| timestamp | DATETIME | When the activity occurred |
| metrics_json | TEXT | JSON storing actual values |
| notes | TEXT | Optional notes |

## Development Setup

### Prerequisites
- Python 3.11.9
- PyCharm (recommended)
- uv package manager

### Installation

```bash
# Install dependencies
uv sync

# Run the application (desktop preview)
uv run python src/main.py
```

### Building for Android (WSL2/Linux)

```bash
# Install buildozer
pip install buildozer

# Build APK
buildozer android debug
```

## Default Categories

The app comes pre-seeded with these categories:

1. **Strength Training** - Sets, Reps, Weight (kg)
2. **Cardio** - Duration, Distance, Heart Rate
3. **Meal** - Calories, Protein, Carbs, Fat
4. **Sleep** - Hours, Quality (1-10)
5. **Water Intake** - Glasses
6. **Weight Log** - Weight (kg)

## Architecture

### DynamicFormBuilder

The core of the flexible logging system. Parses JSON templates and generates appropriate input fields:

```python
template = {"reps": "int", "weight": "float"}
# Generates MDTextField inputs with proper validation
```

### Supported Field Types
- `int` - Integer input with numeric keyboard
- `float` - Decimal input with numeric keyboard
- `str` / `text` - Free text input

## License

MIT License - Feel free to use and modify for personal health tracking needs.
