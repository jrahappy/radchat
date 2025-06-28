from drf_chunked_upload.views import ChunkedUploadView
from rest_framework.response import Response
from .models import MyChunkedUpload
from .serializers import MyChunkedUploadSerializer
from rest_framework.parsers import FileUploadParser


class MyChunkedUploadView(ChunkedUploadView):
    parser_classes = [FileUploadParser]
    model = MyChunkedUpload
    serializer_class = MyChunkedUploadSerializer

    def on_completion(self, chunked_upload, request):
        # Process the completed file (e.g., save to storage)
        file = chunked_upload.file
        # Example: Save or move file
        return Response({"message": "Upload complete", "file_id": chunked_upload.id})
