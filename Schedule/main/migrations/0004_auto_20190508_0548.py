# Generated by Django 2.2 on 2019-05-08 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20190504_0435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='address',
            field=models.CharField(db_index=True, max_length=512),
        ),
    ]
