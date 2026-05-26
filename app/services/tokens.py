import os

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

VERIFY_SALT = "booking-verify"
DECIDE_SALT = "booking-decide"

VERIFY_TTL_SECONDS = 24 * 60 * 60
DECIDE_TTL_SECONDS = 7 * 24 * 60 * 60


def _serializer() -> URLSafeTimedSerializer:
    secret = os.environ["BOOKING_TOKEN_SECRET"]
    return URLSafeTimedSerializer(secret)


def make_verify_token(booking_id: int) -> str:
    return _serializer().dumps(booking_id, salt=VERIFY_SALT)


def make_decide_token(booking_id: int, action: str) -> str:
    return _serializer().dumps({"id": booking_id, "action": action}, salt=DECIDE_SALT)


def read_verify_token(token: str) -> int | None:
    try:
        return _serializer().loads(token, salt=VERIFY_SALT, max_age=VERIFY_TTL_SECONDS)
    except (BadSignature, SignatureExpired):
        return None


def read_decide_token(token: str) -> tuple[int, str] | None:
    try:
        payload = _serializer().loads(token, salt=DECIDE_SALT, max_age=DECIDE_TTL_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    return payload["id"], payload["action"]
