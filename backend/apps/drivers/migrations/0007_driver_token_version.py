from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("drivers", "0006_remove_driver_wallet"),
    ]

    operations = [
        migrations.AddField(
            model_name="driver",
            name="token_version",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
