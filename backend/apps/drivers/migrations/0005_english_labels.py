from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("drivers", "0004_driver_is_approved"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="driver",
            options={"verbose_name": "Driver", "verbose_name_plural": "Drivers"},
        ),
        migrations.AlterField(
            model_name="driver",
            name="is_approved",
            field=models.BooleanField(default=False, verbose_name="Approved"),
        ),
    ]
