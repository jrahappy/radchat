from django.contrib import admin
from .models import Post, Note, NoteRow

admin.site.register(Post)
admin.site.register(Note)
admin.site.register(NoteRow)
