from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wallet", "0002_alter_driverwallet_driver"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="driverwallet",
            options={"verbose_name": "Driver wallet", "verbose_name_plural": "Driver wallets"},
        ),
        migrations.AlterModelOptions(
            name="wallettransaction",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Wallet transaction",
                "verbose_name_plural": "Wallet transactions",
            },
        ),
        migrations.AlterField(
            model_name="wallettransaction",
            name="transaction_type",
            field=models.CharField(
                choices=[
                    ("COMMISSION", "Commission charged"),
                    ("PENALTY", "Penalty charged"),
                    ("TOPUP", "Balance top-up (admin)"),
                    ("ORDER_EARN", "Order earnings"),
                ],
                max_length=20,
            ),
        ),
    ]
