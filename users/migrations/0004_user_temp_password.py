# Generated by Django 5.1.7 on 2025-03-19 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='temp_password',
            field=models.CharField(blank=True, max_length=36, null=True),
        ),
    ]
