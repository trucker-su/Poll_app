# Generated by Django 3.2 on 2021-04-24 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestingService', '0002_answer_votes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='votes',
        ),
        migrations.AddField(
            model_name='studentanswer',
            name='votes',
            field=models.IntegerField(default=0),
        ),
    ]
