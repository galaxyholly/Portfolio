"""
Blog application models.

Defines the database structure for blog posts, comments, and tags.
"""

import logging
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
import datetime

logger = logging.getLogger(__name__)


class Tag(models.Model):
    """
    Model representing a tag for organizing blog posts.
    
    Tags provide a flexible way to categorize posts and enable filtering.
    """
    name = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique tag name (max 50 characters)"
    )
    slug = models.SlugField(
        max_length=50, 
        unique=True, 
        blank=True,
        help_text="URL-friendly version of the tag name"
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When this tag was first created"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
    
    def __str__(self):
        """Return string representation of the tag."""
        return self.name
    
    def clean(self):
        """Validate tag data before saving."""
        super().clean()
        
        # Validate tag name
        if not self.name or not self.name.strip():
            raise ValidationError("Tag name cannot be empty.")
            
        # Normalize tag name (capitalize first letter)
        self.name = self.name.strip().title()
    
    def save(self, *args, **kwargs):
        """Save tag with auto-generated slug."""
        try:
            # Auto-generate slug from name if not provided
            if not self.slug:
                from django.utils.text import slugify
                self.slug = slugify(self.name)
                
            # Run validation
            self.full_clean()
            
            super().save(*args, **kwargs)
            logger.info(f"Tag saved: {self.name}")
            
        except Exception as e:
            logger.error(f"Error saving tag '{self.name}': {e}")
            raise


class BlogPost(models.Model):
    """
    Model representing a blog post.
    
    Uses tags for flexible organization and categorization.
    """
    
    title = models.CharField(
        max_length=100,
        help_text="The title of your blog post (max 100 characters)"
    )
    
    content = RichTextField(
        help_text="The main content of your blog post"
    )
    
    pub_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When this post was published"
    )
    
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='blog_posts',
        help_text="The user who authored this post"
    )
    
    image = models.ImageField(
        upload_to='blog_images/', 
        blank=True, 
        null=True,
        help_text="Optional featured image for the post"
    )
    
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name='blog_posts',
        help_text="Tags to categorize this post"
    )

    class Meta:
        ordering = ['-pub_date']  # Newest posts first
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        """Return string representation of the post."""
        return f"{self.title} by {self.author.username}"
    
    def clean(self):
        """Validate blog post data before saving."""
        super().clean()
        
        # Validate title
        if not self.title or not self.title.strip():
            raise ValidationError("Post title cannot be empty.")
            
        # Validate content
        if not self.content or not self.content.strip():
            raise ValidationError("Post content cannot be empty.")
    
    def save(self, *args, **kwargs):
        """Save blog post with validation."""
        try:
            self.full_clean()
            super().save(*args, **kwargs)
            logger.info(f"Blog post saved: {self.title} (ID: {self.pk})")
            
        except Exception as e:
            logger.error(f"Error saving blog post '{self.title}': {e}")
            raise
    
    def was_published_recently(self):
        """Check if post was published within the last 24 hours."""
        if not self.pub_date:
            return False
            
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def get_tags_display(self):
        """Return comma-separated string of tag names for display."""
        try:
            return ', '.join([tag.name for tag in self.tags.all()])
        except Exception as e:
            logger.error(f"Error getting tags display for post {self.pk}: {e}")
            return ''
    
    def get_primary_category(self):
        """Return the first tag as primary category for backward compatibility."""
        try:
            first_tag = self.tags.first()
            return first_tag.name if first_tag else 'Other'
        except Exception as e:
            logger.error(f"Error getting primary category for post {self.pk}: {e}")
            return 'Other'


class Comment(models.Model):
    """
    Model representing a comment on a blog post.
    """
    
    blog_post = models.ForeignKey(
        BlogPost, 
        related_name='comments', 
        on_delete=models.CASCADE,
        help_text="The blog post this comment belongs to"
    )
    
    comment_text = models.TextField(
        max_length=1000,
        help_text="The comment content (max 1000 characters)"
    )
    
    comment_author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='blog_comments',
        help_text="The user who wrote this comment"
    )
    
    pub_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When this comment was posted"
    )

    class Meta:
        ordering = ['pub_date']  # Oldest comments first
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        """Return string representation of the comment."""
        preview = self.comment_text[:50] + "..." if len(self.comment_text) > 50 else self.comment_text
        return f"Comment by {self.comment_author.username}: {preview}"
    
    def clean(self):
        """Validate comment data before saving."""
        super().clean()
        
        # Validate comment text
        if not self.comment_text or not self.comment_text.strip():
            raise ValidationError("Comment text cannot be empty.")
            
        if len(self.comment_text.strip()) < 3:
            raise ValidationError("Comment must be at least 3 characters long.")
    
    def save(self, *args, **kwargs):
        """Save comment with validation."""
        try:
            self.full_clean()
            super().save(*args, **kwargs)
            logger.info(f"Comment saved by {self.comment_author.username} on post {self.blog_post.id}")
            
        except Exception as e:
            logger.error(f"Error saving comment: {e}")
            raise