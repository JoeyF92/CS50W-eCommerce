# Generated by Django 4.1.4 on 2023-01-10 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_rename_listing_id_bid_listing_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='description',
            new_name='text',
        ),
    ]
