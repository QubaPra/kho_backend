# Generated by Django 5.1.7 on 2025-03-17 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='verified',
            field=models.CharField(default='False', max_length=36),
        ),
    ]
