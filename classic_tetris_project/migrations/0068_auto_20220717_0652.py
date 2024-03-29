# Generated by Django 3.2.11 on 2022-07-17 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classic_tetris_project', '0067_event_withdrawals_allowed'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='vod_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='qualifying_type',
            field=models.IntegerField(choices=[(1, 'Highest Score'), (2, 'Highest 2 Scores'), (3, 'Highest 3 Scores'), (4, 'Most Maxouts')]),
        ),
        migrations.AlterField(
            model_name='qualifier',
            name='qualifying_type',
            field=models.IntegerField(choices=[(1, 'Highest Score'), (2, 'Highest 2 Scores'), (3, 'Highest 3 Scores'), (4, 'Most Maxouts')]),
        ),
    ]
