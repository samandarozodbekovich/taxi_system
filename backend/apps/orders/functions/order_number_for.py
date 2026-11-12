def order_number_for(order_id):
    """Order number derived from the id: TX-000123. The id is unique, so no collisions."""
    return f"TX-{order_id:06d}"
