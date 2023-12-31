# Generated by Django 4.2.3 on 2023-07-30 19:27

import addresses.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(countries=addresses.models.EuropeCountries, max_length=2)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('city', models.CharField(max_length=50)),
                ('region', models.CharField(blank=True, max_length=50)),
                ('street', models.CharField(max_length=75)),
                ('house_number', models.CharField(max_length=75)),
                ('apartment_number', models.CharField(blank=True, max_length=75)),
                ('postal_code', models.CharField(max_length=75)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
        ),
    ]
