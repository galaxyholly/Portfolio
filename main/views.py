import logging
from django.shortcuts import render
from django.core.cache import cache
from django.db import IntegrityError
from django.contrib import messages
from blog.models import BlogPost

# Set up logging
logger = logging.getLogger(__name__)

def home(request):
    """
    Home page view with latest blog posts and projects showcase.
    
    Displays the 3 most recent blog posts and featured projects.
    Uses caching for better performance.
    """
    try:
        # Try to get latest posts from cache first (cache for 15 minutes)
        cache_key = 'home_latest_posts'
        latest_posts = cache.get(cache_key)
        
        if latest_posts is None:
            try:
                # Get latest blog posts with error handling
                latest_posts = BlogPost.objects.select_related('author').prefetch_related('tags').filter(
                    # Optional: only show published posts if you add a published field later
                ).order_by('-pub_date')[:3]
                
                # Cache the posts for 15 minutes
                cache.set(cache_key, latest_posts, 900)
                logger.info(f"Retrieved {len(latest_posts)} latest posts for home page")
                
            except Exception as e:
                logger.error(f"Error retrieving latest blog posts: {e}")
                latest_posts = []
                messages.warning(request, "Some content may not be available right now.")
        
        # Projects data - consider moving to database later
        projects = get_projects_data()
        
        # Dashboard configuration
        dashboard_config = get_dashboard_config()
        
        context = {
            'latest_posts': latest_posts,
            'projects': projects,
            'dashboard_iframe_src': dashboard_config['iframe_src'],
            'dashboard_available': dashboard_config['available'],
        }
        
        logger.info("Home page rendered successfully")
        return render(request, 'main/home.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in home view: {e}")
        # Provide fallback content in case of errors
        context = {
            'latest_posts': [],
            'projects': get_fallback_projects(),
            'dashboard_iframe_src': '',
            'dashboard_available': False,
        }
        messages.error(request, "We're experiencing some technical difficulties. Please try again later.")
        return render(request, 'main/home.html', context)


def get_projects_data():
    """
    Get projects data. Consider moving to database model later.
    
    Returns list of project dictionaries with title, description, URL, and tags.
    """
    try:
        projects = [
            {
                'title': 'Django Portfolio Blog',
                'description': 'Full-stack blog with AJAX search, authentication, and content management.',
                'url': '/blog/blog_index',
                'tags': ['Django', 'Python', 'JavaScript', 'CSS Grid'],
                'featured': False,
                'status': 'live'
            },
            # Add more actual projects here as you build them
            # {
            #     'title': 'E-commerce Platform',
            #     'description': 'Full-stack e-commerce solution with payment integration.',
            #     'url': '/ecommerce/',
            #     'tags': ['Django', 'Stripe', 'PostgreSQL', 'Redis'],
            #     'featured': False,
            #     'status': 'development'
            # },
        ]
        
        logger.info(f"Retrieved {len(projects)} projects")
        return projects
        
    except Exception as e:
        logger.error(f"Error getting projects data: {e}")
        return get_fallback_projects()


def get_fallback_projects():
    """
    Fallback projects data in case of errors.
    """
    return [
        {
            'title': 'Portfolio Projects',
            'description': 'Multiple full-stack projects showcasing various technologies.',
            'url': '#',
            'tags': ['Django', 'Python', 'JavaScript'],
            'featured': False,
            'status': 'available'
        }
    ]


def get_dashboard_config():
    """
    Get dashboard configuration with fallback.
    
    Returns dashboard configuration dictionary.
    """
    try:
        # You could store this in Django settings or database
        config = {
            'iframe_src': 'https://bot.holly-portfolio.com/dashboard',
            'available': True,
            'timeout': 5000,  # 5 seconds
        }
        
        # Optional: Test if dashboard is available
        # You could add a simple health check here
        
        return config
        
    except Exception as e:
        logger.error(f"Error getting dashboard config: {e}")
        return {
            'iframe_src': '',
            'available': False,
            'timeout': 0,
        }


def projects(request):
    """
    Projects page view.
    
    Display detailed information about all projects.
    """
    try:
        # Get all projects (you might want to expand this later)
        all_projects = get_projects_data()
        
        # You could add filtering, sorting, etc. here
        context = {
            'projects': all_projects,
            'page_title': 'My Projects',
        }
        
        logger.info("Projects page rendered successfully")
        return render(request, 'main/projects.html', context)
        
    except Exception as e:
        logger.error(f"Error in projects view: {e}")
        messages.error(request, "Error loading projects. Please try again.")
        return render(request, 'main/projects.html', {'projects': []})


def contact(request):
    """
    Contact page view.
    
    Handle contact form display and submission.
    """
    try:
        context = {
            'page_title': 'Contact Me',
            # Add contact form here later if needed
        }
        
        logger.info("Contact page rendered successfully")
        return render(request, 'main/contact.html', context)
        
    except Exception as e:
        logger.error(f"Error in contact view: {e}")
        messages.error(request, "Error loading contact page. Please try again.")
        return render(request, 'main/contact.html', {})


# Optional: Add a translation view if you have that project
def translation(request):
    """
    Translation microservice showcase page.
    """
    try:
        context = {
            'page_title': 'Translation Microservice',
            'service_url': 'https://bot.holly-portfolio.com/dashboard',
            'features': [
                'Real-time German to English translation',
                'Per-core worker pools for optimal performance',
                'Adaptive scaling based on load',
                'Live metrics and monitoring',
                'Discord bot integration',
            ],
            'tech_stack': ['Python', 'Flask', 'Multiprocessing', 'Discord.py', 'WebSockets'],
        }
        
        logger.info("Translation page rendered successfully")
        return render(request, 'main/translation.html', context)
        
    except Exception as e:
        logger.error(f"Error in translation view: {e}")
        messages.error(request, "Error loading translation service page.")
        return render(request, 'main/translation.html', {})