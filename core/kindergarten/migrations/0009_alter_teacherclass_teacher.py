# Generated by Django 5.1.6 on 2025-02-21 11:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kindergarten', '0008_alter_teacherclass_teacher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacherclass',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_classes', to='kindergarten.teacher'),
        ),
    ]
