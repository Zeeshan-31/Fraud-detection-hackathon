"""Tabs package for dashboard."""

from .upload_tab import render_upload_tab
from .dashboard_tab import render_dashboard_tab
from .about_tab import render_about_tab

__all__ = ["render_upload_tab", "render_dashboard_tab", "render_about_tab"]
