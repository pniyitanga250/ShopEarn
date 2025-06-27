from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop_accounts', '0002_user_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='wallet_balance',
        ),
        migrations.RemoveField(
            model_name='user',
            name='lifetime_earnings',
        ),
        migrations.RemoveField(
            model_name='user',
            name='other_earnings',
        ),
        migrations.RemoveField(
            model_name='user',
            name='total_withdrawals',
        ),
        migrations.RemoveField(
            model_name='user',
            name='total_expenses',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_kyc_verified',
        ),
        migrations.RemoveField(
            model_name='user',
            name='kyc_documents',
        ),
        migrations.RemoveField(
            model_name='user',
            name='kyc_verified_date',
        ),
    ]