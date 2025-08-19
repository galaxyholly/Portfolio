"""
Blog application admin configuration.

Registers blog models with Django admin interface for content management.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import BlogPost, Comment, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model with enhanced functionality."""
    
    list_display = ['name', 'slug', 'post_count', 'created_date']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_date']
    ordering = ['name']
    
    def post_count(self, obj):
        """Display number of posts using this tag."""
        count = obj.blog_posts.count()
        return f"{count} post{'s' if count != 1 else ''}"
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Admin interface for BlogPost model with enhanced functionality."""
    
    list_display = ['title', 'author', 'pub_date', 'comment_count', 'get_tags_display']
    list_filter = ['pub_date', 'author', 'tags']
    search_fields = ['title', 'content', 'author__username']
    filter_horizontal = ['tags']
    date_hierarchy = 'pub_date'
    readonly_fields = ['pub_date']
    ordering = ['-pub_date']
    
    # Organize fields in fieldsets for better UX
    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'content', 'image')
        }),
        ('Organization', {
            'fields': ('tags',),
            'description': 'Select tags to categorize this post'
        }),
        ('Metadata', {
            'fields': ('pub_date',),
            'classes': ('collapse',)
        }),
    )
    
    def comment_count(self, obj):
        """Display number of comments on this post."""
        count = obj.comments.count()
        if count > 0:
            return format_html(
                '<a href="/admin/blog/comment/?blog_post__id__exact={}">{} comment{}</a>',
                obj.id, count, 's' if count != 1 else ''
            )
        return "No comments"
    comment_count.short_description = 'Comments'
    
    def save_model(self, request, obj, form, change):
        """Auto-populate author field with current user when creating new posts."""
        if not change:  # If creating new post
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model with enhanced functionality."""
    
    list_display = ['comment_author', 'blog_post_link', 'comment_preview', 'pub_date']
    list_filter = ['pub_date', 'blog_post', 'comment_author']
    search_fields = ['comment_author__username', 'comment_text', 'blog_post__title']
    readonly_fields = ['pub_date']
    ordering = ['-pub_date']
    
    def blog_post_link(self, obj):
        """Create clickable link to the blog post."""
        return format_html(
            '<a href="/admin/blog/blogpost/{}/change/">{}</a>',
            obj.blog_post.id, obj.blog_post.title
        )
    blog_post_link.short_description = 'Blog Post'
    
    def comment_preview(self, obj):
        """Show first 50 characters of comment text."""
        return obj.comment_text[:50] + "..." if len(obj.comment_text) > 50 else obj.comment_text
    comment_preview.short_description = 'Comment Preview'


# Customize the admin site header and titles
admin.site.site_header = "The Holly Branch Admin"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Welcome to The Holly Branch Administration"