# Generated by Django 4.1.4 on 2023-01-02 06:59

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
                ('d_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('mfi_created', models.BooleanField(default=False)),
                ('d_branch', models.CharField(default='', max_length=50)),
                ('first_name', models.CharField(default='', max_length=50)),
                ('last_name', models.CharField(default='', max_length=50)),
                ('phone', models.CharField(default='', max_length=50)),
                ('plaid_id', models.CharField(default='', max_length=50)),
                ('loan_acc', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('d_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('mfi_created', models.BooleanField(default=False)),
                ('aba_routing', models.CharField(default='', max_length=50)),
                ('account_number', models.CharField(default='', max_length=50)),
                ('name', models.CharField(default='', max_length=50)),
                ('dba', models.CharField(default='', max_length=50)),
                ('ein', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_id', models.CharField(default='', max_length=50)),
                ('amount', models.CharField(default='', max_length=50)),
                ('status', models.CharField(default='NOT EXECUTED', max_length=50)),
                ('last_updated', models.DateTimeField(auto_now_add=True)),
                ('pay_from', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='api.source')),
                ('pay_to', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='api.employee')),
            ],
        ),
    ]
