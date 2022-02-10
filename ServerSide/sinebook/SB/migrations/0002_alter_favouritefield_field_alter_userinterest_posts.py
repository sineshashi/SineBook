# Generated by Django 4.0.2 on 2022-02-07 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SB', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favouritefield',
            name='field',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='userinterest',
            name='posts',
            field=models.ManyToManyField(blank=True, related_name='posting_user', to='SB.Post'),
        ),
    ]
