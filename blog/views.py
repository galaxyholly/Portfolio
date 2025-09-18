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

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

# Set up logging
logger = logging.getLogger(__name__)

@staff_member_required
@ratelimit(key='ip', rate='5/m', method='GET', block=True)
def post_blog(request):
    """Handle blog post creation."""
    if request.method == "POST":
        logger.info("Processing blog post creation request")
        
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    post = form.save(commit=False)
                    post.author = request.user
                    post.save()
                    form.save_m2m()  # Save the many-to-many relationships
                    
                    logger.info(f"Successfully created blog post: {post.title} (ID: {post.id})")
                    messages.success(request, "Post created successfully!")
                    return HttpResponseRedirect(reverse("blog:index"))
                    
            except Exception as e:
                logger.error(f"Error creating blog post: {e}")
                messages.error(request, "Error creating post. Please try again.")
        else:
            logger.warning(f"Blog post form validation failed: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm()
    
    return render(request, 'blog/blog_form.html', {'form': form})

@ratelimit(key='ip', rate='120/m', method='GET', block=True)
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

@ratelimit(key='ip', rate='30/m', method='GET', block=True)
def detail_page(request, pk):
    post = get_object_or_404(
        BlogPost.objects.prefetch_related('tags', 'comments__comment_author'), 
        pk=pk
    )
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('blog:blog_detail', pk=pk)
            
        form = BlogPostCommentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    comment = form.save(commit=False)
                    comment.comment_author = request.user
                    comment.blog_post = post
                    comment.save()
                    
                    logger.info(f"Comment added to post {post.id} by {request.user.username}")
                    messages.success(request, "Comment added successfully!")
                    
            except Exception as e:
                logger.error(f"Error saving comment: {e}")
                messages.error(request, "Error saving comment. Please try again.")
                
            return HttpResponseRedirect(reverse('blog:blog_detail', args=[post.id]))
        else:

            # Add this return statement:
            comments = post.comments.all()
            return render(request, 'blog/blog_detail.html', {
                'form': form,  # This will contain the errors
                'post': post, 
                'comments': comments
            })
    
    # GET request path
    comments = post.comments.all()
    form = BlogPostCommentForm(initial={'blog_post': post})
    
    return render(request, 'blog/blog_detail.html', {
        'form': form, 
        'post': post, 
        'comments': comments
    })

@ratelimit(key='ip', rate='200/m', method='GET', block=True)
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

@ratelimit(key='ip', rate='10/m', method='GET', block=True)
@staff_member_required
def edit_post(request, pk):
    """Handle blog post editing with debugging."""
    post = get_object_or_404(BlogPost, pk=pk)
    
    print(f"=== EDIT POST DEBUG - Post ID: {pk} ===")
    print(f"Post exists: {post}")
    print(f"Post title: {post.title}")
    print(f"Post tags: {[tag.name for tag in post.tags.all()]}")
    
    # Check permissions
    user_is_author = post.author == request.user
    user_is_staff = request.user.is_staff
    
    print(f"User: {request.user}")
    print(f"Is author: {user_is_author}")
    print(f"Is staff: {user_is_staff}")
    
    if not user_is_author and not user_is_staff:
        print("PERMISSION DENIED")
        messages.error(request, "You don't have permission to edit this post.")
        return redirect('blog:blog_detail', pk=post.pk)
    
    if request.method == 'POST':
        print("=== POST REQUEST DEBUG ===")
        print(f"POST data: {dict(request.POST)}")
        print(f"FILES data: {dict(request.FILES)}")
        
        try:
            form = BlogPostForm(request.POST, request.FILES, instance=post)
            print(f"Form created successfully")
            
            print(f"Form is valid: {form.is_valid()}")
            
            if not form.is_valid():
                print(f"Form errors: {form.errors}")
                print(f"Non-field errors: {form.non_field_errors()}")
                messages.error(request, "Please correct the errors below.")
            else:
                print("Form is valid, attempting to save...")
                
                try:
                    with transaction.atomic():
                        print("Starting transaction...")
                        updated_post = form.save()
                        print(f"Form saved successfully: {updated_post}")
                        print(f"Updated post tags: {[tag.name for tag in updated_post.tags.all()]}")
                        
                        logger.info(f"Post {post.id} updated by {request.user.username}")
                        messages.success(request, "Post updated successfully!")
                        return redirect('blog:blog_detail', pk=post.pk)
                        
                except Exception as e:
                    print(f"ERROR during save: {e}")
                    print(f"Exception type: {type(e)}")
                    import traceback
                    traceback.print_exc()
                    logger.error(f"Error updating post {pk}: {e}")
                    messages.error(request, "Error updating post. Please try again.")
                    
        except Exception as e:
            print(f"ERROR creating form: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, "Error loading form. Please try again.")
            
    else:
        print("=== GET REQUEST DEBUG ===")
        try:
            form = BlogPostForm(instance=post)
            print(f"Form created for GET request")
            print(f"Form initial data: {form.initial}")
            print(f"Tags field initial: {form.fields['tags'].initial}")
        except Exception as e:
            print(f"ERROR creating form for GET: {e}")
            import traceback
            traceback.print_exc()
    
    print("=== RENDERING TEMPLATE ===")
    return render(request, 'blog/blog_form.html', {
        'form': form,
        'post': post
    })
    