# Generated by Django 3.2.11 on 2023-04-29 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classic_tetris_project', '0074_auto_20221002_0630'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='bracket_type',
            field=models.CharField(choices=[('SINGLE', 'Single Elimination'), ('DOUBLE', 'Double Elimination')], default='SINGLE', max_length=64),
        ),
        migrations.AlterField(
            model_name='event',
            name='qualifying_type',
            field=models.IntegerField(choices=[(1, 'Highest Score'), (2, 'Highest 2 Scores'), (3, 'Highest 3 Scores'), (4, 'Most Maxouts'), (5, 'Lowest Time')]),
        ),
        migrations.AlterField(
            model_name='qualifier',
            name='qualifying_type',
            field=models.IntegerField(choices=[(1, 'Highest Score'), (2, 'Highest 2 Scores'), (3, 'Highest 3 Scores'), (4, 'Most Maxouts'), (5, 'Lowest Time')]),
        ),
    ]
