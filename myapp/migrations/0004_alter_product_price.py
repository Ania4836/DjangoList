# Generated by Django 5.1.2 on 2024-11-19 21:15

import myapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_order_date_alter_order_customer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[myapp.models.validate_positive]),
        ),
    ]
