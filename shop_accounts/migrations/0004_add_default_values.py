from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_accounts', '0003_remove_financial_fields'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE shop_accounts_user 
            ALTER COLUMN retail_bonus_earnings SET DEFAULT 0.00,
            ALTER COLUMN retail_bonus_earnings DROP NOT NULL;
            
            UPDATE shop_accounts_user 
            SET retail_bonus_earnings = 0.00 
            WHERE retail_bonus_earnings IS NULL;
            
            ALTER TABLE shop_accounts_user 
            ALTER COLUMN referral_earnings SET DEFAULT 0.00,
            ALTER COLUMN referral_earnings DROP NOT NULL;
            
            UPDATE shop_accounts_user 
            SET referral_earnings = 0.00 
            WHERE referral_earnings IS NULL;
            
            ALTER TABLE shop_accounts_user 
            ALTER COLUMN matching_bonus_earnings SET DEFAULT 0.00,
            ALTER COLUMN matching_bonus_earnings DROP NOT NULL;
            
            UPDATE shop_accounts_user 
            SET matching_bonus_earnings = 0.00 
            WHERE matching_bonus_earnings IS NULL;
            
            ALTER TABLE shop_accounts_user 
            ALTER COLUMN leadership_bonus_earnings SET DEFAULT 0.00,
            ALTER COLUMN leadership_bonus_earnings DROP NOT NULL;
            
            UPDATE shop_accounts_user 
            SET leadership_bonus_earnings = 0.00 
            WHERE leadership_bonus_earnings IS NULL;
            
            ALTER TABLE shop_accounts_user 
            ALTER COLUMN personal_sales_volume SET DEFAULT 0.00,
            ALTER COLUMN personal_sales_volume DROP NOT NULL;
            
            UPDATE shop_accounts_user 
            SET personal_sales_volume = 0.00 
            WHERE personal_sales_volume IS NULL;
            
            ALTER TABLE shop_accounts_user 
            ALTER COLUMN group_sales_volume SET DEFAULT 0.00,
            ALTER COLUMN group_sales_volume DROP NOT NULL;
            
            UPDATE shop_accounts_user 
            SET group_sales_volume = 0.00 
            WHERE group_sales_volume IS NULL;
            """
        ),
    ]