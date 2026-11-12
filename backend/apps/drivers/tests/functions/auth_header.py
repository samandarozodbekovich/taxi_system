from apps.drivers.functions import create_driver_token


def auth_header(driver):
    return {"HTTP_AUTHORIZATION": f"Bearer {create_driver_token(driver)}"}
