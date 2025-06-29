# Generated by Django 5.2.2 on 2025-06-24 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_orders', '0005_order_card_expiry_order_card_name_order_card_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product_value',
            field=models.DecimalField(decimal_places=2, default=0, help_text='PV (Product Value) points at time of order for rank advancement', max_digits=10),
        ),
    ]
