from functools import wraps
from sanic import text
from auth.token import check_token

def auth_route(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated = check_token(request)
            if is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text("You are unauthorized.", 401)
        return decorated_function
    return decorator(wrapped)
