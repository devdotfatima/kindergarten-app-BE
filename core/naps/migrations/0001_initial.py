# Generated by Django 5.1.6 on 2025-02-24 20:35

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('children', '0003_children_bio_alter_children_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('sleep_from', models.TimeField()),
                ('sleep_to', models.TimeField()),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='naps', to='children.children')),
            ],
        ),
    ]
