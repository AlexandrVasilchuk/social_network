# Generated by Django 2.2.16 on 2023-02-15 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20230211_2336'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={
                'default_related_name': 'comments',
                'ordering': ('-pub_date',),
                'verbose_name': 'комментарий',
                'verbose_name_plural': 'комментарии',
            },
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='created',
            new_name='pub_date',
        ),
    ]