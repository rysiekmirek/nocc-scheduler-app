# Generated by Django 4.1.2 on 2023-01-24 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NoccSchedulerApp', '0021_alter_tour_end_time_alter_tour_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='type_of_customers',
            field=models.CharField(choices=[('Akamai Internal', 'Akamai Internal'), ('Financial Services', 'Financial Services'), ('Media', 'Media'), ('High Tech', 'High Tech'), ('Retail + Commerce', 'Retail + Commerce'), ('Gaming/OTT', 'Gaming/OTT'), ('Healthcare/Life Science', 'Healthcare/Life Science'), ('Manufacturing', 'Manufacturing'), ('Other', 'Other')], max_length=200),
        ),
    ]
