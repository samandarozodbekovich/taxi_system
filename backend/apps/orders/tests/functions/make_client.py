from apps.clients.models import Client


def make_client(telegram_id):
    return Client.objects.create(
        telegram_id=telegram_id, full_name=f"Client {telegram_id}", phone_number=f"+998{telegram_id}"
    )
