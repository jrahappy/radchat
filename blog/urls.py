from django.urls import path
from . import views

app_name = "blog"
urlpatterns = [
    path("", views.posts_list, name="posts_list"),
    path("post/create/", views.post_create, name="post_create"),  # Add this line
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("plan_editor/", views.plan_editor, name="plan_editor"),
    path("notes/", views.notes_list, name="notes_list"),
    path("note/<slug:slug>/", views.note_detail, name="note_detail"),
    # path("note/view/<slug:slug>/", views.note_view, name="note_view"),
    path("note/<int:note_id>/", views.note_view, name="note_view"),
    path("note/<int:note_id>/save/", views.save_rows, name="save_rows"),
    path(
        "note/<int:note_id>/row/<int:row_id>/collapse/",
        views.toggle_collapse,
        name="toggle_collapse",
    ),
    path("note/<int:note_id>/row/<int:row_id>/move/", views.move_row, name="move_row"),
    path("note/<int:note_id>/add_row/", views.add_row, name="add_row"),
    path(
        "note/<int:note_id>/row/<int:row_id>/indent/",
        views.update_indent,
        name="update_indent",
    ),
]
