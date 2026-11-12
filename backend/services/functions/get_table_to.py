import logging

import requests

from .osrm_base_url import osrm_base_url

logger = logging.getLogger(__name__)


def get_table_to(sources, end_lat, end_lon):
    """
    Road travel time and distance from several points (drivers) to one point (client)
    in a SINGLE OSRM table request (N x 1 matrix).

    sources: [(lat, lon), ...]
    Returns [{"duration_minutes", "distance_km"} or None, ...] in sources order,
    or None if the request failed entirely.
    """
    if not sources:
        return []

    coords = ";".join(f"{lon},{lat}" for lat, lon in sources) + f";{end_lon},{end_lat}"
    params = {
        "sources": ";".join(str(i) for i in range(len(sources))),
        "destinations": str(len(sources)),
        "annotations": "duration,distance",
    }
    try:
        response = requests.get(f"{osrm_base_url()}/table/v1/driving/{coords}", params=params, timeout=5)
        data = response.json() if response.status_code == 200 else {}
    except (requests.RequestException, ValueError) as e:
        logger.error(f"OSRM table error: {e}")
        return None

    if data.get("code") != "Ok":
        logger.warning(f"OSRM table response: {response.status_code} - {data.get('code')} {data.get('message')}")
        return None

    return [
        None if duration is None or distance is None  # no route found
        else {"duration_minutes": round(duration / 60, 1), "distance_km": round(distance / 1000, 2)}
        for (duration,), (distance,) in zip(data["durations"], data["distances"])
    ]
