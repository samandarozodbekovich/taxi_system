import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

INIT_DATA_MAX_AGE = 60 * 60 * 24  # 24 hours - the Mini App may stay open for a long time


def verify_telegram_init_data(init_data, bot_token, max_age=INIT_DATA_MAX_AGE):
    """
    Verify Telegram Mini App initData (HMAC-SHA256 with the bot token) and return the user dict.
    Raises ValueError if invalid. https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    except ValueError:
        raise ValueError("Malformed initData.")

    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise ValueError("initData has no hash.")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(pairs.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Invalid initData signature.")

    try:
        auth_date = int(pairs.get("auth_date", "0"))
    except ValueError:
        raise ValueError("Invalid auth_date.")
    if time.time() - auth_date > max_age:
        raise ValueError("initData has expired. Please reopen the app.")

    try:
        user = json.loads(pairs["user"])
        user["id"] = int(user["id"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("initData has no user data.")
    return user
