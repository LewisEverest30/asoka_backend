# Generated by Django 4.2 on 2024-08-28 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_remove_cart_component_remove_cart_cost_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='letter',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='自定义文字（目前只有印章用的到）'),
        ),
    ]
