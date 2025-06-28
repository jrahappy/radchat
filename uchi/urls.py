# urls.py
from django.urls import path
from .views import MyChunkedUploadView

app_name = "uchi"
urlpatterns = [
    path("upload/", MyChunkedUploadView.as_view(), name="chunked-upload"),
]
