from rest_framework import serializers
from django.contrib.auth.hashers import check_password, make_password
from ..models import Driver

# Don't reveal whether the code or the password is wrong - otherwise existing driver codes can be enumerated
INVALID_CREDENTIALS = "Invalid driver code or password."


class DriverLoginSerializer(serializers.Serializer):
    driver_code = serializers.CharField()
    password = serializers.CharField(write_only=True)

    # The view counts failed attempts based on this (blocked/unapproved accounts don't count as attempts)
    credentials_ok = False

    def validate(self, data):

        driver_code = data.get('driver_code')
        password = data.get('password')
        try:
            driver = Driver.objects.get(driver_code=driver_code)
        except Driver.DoesNotExist:
            # Response timing must not reveal whether the code exists either
            make_password(password)
            raise serializers.ValidationError(INVALID_CREDENTIALS)

        if not check_password(password, driver.password_hash):
            raise serializers.ValidationError(INVALID_CREDENTIALS)

        self.credentials_ok = True

        if driver.is_blocked:
            raise serializers.ValidationError("Your account is blocked.")

        if not driver.is_approved:
            raise serializers.ValidationError("Your account has not been approved by an admin yet. Please wait.")

        data['driver'] = driver
        return data
