# Generated by Django 5.0.4 on 2024-04-08 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_naseeba', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='url',
        ),
        migrations.AddField(
            model_name='image',
            name='image',
            field=models.FileField(default='', upload_to='images/instaPosts/'),
            preserve_default=False,
        ),
    ]
