# Generated by Django 3.0.5 on 2020-05-14 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20200425_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concretesample',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='concretesample',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='dashboard.ConcreteReport'),
        ),
        migrations.AlterField(
            model_name='concretesample',
            name='result',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Pass'), (1, 'Warning'), (2, 'Fail')], null=True),
        ),
        migrations.AlterField(
            model_name='concretesample',
            name='strength',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='concretesample',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='concretesample',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]