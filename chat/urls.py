from django.urls import include, path
from . import views

app_name = "chat"
urlpatterns = [
    path("", views.index, name="index"),
    path("room/", views.room, name="room"),
]
