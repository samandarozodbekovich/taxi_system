import requests
import logging

logger = logging.getLogger(__name__)


class RoutingService:
    # Public OSRM demo server — free, no API key needed
    BASE_URL = "https://router.project-osrm.org/route/v1/driving"

    @classmethod
    def get_route(cls, start_lat, start_lon, end_lat, end_lon):
        """
        Calculate route between two points using OSRM.
        Coordinates format: lat/lon (floats)
        Returns: duration in minutes, distance in km, geometry (GeoJSON)
        """
        # OSRM expects: lon,lat (reversed from lat,lon!)
        url = f"{cls.BASE_URL}/{start_lon},{start_lat};{end_lon},{end_lat}"

        params = {
            "overview": "full",       # full route geometry
            "geometries": "geojson",  # GeoJSON format for frontend
            "steps": "false",
            "annotations": "false"
        }

        try:
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if data.get("code") != "Ok":
                    logger.warning(f"OSRM error code: {data.get('code')} — {data.get('message')}")
                    return {"status": "error", "message": f"Yo'nalish topilmadi: {data.get('message')}"}

                route = data["routes"][0]
                duration_seconds = route["duration"]   # seconds
                distance_meters  = route["distance"]   # meters
                geometry         = route["geometry"]   # GeoJSON LineString

                return {
                    "status": "success",
                    "duration_minutes": round(duration_seconds / 60, 1),
                    "distance_km": round(distance_meters / 1000, 2),
                    "geometry": geometry  # { "type": "LineString", "coordinates": [[lon, lat], ...] }
                }

            logger.warning(f"OSRM HTTP xatolik: {response.status_code} — {response.text}")
            return {"status": "error", "message": f"OSRM server xatolik: {response.status_code}"}

        except requests.Timeout:
            logger.error("OSRM so'rov vaqti tugadi (timeout)")
            return {"status": "error", "message": "Yo'nalish serveri javob bermadi. Qayta urinib ko'ring."}

        except requests.RequestException as e:
            logger.error(f"OSRM bilan bog'lanishda xatolik: {str(e)}")
            return {"status": "error", "message": "Yo'nalish serveriga ulanib bo'lmadi."}