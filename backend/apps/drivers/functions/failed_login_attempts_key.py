def failed_login_attempts_key(driver_code, source):
    """Cache key counting failed login attempts for one driver code from one source (see login_source)."""
    return f"driver-login-fail:{str(driver_code).strip().upper()[:32]}:{source}"
