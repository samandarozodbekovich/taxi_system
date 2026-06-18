from decimal import Decimal
import string
import random
import logging
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.orders.models import Order
from apps.dispatch.models import OrderDispatch
from apps.drivers.models import Driver
from apps.settings_app.models import SystemSetting
from apps.wallet.models.wallet_transaction import WalletTransaction
from services.yandex_maps import RoutingService
from .tasks import process_order_dispatch

logger = logging.getLogger(__name__)

class OrderService:
    
    @staticmethod
    def calculate_estimate_price(distance_km, waiting_time_minutes=0):
        base_fare = Decimal(SystemSetting.get_setting("MIN_PRICE", 5000))
        per_km_rate = Decimal(SystemSetting.get_setting("PRICE_PER_KM", 2000))
        per_min_minute = Decimal(SystemSetting.get_setting("WAITING_PRICE_PER_MINUTE", 500))
        free_waiting_time = Decimal(SystemSetting.get_setting("FREE_WAITING_TIME", 3))
        
        price = base_fare + (per_km_rate * Decimal(distance_km))
        
        if waiting_time_minutes > free_waiting_time:
            extre_waiting = waiting_time_minutes - free_waiting_time
            price += per_min_minute * Decimal(extre_waiting)
        
        return round(price, -2)
    
    @staticmethod
    def create_order(client, pickup_lat, pickup_lon, destination_lat=None, destination_lon=None, pickup_address="", destination_address=""):
        pickup_point = Point(float(pickup_lon), float(pickup_lat), srid=4326)
        distance = 0
        destination_point = None
        
        if destination_lat and destination_lon:
            destination_point = Point(float(destination_lon), float(destination_lat), srid=4326)
            # Masofani hisoblash
            distance = pickup_point.distance(destination_point) * 100 

        estimated_price = OrderService.calculate_estimate_price(distance)
        
        
        # Modelga barcha kerakli maydonlarni uzatamiz
        order = Order.objects.create(
            order_number=generate_order_number(),
            client=client,
            pickup_location=pickup_point,
            pickup_latitude=pickup_lat,
            pickup_longitude=pickup_lon,
            pickup_address=pickup_address, # Bu yerda yetishmayotgan edi
            destination_location=destination_point,
            destination_latitude=destination_lat,
            destination_longitude=destination_lon,
            destination_address=destination_address, # Buni ham qo'shdik
            distance_km=distance,
            estimated_price=estimated_price,
            total_price=estimated_price,
            status='SEARCHING'
        )
        
        OrderService.dispatch_order_to_drivers(order)
        return order
    
    @staticmethod
    def dispatch_order_to_drivers(order):
        search_radius = 5  # km
        
        # Rad etgan haydovchilarni chiqarib tashlash
        exclude_driver_ids = OrderDispatch.objects.filter(
            order=order,
            is_rejected=True
        ).values_list('driver_id', flat=True)
        
        # 1-QADAM: PostGIS orqali barcha talablarga mos va 5km radiusdagi haydovchilarni topish
        nearby_drivers = Driver.objects.filter(
            status="ONLINE",
            is_blocked=False,
            wallet__gte=0,
        ).exclude(
            id__in=exclude_driver_ids
        ).filter(
            current_location__distance_lte=(order.pickup_location, D(km=search_radius))
        ).annotate(
            # Havo liniyasi bo'yicha masofani hisoblash (baza darajasida tez ishlashi uchun)
            air_distance=Distance('current_location', order.pickup_location)
        ).order_by('air_distance')[:5]  # Yandex API-ni qiynamaslik uchun ENG YAQIN 5 tasini olamiz

        client_lat, client_lon = order.pickup_location.y, order.pickup_location.x
        calculated_drivers = []

        # 2-QADAM: Saralangan 5 ta haydovchi uchun Yandex orqali PROBKA va real yo'lni tekshirish
        for driver in nearby_drivers:
            driver_lat, driver_lon = driver.current_location.y, driver.current_location.x
            
            # Yandex Routing API-ga so'rov yuboramiz
            route_info = RoutingService.get_route(
                start_lat=driver_lat, start_lon=driver_lon,
                end_lat=client_lat, end_lon=client_lon
            )
            
            if route_info["status"] == "success":
                # API muvaffaqiyatli ishlasa, Yandex ma'lumotlarini biriktiramiz
                real_distance = route_info["distance_km"]
                eta_minutes = route_info["duration_minutes"]
                geometry = route_info["geometry"]
            else:
                # Agar Yandex-da muammo bo'lsa (masalan limit tugasa), PostGIS hisoblagan masofani vaqtinchalik ishlatamiz
                real_distance = driver.air_distance.km
                eta_minutes = (real_distance / 40) * 60  # O'rtacha 40 km/h tezlik bilan taxminiy vaqt
                geometry = None

            calculated_drivers.append({
                "driver_obj": driver,
                "real_distance": real_distance,
                "eta_minutes": eta_minutes,
                "geometry": geometry
            })

        # 3-QADAM: Haydovchilarni havo liniyasi bo'yicha emas, YANDEX BERGAN ANIQ ETA (vaqt) bo'yicha saralaymiz
        calculated_drivers.sort(key=lambda x: x["eta_minutes"])

        # 4-QADAM: OrderDispatch ob'ektlarini yaratish
        dispatch_list = []
        for item in calculated_drivers:
            driver = item["driver_obj"]
            
            dispatch = OrderDispatch.objects.create(
                order=order,
                driver=driver,
                distance_to_client_km=item["real_distance"],  # Endi bu yerda Yandex bergan aniq yo'l masofasi bo'ladi
                is_sent=True,
                expires_at=timezone.now() + timedelta(seconds=60)
            )
            
            # Agar keyinchalik frontendga yo'l chizig'ini (geometry) ham uzatish kerak bo'lsa, 
            # uni dispatch ob'ektiga vaqtinchalik atribut qilib yopishtirib qo'yish mumkin
            dispatch.route_geometry = item["geometry"]
            dispatch_list.append(dispatch)
        
        return dispatch_list
    
    # OrderService klassi ichiga davom ettiramiz...

    @staticmethod
    def create_and_start_search(order):
        """
        Buyurtma uchun qidiruvni boshlash.
        """
        # 1. Statusni qidiruvga o'zgartiramiz
        order.status = "SEARCHING"
        order.save()

        # 2. Yandex + PostGIS orqali haydovchilarni yaratamiz (oldingi metodimiz)
        dispatch_list = OrderService.dispatch_order_to_drivers(order)

        if dispatch_list:
            # 3. Celery taskni fonda ishga tushiramiz
            process_order_dispatch.delay(order.id)
            return True
        else:
            order.status = "NO_DRIVER"
            order.save()
            return False
    
    @staticmethod
    def update_status(order_id, new_status, extra_data=None):
        """
        Statusni yangilash va WebSocketga push qilish uchun universal metod
        """
        from django.utils import timezone
        order = Order.objects.get(id=order_id)
        order.status = new_status
        
        if new_status == 'WAITING':
            order.arrived_at = timezone.now()
        elif new_status == 'IN_PROGRESS':
            order.started_at = timezone.now()
        
        order.save()
        
        # Klientga websocket orqali xabar yuboramiz
        data = {'status': new_status}
        if extra_data:
            data.update(extra_data)
        
        notify_order_update(order.id, data)
        return order
    
    @staticmethod
    def accept_order(order_id, driver):
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            if order.status != "SEARCHING":
                raise ValueError("Buyurtma allaqachon qabul qilingan.")
            
            order.driver = driver
            order.status = "ACCEPTED"
            order.accepted_at = timezone.now()
            order.save()

            # WebSocket xabari
            notify_order_update(order.id, {
                'status': 'ACCEPTED',
                'driver_name': driver.full_name,
                'car_model': driver.car_model,
                'car_number': driver.car_number,
                'driver_phone': driver.phone_number if hasattr(driver, 'phone_number') else ""
            })

            driver.status = "BUSY"
            driver.save()
            
            # Dispatchlarni yangilash
            OrderDispatch.objects.filter(order=order).exclude(driver=driver).update(
                is_accepted=False, is_rejected=True, responded_at=timezone.now()
            )
            OrderDispatch.objects.filter(order=order, driver=driver).update(
                is_accepted=True, is_rejected=False, responded_at=timezone.now()
            )
            
            return order
        
    @staticmethod
    def complete_order(order_id):
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)

            if order.status != "IN_PROGRESS":
                raise ValueError("Buyurtma statusi noto'g'ri.")

            order.total_price = order.estimated_price + order.waiting_price
            order.status = "COMPLETED"
            order.completed_at = timezone.now()

            comm_percent = Decimal(SystemSetting.get_setting("COMMISSION_PERCENT", 10))
            commission_amount = (order.total_price * comm_percent) / Decimal(100)
            order.commission_amount = commission_amount
            order.save()

            driver = order.driver
            driver.status = "ONLINE"

            # ✅ TO'G'RI — driver.wallet bu Decimal, to'g'ridan o'zgartirish
            before_balance = driver.wallet
            driver.wallet -= commission_amount
            driver.save()

            # WalletTransaction uchun DriverWallet modeli bormi tekshiring
            # Agar DriverWallet alohida model bo'lsa:
            try:
                from apps.wallet.models import DriverWallet, WalletTransaction
                wallet_obj = DriverWallet.objects.get(driver=driver)
                before_bal = wallet_obj.balance
                wallet_obj.balance -= commission_amount
                wallet_obj.save()
                WalletTransaction.objects.create(
                    wallet=wallet_obj,
                    order=order,
                    amount=commission_amount,
                    transaction_type='COMMISSION',
                    before_balance=before_bal,
                    after_balance=wallet_obj.balance
                )
            except Exception as e:
                logger.warning(f"WalletTransaction yaratishda xato: {e}")

            notify_order_update(order.id, {'status': 'COMPLETED'})
            return order
        
    @staticmethod
    def cancel_by_driver(order_id, driver):
        with transaction.atomic():
            try:
                order = Order.objects.select_for_update().get(id=order_id)
            except Order.DoesNotExist:
                raise ValueError("Order not found.")
            
            if order.status not in ["ACCEPTED", "IN_PROGRESS"]:
                raise ValueError("Buyurtma hali qabul qilinmagan yoki allaqachon tugatilgan.")
            
            if order.driver != driver:
                raise ValueError("Siz bu buyurtmani bekor qilish huquqiga ega emassiz.")
            
            OrderDispatch.objects.filter(order=order, driver=driver).update(
                is_accepted=False, 
                is_rejected=False,
                responded_at=timezone.now()
            )
            
            order.driver = None
            order.status = "SEARCHING"
            order.save()
            
            driver.status = "ONLINE"
            driver.save()
            
            OrderService.dispatch_order_to_drivers(order)
            
            return order

    @staticmethod
    def cancel_by_client(order_id, client, cancel_reason=None):
        with transaction.atomic():
            try:
                order = Order.objects.select_for_update().get(id=order_id)
            except Order.DoesNotExist:
                raise ValueError("Order not found.")

            if order.client != client:
                raise ValueError("Siz bu buyurtmani bekor qilish huquqiga ega emassiz.")

            if order.status in ["COMPLETED", "CANCELED"]:
                raise ValueError("Buyurtma allaqachon tugatilgan yoki bekor qilingan.")

            if order.status == "SEARCHING":
                OrderDispatch.objects.filter(order=order).update(
                    is_accepted=False,
                    is_rejected=True,
                    responded_at=timezone.now()
                )

            if order.driver:
                driver = order.driver
                driver.status = "ONLINE"
                driver.save()
                order.driver = None

            order.status = "CANCELED"
            order.canceled_at = timezone.now()
            order.cancel_by = "CLIENT"
            if cancel_reason:
                order.cancel_reason = cancel_reason
            order.save()

            notify_order_update(order.id, {
                'status': 'CANCELED',
                'cancel_by': 'CLIENT',
                'cancel_reason': cancel_reason
            })
            
            return order
        

def notify_client_driver_found(order_id, driver_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'order_{order_id}',
        {
            'type': 'order_update',
            'data': {
                'status':"ACCEPTED",
                'driver_name': driver_data.full_name,
                "car_model": driver_data.car_model,
                "lat": float(driver_data.current_latitude),
                "lon": float(driver_data.current_longitude)
            }
        }
    )
    
    
def notify_order_update(order_id, data):
    """
    Clientga (TMA) barcha turdagi status o'zgarishlarini yuborish
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'order_{order_id}',
        {
            'type': 'order_update',
            'data': data
        }
    )
    
def generate_order_number():
        return 'TX-' + ''.join(random.choices(string.digits, k=4))