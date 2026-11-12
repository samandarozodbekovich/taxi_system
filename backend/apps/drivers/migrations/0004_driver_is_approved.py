from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("drivers", "0003_driver_telegram_id"),
    ]

    operations = [
        # Existing drivers also stay unapproved - the admin reviews and approves them
        migrations.AddField(
            model_name="driver",
            name="is_approved",
            field=models.BooleanField(default=False, verbose_name="Approved"),
        ),
    ]
