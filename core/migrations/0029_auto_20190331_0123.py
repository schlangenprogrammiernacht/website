# Generated by Django 2.0.4 on 2019-03-31 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20190309_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snakeversion',
            name='compile_state',
            field=models.CharField(choices=[('not_compiled', 'Not compiled yet'), ('successful', 'Compiled successfully'), ('failed', 'Compilation failed'), ('crashed', 'Compilation successful, but init failed')], default='not_compiled', max_length=12),
        ),
    ]
