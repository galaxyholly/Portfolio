"""
Blog application views.

Handles blog post creation, listing, detail pages, comments, and search functionality.
"""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction, IntegrityError

from .models import BlogPost, Comment, Tag
from .forms import BlogPostForm, BlogPostCommentForm

# Set up logging
logger = logging.getLogger(__name__)


@staff_member_required
def post_blog(request):
    """
    Handle blog post creation.
    
    GET: Display empty blog post form
    POST: Process form submission and create new blog post
    """
    if request.method == "POST":
        logger.info("Processing blog post creation request")
        
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save post but don't commit to database yet
                    post = form.save(commit=False)
                    # Set the author to current logged-in user
                    post.author = request.user
                    # Save to database first (this gives the post an ID)
                    post.save()
                    
                    # Now call the form's save method to handle tags
                    form.save()
                    
                    logger.info(f"Successfully created blog post: {post.title} (ID: {post.id})")
                    messages.success(request, "Post created successfully!")
                    return HttpResponseRedirect(reverse("blog:index"))
                    
            except (IntegrityError, Exception) as e:
                logger.error(f"Error creating blog post: {e}")
                messages.error(request, "Error creating post. Please try again.")
        else:
            logger.warning(f"Blog post form validation failed: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        # Display empty form for GET requests
        form = BlogPostForm()
    
    return render(request, 'blog/blog_form.html', {'form': form})


def blog_post_view(request):
    """
    Display paginated list of blog posts.
    
    Supports both regular HTTP requests (returns HTML template) and 
    AJAX requests (returns JSON data) for dynamic loading.
    """
    try:
        # Validate and sanitize page parameter
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        # Get all blog posts ordered by publication date (newest first)
        # Use prefetch_related for tags to avoid N+1 queries
        blog_posts = BlogPost.objects.prefetch_related('tags').all().order_by('-pub_date')
        
        # Set up pagination - 6 posts per page
        paginator = Paginator(blog_posts, 6)
        page_obj = paginator.get_page(page)
        
        # Check if this is an AJAX request for dynamic content loading
        is_ajax_request = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        has_page_param = request.GET.get('page')
        
        if is_ajax_request or has_page_param:
            # Return JSON data for AJAX requests or pagination requests
            blog_posts_data = []
            for post in page_obj:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'category': post.get_primary_category(),
                    'tags': post.get_tags_display(),
                    'image': post.image.url if post.image else None,
                    'pub_date': post.pub_date.strftime('%B %d, %Y') if post.pub_date else '',
                    'author': str(post.author) if post.author else '',
                    'url': reverse('blog:blog_detail', kwargs={'pk': post.id}),
                }
                blog_posts_data.append(post_data)
            
            return JsonResponse({
                'blog_posts': blog_posts_data, 
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
            })
        else:
            # Return HTML template for regular browser requests
            return render(request, 'blog/blog_index.html', {
                'posts': page_obj
            })
            
    except Exception as e:
        logger.error(f"Error in blog_post_view: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Unable to load posts',
                'blog_posts': [],
                'has_next': False,
                'has_previous': False,
                'current_page': 1,
                'total_pages': 1,
            }, status=500)
        else:
            messages.error(request, "Error loading blog posts.")
            return render(request, 'blog/blog_index.html', {'posts': []})


