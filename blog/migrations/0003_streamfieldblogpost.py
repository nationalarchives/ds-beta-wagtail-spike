# Generated by Django 3.1.3 on 2020-11-13 11:53

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('blog', '0002_auto_20201113_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamFieldBlogPost',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('content', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('premium_paragraph', wagtail.core.blocks.RichTextBlock()), ('image_viewer', wagtail.embeds.blocks.EmbedBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('embed', wagtail.embeds.blocks.EmbedBlock())])),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
