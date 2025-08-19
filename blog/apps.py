"""
Blog application configuration.

Django app configuration for the blog application.
"""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Configuration class for the blog application."""
    
    # Use BigAutoField for primary keys (Django 3.2+ default)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Application name
    name = 'blog'