def detail_page(request, pk):
    """
    Display blog post detail page with comments and comment form.
    
    GET: Show blog post, existing comments, and empty comment form
    POST: Process new comment submission
    """
    # Get the blog post or return 404 if not found
    post = get_object_or_404(
        BlogPost.objects.prefetch_related('tags', 'comments__comment_author'), 
        pk=pk
    )
    
    if request.method == "POST":
        # Handle comment submission
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('blog:blog_detail', pk=pk)
            
        form = BlogPostCommentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save comment but don't commit to database yet
                    comment = form.save(commit=False)
                    # Set comment author and associated blog post
                    comment.comment_author = request.user
                    comment.blog_post = post
                    # Save comment to database
                    comment.save()
                    
                    logger.info(f"Comment added to post {post.id} by {request.user.username}")
                    messages.success(request, "Comment added successfully!")
                    
            except Exception as e:
                logger.error(f"Error saving comment: {e}")
                messages.error(request, "Error saving comment. Please try again.")
                
            # Redirect to same page to prevent resubmission on refresh
            return HttpResponseRedirect(reverse('blog:blog_detail', args=[post.id]))
        else:
            messages.error(request, "Please correct the errors in your comment.")
    else:
        # GET request - display post, comments, and empty form
        comments = post.comments.all()
        form = BlogPostCommentForm(initial={'blog_post': post})
        
        return render(request, 'blog/blog_detail.html', {
            'form': form, 
            'post': post, 
            'comments': comments
        })


def blog_post_search(request):
    """
    Handle blog post search and filtering via AJAX.
    
    Supports:
    - Text search in post title, content, and tags
    - Pagination of search results
    
    Returns JSON response with filtered and paginated results.
    """
    try:
        # Get and validate search parameters
        search_query = request.GET.get('search', '').strip()
        
        # Sanitize search query (prevent overly long queries)
        if len(search_query) > 100:
            search_query = search_query[:100]
            
        # Validate page parameter
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        logger.info(f"Search request: query='{search_query}', page={page}")
        
        # Start with all blog posts, prefetch tags for efficiency
        posts = BlogPost.objects.prefetch_related('tags').all()
        
        # Apply text search filter if search query provided
        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()  # Use distinct to avoid duplicate results from tag matches
        
        # Order by most recent first
        posts = posts.order_by('-pub_date')
        
        # Set up pagination for search results
        paginator = Paginator(posts, 6)
        page_obj = paginator.get_page(page)
        
        # Build JSON response data
        posts_data = []
        for post in page_obj:
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'category': post.get_primary_category(),
                'tags': post.get_tags_display(),
                'image': post.image.url if post.image else None,
                'pub_date': post.pub_date.strftime('%B %d, %Y') if post.pub_date else '',
                'author': str(post.author) if post.author else '',
                'url': reverse('blog:blog_detail', kwargs={'pk': post.id}),
            }
            posts_data.append(post_data)
        
        response_data = {
            'blog_posts': posts_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_results': paginator.count,
        }
        
        logger.info(f"Search completed: {len(posts_data)} posts returned")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in blog search: {e}")
        return JsonResponse({
            'error': 'Search temporarily unavailable',
            'blog_posts': [],
            'has_next': False,
            'has_previous': False,
            'current_page': 1,
            'total_pages': 1,
            'total_results': 0,
        }, status=500)


@staff_member_required
def edit_post(request, pk):
    """
    Handle blog post editing.
    
    Only allows editing by:
    - The original post author
    - Staff/admin users
    
    GET: Display pre-filled edit form
    POST: Process form submission and update post
    """
    # Get the blog post or return 404 if not found
    post = get_object_or_404(BlogPost, pk=pk)
    
    # Check if user has permission to edit this post
    user_is_author = post.author == request.user
    user_is_staff = request.user.is_staff
    
    if not user_is_author and not user_is_staff:
        logger.warning(f"Unauthorized edit attempt on post {pk} by {request.user.username}")
        messages.error(request, "You don't have permission to edit this post.")
        return redirect('blog:blog_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save updated post to database (this will also handle tags)
                    form.save()
                    
                    logger.info(f"Post {post.id} updated by {request.user.username}")
                    messages.success(request, "Post updated successfully!")
                    return redirect('blog:blog_detail', pk=post.pk)
                    
            except Exception as e:
                logger.error(f"Error updating post {pk}: {e}")
                messages.error(request, "Error updating post. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Display pre-filled form for GET requests
        form = BlogPostForm(instance=post)
    
    return render(request, 'blog/blog_edit.html', {
        'form': form,
        'post': post
    })