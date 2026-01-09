import hmac, hashlib

def verify_slack_signature(secret, body, timestamp, signature):
    basestring = f"v0:{timestamp}:{body}"
    hash = "v0=" + hmac.new(
        secret.encode(), basestring.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(hash, signature)
