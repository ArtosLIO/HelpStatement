# Generated by Django 3.2 on 2021-04-26 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('desk', '0002_auto_20210426_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statement',
            name='level_important',
            field=models.CharField(choices=[('L', 'Low'), ('M', 'Medium'), ('H', 'High')], default='Low', max_length=10),
        ),
        migrations.AlterField(
            model_name='statement',
            name='success',
            field=models.CharField(choices=[('P', 'Process'), ('C', 'Confirmed'), ('F', 'Rejected'), ('R', 'Returned')], default='Process', max_length=10),
        ),
    ]
