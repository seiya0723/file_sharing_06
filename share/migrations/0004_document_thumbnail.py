# Generated by Django 3.2.9 on 2022-02-28 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0003_review_star'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='share/document/thumbnail', verbose_name='ファイルのサムネイル'),
        ),
    ]
