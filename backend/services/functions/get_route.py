import logging

import requests

from .osrm_base_url import osrm_base_url

logger = logging.getLogger(__name__)


def get_route(start_lat, start_lon, end_lat, end_lon):
    """
    Road route between two points via OSRM.
    Returns {"status": "success", "duration_minutes", "distance_km", "geometry" (GeoJSON LineString)}
    or {"status": "error", "message"}.
    """
    # OSRM expects lon,lat (reversed!)
    url = f"{osrm_base_url()}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
    params = {"overview": "full", "geometries": "geojson", "steps": "false", "annotations": "false"}

    try:
        response = requests.get(url, params=params, timeout=5)
    except requests.Timeout:
        logger.error("OSRM request timed out")
        return {"status": "error", "message": "The routing server did not respond. Please try again."}
    except requests.RequestException as e:
        logger.error(f"Failed to connect to OSRM: {e}")
        return {"status": "error", "message": "Could not connect to the routing server."}

    if response.status_code != 200:
        logger.warning(f"OSRM HTTP error: {response.status_code} - {response.text}")
        return {"status": "error", "message": f"OSRM server error: {response.status_code}"}

    data = response.json()
    if data.get("code") != "Ok":
        logger.warning(f"OSRM error code: {data.get('code')} - {data.get('message')}")
        return {"status": "error", "message": f"Route not found: {data.get('message')}"}

    route = data["routes"][0]
    return {
        "status": "success",
        "duration_minutes": round(route["duration"] / 60, 1),
        "distance_km": round(route["distance"] / 1000, 2),
        "geometry": route["geometry"],
    }
