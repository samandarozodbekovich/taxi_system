import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

TEST_BOT_TOKEN = "123456:TEST-TOKEN"


def make_init_data(telegram_id, bot_token=TEST_BOT_TOKEN, auth_date=None):
    """Build Mini App initData signed the same way Telegram signs it."""
    fields = {
        "query_id": "AAHtest",
        "user": json.dumps({"id": telegram_id, "first_name": "Test"}),
        "auth_date": str(int(auth_date if auth_date is not None else time.time())),
    }
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)
