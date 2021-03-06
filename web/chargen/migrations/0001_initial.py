# Generated by Django 2.2.18 on 2021-02-13 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CharApp',
            fields=[
                ('app_id', models.AutoField(primary_key=True, serialize=False)),
                ('sexus', models.CharField(max_length=80, verbose_name='Sexus')),
                ('gens', models.CharField(max_length=80, verbose_name='Gens')),
                ('praenomen', models.CharField(max_length=80, verbose_name='Praenōmen')),
                ('date_applied', models.DateTimeField(verbose_name='Date Applied')),
                ('account_id', models.IntegerField(default=1, verbose_name='Account ID')),
                ('submitted', models.BooleanField(default=False)),
            ],
        ),
    ]
