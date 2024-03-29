# Generated by Django 3.1.3 on 2021-04-04 22:42

import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classic_tetris_project', '0043_auto_20210327_2316'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='color',
            field=colorfield.fields.ColorField(default='#000000', max_length=18),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='short_name',
            field=models.CharField(help_text='Used in the context of an event, e.g. "Masters Event"', max_length=64),
        ),
        migrations.AlterField(
            model_name='tournamentplayer',
            name='tournament',
            field=models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.CASCADE, related_name='tournament_players', to='classic_tetris_project.tournament'),
        ),
        migrations.AlterField(
            model_name='tournamentplayer',
            name='user',
            field=models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.PROTECT, related_name='tournament_players', to='classic_tetris_project.user'),
        ),
        migrations.AddConstraint(
            model_name='tournamentplayer',
            constraint=models.UniqueConstraint(fields=('tournament', 'seed'), name='unique_tournament_seed'),
        ),
    ]
