# Generated by Django 4.1.2 on 2023-02-08 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NoccSchedulerApp', '0026_alter_tour_feedback_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='custom_welcome_screen_needed',
            field=models.CharField(blank=True, choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=10, null=True),
        ),
    ]
