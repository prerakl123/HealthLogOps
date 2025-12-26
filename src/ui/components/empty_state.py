"""
Empty state widget for HealthLogOps.

This module provides placeholder widgets displayed when there is no
content to show, such as when no health logs have been recorded yet.

Classes:
    EmptyStateWidget: A friendly empty state placeholder.

Example:
    >>> if not logs:
    ...     container.add_widget(EmptyStateWidget())
"""

from kivy.metrics import dp, sp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon, MDLabel


class EmptyStateWidget(MDBoxLayout):
    """
    Widget displayed when there are no logs to show.

    Presents a friendly message encouraging the user to log their
    first activity, with an icon and instructional text.

    Attributes:
        None (configuration is fixed)

    Args:
        **kwargs: Additional keyword arguments passed to MDBoxLayout.

    Example:
        >>> empty_widget = EmptyStateWidget()
        >>> container.add_widget(empty_widget)
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize an EmptyStateWidget.

        :param kwargs: Additional keyword arguments passed to MDBoxLayout.
        """
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(16)
        self.padding = dp(40)
        self.adaptive_height = True

        # Icon
        icon = MDIcon(
            icon="clipboard-text-outline",
            font_size=sp(72),
            theme_icon_color="Custom",
            icon_color=(0.75, 0.75, 0.78, 1),
            halign="center"
        )
        self.add_widget(icon)

        # Title - no shorten needed
        title = MDLabel(
            text="No activities yet",
            font_style="Title",
            role="large",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.45, 0.45, 0.5, 1),
            adaptive_height=True
        )
        self.add_widget(title)

        # Subtitle - no shorten needed
        subtitle = MDLabel(
            text="Tap + to log your first activity",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.6, 0.6, 0.65, 1),
            adaptive_height=True
        )
        self.add_widget(subtitle)
