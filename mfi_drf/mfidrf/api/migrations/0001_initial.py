# Generated by Django 4.1.4 on 2023-01-01 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('dunkin_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('mfi_acc_id', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('dunkin_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('mfi_acc_id', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_id', models.CharField(max_length=50)),
                ('status', models.CharField(default='NOT EXECUTED', max_length=50)),
                ('pay_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.source')),
                ('pay_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.employee')),
            ],
        ),
    ]
