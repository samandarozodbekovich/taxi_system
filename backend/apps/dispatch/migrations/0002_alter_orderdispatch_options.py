from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dispatch", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="orderdispatch",
            options={"verbose_name": "Order dispatch", "verbose_name_plural": "Order dispatches"},
        ),
    ]
