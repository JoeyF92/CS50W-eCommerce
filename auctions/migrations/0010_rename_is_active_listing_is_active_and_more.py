# Generated by Django 4.1.4 on 2022-12-18 19:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_bid_listing_id_alter_bid_user_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='is_Active',
            new_name='is_active',
        ),
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.CharField(help_text='(optional- must be jpg/png url', max_length=100, validators=[django.core.validators.RegexValidator(regex='([^\\s]+(\\.(?i)(jpe?g|png|gif|bmp))$)')]),
        ),
    ]