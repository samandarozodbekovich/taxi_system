from django.db.models import Avg, Count, Sum


def completed_orders_summary(queryset):
    """Totals for the admin order list (templates/admin/orders/order/change_list.html)."""
    return queryset.filter(status='COMPLETED').aggregate(
        total_sum=Sum('total_price'),
        total_commission=Sum('commission_amount'),
        orders_count=Count('id'),
        avg_price=Avg('total_price'),
    )
