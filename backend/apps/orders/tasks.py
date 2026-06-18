import time
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.orders.models import Order
from apps.dispatch.models import OrderDispatch


@shared_task(name="apps.orders.tasks.process_order_dispatch")
def process_order_dispatch(order_id):
    """
    OrderDispatch ro'yxatidagi haydovchilarga tartib bilan buyurtmani yuboruvchi Celery Task.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f"Order {order_id} topilmadi."

    # Agar buyurtma allaqachon qabul qilingan yoki bekor qilingan bo'lsa, jarayonni to'xtatamiz
    if order.status != "SEARCHING":
        return f"Order {order_id} qidiruv holatida emas (Hozirgi status: {order.status})."

    # Hali so'rov yuborilmagan yoki muddati o'tmagan aktiv dispatch bor-yo'qligini tekshiramiz
    # Biz yuqorida dispatch_list yaratgandik, ularni ketma-ketlikda qayta ishlaymiz
    current_dispatch = OrderDispatch.objects.filter(
        order=order,
        is_rejected=False,
        is_accepted=False
    ).order_by('id').first()  # ID bo'yicha tartiblangan, ya'ni Yandex bo'yicha eng birinchisi

    if not current_dispatch:
        # Agar ro'yxat tugagan bo'lsa, radiusi kengaytirish yoki mijozga "Haydovchi topilmadi" deyish kerak
        # Hozircha statusni o'zgartirib qo'yamiz
        order.status = "NO_DRIVER"
        order.save()
        
        # Mijozga WebSocket orqali xabar berish
        notify_client(order.client_id, {"status": "no_driver_found"})
        return f"Order {order_id} uchun haydovchi topilmadi."

    driver = current_dispatch.driver
    channel_layer = get_channel_layer()
    
    # WebSocket guruh nomi (Har bir haydovchi o'z ID-si bilan guruhga ulanadi)
    driver_group_name = f"driver_{driver.id}"

    # Haydovchiga WebSocket orqali buyurtma ma'lumotlarini yuboramiz
    async_to_sync(channel_layer.group_send)(
        driver_group_name,
        {
            "type": "send_order_offer",
            "dispatch_id": current_dispatch.id,
            "order_id": order.id,
            "pickup_location": {"lat": order.pickup_location.y, "lon": order.pickup_location.x},
            "dropoff_location": {"lat": order.dropoff_location.y, "lon": order.dropoff_location.x},
            "distance_to_client_km": float(current_dispatch.distance_to_client_km),
            "timeout_seconds": 15
        }
    )

    # Haydovchiga o'ylab ko'rish uchun 15 soniya vaqt beramiz (Bloklovchi uyqu)
    time.sleep(15)

    # 15 soniyadan keyin bazani qayta tekshiramiz: haydovchi qabul qildimi?
    current_dispatch.refresh_from_db()
    order.refresh_from_db()

    if current_dispatch.is_accepted or order.status != "SEARCHING":
        return f"Order {order_id} muvaffaqiyatli qabul qilindi."

    # Agar haydovchi 15 soniya ichida javob bermasa (Timeout), uni avtomatik rad etgan deb hisoblaymiz
    if not current_dispatch.is_rejected:
        current_dispatch.is_rejected = True
        current_dispatch.save()

    # Navbatdagi haydovchiga o'tish uchun xuddi shu Celery taskni qaytadan chaqiramiz (Recusive Call)
    process_order_dispatch.delay(order_id)


def notify_client(client_id, data):
    """Mijozga WebSocket orqali ma'lumot yuborish yordamchi funksiyasi"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"client_{client_id}",
        {
            "type": "client_order_update",
            "data": data
        }
    )