from django.db import migrations, models
from django.db.models import Count
from django.utils import timezone

ACTIVE_STATUSES = ["SEARCHING", "ACCEPTED", "WAITING", "IN_PROGRESS"]


def cancel_duplicate_active_orders(apps, schema_editor):
    """
    Before adding the constraint: if a client has several active orders
    (left over from double-clicking the button), keep the newest one and mark the
    rest CANCELED (cancel_by=SYSTEM). Nothing is deleted.
    """
    Order = apps.get_model("orders", "Order")
    duplicate_clients = (
        Order.objects.filter(status__in=ACTIVE_STATUSES)
        .values("client_id")
        .annotate(n=Count("id"))
        .filter(n__gt=1)
        .values_list("client_id", flat=True)
    )
    for client_id in list(duplicate_clients):
        active = Order.objects.filter(client_id=client_id, status__in=ACTIVE_STATUSES).order_by("-created_at", "-id")
        stale_ids = list(active.values_list("id", flat=True)[1:])
        Order.objects.filter(id__in=stale_ids).update(
            status="CANCELED",
            cancel_by="SYSTEM",
            cancel_reason="Duplicate active order (one_active_order_per_client migration)",
            canceled_at=timezone.now(),
        )


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_order_route_geometry_order_total_distance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("SEARCHING", "Searching"),
                    ("ACCEPTED", "Accepted"),
                    ("WAITING", "Waiting"),
                    ("IN_PROGRESS", "In Progress"),
                    ("COMPLETED", "Completed"),
                    ("CANCELED", "Canceled"),
                    ("NO_DRIVER", "No driver"),
                ],
                db_index=True,
                default="SEARCHING",
                max_length=20,
            ),
        ),
        migrations.RunPython(cancel_duplicate_active_orders, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status__in", ACTIVE_STATUSES)),
                fields=("client",),
                name="one_active_order_per_client",
            ),
        ),
    ]
