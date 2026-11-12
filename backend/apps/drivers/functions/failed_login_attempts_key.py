def failed_login_attempts_key(driver_code):
    """Cache key counting failed login attempts for one driver code."""
    return f"driver-login-fail:{str(driver_code).strip().upper()[:32]}"
