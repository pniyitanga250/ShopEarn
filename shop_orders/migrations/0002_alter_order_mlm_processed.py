from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='mlm_processed',
            field=models.BooleanField(default=False, null=True, blank=True),
        ),
    ]