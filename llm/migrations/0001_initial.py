# Generated by Django 4.2 on 2024-07-16 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evalcontent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forself', models.BooleanField(default=True, verbose_name='为自己测')),
                ('name', models.CharField(max_length=15, verbose_name='姓名')),
                ('gender', models.IntegerField(choices=[(0, '男'), (1, '女')], verbose_name='性别')),
                ('birthdt', models.DateTimeField(verbose_name='出生时间')),
                ('birthloc', models.CharField(max_length=30, verbose_name='出生地')),
                ('liveloc', models.CharField(max_length=30, verbose_name='现居地')),
                ('job', models.CharField(max_length=15, verbose_name='职业')),
                ('belief', models.IntegerField(choices=[(0, '其他'), (1, '佛教')], verbose_name='信仰')),
                ('mood', models.IntegerField(choices=[(0, '好'), (1, '一般'), (2, '不好')], verbose_name='心情')),
                ('question1', models.IntegerField(choices=[(0, '选项一'), (1, '选项二')], verbose_name='问题1')),
                ('question2', models.IntegerField(choices=[(0, '选项一'), (1, '选项二')], verbose_name='问题2')),
                ('question3', models.IntegerField(choices=[(0, '选项一'), (1, '选项二')], verbose_name='问题3')),
                ('question4', models.IntegerField(choices=[(0, '选项一'), (1, '选项二')], verbose_name='问题4')),
                ('wish', models.IntegerField(choices=[(1, '事业'), (2, '学业'), (3, '财富'), (4, '爱情'), (5, '健康'), (6, '安全'), (7, '家庭'), (8, '快乐'), (9, '万事顺意')], verbose_name='心愿')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '测评内容',
                'verbose_name_plural': '测评内容',
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Evalreport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20, verbose_name='标题')),
                ('overall', models.CharField(max_length=400, verbose_name='整体解读')),
                ('wish', models.CharField(max_length=400, verbose_name='心愿')),
                ('advice', models.CharField(max_length=200, verbose_name='建议')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('evalcontent', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='llm.evalcontent', verbose_name='测评内容')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '测评报告',
                'verbose_name_plural': '测评内容',
            },
        ),
        migrations.CreateModel(
            name='Chathistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('talker', models.IntegerField(choices=[(0, '大模型'), (1, '用户')], verbose_name='说话人')),
                ('msg', models.CharField(max_length=300, verbose_name='信息')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '大模型对话记录',
                'verbose_name_plural': '大模型对话记录',
            },
        ),
    ]
