import jwt
import env

def check_token(request):
    if not request.token:
        return False
    try:
        jwt.decode(request.token, env.env_jwt_secret(), algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True

def decode_token(token):
  return jwt.decode(token, env.env_jwt_secret(), algorithms=["HS256"])

def encode_token(payload={}):
  return jwt.encode(payload, env.env_jwt_secret())