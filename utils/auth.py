import jwt
from fastapi import HTTPException, Header, Depends
from config import JWT_SECRET, JWT_ALGORITHM
import datetime

"""
Middleware/Auth Logic: Created utils/auth.py
which contains:
* verify_jwt(authorization): Decodes and validates the Authorization: Bearer <token> header.
* get_current_user(...) : A FastAPI dependency that extracts and returns the user_id from the valid token.
"""

def create_access_token(user_id: str):
    """
    Creates a JWT token for testing purposes.
    """
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7) # Expires in 7 days
    }
    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def verify_jwt(authorization: str = Header(None)):
    """
    Decodes and validates the Authorization: Bearer <token> header.
    Verifies the JWT token from the Authorization header.
    Expected format: "Bearer <token>"
    """
    if not authorization:
        # For now, we might allow non-authed strictly if we want to support legacy mixed mode,
        # but the user asked to "add jwt auth middleware".
        # If we raise 401 here, any route using this dependency becomes Strict Auth.
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
            
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
        
    except (ValueError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        # Note: PyJWT raises ExpiredSignatureError or InvalidTokenError
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
         raise HTTPException(status_code=401, detail=f"Authentication Error: {str(e)}")

def get_current_user(payload: dict = Depends(verify_jwt)):
    """
    Dependency to get the current user ID from the verified token.
    """
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user identification")
        
    # Ensure user_id is consistent (e.g. string vs int). B
    # Backend mostly uses Int but frontend sends strings. 
    # Let's keep it robust.
    return str(user_id)
