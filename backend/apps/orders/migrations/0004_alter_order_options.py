from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_order_status_no_driver_one_active_order_per_client"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ["-created_at"], "verbose_name": "Order", "verbose_name_plural": "Orders"},
        ),
    ]
