from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Note, NoteRow
from .forms import PostForm, NoteForm, NoteRowForm
from django.http import HttpResponseRedirect
import json


def notes_list(request):
    notes = Note.objects.all()
    return render(request, "blog/notes_list.html", {"notes": notes})


def note_detail(request, slug):
    note = get_object_or_404(Note, title_slug=slug)
    rows = NoteRow.objects.filter(note=note).order_by("tree_id", "lft")
    return render(request, "blog/note_detail.html", {"note": note, "rows": rows})


def note_row_1st_create(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == "POST":
        form = NoteRowForm(request.POST)
        if form.is_valid():
            texts = form.cleaned_data["content"]
            for text in texts.splitlines():
                if text.strip():
                    row = form.save(commit=False)
                    row.note = note
                    row.content = text.strip()
                    row.save()
                    return redirect("blog:note_detail", note_id=note.id)
    else:
        form = NoteRowForm()
    return render(request, "blog/note_row_form.html", {"form": form, "note": note})


@login_required
def note_view(request, note_id):
    """
    Render the note-taking UI and provide initial row data.
    """
    note = get_object_or_404(Note, id=note_id, owner=request.user)
    rows = note.rows.order_by("order")
    row_data = [
        {
            "id": row.id,
            "content": row.content,
            "indent_level": row.indent_level,
            "is_collapsed": row.is_collapsed,
            "line_number": row.get_line_number(),
        }
        for row in rows
    ]
    return render(
        request, "blog/note.html", {"note": note, "row_data": json.dumps(row_data)}
    )


@login_required
def save_rows(request, note_id):
    """
    Save textarea rows to the NoteRow table via AJAX.
    """
    if request.method == "POST" and request.is_ajax():
        note = get_object_or_404(Note, id=note_id, owner=request.user)
        rows_data = json.loads(
            request.POST.get("rows_data", "[]")
        )  # Array of row objects
        existing_rows = list(note.rows.order_by("order"))
        parent_stack = {0: None}
        indent_size = 4
        updated_rows = []

        for i, row_data in enumerate(rows_data):
            indent_level = row_data["indent_level"]
            content = row_data["content"]
            parent = parent_stack.get(indent_level - 1) if indent_level > 0 else None

            if i < len(existing_rows):
                # Update existing row
                row = existing_rows[i]
                row.content = content
                row.indent_level = indent_level
                row.order = i
                row.parent = parent
                row.save()
            else:
                # Create new row
                row = NoteRow.objects.create(
                    note=note,
                    content=content,
                    indent_level=indent_level,
                    order=i,
                    parent=parent,
                )

            parent_stack[indent_level] = row
            updated_rows.append(
                {
                    "id": row.id,
                    "content": row.content,
                    "indent_level": row.indent_level,
                    "is_collapsed": row.is_collapsed,
                    "line_number": row.get_line_number(),
                }
            )

        # Delete excess rows
        for row in existing_rows[len(rows_data) :]:
            row.delete()

        return JsonResponse({"status": "success", "row_data": updated_rows})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def toggle_collapse(request, note_id, row_id):
    """
    Toggle the collapsed state of a row via AJAX.
    """
    if request.method == "POST" and request.is_ajax():
        note = get_object_or_404(Note, id=note_id, owner=request.user)
        row = get_object_or_404(NoteRow, id=row_id, note=note)
        row.is_collapsed = not row.is_collapsed
        row.save()
        return JsonResponse(
            {
                "status": "success",
                "is_collapsed": row.is_collapsed,
                "row_data": [
                    {
                        "id": r.id,
                        "content": r.content,
                        "indent_level": r.indent_level,
                        "is_collapsed": r.is_collapsed,
                        "line_number": r.get_line_number(),
                    }
                    for r in note.rows.order_by("order")
                ],
            }
        )
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def move_row(request, note_id, row_id):
    """
    Move a row up or down via AJAX.
    """
    if request.method == "POST" and request.is_ajax():
        note = get_object_or_404(Note, id=note_id, owner=request.user)
        row = get_object_or_404(NoteRow, id=row_id, note=note)
        direction = request.POST.get("direction", "up")
        row.move_block(direction)
        return JsonResponse(
            {
                "status": "success",
                "row_data": [
                    {
                        "id": r.id,
                        "content": r.content,
                        "indent_level": r.indent_level,
                        "is_collapsed": r.is_collapsed,
                        "line_number": r.get_line_number(),
                    }
                    for r in note.rows.order_by("order")
                ],
            }
        )
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def add_row(request, note_id):
    """
    Add a new row after the current row via AJAX (Enter key).
    """
    if request.method == "POST" and request.is_ajax():
        note = get_object_or_404(Note, id=note_id, owner=request.user)
        row_id = request.POST.get("row_id")
        cursor_line = int(request.POST.get("cursor_line", 0))
        row = get_object_or_404(NoteRow, id=row_id, note=note)
        new_row = NoteRow.objects.create(
            note=note,
            content="",
            indent_level=row.indent_level,
            order=cursor_line + 1,
            parent=row.parent,
        )
        for subsequent_row in note.rows.filter(order__gte=cursor_line + 1).exclude(
            id=new_row.id
        ):
            subsequent_row.order += 1
            subsequent_row.save()
        return JsonResponse(
            {
                "status": "success",
                "new_row_id": new_row.id,
                "row_data": [
                    {
                        "id": r.id,
                        "content": r.content,
                        "indent_level": r.indent_level,
                        "is_collapsed": r.is_collapsed,
                        "line_number": r.get_line_number(),
                    }
                    for r in note.rows.order_by("order")
                ],
            }
        )
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def update_indent(request, note_id, row_id):
    """
    Update indentation level for a row via AJAX (Tab/Shift+Tab).
    """
    if request.method == "POST" and request.is_ajax():
        note = get_object_or_404(Note, id=note_id, owner=request.user)
        row = get_object_or_404(NoteRow, id=row_id, note=note)
        direction = request.POST.get("direction", "increase")
        if direction == "increase":
            row.indent_level += 1
        else:
            row.indent_level = max(0, row.indent_level - 1)
        row.save()
        return JsonResponse(
            {
                "status": "success",
                "indent_level": row.indent_level,
                "row_data": [
                    {
                        "id": r.id,
                        "content": r.content,
                        "indent_level": r.indent_level,
                        "is_collapsed": r.is_collapsed,
                        "line_number": r.get_line_number(),
                    }
                    for r in note.rows.order_by("order")
                ],
            }
        )
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def plan_editor(request):
    if request.method == "POST":
        # Handle form submission here
        print("Form submitted")
        return HttpResponse
    else:
        # Render the initial form
        print("Rendering form")
        return render(request, "blog/plan_editor.html")
    return render(request, "blog/plan_editor.html")


def posts_list(request):
    posts = Post.objects.all()
    return render(request, "blog/posts_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "blog/post_detail.html", {"post": post})


def post_create(request):
    print("Creating a new post")
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog:post_detail", slug=post.slug)
        else:
            print(form.errors)
    else:
        form = PostForm()
    return render(request, "blog/post_form.html", {"form": form})


def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, "blog/post_form.html", {"form": form})


def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        post.delete()
        return redirect("blog:posts_list")
    return render(request, "blog/post_confirm_delete.html", {"post": post})
