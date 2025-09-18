# Portfolio Website

A full-stack personal portfolio and blog built with Django and vanilla JavaScript, featuring dynamic content loading and real-time search functionality.

**Live Site:** [https://www.holly-portfolio.com/](https://www.holly-portfolio.com/)

## Features

- **Full-Stack Architecture**: Django backend with vanilla JavaScript frontend
- **Dynamic Blog System**: Complete CRUD operations for blog posts and comments
- **Real-Time Search**: AJAX-powered search with live filtering and pagination
- **Infinite Scroll**: Seamless content loading without page refreshes
- **Responsive Design**: Clean, modern interface that works across devices
- **Tag-Based Organization**: Flexible content categorization system
- **Admin Interface**: Custom Django admin for content management

## Technical Stack

- **Backend**: Python, Django, PostGreSQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Features**: AJAX, RESTApi's, Django ORM, Form validation
- **Deployment**: Self-hosted on home server with Cloudflare tunnel

## Key Components

### Models
- Blog posts with rich text content and image support
- Tag-based categorization system
- User comments with authentication
- Comprehensive data validation

### Views
- Paginated blog listing with AJAX support
- Real-time search and filtering
- Staff-only content creation and editing
- JSON API endpoints for dynamic loading

### Frontend
- Vanilla JavaScript for dynamic interactions
- Infinite scroll pagination
- Real-time search without page reloads
- Responsive CSS Grid layouts

## Architecture Highlights

- **Database Optimization**: Efficient queries using `prefetch_related` to avoid N+1 problems
- **Error Handling**: Comprehensive logging and graceful error recovery
- **Security**: Input validation, authentication checks, file upload restrictions
- **Performance**: AJAX pagination and search for smooth user experience

## Setup

Please do not copy my website. You are welcome to use the code if you like, but don't directly copy it.

## Project Structure

- Django models for blog posts, comments, and tags
- Custom forms with validation and CKEditor integration
- AJAX views returning JSON for dynamic content
- Vanilla JavaScript handling infinite scroll and search
- Custom admin interface for content management

Built as a showcase of full-stack web development skills, demonstrating both backend Django proficiency and frontend JavaScript capabilities.
