# Generated by Django 3.0.4 on 2020-03-27 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scores', '0004_auto_20200325_1143'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='score',
            options={'ordering': ['title']},
        ),
        migrations.RenameField(
            model_name='score',
            old_name='alias',
            new_name='slug',
        ),
    ]
