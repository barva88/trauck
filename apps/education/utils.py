import hmac
import hashlib


def verify_hmac_signature(request_body: bytes, header_signature: str, secret: str) -> bool:
    if not header_signature or not secret:
        return False
    mac = hmac.new(secret.encode('utf-8'), msg=request_body, digestmod=hashlib.sha256)
    expected = mac.hexdigest()
    try:
        return hmac.compare_digest(expected, header_signature)
    except Exception:
        return False
