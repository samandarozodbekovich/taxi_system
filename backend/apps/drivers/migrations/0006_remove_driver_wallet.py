from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("drivers", "0005_english_labels"),
        # Balances are copied into DriverWallet before the column is dropped
        ("wallet", "0004_create_missing_driver_wallets"),
    ]

    operations = [
        migrations.RemoveField(model_name="driver", name="wallet"),
    ]
