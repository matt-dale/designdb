# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-04 19:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connectionType', models.CharField(max_length=100)),
                ('connectionName', models.CharField(max_length=100)),
                ('gender', models.CharField(max_length=50)),
                ('defaultLabelSize', models.CharField(choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large'), ('Custom', 'Custom')], default='Small', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GlobalEquipmentCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GlobalEquipmentConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('connectionType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connection_type', to='Global_Equipment_library.GlobalConnection')),
                ('matesWith', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mates_with', to='Global_Equipment_library.GlobalConnection')),
            ],
        ),
        migrations.CreateModel(
            name='GlobalEquipmentItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('model', models.CharField(blank=True, max_length=100, null=True)),
                ('hasMainLabel', models.BooleanField(default=True)),
                ('qtyMainLabel', models.IntegerField(default=1)),
                ('mainLabelSize', models.CharField(choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large'), ('Custom', 'Custom')], default='Small', max_length=50)),
                ('equipmentType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Global_Equipment_library.GlobalEquipmentCategory')),
            ],
        ),
        migrations.CreateModel(
            name='GlobalManufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='globalequipmentitem',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Global_Equipment_library.GlobalManufacturer'),
        ),
        migrations.AddField(
            model_name='globalequipmentconnection',
            name='parentEquipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Global_Equipment_library.GlobalEquipmentItem'),
        ),
    ]
