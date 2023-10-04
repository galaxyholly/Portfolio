from django.shortcuts import render
from blog.models import BlogPost
from django.views import generic

# Create your views here.
class IndexView(generic.ListView):
    template_name = "main/home.html"
    context_object_name = "latest_post_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return BlogPost.objects.order_by("-pub_date")[:2]