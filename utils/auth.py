import jwt
import datetime


def create_jwt(payload, secretkey, algorithm):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    return jwt.encode(payload, secretkey, algorithm=algorithm)


def parse_jwt(token, secretkey):
    try:
        payload = jwt.decode(token, secretkey, algorithms='HS256')
    except jwt.ExpiredSignatureError:
        return False, "令牌过期"
    except jwt.InvalidTokenError:
        return False, "非法的令牌"
    return True, payload
