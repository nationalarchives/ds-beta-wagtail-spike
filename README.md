# DS Beta Wagtail CMS Example

This contains a spike into wagtail cms. Cloning the repo and reading through the steps taken to get to this stage is probably the best first step. Then you could try and implement the headless CMS yourself.

# Running this project

You will need python on your machine.

1. Clone this project and `cd` into it.
2. Run `python -m venv venv` to create a virtual environment. Run `source venv/bin/activate` to active the venv (or `source venv/Scripts/activate` in Windows.)
3. Run `pip install -r requirements.txt` to install wagtail
4. Run `./manage.py migrate` to setup the local database
5. Run `./manage.py createsuperuser` to create an admin account for the dashboard
6. Run `./manage.py runserver` to start the server.
7. Visit http://localhost:8000 to view the homepage (note `http://127.0.0.1:8000` doesn't seem to work)
8. Visit http://localhost:8000/admin and login with your admin account. 
9. Visit http://localhost:8000/admin/sites/ and add `localhost:8000` as a site. Once that is done, click on the default `localhost` site and delete it. (This is done to prevent the API giving us links with the wrong port on them)
10. We now need to create some posts to make the API more useful. Wagtail only ships with a homepage, so I have created a blog app in the CMS, which we will use.
11. To create a blog homepage: click Pages on the left of the Admin panel. Then click "Home". On this page, click "Add a child page", and create a "Blog index page". Give it any title you want. In the promote tab set the Slug to `blog`. Click the arrow next to "Save as draft" and hit publish
12. To create a generic blog post, click Pages on the left of the Admin panel. Then click "Home". Hover over your Blog Index Page and click "Add child page". Select "Blog post". Give it any content you want and publish it.
13. To create a "Streamfield" (more dynamic) post, repeat the above step but select "Stream field blog post" instead of "Blog post" when adding a child page.
14. See your posts in the API at http://localhost:8000/api

# Explaining how wagtail works

