# Generated by Django 4.2.11 on 2024-04-02 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('online_market_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlinemarketuser',
            name='role',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='online_market_app.role'),
            preserve_default=False,
        ),
    ]
