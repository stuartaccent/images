# Generated by Django 2.0.4 on 2018-04-07 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='focal_point_height',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='focal_point_width',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='focal_point_x',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='focal_point_y',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
