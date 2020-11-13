from django.db import models
from wagtail.search import index
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.api import APIField
# Create your models here.

class BlogIndexPage(Page):
    pass

class BlogPost(Page):
    date = models.DateField("Post date")
    summary = models.CharField(max_length=140)
    body = RichTextField(blank=True)

    api_fields = [
        APIField("summary")
    ]

    search_fields = Page.search_fields + [
        index.SearchField('summary'),
        index.SearchField('body')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('summary'),
        FieldPanel('body', classname="container")

    ]

class StreamFieldBlogPost(Page):

    content = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('premium_paragraph', blocks.RichTextBlock()),
        ('discovery_url', blocks.TextBlock()),
        ('image', ImageChooserBlock()),
        ('youtube_video', EmbedBlock())])

    api_fields = [
        APIField("content")
    ]

    content_panels = Page.content_panels + [StreamFieldPanel('content')]