from django.shortcuts import render, redirect
from .models import BlogPost
from .forms import BlogPostForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .forms import BlogPostForm, BlogPostCommentForm
from django.contrib.auth.decorators import login_required


@login_required
def post_blog(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return HttpResponseRedirect(reverse("blog:index"))
    else:
        form = BlogPostForm()
    return render(request, 'blog/post_blog.html', {'form': form}) # Something can be added here to make text display to the user after an error?


class IndexView(generic.ListView):
    template_name = "blog/index.html"
    context_object_name = "latest_post_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return BlogPost.objects.order_by("-pub_date")[:5]
    
def add_comment(request, blogpost_id):
    if request.method == "POST":
        form = BlogPostCommentForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return HttpResponseRedirect("blog:post") # Do this like polls does

def post_view(request, blogpost_id):
    template_name = "blog/entry.html"
    context_object_name = "entry_and_comments"

    