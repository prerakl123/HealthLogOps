"""
Database Manager for HealthLogOps.

This module provides the DatabaseManager class for handling all SQLite
database operations including category management and health log tracking.

Classes:
    DatabaseManager: Main database interface for CRUD operations.
    DatabaseError: Custom exception for database-related errors.

The database schema supports:
    - Categories with dynamic JSON templates for flexible field definitions
    - Health logs with JSON-based metrics storage
    - Efficient indexing for timestamp-based queries

Example:
    >>> db = DatabaseManager("health_tracker.db")
    >>> db.seed_default_categories()
    >>> log_id = db.add_log(
    ...     category_id=1,
    ...     activity_name="Morning Run",
    ...     metrics={"duration_min": 30, "distance_km": 5.0}
    ... )
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Optional


class DatabaseError(Exception):
    """
    Custom exception for database operations.

    Raised when a database operation fails, wrapping the underlying
    SQLite error with additional context.

    Attributes:
        message: Human-readable error description.

    Example:
        >>> try:
        ...     db.add_category("Existing Category", "icon")
        ... except DatabaseError as e:
        ...     print(f"Failed: {e}")
    """
    pass


class DatabaseManager:
    """
    SQLite database manager for the Health Activity Tracker.

    Provides a clean interface for managing health tracking data including
    categories with customizable templates and log entries with flexible
    metrics storage.

    The manager handles:
        - Database initialization and schema creation
        - Category CRUD operations with JSON templates
        - Health log CRUD operations with JSON metrics
        - Default category seeding

    Attributes:
        db_path: Path to the SQLite database file.

    Args:
        db_path: Path to the SQLite database file. Can be a string or Path.
            Defaults to "health_tracker.db" in the current directory.

    Example:
        >>> db = DatabaseManager(Path.home() / ".healthlogops" / "data.db")
        >>> db.seed_default_categories()
        >>>
        >>> # Add a log entry
        >>> log_id = db.add_log(
        ...     category_id=1,
        ...     activity_name="Bench Press",
        ...     metrics={"sets": 3, "reps": 10, "weight_kg": 60.0}
        ... )
        >>>
        >>> # Retrieve recent logs
        >>> recent = db.get_recent_logs(limit=10)
    """

    def __init__(self, db_path: str | Path = "health_tracker.db") -> None:
        """
        Initialize the DatabaseManager.

        Creates the database file and initializes tables if they don't exist.

        :param db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path)
        self._init_database()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections.

        Provides automatic connection management with commit on success
        and rollback on failure.

        :yields: SQLite connection with row factory enabled.
        :raises DatabaseError: If the database operation fails.

        Example:
            >>> with self._get_connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT * FROM categories")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            conn.close()

    def _init_database(self) -> None:
        """
        Initialize database tables if they don't exist.

        Creates the following tables:
            - categories: Stores activity categories with templates
            - health_logs: Stores individual log entries

        Also creates indexes for efficient querying.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    icon TEXT NOT NULL DEFAULT 'checkbox-blank-circle',
                    template_json TEXT NOT NULL DEFAULT '{}'
                )
            """)

            # Create health_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    activity_name TEXT NOT NULL,
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    metrics_json TEXT NOT NULL DEFAULT '{}',
                    notes TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                        ON DELETE CASCADE
                )
            """)

            # Create index for faster log queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
                ON health_logs (timestamp DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_category 
                ON health_logs (category_id)
            """)

    # ========== Category Operations ==========

    def add_category(
        self,
        name: str,
        icon: str = "checkbox-blank-circle",
        template: Optional[dict[str, str]] = None
    ) -> int:
        """
        Add a new category with an optional template.

        :param name: Category name (e.g., 'Strength Training', 'Meal').
            Must be unique across all categories.
        :param icon: Material Design icon name for the category.
        :param template: Dictionary defining input fields for this category.
            Keys are field names, values are type strings ('int', 'float', 'str').
        :returns: The ID of the newly created category.
        :raises DatabaseError: If the category already exists or insertion fails.

        Example:
            >>> category_id = db.add_category(
            ...     name="Strength Training",
            ...     icon="weight-lifter",
            ...     template={"sets": "int", "reps": "int", "weight_kg": "float"}
            ... )
        """
        template_json = json.dumps(template or {})

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (name, icon, template_json) VALUES (?, ?, ?)",
                (name, icon, template_json)
            )
            return cursor.lastrowid

    def get_category(self, category_id: int) -> Optional[dict[str, Any]]:
        """
        Get a category by ID.

        :param category_id: The category ID to retrieve.
        :returns: Category dictionary with parsed template, or None if not found.
            Dictionary keys: id, name, icon, template

        Example:
            >>> category = db.get_category(1)
            >>> if category:
            ...     print(f"Name: {category['name']}")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_category(row)
            return None

    def get_all_categories(self) -> list[dict[str, Any]]:
        """
        Get all categories.

        :returns: List of category dictionaries with parsed templates,
            ordered alphabetically by name.

        Example:
            >>> categories = db.get_all_categories()
            >>> for cat in categories:
            ...     print(f"{cat['name']}: {cat['icon']}")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            return [self._row_to_category(row) for row in cursor.fetchall()]

    def update_category(
        self,
        category_id: int,
        name: Optional[str] = None,
        icon: Optional[str] = None,
        template: Optional[dict[str, str]] = None
    ) -> bool:
        """
        Update a category.

        Only provided fields will be updated; others remain unchanged.

        :param category_id: The category ID to update.
        :param name: New name (optional).
        :param icon: New icon (optional).
        :param template: New template dict (optional).
        :returns: True if updated, False if category not found or no changes.

        Example:
            >>> success = db.update_category(
            ...     category_id=1,
            ...     icon="dumbbell"
            ... )
        """
        updates: list[str] = []
        values: list[Any] = []

        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if icon is not None:
            updates.append("icon = ?")
            values.append(icon)
        if template is not None:
            updates.append("template_json = ?")
            values.append(json.dumps(template))

        if not updates:
            return False

        values.append(category_id)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE categories SET {', '.join(updates)} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0

    def delete_category(self, category_id: int) -> bool:
        """
        Delete a category (cascades to related logs).

        Warning: This will also delete all health logs associated
        with this category due to the foreign key cascade.

        :param category_id: The category ID to delete.
        :returns: True if deleted, False if not found.

        Example:
            >>> if db.delete_category(5):
            ...     print("Category deleted")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0

    # ========== Health Log Operations ==========

    def add_log(
        self,
        category_id: int,
        activity_name: str,
        metrics: Optional[dict[str, Any]] = None,
        notes: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Add a new health log entry.

        :param category_id: The category this log belongs to.
        :param activity_name: Name of the activity (e.g., 'Bench Press').
        :param metrics: Dictionary of metric values (e.g., {"reps": 12, "weight": 60}).
        :param notes: Optional notes for this log entry.
        :param timestamp: Optional timestamp (defaults to current time).
        :returns: The ID of the newly created log.
        :raises DatabaseError: If the category doesn't exist or insertion fails.

        Example:
            >>> log_id = db.add_log(
            ...     category_id=1,
            ...     activity_name="Bench Press",
            ...     metrics={"sets": 3, "reps": 10, "weight_kg": 60.0},
            ...     notes="Felt strong today!"
            ... )
        """
        metrics_json = json.dumps(metrics or {})
        ts = timestamp or datetime.now()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO health_logs 
                (category_id, activity_name, timestamp, metrics_json, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (category_id, activity_name, ts.isoformat(), metrics_json, notes)
            )
            return cursor.lastrowid

    def get_log(self, log_id: int) -> Optional[dict[str, Any]]:
        """
        Get a log by ID.

        :param log_id: The log ID to retrieve.
        :returns: Log dictionary with parsed metrics, or None if not found.
            Dictionary keys: id, category_id, activity_name, timestamp, metrics, notes

        Example:
            >>> log = db.get_log(42)
            >>> if log:
            ...     print(f"Activity: {log['activity_name']}")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM health_logs WHERE id = ?", (log_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_log(row)
            return None

    def get_recent_logs(self, limit: int = 20) -> list[dict[str, Any]]:
        """
        Get the most recent logs with category information.

        Includes joined category data (name and icon) for display purposes.

        :param limit: Maximum number of logs to return.
        :returns: List of log dictionaries with parsed metrics and category info,
            ordered by timestamp descending (newest first).

        Example:
            >>> recent = db.get_recent_logs(limit=10)
            >>> for log in recent:
            ...     print(f"{log['activity_name']} ({log['category_name']})")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT hl.*, c.name as category_name, c.icon as category_icon
                FROM health_logs hl
                LEFT JOIN categories c ON hl.category_id = c.id
                ORDER BY hl.timestamp DESC
                LIMIT ?
                """,
                (limit,)
            )
            return [self._row_to_log(row) for row in cursor.fetchall()]

    def get_logs_by_category(
        self,
        category_id: int,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Get logs for a specific category.

        :param category_id: The category ID to filter by.
        :param limit: Maximum number of logs to return.
        :returns: List of log dictionaries for the specified category,
            ordered by timestamp descending.

        Example:
            >>> cardio_logs = db.get_logs_by_category(category_id=2, limit=30)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM health_logs 
                WHERE category_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (category_id, limit)
            )
            return [self._row_to_log(row) for row in cursor.fetchall()]

    def delete_log(self, log_id: int) -> bool:
        """
        Delete a log entry.

        :param log_id: The log ID to delete.
        :returns: True if deleted, False if not found.

        Example:
            >>> if db.delete_log(42):
            ...     print("Log deleted")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM health_logs WHERE id = ?", (log_id,))
            return cursor.rowcount > 0

    def update_log(
        self,
        log_id: int,
        activity_name: Optional[str] = None,
        metrics: Optional[dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update an existing log entry.

        :param log_id: The log ID to update.
        :param activity_name: New activity name (optional).
        :param metrics: New metrics dictionary (optional).
        :param notes: New notes (optional).
        :returns: True if updated, False if not found.

        Example:
            >>> success = db.update_log(
            ...     log_id=42,
            ...     activity_name="Updated Activity",
            ...     metrics={"sets": 4, "reps": 12}
            ... )
        """
        updates: list[str] = []
        values: list[Any] = []

        if activity_name is not None:
            updates.append("activity_name = ?")
            values.append(activity_name)
        if metrics is not None:
            updates.append("metrics_json = ?")
            values.append(json.dumps(metrics))
        if notes is not None:
            updates.append("notes = ?")
            values.append(notes)

        if not updates:
            return False

        values.append(log_id)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE health_logs SET {', '.join(updates)} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0

    # ========== Helper Methods ==========

    @staticmethod
    def _row_to_category(row: sqlite3.Row) -> dict[str, Any]:
        """
        Convert a database row to a category dictionary.

        :param row: SQLite Row object from categories table.
        :returns: Dictionary with parsed template JSON.
        """
        return {
            "id": row["id"],
            "name": row["name"],
            "icon": row["icon"],
            "template": json.loads(row["template_json"])
        }

    @staticmethod
    def _row_to_log(row: sqlite3.Row) -> dict[str, Any]:
        """
        Convert a database row to a log dictionary.

        :param row: SQLite Row object from health_logs table.
        :returns: Dictionary with parsed metrics JSON and datetime timestamp.
        """
        log_dict = {
            "id": row["id"],
            "category_id": row["category_id"],
            "activity_name": row["activity_name"],
            "timestamp": datetime.fromisoformat(row["timestamp"]),
            "metrics": json.loads(row["metrics_json"]),
            "notes": row["notes"]
        }

        # Include joined category info if available
        if "category_name" in row.keys():
            log_dict["category_name"] = row["category_name"]
            log_dict["category_icon"] = row["category_icon"]

        return log_dict

    def seed_default_categories(self) -> None:
        """
        Seed the database with default categories if empty.

        Creates common health tracking categories with appropriate
        templates. Does nothing if categories already exist.

        Default categories:
            - Strength Training (sets, reps, weight)
            - Cardio (duration, distance, heart rate)
            - Meal (calories, protein, carbs, fat)
            - Sleep (hours, quality)
            - Water Intake (glasses)
            - Weight Log (weight)

        Example:
            >>> db = DatabaseManager("new_database.db")
            >>> db.seed_default_categories()
        """
        existing = self.get_all_categories()
        if existing:
            return  # Don't seed if categories exist

        default_categories = [
            {
                "name": "Strength Training",
                "icon": "weight-lifter",
                "template": {
                    "sets": "int",
                    "reps": "int",
                    "weight_kg": "float"
                }
            },
            {
                "name": "Cardio",
                "icon": "run",
                "template": {
                    "duration_min": "int",
                    "distance_km": "float",
                    "avg_heart_rate": "int"
                }
            },
            {
                "name": "Meal",
                "icon": "food",
                "template": {
                    "calories": "int",
                    "protein_g": "float",
                    "carbs_g": "float",
                    "fat_g": "float"
                }
            },
            {
                "name": "Sleep",
                "icon": "sleep",
                "template": {
                    "hours": "float",
                    "quality_1_10": "int"
                }
            },
            {
                "name": "Water Intake",
                "icon": "water",
                "template": {
                    "glasses": "int"
                }
            },
            {
                "name": "Weight Log",
                "icon": "scale-bathroom",
                "template": {
                    "weight_kg": "float"
                }
            }
        ]

        for cat in default_categories:
            try:
                self.add_category(
                    name=cat["name"],
                    icon=cat["icon"],
                    template=cat["template"]
                )
            except DatabaseError:
                pass  # Skip if already exists
