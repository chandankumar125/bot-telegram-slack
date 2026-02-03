import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.auth import create_state_token, verify_state_token

def test_auth_logic():
    print("Testing Security Token Logic...")
    
    test_user_id = "123"
    
    # 1. Generate Token
    token = create_state_token(test_user_id)
    print(f"Generated Token: {token[:20]}...")
    
    # 2. Verify Token
    verified_id = verify_state_token(token)
    print(f"Verified User ID: {verified_id}")
    
    if verified_id == test_user_id:
        print("✅ Token verification works!")
    else:
        print("❌ Token verification failed!")
        sys.exit(1)

    # 3. Test tampered token
    tampered_token = token[:-5] + "aaaaa"
    try:
        ver_tampered = verify_state_token(tampered_token)
        if ver_tampered is None:
            print("✅ Tampered token correctly rejected!")
        else:
            print("❌ Security vulnerability: Tampered token accepted!")
            sys.exit(1)
    except:
        print("✅ Tampered token caused error (Safe).")

if __name__ == "__main__":
    test_auth_logic()
