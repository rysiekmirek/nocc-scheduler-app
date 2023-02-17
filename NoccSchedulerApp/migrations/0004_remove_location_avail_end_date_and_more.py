# Generated by Django 4.1.2 on 2022-11-08 23:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NoccSchedulerApp', '0003_location_time_interval_alter_location_time_slots_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='avail_end_date',
        ),
        migrations.RemoveField(
            model_name='location',
            name='avail_end_time',
        ),
        migrations.RemoveField(
            model_name='location',
            name='avail_start_date',
        ),
        migrations.RemoveField(
            model_name='location',
            name='avail_start_time',
        ),
        migrations.RemoveField(
            model_name='location',
            name='time_interval',
        ),
        migrations.RemoveField(
            model_name='location',
            name='time_slots',
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avail_date', models.DateField()),
                ('time_slots', models.TextField(max_length=5000)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NoccSchedulerApp.location')),
            ],
        ),
    ]