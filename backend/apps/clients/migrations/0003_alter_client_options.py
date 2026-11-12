from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0002_alter_client_telegram_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="client",
            options={"ordering": ["-created_at"], "verbose_name": "Client", "verbose_name_plural": "Clients"},
        ),
    ]
