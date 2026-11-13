from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0004_alter_order_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="dispatch_wave",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
