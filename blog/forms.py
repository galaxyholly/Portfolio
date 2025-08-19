"""
Blog application forms.

Defines forms for creating/editing blog posts and comments.
"""

import logging
from django import forms
from django.core.exceptions import ValidationError
from ckeditor.widgets import CKEditorWidget

from .models import BlogPost, Comment, Tag

logger = logging.getLogger(__name__)


class BlogPostForm(forms.ModelForm):
    """
    Form for creating and editing blog posts.
    
    Uses predefined tags instead of free-form input for better organization.
    """
    
    # Predefined tag choices for consistent categorization
    PREDEFINED_TAGS = [
        ('Project', 'Project'),
        ('Thoughts', 'Thoughts'), 
        ('Stories', 'Stories'),
        ('Career', 'Career'),
        ('Tech', 'Tech'),
        ('Other', 'Other'),
    ]
    
    # Replace free-form tags with predefined checkboxes
    tags_selection = forms.MultipleChoiceField(
        choices=PREDEFINED_TAGS,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tag-checkbox-group'
        }),
        required=False,
        label="Tags",
        help_text="Select one or more tags that describe your post"
    )
    
    # Image field with validation and custom styling
    image = forms.ImageField(
        required=False,
        help_text="Upload a featured image for your post (optional, max 5MB)",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        """Form metadata and field configuration."""
        model = BlogPost
        fields = ['title', 'content', 'image']
        
        # Custom widgets for form fields
        widgets = {
            'content': CKEditorWidget(),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your post title...',
                'maxlength': 100
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form and populate tags if editing existing post."""
        super().__init__(*args, **kwargs)
        
        # If editing existing post, pre-select current tags
        if self.instance and self.instance.pk:
            current_tags = [tag.name for tag in self.instance.tags.all()]
            self.fields['tags_selection'].initial = current_tags
    
    def clean_title(self):
        """Validate blog post title."""
        title = self.cleaned_data.get('title', '').strip()
        
        if not title:
            raise ValidationError("Title is required.")
            
        if len(title) < 3:
            raise ValidationError("Title must be at least 3 characters long.")
            
        return title
    
    def clean_image(self):
        """Validate uploaded image."""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file size must be under 5MB.")
                
            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError("Please upload a valid image file.")
                
        return image
    
    def save(self, commit=True):
        """Save the form and handle tags processing."""
        try:
            # Save the blog post first
            instance = super().save(commit=commit)
            
            if commit:
                # Process tags after the instance is saved
                self._save_tags(instance)
            
            return instance
            
        except Exception as e:
            logger.error(f"Error saving blog post form: {e}")
            raise ValidationError("Error saving post. Please try again.")
    
    def _save_tags(self, instance):
        """Process and save selected tags."""
        try:
            selected_tags = self.cleaned_data.get('tags_selection', [])
            logger.info(f"Processing tags for post {instance.id}: {selected_tags}")
            
            # Clear existing tags
            instance.tags.clear()
            
            # Add selected tags
            for tag_name in selected_tags:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'name': tag_name}
                )
                instance.tags.add(tag)
                
            logger.info(f"Successfully updated tags for post {instance.id}")
            
        except Exception as e:
            logger.error(f"Error processing tags: {e}")
            # Don't raise exception here to avoid breaking post save


class BlogPostCommentForm(forms.ModelForm):
    """
    Form for adding comments to blog posts.
    """
    
    class Meta:
        """Form metadata and field configuration."""
        model = Comment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts...',
                'rows': 4,
                'maxlength': 1000
            }),
        }
    
    def clean_comment_text(self):
        """Validate comment content."""
        comment_text = self.cleaned_data.get('comment_text', '').strip()
        
        if not comment_text:
            raise ValidationError("Comment cannot be empty.")
            
        if len(comment_text) < 3:
            raise ValidationError("Comment must be at least 3 characters long.")
            
        if len(comment_text) > 1000:
            raise ValidationError("Comment must be under 1000 characters.")
            
        return comment_text