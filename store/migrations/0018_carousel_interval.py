# Generated by Django 4.0.4 on 2022-11-25 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_carousel'),
    ]

    operations = [
        migrations.AddField(
            model_name='carousel',
            name='interval',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
