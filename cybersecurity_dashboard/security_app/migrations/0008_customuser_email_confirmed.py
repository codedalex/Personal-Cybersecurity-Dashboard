# Generated by Django 4.2.7 on 2023-11-22 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security_app', '0007_customuser_security_questions_answered'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='email_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
