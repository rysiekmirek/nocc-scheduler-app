# Generated by Django 4.1.2 on 2022-11-07 01:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NoccSchedulerApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='avail_date_start',
            new_name='avail_end_date',
        ),
        migrations.AddField(
            model_name='location',
            name='avail_start_date',
            field=models.DateField(default='2022-11-07'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tour',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NoccSchedulerApp.location'),
        ),
    ]