I used [this series](https://www.youtube.com/watch?v=plggtgoQjcs) and [the 3 API videos in this series](https://www.youtube.com/playlist?list=PLMQHMcNi6ocsS8Bfnuy_IDgJ4bHRRrvub) to understand everything I've written below, incase you don't like reading!

(Note: in the code snippets below I haven't included all the imports for each python file, so look in the source code for these.)

## Creating the python project

1. Create a Python virtual environment
2. Activate the virtual environment
3. Install `wagtail` with pip
4. run `wagtail start [project_name]` to create a project
5. `cd` into the project and run `./manage.py migrate` to run migrations
6. run `./manage.py createsuperuser` to create an admin
7. run `./manage.py runserver` to start the CMS server
8. Visit http://localhost:8000 (note `http://127.0.0.1:8000` doesn't seem to work)

## Initial CMS setup

Initially, a few routes are pre-created. These are

- Admin panel for the CMS (for editors/setting things up) at http://localhost:8000/admin
- Admin panel for django (for backend devs) at http://localhost:8000/django-admin
- To read the docs, at http://localhost:8000/documents/
- To search the site, at http://localhost:8000/search/

By default a "Home" page is setup. This is accessible in the admin panel under the pages section on the left.

## Creating a blog section in our CMS

### Code setup

In wagtail, content is ordered in a heirarchical nature. Therefore, all our content will descend from the parent page, called home. You can then have apps which descend from the home page.

Think of an "app" like a WordPress child theme - it has it's own code to define what editors can input on the UI, and defines how we output this content as HTML. We could have a base HTML layout in our home app which every app could inherit.

Each app has a model, which defines classes. These classes are post types. In these classes, you define what fields the editors can enter information into. You also define which fields are accessible by the API, and which fields are indexed in the search. For example, in a blog you would have:

A `BlogIndexPage` class which lists the blog pages, and underneath that you would have `BlogPost` which displays the blog post. Our `BlogIndexPage` could have two fields: Title and Description. Our `BlogPost` class could have a date, summary, body, and related documents field. You would then reuse the `BlogPost` class for each blog post.

To create a blog example, in this repo we have created a `blog` parent app, by running `./manage.py startapp blog` - this creates a `blog` folder in the root folder, with an empty `models.py` file.

In `models.py`, we define a BlogIndexPage, which inherits from the default Page class:

`class BlogHomePage(Page):
    pass`

Although it is empty, it inherits some fields from Wagtail. It inherits a default "Title" attribute which editors can input into, and that developers would use in the HTML.

We then define our own BlogPost class, where we add our own additional fields. We also add the fields we want to add to the website's search index, and what fields we want displayed to the editors (content_panels). Therefore we can define fields that the editors can't see but would be useful for developers etc.

```python 
from django.db import models
from wagtail.search import index
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel

class BlogPost(Page):
    date = models.DateField("Post date")
    summary = models.CharField(max_length=140)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('summary'),
        index.SearchField('body')
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('summary'),
        FieldPanel('body', classname="container")

    ]
```

We then add this blog application to `base.py` in `ds_beta_wagtail_example/settings/base.py` so that Wagtail can utilise it.

```python
INSTALLED_APPS = [
    'home',
    'search',
    'blog',
]
```

We then make migrations to allow updating of the database. This is achieved by running `./manage.py makemigrations` in the main `ds_beta_wagtail_example` wagtail folder. Then, we migrate the database with `./manage.py migrate`

### Editor's setup

Now, in the Wagtail admin panel, editors can click "Add child page" under the "Home" section. They are then presented with the types of pages they can create.

[!image](images/create-page.png)

They can then create a BlogIndexPage. We can then see the one field that `BlogIndexPage` inherited, title.

[!image](images/blog-index.png)

In the promote section, we are given some SEO settings. This is important to give us the url of the published page. In this case we want `localhost:8000/blog`

[!image](images/promote.png)

You can also schedule a post to go live and have it expire.

[!image](images/expire.png)

We then create `BlogPost` instances which are children of our `BlogIndexPage.` You can see the fields we defined are available to editors:

[!image](images/blog-post.png)

### Displaying our content with HTML templates 

Currently, we will get a 500 error if we published our posts. We have created pages, but not defined how they will be displayed as HTML. Therefore we need to create some templates (aka views).

If you try and view a published page and view the error, you can see we need to create a `blog/templates/blog_post.html` view. We also need a `blog/templates/blog_index_page.html` file for our blog homepage.

By default, there is a `base.html` template in the `home` app with some predefined HTML. We use a templating syntax, very similar to Flask's Jinja2 to inherit from this. Our fields that we defined in the model, and that the editors have now populated are available in the `page` object. This is our `blog/templates/blog_post.html`:

```html
{% extends "base.html" %}

{% load wagtailcore_tags %}

{% block body_class}template-blogpage{% endblock %}

{% block content %}
    <h1>{{page.title}}</h1>
    <p class="meta">{{ page.date }}</p>
    <p class="short-desc">{{page.short_description}}</p>

    {{page.body|richtext}

    <p><a href="{{page.get_parent.url}}">Go back</a></p>
{% endblock %}
```
We have used a for loop to display each blog post on our `blog_index_page.html` page:

```html
{% extends "base.html" %}

{% load wagtailcore_tags %}

{% block body_class %}template-blogindexpage{% endblock %}

{% block content %}
    <h1>{{ page.title }}</h1>
    {% for post in page.get_children %}
        <h2><a href="{% pageurl post%}">{{post.title}}</a></h2>
        <p>{{post.specific.summary}}</p>
    {% endfor %}
{% endblock %}
```

And a `slug-url` to easily link to the blog from the default homepage in `home/templates/home/welcome_page.html`: 
```
<a href="{% slugurl 'blog' %}">
{% trans "Blog" %}
</a>
```

### Making our content more dynamic with Streamfield

Streamfield allows us to structure our content so that we can control it.

Instead of defining one big "body" RichTextField and inserting HTML into it, we can breakdown our content into blocks. This is similar to "metaboxes" in our old WordPress CMS, but it is a lot easier to use.

These blocks can then be displayed based on parameters (such as pay-restricted news sites), or accessed via an api.

Streamfield content is defined in a similar way to traditional content:

```python
from django.db import models
from wagtail.search import index
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock

class StreamFieldBlogPost(Page):
    content = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('premium_paragraph', blocks.RichTextBlock()),
        ('discovery_url', blocks.TextBlock()),
        ('image', ImageChooserBlock()),
        ('youtube_video', EmbedBlock())])
    content_panels = Page.content_panels + [StreamFieldPanel('content')]
```

After migrating your database again, you can then access this Streamfield page in the editor:

[!image](images/streamfield.png)

We can create as many content blocks as we want. They will be served in the order they are displayed. Then we have defined our template `blog/templates/blog/stream_field_blog_post.html` as:

```
{% extends "base.html" %}

{% load wagtailcore_tags %}

{% block content %}
    <h1>{{page.title}}</h1>
    {% for block in page.content %}
        <section class="block-{{block.block_type}}">
            {% include_block block %}
        </section>
    {% endfor %}
{% endblock %}
```
This simply loops over each block and renders it in a `<section>` tag, with a class name relevant to its block name.

## Using the API - Headless CMS

For beta, it is likely that we will use the API to access content entered into wagtail. Therefore, we will need to enable the API. To do this we add `'wagtail.api.v2'` to the `INSTALLED_APPS` array in `ds_beta_wagtail_example/base.py`. We can also install `rest_framework` for an API GUI.


We then create an `api.py` file in `ds_beta_wagtail_example`. We import four libraries:
```
PagesAPIViewSet - this is for accessing pages
ImagesAPIViewSet - this is for accessing images
DocumentsAPIViewSet - this is for accessing documents (PDFs, Word docs)
WagtailAPIRouter - this is for routing
```

We can then define the api, and register it. In `api.py`:

```python
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter

api_router = WagtailAPIRouter('wagtail')
api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)
```

Then, in `urls.py` of `ds_beta_wagtail_example`, we import our api file - `from .api import api_router` and then register it in the `url_patterns` array:
```python
    path('api/v2/', api_router.urls)
```

You can now view the API at:
- http://127.0.0.1:8000/api/v2/pages/
- http://127.0.0.1:8000/api/v2/images/
- http://127.0.0.1:8000/api/v2/documents/

[!image](images/api.png)

This is the Page API and it's displaying all our pages. We can expand a page by clicking its `detail_url` link, e.g. `http://localhost:8000/api/v2/pages/6/` which gives us a bit more information. But it doesn't give us the content blocks yet.

### Grabbing content from the API

To access page fields, such as our `summary` field in our regular blog post, we need to edit our page model.

In our blog `models.py`, we'll import APIField: `from wagtail.api import APIField` and then define what content we want from each Page type exposed to the API. In this case, we want to expose the `summary` field of BlogPost to our API:


```python
from django.db import models
from wagtail.search import index
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.api import APIField
class BlogPost(Page):
    date = models.DateField("Post date")
    summary = models.CharField(max_length=140)
    body = RichTextField(blank=True)

    api_fields = [
        APIField("summary")
    ]
```
and now we can access the summary for each `BlogPost` in the API.:

[!image](images/summary.png)

Note by default wagtail thinks our website is setup at localhost:80 - therefore links in the JSON will be incorrect. You need to go into `http://localhost:8000/admin/sites/`, add `localhost:8000` as a site, and delete `localhost:80` to fix the API.

With the `&fields=` key we can modify what is returned. We can remove individual fields with `-`. We can show all fields with `*`. To remove all fields we can use `_`. We can then specify fields to show. For example This:
`http://localhost:8000/api/v2/pages/5/?fields=_,summary` returns the summary only:

```json
{
    "summary": "Resources for the 100 year anniversary of the First World War"
}
```

This: `http://localhost:8000/api/v2/pages/5/?fields=-summary` would return everything except for the summary.

 **Best practice in Wagtail is to only return fields we need to reduce database queries.**

For our streamfield post, we can expose all the APIFields in the model as well:

```python
from django.db import models
from wagtail.search import index
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.api import APIField
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
```

and now our API returns this `content` field for our Streamfield posts:

```
    "title": "Felix Ruddick",
    "content": [
        {
            "type": "paragraph",
            "value": "<p>Felix Ruddick has been commonly used as a test record by Digital Services when working on our website.</p>",
            "id": "2081475f-5c77-49c7-802f-3db15062a525"
        },
        {
            "type": "discovery_url",
            "value": "https://discovery.nationalarchives.gov.uk/details/r/0125874efb9c41f78f1cfdbdb1544e08",
            "id": "e8d2d783-e1f0-4b1d-9a19-4120f32c2312"
        }
    ]
```

We can then use this data in any way we want.

When listing content we can also filter for specific types of content. If we only want our StreamFieldBlogPosts we can use `http://localhost:8000/api/v2/pages/?type=blog.StreamFieldBlogPost`. This works with inheritance, so if we create another class which inherits StreamFieldBlogPost, it will appear in this query.

Pagination is also available in the api. `http://localhost:8000/api/v2/pages/?limit=2` will give us just two posts per page. We can offset this with the `offset` key: `http://localhost:8000/api/v2/pages/?limit=2&offset=2` to get the next two posts.

We can order by certain fields as well. By default the order is ID. To order by title: `http://localhost:8000/api/v2/pages/?order=title`. To reverse it prepend it with a `-`: `http://localhost:8000/api/v2/pages/?order=-title`

We can even order by random with `http://localhost:8000/api/v2/pages/?order=random`. This is expensive on the database though.

You can get all posts under a certain url by filtering by slug:

`http://localhost:8000/api/v2/pages/?slug=blog` - this would return all posts under `/blog`.

We can get  children of a page with:

`http://localhost:8000/api/v2/pages/?child_of=4`

We can get children and those pages' children of a page with:
`http://localhost:8000/api/v2/pages/?descendant_of=4`

We can search all searchable fields (as defined by us in Python) with:

`http://localhost:8000/api/v2/pages/?search=hello`

We can also find a page by its frontend Wagtail URL:

`http://localhost:8000/api/v2/pages/find/?html_path=/blog` -> redirects to `http://localhost:8000/api/v2/pages/4/`




# ds-beta-wagtail-spike
