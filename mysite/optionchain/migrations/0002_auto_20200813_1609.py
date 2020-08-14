# Generated by Django 3.0.8 on 2020-08-13 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optionchain', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='symbol',
            field=models.CharField(max_length=30, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='optionprice',
            name='open_interest',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='optionprice',
            name='trades',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='optionprice',
            name='volume',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='optionprice',
            name='volume_ask',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='optionprice',
            name='volume_bid',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
