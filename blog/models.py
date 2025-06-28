from django.db import models
from django.contrib.auth.models import User
import markdown
import bleach
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)  # Slug field for URL
    content = models.TextField()  # Raw Markdown
    content_html = models.TextField(blank=True)  # Pre-rendered HTML (optional)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Convert Markdown to HTML on save
        md = markdown.Markdown(extensions=["extra", "codehilite", "toc"])
        html = md.convert(self.content)
        allowed_tags = [
            "p",
            "h1",
            "h2",
            "h3",
            "pre",
            "code",
            "a",
            "strong",
            "em",
            "ul",
            "ol",
            "li",
        ]
        self.content_html = bleach.clean(
            html, tags=allowed_tags, attributes={"a": ["href"]}
        )
        # Generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        # Ensure the slug is unique
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Note(models.Model):
    """
    Represents a note document containing multiple hierarchical rows.
    """

    title = models.CharField(max_length=255, default="Untitled Note")
    title_slug = models.SlugField(unique=True, blank=True)  # Slug field for URL
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["owner", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} (Owner: {self.owner.username})"


class NoteRow(MPTTModel):
    """
    Represents a single row in a note with hierarchical structure.
    """

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="rows")
    task = models.CharField(max_length=255, blank=True, default="")
    link = models.URLField(blank=True, default="")
    content = models.TextField(blank=True, default="")
    indent_level = models.PositiveIntegerField(
        default=0
    )  # Tracks indentation (0, 1, 2, ...)
    is_collapsed = models.BooleanField(default=False)  # Tracks collapsed state
    order = models.PositiveIntegerField(default=0)  # For same-level ordering
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        indexes = [
            models.Index(fields=["note", "order"]),
            models.Index(fields=["note", "indent_level"]),
        ]
        ordering = ["note", "order"]

    class MPTTMeta:
        order_insertion_by = ["order"]

    def __str__(self):
        return f"Row {self.get_line_number()}: {self.task[:30]}"

    def get_line_number(self):
        """
        Generates hierarchical line number (e.g., '1-1-1') based on tree position.
        """
        ancestors = self.get_ancestors(include_self=True).exclude(id=self.note.id)
        return "-".join(str(a.get_sibling_order() + 1) for a in ancestors)

    def get_sibling_order(self):
        """
        Returns the 0-based order among siblings at the same level.
        """
        siblings = NoteRow.objects.filter(
            note=self.note, parent=self.parent, indent_level=self.indent_level
        ).order_by("order")
        return list(siblings).index(self)

    def move_block(self, direction="up"):
        """
        Moves the row and its subtree up or down among same-level siblings.
        """
        siblings = NoteRow.objects.filter(
            note=self.note, parent=self.parent, indent_level=self.indent_level
        ).order_by("order")
        sibling_list = list(siblings)
        current_index = sibling_list.index(self)

        if direction == "up" and current_index > 0:
            target = sibling_list[current_index - 1]
            self.order, target.order = target.order, self.order
            self.save()
            target.save()
        elif direction == "down" and current_index < len(sibling_list) - 1:
            target = sibling_list[current_index + 1]
            self.order, target.order = target.order, self.order
            self.save()
            target.save()
