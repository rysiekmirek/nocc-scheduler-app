# Generated by Django 4.1.2 on 2023-01-12 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NoccSchedulerApp', '0020_alter_tour_division'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='end_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='tour',
            name='start_time',
            field=models.TimeField(null=True),
        ),
    ]
