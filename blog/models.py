from django.db import models
from django.contrib.auth.models import User
import markdown
import bleach
from django.utils.text import slugify


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
