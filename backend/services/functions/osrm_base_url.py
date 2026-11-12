from django.conf import settings

# router.project-osrm.org is a demo server for testing only: its usage policy forbids production
# use and it is rate-limited. In production use your own OSRM server (.env: OSRM_BASE_URL).
OSRM_DEMO_URL = "https://router.project-osrm.org"


def osrm_base_url():
    return (getattr(settings, "OSRM_BASE_URL", "") or OSRM_DEMO_URL).rstrip("/")
