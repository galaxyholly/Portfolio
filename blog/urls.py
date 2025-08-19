"""
Blog application URL configuration.

Maps URL patterns to view functions for the blog app.
"""

from django.urls import path
from . import views

# Namespace for blog app URLs
app_name = "blog"

urlpatterns = [
    # Blog post listing page
    path("blog_index", views.blog_post_view, name="index"),
    
    # Create new blog post page
    path("blog_form", views.post_blog, name="blog_form"),
    
    # Individual blog post detail page
    path("blog_detail/<int:pk>/", views.detail_page, name="blog_detail"),
    
    # AJAX search endpoint for filtering posts
    path('search/', views.blog_post_search, name='blog_search'),
    
    # Edit existing blog post page
    path('blog_detail/<int:pk>/edit/', views.edit_post, name='edit_post'),
]