"""
Database Package for HealthLogOps.

This package provides database management functionality for the
health tracking application, including category and log CRUD operations.

Modules:
    - manager: DatabaseManager class and DatabaseError exception

Example:
    >>> from database import DatabaseManager
    >>> db = DatabaseManager("health_tracker.db")
    >>> db.seed_default_categories()
"""

from .manager import DatabaseManager, DatabaseError

__all__ = [
    "DatabaseManager",
    "DatabaseError",
]
