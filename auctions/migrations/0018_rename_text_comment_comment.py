# Generated by Django 4.1.4 on 2023-01-10 15:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_comment_timestamp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='text',
            new_name='comment',
        ),
    ]
