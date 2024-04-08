# Generated by Django 4.2.11 on 2024-04-08 04:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OnlineMarketLogs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_date', models.DateTimeField(auto_now_add=True)),
                ('request_method', models.CharField()),
                ('request_path', models.CharField()),
                ('request_status', models.SmallIntegerField()),
                ('response', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='OnlineMarketOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
