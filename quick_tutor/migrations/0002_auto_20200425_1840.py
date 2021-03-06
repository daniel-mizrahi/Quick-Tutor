# Generated by Django 3.0.2 on 2020-04-25 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quick_tutor', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='share_email',
        ),
        migrations.RemoveField(
            model_name='student',
            name='share_phone',
        ),
        migrations.RemoveField(
            model_name='tutor',
            name='notify_desktop',
        ),
        migrations.RemoveField(
            model_name='tutor',
            name='notify_email',
        ),
        migrations.RemoveField(
            model_name='tutor',
            name='notify_phone',
        ),
        migrations.RemoveField(
            model_name='tutor',
            name='on_call',
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_email',
            field=models.BooleanField(default=True),
        ),
    ]
