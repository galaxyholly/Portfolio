let page_num = 1;
const container = document.querySelector('body');
let isLoading = false;
// Search variables
let currentSearchQuery = '';
let currentTag = '';
let isSearchMode = false;
let supportsAjax = true;

// Initialize the application
try {
    loadImages();
    isLoading = false;
} catch (error) {
    console.error('Error initializing application:', error);
    showErrorMessage('Failed to initialize the blog. Please refresh the page.');
}

// Enhanced error logging
function logError(functionName, error, context = {}) {
    console.error(`Error in ${functionName}:`, error);
    console.error('Context:', context);
}

// Show user-friendly error messages
function showErrorMessage(message, container = null) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        background: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 8px;
        margin: 20px;
        border: 1px solid #f5c6cb;
        text-align: center;
    `;
    errorDiv.textContent = message;
    
    if (container) {
        container.appendChild(errorDiv);
    } else {
        const postList = document.getElementById('post-list');
        if (postList) {
            postList.appendChild(errorDiv);
        }
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

// Enhanced HTML sanitization with error handling
function stripHtmlTags(html) {
    try {
        if (!html) return '';
        const temp = document.createElement('div');
        temp.innerHTML = html;
        return temp.textContent || temp.innerText || '';
    } catch (error) {
        logError('stripHtmlTags', error, { html });
        return String(html || ''); // Fallback to string conversion
    }
}

// Helper function to determine category with error handling
function getPostCategory(postData) {
    try {
        if (!postData) return 'post';
        
        // Try category field first
        if (postData.category && typeof postData.category === 'string' && postData.category.trim()) {
            return postData.category.trim();
        }
        
        // Try first tag
        if (postData.tags && typeof postData.tags === 'string' && postData.tags.trim()) {
            const firstTag = postData.tags.split(',')[0]?.trim();
            if (firstTag) {
                return firstTag;
            }
        }
        
        // Fallback to generic
        return 'post';
    } catch (error) {
        logError('getPostCategory', error, { postData });
        return 'post';
    }
}

// Helper function for display text with error handling
function getCategoryDisplayText(category) {
    try {
        const displayNames = {
            'tech': 'Tech',
            'thoughts': 'Thoughts', 
            'stories': 'Stories',
            'career': 'Career',
            'project': 'Project',
            'post': 'Post'
        };
        
        if (!category || typeof category !== 'string') {
            return 'Post';
        }
        
        return displayNames[category.toLowerCase()] || 
               category.charAt(0).toUpperCase() + category.slice(1).toLowerCase();
    } catch (error) {
        logError('getCategoryDisplayText', error, { category });
        return 'Post';
    }
}

// Enhanced ghost cards function with error handling
function addGhostCards() {
    try {
        const postList = document.getElementById('post-list');
        if (!postList) {
            console.warn('Post list container not found');
            return;
        }
        
        const posts = postList.children;
        const postsCount = posts.length;
        
        // Remove any existing ghost cards first
        const existingGhosts = postList.querySelectorAll('.ghost-card');
        existingGhosts.forEach(ghost => {
            try {
                ghost.remove();
            } catch (error) {
                logError('addGhostCards - removing ghost', error);
            }
        });
        
        // Calculate how many cards per row
        const containerWidth = postList.offsetWidth;
        if (containerWidth <= 0) return;
        
        const cardsPerRow = Math.floor(containerWidth / 350);
        
        // Calculate how many ghost cards needed
        const remainder = postsCount % cardsPerRow;
        if (remainder !== 0 && cardsPerRow > 1) {
            const ghostsNeeded = cardsPerRow - remainder;
            
            for (let i = 0; i < ghostsNeeded; i++) {
                try {
                    const ghostCard = document.createElement('div');
                    ghostCard.className = 'ghost-card';
                    ghostCard.style.visibility = 'hidden';
                    ghostCard.style.minHeight = '280px';
                    ghostCard.style.minWidth = '350px';
                    postList.appendChild(ghostCard);
                } catch (error) {
                    logError('addGhostCards - creating ghost card', error, { i });
                }
            }
        }
    } catch (error) {
        logError('addGhostCards', error);
    }
}

// Enhanced featured post creation with error handling
function createFeaturedPost(postData, index) {
    try {
        if (!postData) {
            throw new Error('Post data is required');
        }
        
        const featured = document.getElementById("featured");
        if (!featured) {
            throw new Error('Featured container not found');
        }
        
        const featured_post_wrapper = document.createElement('div');
        featured_post_wrapper.className = 'featured-post-wrapper';
        featured_post_wrapper.style.cursor = 'pointer';
        
        // Add click handler with error handling
        featured_post_wrapper.addEventListener("click", function(e) {
            try {
                if (e.target.tagName === 'BUTTON') return;
                if (postData.url) {
                    window.location.href = postData.url;
                }
            } catch (error) {
                logError('featured post click handler', error, { postData });
            }
        });
        
        // Create image section with thumbnail support
        const featured_post_image = document.createElement('div');
        featured_post_image.className = 'featured-post-image';
        
        try {
            if (postData.thumbnail || postData.image) {
                const img = document.createElement('img');
                img.src = index === 0 ? 
                    (postData.thumbnail || postData.image) : 
                    (postData.thumbnail_small || postData.thumbnail || postData.image);
                img.alt = stripHtmlTags(postData.title) || 'Featured post image';
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                img.style.objectPosition = 'center';
                
                // Add error handling for image loading
                img.onerror = function() {
                    console.warn('Failed to load featured post image:', img.src);
                    featured_post_image.textContent = getCategoryDisplayText(getPostCategory(postData));
                };
                
                featured_post_image.appendChild(img);
            } else {
                featured_post_image.textContent = getCategoryDisplayText(getPostCategory(postData));
            }
        } catch (error) {
            logError('featured post image creation', error, { postData, index });
            featured_post_image.textContent = getCategoryDisplayText(getPostCategory(postData));
        }
        
        const featured_post_content_wrapper = document.createElement('div');
        featured_post_content_wrapper.className = 'featured-post-content-wrapper';
        
        // Create content elements with error handling
        try {
            const featured_post_title = document.createElement('div');
            featured_post_title.className = 'featured-post-title';
            const featured_post_title_span = document.createElement('span');
            featured_post_title_span.className = "featured-post-title-span";
            featured_post_title_span.textContent = stripHtmlTags(postData.title) || 'Untitled Post';
            featured_post_title.appendChild(featured_post_title_span);
            
            // Tags section
            const featured_post_tags = document.createElement('div');
            featured_post_tags.className = 'featured-post-tags';
            
            if (postData.tags && typeof postData.tags === 'string') {
                const tagsList = postData.tags.split(', ').filter(tag => tag && tag.trim());
                tagsList.forEach(tagName => {
                    try {
                        const tag = document.createElement('div');
                        tag.className = 'tag-example post-tag';
                        tag.textContent = tagName.trim();
                        tag.style.cursor = 'pointer';
                        tag.addEventListener('click', function(e) {
                            try {
                                e.stopPropagation();
                                filterByTag(tagName.trim());
                            } catch (error) {
                                logError('tag click handler', error, { tagName });
                            }
                        });
                        featured_post_tags.appendChild(tag);
                    } catch (error) {
                        logError('featured post tag creation', error, { tagName });
                    }
                });
            }
            
            // Content section
            const featured_post_content = document.createElement('div');
            featured_post_content.className = 'featured-post-content';
            const featured_post_content_span = document.createElement('span');
            featured_post_content_span.className = "featured-post-content-span";
            featured_post_content_span.textContent = stripHtmlTags(postData.content) || '';
            featured_post_content.appendChild(featured_post_content_span);
            
            // Bottom section
            const featured_post_bottom = document.createElement('div');
            featured_post_bottom.className = 'featured-post-bottom';
            const featured_post_bottom_span = document.createElement('span');
            featured_post_bottom_span.className = "featured-post-bottom-span";
            featured_post_bottom_span.textContent = `${postData.author || 'Anonymous'} • ${postData.pub_date || ''}`;
            featured_post_bottom.appendChild(featured_post_bottom_span);
            
            // Assemble content wrapper
            featured_post_content_wrapper.appendChild(featured_post_title);
            featured_post_content_wrapper.appendChild(featured_post_tags);
            featured_post_content_wrapper.appendChild(featured_post_content);
            featured_post_content_wrapper.appendChild(featured_post_bottom);
            
        } catch (error) {
            logError('featured post content creation', error, { postData });
            // Create minimal fallback content
            const fallback = document.createElement('div');
            fallback.textContent = 'Error loading post content';
            featured_post_content_wrapper.appendChild(fallback);
        }
        
        // Assemble main wrapper
        featured_post_wrapper.appendChild(featured_post_image);
        featured_post_wrapper.appendChild(featured_post_content_wrapper);
        
        // Add to featured container
        featured.appendChild(featured_post_wrapper);
        
    } catch (error) {
        logError('createFeaturedPost', error, { postData, index });
        showErrorMessage('Error creating featured post');
    }
}

// Enhanced regular post creation with error handling
function createRegularPost(postData) {
    try {
        if (!postData) {
            throw new Error('Post data is required');
        }
        
        const post_wrapper = document.createElement('div');
        post_wrapper.className = 'post_wrapper';
        post_wrapper.style.cursor = 'pointer';
        
        // Add click handler with error handling
        post_wrapper.addEventListener("click", function(e) {
            try {
                if (e.target.classList.contains('post-tag')) return;
                if (postData.url) {
                    window.location.href = postData.url;
                }
            } catch (error) {
                logError('regular post click handler', error, { postData });
            }
        });
        
        // Create thumbnail or placeholder with error handling
        try {
            if (postData.thumbnail_small || postData.thumbnail || postData.image) {
                const thumbnail = document.createElement('div');
                thumbnail.className = 'post-thumbnail';
                const img = document.createElement('img');
                img.src = postData.thumbnail_small || postData.thumbnail || postData.image;
                img.alt = stripHtmlTags(postData.title) || 'Post thumbnail';
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                img.style.objectPosition = 'center';
                
                // Add error handling for image loading
                img.onerror = function() {
                    console.warn('Failed to load post thumbnail:', img.src);
                    thumbnail.innerHTML = '';
                    thumbnail.className = 'post-placeholder';
                    const category = getPostCategory(postData);
                    thumbnail.classList.add(category.toLowerCase());
                    thumbnail.textContent = getCategoryDisplayText(category);
                };
                
                thumbnail.appendChild(img);
                post_wrapper.appendChild(thumbnail);
            } else {
                const placeholder = document.createElement('div');
                placeholder.className = 'post-placeholder';
                const category = getPostCategory(postData);
                const displayText = getCategoryDisplayText(category);
                placeholder.classList.add(category.toLowerCase());
                placeholder.textContent = displayText;
                post_wrapper.appendChild(placeholder);
            }
        } catch (error) {
            logError('regular post thumbnail creation', error, { postData });
            // Fallback placeholder
            const placeholder = document.createElement('div');
            placeholder.className = 'post-placeholder post';
            placeholder.textContent = 'Post';
            post_wrapper.appendChild(placeholder);
        }
        
        const div_post = document.createElement('div');
        div_post.className = 'post';
        
        try {
            // Title
            const h2 = document.createElement('h2');
            h2.textContent = stripHtmlTags(postData.title) || 'Untitled Post';
            
            // Tags section
            const tags_section = document.createElement('div');
            tags_section.className = 'post-tags-section';
            
            if (postData.tags && typeof postData.tags === 'string') {
                const tagsList = postData.tags.split(', ').filter(tag => tag && tag.trim());
                tagsList.forEach(tagName => {
                    try {
                        const tag = document.createElement('div');
                        tag.className = 'tag-example post-tag';
                        tag.textContent = tagName.trim();
                        tag.style.cursor = 'pointer';
                        tag.addEventListener('click', function(e) {
                            try {
                                e.stopPropagation();
                                filterByTag(tagName.trim());
                            } catch (error) {
                                logError('regular post tag click', error, { tagName });
                            }
                        });
                        tags_section.appendChild(tag);
                    } catch (error) {
                        logError('regular post tag creation', error, { tagName });
                    }
                });
            }
            
            // Content
            const span_content = document.createElement('span');
            span_content.textContent = stripHtmlTags(postData.content) || '';
            
            // Bottom bar
            const blog_bottom_bar = document.createElement('div');
            blog_bottom_bar.className = 'blog_bottom_bar';
            
            const span_author = document.createElement('span');
            span_author.textContent = postData.author || 'Anonymous';
            
            const span_pub_date = document.createElement('span');
            span_pub_date.textContent = " " + (postData.pub_date || '') + " ";
            
            // Assemble the post
            div_post.appendChild(h2);
            div_post.appendChild(tags_section);
            div_post.appendChild(span_content);
            blog_bottom_bar.appendChild(span_author);
            blog_bottom_bar.appendChild(span_pub_date);
            post_wrapper.appendChild(div_post);
            post_wrapper.appendChild(blog_bottom_bar);
            
        } catch (error) {
            logError('regular post content creation', error, { postData });
            // Create minimal fallback
            const fallback = document.createElement('div');
            fallback.textContent = 'Error loading post';
            div_post.appendChild(fallback);
            post_wrapper.appendChild(div_post);
        }
        
        return post_wrapper;
        
    } catch (error) {
        logError('createRegularPost', error, { postData });
        // Return a minimal error post
        const errorPost = document.createElement('div');
        errorPost.className = 'post_wrapper error-post';
        errorPost.style.cssText = 'padding: 20px; text-align: center; color: #666;';
        errorPost.textContent = 'Error loading post';
        return errorPost;
    }
}

// Enhanced filter by tag function with error handling
function filterByTag(tagName) {
    try {
        if (!tagName || typeof tagName !== 'string') {
            console.warn('Invalid tag name provided to filterByTag');
            return;
        }
        
        console.log('Filtering by tag:', tagName);
        
        // Clear search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = tagName;
        }
        
        // Clear filter pills
        const filterPills = document.querySelectorAll('.pill');
        filterPills.forEach(p => p.classList.remove('active'));
        
        // Set up tag search
        currentSearchQuery = tagName;
        currentTag = tagName;
        isSearchMode = true;
        
        // Update UI
        document.body.classList.add('search-active');
        
        const sectionTitle = document.querySelector('.posts-section .section-title');
        if (sectionTitle) {
            sectionTitle.textContent = `Posts tagged "${tagName}"`;
        }
        
        // Clear content and load search results
        const postList = document.getElementById('post-list');
        if (postList) {
            postList.innerHTML = '<div class="loading">🔍 Searching by tag...</div>';
            loadSearchResults(tagName, 1);
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
    } catch (error) {
        logError('filterByTag', error, { tagName });
        showErrorMessage('Error filtering posts by tag');
    }
}

// Enhanced loadImages function with comprehensive error handling
async function loadImages() {
    try {
        console.log('loadImages called', { isLoading, page_num });
        
        if (isLoading) return;
        
        isLoading = true;
        
        let page_url = "?page=" + page_num;
        console.log('Fetching:', page_url);
        
        const response = await fetch(page_url, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (!data.has_next && page_num > 1) {
            console.log('No more pages available');
            isLoading = false;
            return;
        }
        
        // Handle first page - featured posts
        if (page_num === 1 && data.blog_posts && Array.isArray(data.blog_posts) && data.blog_posts.length > 0) {
            const featured = document.getElementById("featured");
            if (featured) {
                featured.innerHTML = '';
                
                // Create featured posts - ONLY take first 3 posts
                const featuredPosts = data.blog_posts.slice(0, 3);
                featuredPosts.forEach((post, index) => {
                    try {
                        createFeaturedPost(post, index);
                    } catch (error) {
                        logError('loadImages - creating featured post', error, { post, index });
                    }
                });
                
                // Add remaining posts to regular posts section
                if (data.blog_posts.length > 3) {
                    const post_list = document.getElementById("post-list");
                    if (post_list) {
                        const remainingPosts = data.blog_posts.slice(3);
                        remainingPosts.forEach(post => {
                            try {
                                const regularPost = createRegularPost(post);
                                post_list.appendChild(regularPost);
                            } catch (error) {
                                logError('loadImages - creating regular post', error, { post });
                            }
                        });
                        
                        addGhostCards();
                    }
                }
            }
        }
        // Handle regular posts for subsequent pages
        else if (page_num > 1 && data.blog_posts && Array.isArray(data.blog_posts) && data.blog_posts.length > 0) {
            const post_list = document.getElementById("post-list");
            if (post_list) {
                data.blog_posts.forEach(post => {
                    try {
                        const regularPost = createRegularPost(post);
                        post_list.appendChild(regularPost);
                    } catch (error) {
                        logError('loadImages - appending regular post', error, { post });
                    }
                });
                
                addGhostCards();
            }
        }
        
        page_num += 1;
        
    } catch (error) {
        logError('loadImages', error, { page_num });
        showErrorMessage('Error loading blog posts. Please try refreshing the page.');
    } finally {
        isLoading = false;
        
        // Check if we need to load more content automatically
        setTimeout(() => {
            try {
                checkIfMoreContentNeeded();
            } catch (error) {
                logError('loadImages - checkIfMoreContentNeeded', error);
            }
        }, 100);
    }
}

// Enhanced search initialization with error handling
document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeSearch();
    } catch (error) {
        logError('DOMContentLoaded - initializeSearch', error);
        showErrorMessage('Error initializing search functionality');
    }
});

// Enhanced search initialization
function initializeSearch() {
    try {
        const searchForm = document.getElementById('search-form');
        const searchInput = document.getElementById('search-input');
        const clearButton = document.getElementById('clear-search');
        const filterPills = document.querySelectorAll('.pill');
        
        const postList = document.getElementById('post-list');
        supportsAjax = !!postList;
        
        if (!supportsAjax) {
            console.warn('AJAX not supported - post list container not found');
            return;
        }
        
        // Search form handler
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                try {
                    e.preventDefault();
                    const query = searchInput ? searchInput.value.trim() : '';
                    performSearch(query);
                } catch (error) {
                    logError('search form submit', error);
                    showErrorMessage('Error performing search');
                }
            });
        }
        
        // Clear button handler
        if (clearButton) {
            clearButton.addEventListener('click', function() {
                try {
                    clearSearch();
                } catch (error) {
                    logError('clear search button', error);
                    showErrorMessage('Error clearing search');
                }
            });
        }
        
        // Filter pills handlers
        filterPills.forEach(pill => {
            try {
                pill.addEventListener('click', function() {
                    try {
                        filterPills.forEach(p => p.classList.remove('active'));
                        this.classList.add('active');
                        
                        const tagName = this.dataset.category || this.textContent.trim();
                        
                        if (!tagName || tagName === 'All') {
                            clearSearch();
                            return;
                        }
                        
                        filterByTag(tagName);
                    } catch (error) {
                        logError('filter pill click', error, { pill: this });
                        showErrorMessage('Error filtering posts');
                    }
                });
            } catch (error) {
                logError('adding filter pill listener', error, { pill });
            }
        });
        
        // Search input handler with debouncing
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                try {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {
                        try {
                            const query = this.value.trim();
                            if (query.length >= 2 || query.length === 0) {
                                performSearch(query);
                            }
                        } catch (error) {
                            logError('search input timeout', error);
                        }
                    }, 500);
                } catch (error) {
                    logError('search input handler', error);
                }
            });
        }
        
    } catch (error) {
        logError('initializeSearch', error);
        showErrorMessage('Error setting up search functionality');
    }
}

// Enhanced search performance with error handling
function performSearch(query) {
    try {
        currentSearchQuery = query || '';
        currentTag = currentSearchQuery;
        isSearchMode = currentSearchQuery.length > 0;
        
        const body = document.body;
        if (isSearchMode) {
            body.classList.add('search-active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            body.classList.remove('search-active');
            page_num = 1;
            const featured = document.getElementById("featured");
            const postList = document.getElementById('post-list');
            
            if (featured) featured.innerHTML = '';
            if (postList) postList.innerHTML = '';
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
            loadImages();
            return;
        }
        
        const sectionTitle = document.querySelector('.posts-section .section-title');
        if (sectionTitle) {
            sectionTitle.textContent = `Search Results for "${currentSearchQuery}"`;
        }
        
        const postList = document.getElementById('post-list');
        if (postList) {
            postList.innerHTML = '<div class="loading">🔍 Searching...</div>';
            loadSearchResults(currentSearchQuery, 1);
        }
        
    } catch (error) {
        logError('performSearch', error, { query });
        showErrorMessage('Error performing search');
    }
}

// Enhanced search results loading with error handling
function loadSearchResults(query, page) {
    try {
        if (typeof query !== 'string') {
            query = String(query || '');
        }
        
        if (!Number.isInteger(page) || page < 1) {
            page = 1;
        }
        
        let url = `/blog/search/?page=${page}`;
        if (query) {
            url += `&search=${encodeURIComponent(query)}`;
        }
        
        console.log('Loading search results:', { query, page, url });
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Search failed with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            try {
                console.log('Search results received:', data);
                
                if (page === 1) {
                    displaySearchResults(data.blog_posts || []);
                } else {
                    appendSearchResults(data.blog_posts || []);
                }
                
                window.hasNext = Boolean(data.has_next);
                window.currentPage = page;
                updateSearchStatus(data.total_results || 0, query);
                
                isLoading = false;
                
                setTimeout(() => {
                    try {
                        checkIfMoreContentNeeded();
                    } catch (error) {
                        logError('loadSearchResults - checkIfMoreContentNeeded', error);
                    }
                }, 100);
                
            } catch (error) {
                logError('loadSearchResults - processing response', error, { data });
                showSearchError();
                isLoading = false;
            }
        })
        .catch(error => {
            logError('loadSearchResults - fetch', error, { query, page, url });
            showSearchError();
            isLoading = false;
        });
        
    } catch (error) {
        logError('loadSearchResults', error, { query, page });
        showSearchError();
        isLoading = false;
    }
}

// Enhanced search results display with error handling
function displaySearchResults(posts) {
    try {
        const postList = document.getElementById('post-list');
        if (!postList) {
            throw new Error('Post list container not found');
        }
        
        postList.innerHTML = '';
        
        if (!Array.isArray(posts) || posts.length === 0) {
            postList.innerHTML = `
                <div class="no-results">
                    <h3>No posts found</h3>
                    <p>No results found. <a href="#" onclick="clearSearch()">Clear search</a> to see all posts.</p>
                </div>
            `;
            return;
        }
        
        posts.forEach(post => {
            try {
                const regularPost = createRegularPost(post);
                postList.appendChild(regularPost);
            } catch (error) {
                logError('displaySearchResults - creating post', error, { post });
            }
        });
        
        addGhostCards();
        
    } catch (error) {
        logError('displaySearchResults', error, { posts });
        showSearchError();
    }
}

// Enhanced search results appending with error handling
function appendSearchResults(posts) {
    try {
        const postList = document.getElementById('post-list');
        if (!postList) {
            throw new Error('Post list container not found');
        }
        
        if (!Array.isArray(posts)) {
            console.warn('Invalid posts data provided to appendSearchResults');
            return;
        }
        
        posts.forEach(post => {
            try {
                const regularPost = createRegularPost(post);
                postList.appendChild(regularPost);
            } catch (error) {
                logError('appendSearchResults - creating post', error, { post });
            }
        });
        
        addGhostCards();
        
    } catch (error) {
        logError('appendSearchResults', error, { posts });
    }
}

// Enhanced search status update with error handling (continued)
function updateSearchStatus(totalResults, query) {
   try {
       const searchStatus = document.getElementById('search-status');
       
       if (query && searchStatus) {
           const count = Number(totalResults) || 0;
           let statusText = `${count} result${count !== 1 ? 's' : ''}`;
           searchStatus.textContent = statusText;
           searchStatus.style.display = 'block';
           searchStatus.style.order = '1.5';
       } else if (searchStatus) {
           searchStatus.style.display = 'none';
       }
       
   } catch (error) {
       logError('updateSearchStatus', error, { totalResults, query });
   }
}

// Enhanced clear search with error handling
function clearSearch() {
   try {
       const searchInput = document.getElementById('search-input');
       const filterPills = document.querySelectorAll('.pill');
       const searchStatus = document.getElementById('search-status');
       
       if (searchInput) {
           searchInput.value = '';
       }
       
       if (searchStatus) {
           searchStatus.style.display = 'none';
       }
       
       filterPills.forEach(p => {
           try {
               p.classList.remove('active');
           } catch (error) {
               logError('clearSearch - removing active class', error, { pill: p });
           }
       });
       
       const allPill = document.querySelector('.pill[data-category=""]') || document.querySelector('.pill:first-child');
       if (allPill) {
           try {
               allPill.classList.add('active');
           } catch (error) {
               logError('clearSearch - adding active class to all pill', error);
           }
       }
       
       document.body.classList.remove('search-active');
       
       // Reset pagination state
       page_num = 1;
       currentSearchQuery = '';
       currentTag = '';
       isSearchMode = false;
       window.hasNext = true;
       window.currentPage = 1;
       
       // Clear and reload regular content
       const featured = document.getElementById("featured");
       const postList = document.getElementById('post-list');
       
       if (featured) featured.innerHTML = '';
       if (postList) postList.innerHTML = '';
       
       // Reset section title
       const sectionTitle = document.querySelector('.posts-section .section-title');
       if (sectionTitle) {
           sectionTitle.textContent = 'All Posts';
       }
       
       // Scroll to top
       window.scrollTo({ top: 0, behavior: 'smooth' });
       
       // Load regular content
       loadImages();
       
   } catch (error) {
       logError('clearSearch', error);
       showErrorMessage('Error clearing search');
   }
}

// Enhanced search error display
function showSearchError() {
   try {
       const postList = document.getElementById('post-list');
       if (postList) {
           postList.innerHTML = `
               <div class="search-error">
                   <h3>Search temporarily unavailable</h3>
                   <p>Please try again in a moment or <a href="#" onclick="clearSearch()">view all posts</a>.</p>
               </div>
           `;
       }
   } catch (error) {
       logError('showSearchError', error);
       console.error('Critical error: Cannot display search error message');
   }
}

// Enhanced scroll listener with error handling
window.addEventListener('scroll', function() {
   try {
       // Debounce scroll events
       if (window.scrollTimeout) {
           return;
       }
       
       window.scrollTimeout = setTimeout(() => {
           try {
               window.scrollTimeout = null;
               
               // Check if we're near the bottom of the page
               if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
                   if (isSearchMode) {
                       // Load more search results
                       if (window.hasNext && !isLoading) {
                           isLoading = true;
                           loadSearchResults(currentSearchQuery, window.currentPage + 1);
                       }
                   } else {
                       // Load more regular content
                       if (!isLoading) {
                           loadImages();
                       }
                   }
               }
           } catch (error) {
               logError('scroll handler timeout', error);
           }
       }, 100);
       
   } catch (error) {
       logError('scroll handler', error);
   }
});

// Enhanced content check with error handling
function checkIfMoreContentNeeded() {
   try {
       // Wait for scroll animation to complete
       setTimeout(() => {
           try {
               const documentHeight = document.documentElement.scrollHeight;
               const windowHeight = window.innerHeight;
               const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
               
               console.log('Checking if more content needed:', {
                   documentHeight,
                   windowHeight,
                   scrollTop,
                   hasScrollbar: documentHeight > windowHeight,
                   hasNext: window.hasNext,
                   isLoading
               });
               
               // If no scrollbar and we have more content, load it automatically
               if (documentHeight <= windowHeight + 100 && window.hasNext && !isLoading) {
                   console.log('No scrollbar detected, auto-loading more content...');
                   
                   if (isSearchMode) {
                       isLoading = true;
                       loadSearchResults(currentSearchQuery, window.currentPage + 1);
                   } else {
                       loadImages();
                   }
               }
           } catch (error) {
               logError('checkIfMoreContentNeeded - inner timeout', error);
           }
       }, 500);
       
   } catch (error) {
       logError('checkIfMoreContentNeeded', error);
   }
}

// Enhanced window resize listener with error handling
window.addEventListener('resize', function() {
   try {
       // Debounce resize events
       if (window.resizeTimeout) {
           clearTimeout(window.resizeTimeout);
       }
       
       window.resizeTimeout = setTimeout(() => {
           try {
               addGhostCards();
           } catch (error) {
               logError('resize handler - addGhostCards', error);
           }
       }, 250);
       
   } catch (error) {
       logError('resize handler', error);
   }
});

// Error boundary for unhandled errors
window.addEventListener('error', function(event) {
   logError('Unhandled error', event.error, {
       filename: event.filename,
       lineno: event.lineno,
       colno: event.colno,
       message: event.message
   });
});

// Error boundary for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
   logError('Unhandled promise rejection', event.reason);
   event.preventDefault(); // Prevent default browser error handling
});

// Utility function to safely get element by ID
function safeGetElementById(id) {
   try {
       return document.getElementById(id);
   } catch (error) {
       logError('safeGetElementById', error, { id });
       return null;
   }
}

// Utility function to safely add event listener
function safeAddEventListener(element, event, handler) {
   try {
       if (element && typeof element.addEventListener === 'function') {
           element.addEventListener(event, handler);
           return true;
       }
       return false;
   } catch (error) {
       logError('safeAddEventListener', error, { element, event });
       return false;
   }
}

// Initialize error handling
try {
   console.log('Blog application initialized with enhanced error handling');
} catch (error) {
   console.error('Failed to initialize blog application:', error);
}