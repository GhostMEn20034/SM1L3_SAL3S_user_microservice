# Generated by Django 4.2.3 on 2023-07-30 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_address_options_rename_user_id_address_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.DeleteModel(
            name='Address',
        ),
    ]
