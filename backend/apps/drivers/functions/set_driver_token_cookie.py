from .create_driver_token import TOKEN_MAX_AGE

# The driver panel's login token lives in this HttpOnly cookie, never in JavaScript
# (localStorage could be read by any injected script)
DRIVER_TOKEN_COOKIE = "driver_token"


def set_driver_token_cookie(response, request, token):
    # Over HTTPS: SameSite=None, so it also works when Telegram Web shows the panel in an
    # iframe; DriverTokenAuthentication requires a custom header against CSRF.
    # Plain-http local development can't use SameSite=None (it needs Secure) - Lax there.
    secure = request.is_secure()
    response.set_cookie(
        DRIVER_TOKEN_COOKIE, token,
        max_age=TOKEN_MAX_AGE, path="/", httponly=True,
        secure=secure, samesite="None" if secure else "Lax",
    )
    return response
