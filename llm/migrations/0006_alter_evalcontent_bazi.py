# Generated by Django 4.2 on 2024-07-28 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('llm', '0005_evalcontent_bazi_alter_evalcontent_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evalcontent',
            name='bazi',
            field=models.CharField(max_length=200, verbose_name='八字'),
        ),
    ]
