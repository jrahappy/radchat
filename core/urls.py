from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("chat/", include("chat.urls")),
    path("blog/", include("blog.urls")),
    path("uchi/", include("uchi.urls")),
]
