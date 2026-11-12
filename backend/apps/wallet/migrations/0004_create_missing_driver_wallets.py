from django.db import migrations


def create_missing_driver_wallets(apps, schema_editor):
    """
    DriverWallet becomes the only balance (Driver.wallet is removed next). Drivers without a
    wallet get one with their old Driver.wallet balance, so no money is lost. Existing
    wallets are kept as they are - they already hold the admin top-ups and commissions.
    """
    Driver = apps.get_model("drivers", "Driver")
    DriverWallet = apps.get_model("wallet", "DriverWallet")
    for driver in Driver.objects.filter(wallet_record__isnull=True):
        DriverWallet.objects.create(driver=driver, balance=driver.wallet)


class Migration(migrations.Migration):

    dependencies = [
        ("wallet", "0003_english_labels"),
        ("drivers", "0005_english_labels"),
    ]

    operations = [
        migrations.RunPython(create_missing_driver_wallets, migrations.RunPython.noop),
    ]
