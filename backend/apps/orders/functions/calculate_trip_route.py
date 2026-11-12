import json
import logging

from django.contrib.gis.geos import GEOSGeometry

from services import get_route

from .haversine_km import haversine_km

logger = logging.getLogger(__name__)


def calculate_trip_route(pickup_lat, pickup_lon, destination_lat, destination_lon):
    """
    Trip distance (km) and route line: the real road route via OSRM first;
    if that fails, the straight-line (Haversine) distance and no line (None).
    """
    route_info = get_route(
        start_lat=float(pickup_lat), start_lon=float(pickup_lon),
        end_lat=float(destination_lat), end_lon=float(destination_lon),
    )
    if route_info.get("status") != "success":
        return haversine_km(pickup_lat, pickup_lon, destination_lat, destination_lon), None

    line = None
    geometry = route_info.get("geometry")
    if geometry:
        try:
            line = GEOSGeometry(json.dumps(geometry), srid=4326)
        except Exception:
            # The line is only extra information - if it is broken, still create the order
            logger.warning("Could not parse OSRM geometry", exc_info=True)
    return float(route_info["distance_km"]), line
