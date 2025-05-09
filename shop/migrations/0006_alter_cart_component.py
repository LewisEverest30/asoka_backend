# Generated by Django 4.2 on 2024-08-09 22:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='component',
            field=models.CharField(max_length=200, validators=[django.core.validators.RegexValidator('^(\\d+\\*[^\\|\\*]+\\|)*(\\d+\\*[^\\|\\*]+)$', '请用这样的格式来表示产品的组成: 3*塑料石|2*蓝宝石|1*玉髓手环')], verbose_name='组成'),
        ),
    ]
