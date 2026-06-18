from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from ..models import Driver


class DriverLoginSerializer(serializers.Serializer):
    driver_code = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        driver_code = data.get('driver_code')
        password = data.get('password')
        try:
            driver = Driver.objects.get(driver_code=driver_code)
        except Driver.DoesNotExist:
            raise serializers.ValidationError("Driver kodi noto'g'ri.")

        if driver.is_blocked:
            raise serializers.ValidationError("Sizning hisobingiz bloklangan.")

        if not check_password(password, driver.password_hash):
            raise serializers.ValidationError("Parol noto'g'ri.")

        data['driver'] = driver
        return data