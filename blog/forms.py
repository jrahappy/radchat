from django.contrib.auth.models import User
from django import forms
from .models import Post, Note, NoteRow


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "slug", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10, "cols": 80}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["slug"].widget.attrs.update({"class": "form-control"})
        self.fields["content"].widget.attrs.update({"class": "form-control"})


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})


class NoteRowForm(forms.ModelForm):
    class Meta:
        model = NoteRow
        fields = [
            "task",
            "link",
            "content",
            "indent_level",
            "is_collapsed",
            "order",
            "parent",
        ]
        widgets = {
            "task": forms.TextInput(),
            "link": forms.TextInput(),
            "content": forms.Textarea(attrs={"rows": 2, "cols": 80}),
            "parent": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs.update({"class": "form-control"})
        self.fields["parent"].widget.attrs.update({"class": "form-control"})
