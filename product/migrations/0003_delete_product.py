# Generated by Django 4.2 on 2024-07-17 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_remove_cart_product_cart_bracelet_cart_gemstone_and_more'),
        ('product', '0002_bracelet_gemstone_gift_delete_component'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Product',
        ),
    ]
