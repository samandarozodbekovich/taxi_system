from apps.drivers.authentication import DriverTokenAuthentication
from apps.drivers.permissions import IsDriver


class DriverAuthMixin:
    """For driver endpoints: access only with a valid token."""
    authentication_classes = [DriverTokenAuthentication]
    permission_classes = [IsDriver]
