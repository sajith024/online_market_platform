# Generated by Django 4.2.11 on 2024-04-02 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_market_app', '0002_alter_onlinemarketuser_role'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='onlinemarketuser',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(unique=True),
        ),
    ]