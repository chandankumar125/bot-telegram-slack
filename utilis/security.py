import hmac, hashlib

def verify_slack_signature(secret, body, timestamp, signature):
    basestring = f"v0:{timestamp}:{body}"
    hash = "v0=" + hmac.new(
        secret.encode(), basestring.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(hash, signature)

def verify_whatsapp_signature(secret, body, signature):
    """
    Verifies the X-Hub-Signature-256 header from Meta/WhatsApp.
    Signature format: sha256=<hash>
    """
    if not signature.startswith("sha256="):
        return False
        
    expected_hash = "sha256=" + hmac.new(
        secret.encode(), body.encode(), hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_hash, signature)
