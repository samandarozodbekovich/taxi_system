from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("settings_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="systemsetting",
            options={"verbose_name": "System setting", "verbose_name_plural": "System settings"},
        ),
        migrations.AlterField(
            model_name="systemsetting",
            name="key",
            field=models.CharField(
                help_text="Setting key (e.g. MIN_PRICE, COMMISSION_PERCENT)", max_length=100, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="systemsetting",
            name="value",
            field=models.CharField(help_text="Setting value (as text)", max_length=255),
        ),
        migrations.AlterField(
            model_name="systemsetting",
            name="description",
            field=models.TextField(blank=True, help_text="What this setting controls", null=True),
        ),
    ]
