# Generated by Django 4.2 on 2024-08-25 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0026_alter_bracelet_symbol_alter_gemstone_symbol_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gemstone',
            name='name',
            field=models.CharField(db_index=True, max_length=20, verbose_name='名称'),
        ),
    ]
