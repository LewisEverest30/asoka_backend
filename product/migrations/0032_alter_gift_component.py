# Generated by Django 4.2 on 2024-09-04 11:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0031_alter_gemstone_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gift',
            name='component',
            field=models.CharField(help_text='请用这样的格式来表示产品的组成: 个数*珠/手链-id 个数*珠/手链-id。例如: 3*珠-1 2*珠-2 1*手链-1', max_length=200, validators=[django.core.validators.RegexValidator('^(\\d+\\*(珠|手链|印章)\\-\\d+ )*(\\d+\\*(珠|手链|印章)\\-\\d+)$', '请用这样的格式来表示产品的组成: 个数*珠/手链-id 个数*珠/手链-id。例如: 3*珠-1 2*珠-2 1*手链-1')], verbose_name='组成 '),
        ),
    ]
