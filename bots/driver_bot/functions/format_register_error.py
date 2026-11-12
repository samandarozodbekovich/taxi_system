def format_register_error(raw_message: str) -> str:
    """Turn backend registration errors into user-friendly text."""
    if "telegram_id" in raw_message and "already exists" in raw_message:
        return (
            "⚠️ <b>You are already registered!</b>\n\n"
            "Use your driver code to log in.\n\n"
            "👇 Press /start to log in"
        )
    if "phone_number" in raw_message and "already" in raw_message:
        return (
            "⚠️ <b>This phone number is already registered!</b>\n\n"
            "Enter a different number or log in via /start."
        )
    if "car_number" in raw_message and "already" in raw_message:
        return (
            "⚠️ <b>This car number is already registered!</b>\n\n"
            "Enter a different car number or contact us via /start."
        )
    return "❌ <b>Registration failed.</b>\n\nPlease try again or press /start."
