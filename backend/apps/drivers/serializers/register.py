from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from ..models import Driver
import random


class DriverRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Driver
        fields = [
            'full_name',
            'phone_number',
            'car_model',
            'car_color',
            'car_number',
            'password',
            'photo',
            'telegram_id',
        ]

    def validate_phone_number(self, value):

        if Driver.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")
        return value

    def validate_car_number(self, value):

        if Driver.objects.filter(car_number=value).exists():
            raise serializers.ValidationError("Bu mashina raqami allaqachon ro'yxatdan o'tgan.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password') 

        driver = Driver(
            driver_code=generate_driver_code(),      
            password_hash=make_password(password),    
            **validated_data
        )
        driver.save()
        return driver
    
def generate_driver_code():

    while True:
        number = random.randint(10000, 99999)
        code = f"DRV-{number}"
        if not Driver.objects.filter(driver_code=code).exists():
            return code