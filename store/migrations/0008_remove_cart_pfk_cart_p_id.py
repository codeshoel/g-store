# Generated by Django 4.0.4 on 2022-08-05 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_cart_pfk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='pfk',
        ),
        migrations.AddField(
            model_name='cart',
            name='p_id',
            field=models.PositiveBigIntegerField(default=0, verbose_name='product id'),
            preserve_default=False,
        ),
    ]
