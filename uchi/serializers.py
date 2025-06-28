# serializers.py
from drf_chunked_upload.serializers import ChunkedUploadSerializer
from .models import MyChunkedUpload


class MyChunkedUploadSerializer(ChunkedUploadSerializer):
    class Meta:
        model = MyChunkedUpload
        fields = ("id", "file", "status", "offset", "completed_at")
