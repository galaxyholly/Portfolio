"""
Blog application forms.

Defines forms for creating/editing blog posts and comments.
"""

import logging
from django import forms
from django.core.exceptions import ValidationError
from ckeditor.widgets import CKEditorWidget
from better_profanity import profanity

from .models import BlogPost, Comment, Tag

logger = logging.getLogger(__name__)

class BlogPostForm(forms.ModelForm):
    """
    Form for creating and editing blog posts with predefined tags.
    """
    
    # Use ModelMultipleChoiceField to work directly with Tag objects
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tag-checkbox-group'
        }),
        required=False,
        label="Tags",
        help_text="Select one or more tags that describe your post"
    )
    
    # Image field with validation
    image = forms.ImageField(
        required=False,
        help_text="Upload a featured image for your post (optional, max 5MB)",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'tags', 'image']  # Include tags in fields
        
        widgets = {
            'content': CKEditorWidget(),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your post title...',
                'maxlength': 100
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form and ensure we have the predefined tags."""
        super().__init__(*args, **kwargs)
        
        # Create predefined tags if they don't exist
        predefined_tags = ['Project', 'Thoughts', 'Stories', 'Career', 'Tech', 'Other']
        for tag_name in predefined_tags:
            Tag.objects.get_or_create(name=tag_name)
        
        # Update the queryset to only show predefined tags
        self.fields['tags'].queryset = Tag.objects.filter(name__in=predefined_tags)
    
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
    from django.core.files.uploadedfile import UploadedFile
    
    image = self.cleaned_data.get('image')
    
    if image and isinstance(image, UploadedFile):
        # Only validate newly uploaded files
        # Check file size (5MB limit)
        if image.size > 5 * 1024 * 1024:
            raise ValidationError("Image file size must be under 5MB.")
            
        # Check file type
        if not image.content_type.startswith('image/'):
            raise ValidationError("Please upload a valid image file.")
                
    return image



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
        """Validate comment content for profanity and basic spam patterns."""
        comment_text = self.cleaned_data.get('comment_text', '').strip()
        
        # Basic length validation
        if not comment_text:
            raise ValidationError("Comment cannot be empty.")
            
        if len(comment_text) < 3:
            raise ValidationError("Comment must be at least 3 characters long.")
            
        if len(comment_text) > 1000:
            raise ValidationError("Comment must be under 1000 characters.")
        
        # Profanity check
        if profanity.contains_profanity(comment_text):
            raise ValidationError("Please keep comments respectful and avoid inappropriate language.")
            
        return comment_text
