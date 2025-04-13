from django.urls import path
from . import views

app_name = "blog"
urlpatterns = [
    path("", views.posts_list, name="posts_list"),
    path("post/create/", views.post_create, name="post_create"),  # Add this line
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
]
