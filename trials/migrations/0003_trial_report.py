# Generated by Django 5.1.6 on 2025-03-08 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trials', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='report',
            field=models.TextField(blank=True),
        ),
    ]
