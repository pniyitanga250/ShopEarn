# Generated by Django 5.2.2 on 2025-06-24 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_orders', '0002_remove_orderitem_commission_value_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_proof',
            field=models.ImageField(blank=True, help_text='Upload payment proof (screenshot)', null=True, upload_to='payment_proofs/'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('', 'Select Payment Method'), ('MTN_MOBILE_MONEY', 'MTN Mobile Money'), ('AIRTEL_MONEY', 'Airtel Money'), ('CARD', 'Card'), ('CASH', 'Cash')], max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(blank=True, help_text='Transaction ID (TxId) for Mobile Money payments', max_length=100),
        ),
    ]
