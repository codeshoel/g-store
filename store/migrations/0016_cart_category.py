# Generated by Django 4.0.4 on 2022-11-15 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_product_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='category',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
