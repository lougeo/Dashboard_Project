# Generated by Django 3.0.5 on 2020-04-17 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_projects'),
        ('dashboard', '0002_auto_20200416_1543'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='concretereport',
            name='cust_id',
        ),
        migrations.AlterField(
            model_name='concretereport',
            name='project_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Projects'),
        ),
        migrations.AlterField(
            model_name='concretereport',
            name='strength',
            field=models.IntegerField(null=True),
        ),
        migrations.RemoveField(
            model_name='concretereport',
            name='technician',
        ),
        migrations.AddField(
            model_name='concretereport',
            name='technician',
            field=models.ForeignKey(limit_choices_to={'is_Technician': True, 'is_manager': True}, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]