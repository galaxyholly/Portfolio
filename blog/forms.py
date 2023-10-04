from django import forms
from .models import BlogPost, Comment

class BlogPostForm(forms.ModelForm):
    
    class Meta:	
        model = BlogPost
        fields = ['title', 'content']  # or whatever fields your BlogPost model has

class BlogPostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment', 'blogpostid']