# Generated by Django 4.2 on 2024-07-19 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name': '地址', 'verbose_name_plural': '地址'},
        ),
    ]
