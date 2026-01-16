"""
Check WhatsApp Business API setup
"""
import requests
from config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_VERIFY_TOKEN
import sys

def check_credentials():
    """Check if credentials are set"""
    print("=" * 60)
    print("WhatsApp Business API Setup Checker")
    print("=" * 60)
    print()
    
    issues = []
    
    if not WHATSAPP_PHONE_NUMBER_ID:
        print("[ERROR] WHATSAPP_PHONE_NUMBER_ID is not set in .env file")
        issues.append("WHATSAPP_PHONE_NUMBER_ID")
    else:
        print(f"[OK] WHATSAPP_PHONE_NUMBER_ID is set: {WHATSAPP_PHONE_NUMBER_ID}")
    
    if not WHATSAPP_ACCESS_TOKEN:
        print("[ERROR] WHATSAPP_ACCESS_TOKEN is not set in .env file")
        issues.append("WHATSAPP_ACCESS_TOKEN")
    else:
        # Mask token for security
        masked_token = WHATSAPP_ACCESS_TOKEN[:10] + "..." if len(WHATSAPP_ACCESS_TOKEN) > 10 else "***"
        print(f"[OK] WHATSAPP_ACCESS_TOKEN is set: {masked_token}")
    
    if not WHATSAPP_VERIFY_TOKEN:
        print("[ERROR] WHATSAPP_VERIFY_TOKEN is not set in .env file")
        issues.append("WHATSAPP_VERIFY_TOKEN")
    else:
        print(f"[OK] WHATSAPP_VERIFY_TOKEN is set: {WHATSAPP_VERIFY_TOKEN[:10]}...")
    
    print()
    
    if issues:
        print("=" * 60)
        print("SETUP REQUIRED")
        print("=" * 60)
        print("Please add the following to your .env file:")
        print()
        for issue in issues:
            if issue == "WHATSAPP_PHONE_NUMBER_ID":
                print(f"{issue}=123456789012345")
            elif issue == "WHATSAPP_ACCESS_TOKEN":
                print(f"{issue}=EAAxxxxxxxxxxxxx")
            elif issue == "WHATSAPP_VERIFY_TOKEN":
                print(f"{issue}=your_secure_verify_token")
        print()
        print("Get these from Meta Developer Dashboard:")
        print("  https://developers.facebook.com/apps/")
        print()
        return False
    
    return True

def check_api_connection():
    """Check if API connection works"""
    if not WHATSAPP_PHONE_NUMBER_ID or not WHATSAPP_ACCESS_TOKEN:
        return False
    
    api_url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}"
    
    try:
        response = requests.get(
            api_url,
            headers={"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("=" * 60)
            print("SUCCESS: WhatsApp API connection works!")
            print("=" * 60)
            print()
            print(f"Phone Number ID: {data.get('id', 'N/A')}")
            print(f"Display Phone Number: {data.get('display_phone_number', 'N/A')}")
            print(f"Verified Name: {data.get('verified_name', 'N/A')}")
            print()
            return True
        else:
            print("=" * 60)
            print("API CONNECTION ERROR")
            print("=" * 60)
            print(f"Status Code: {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Response: {response.text}")
            print()
            print("Possible issues:")
            print("  - Access token is invalid or expired")
            print("  - Phone number ID is incorrect")
            print("  - Token doesn't have required permissions")
            print()
            return False
            
    except requests.exceptions.RequestException as e:
        print("=" * 60)
        print("CONNECTION ERROR")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        return False

def check_server():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("[OK] Server is running on port 8000")
            return True
        else:
            print(f"[WARNING] Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[WARNING] Server is NOT running")
        print("   Start it with: uvicorn main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"[WARNING] Error checking server: {e}")
        return False

def main():
    print()
    
    # Check credentials
    if not check_credentials():
        sys.exit(1)
    
    # Check server
    server_ok = check_server()
    print()
    
    # Check API connection
    api_ok = check_api_connection()
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if not api_ok:
        print("[ERROR] API connection failed")
        print("   - Check your access token is valid")
        print("   - Verify phone number ID is correct")
        print("   - Ensure token has WhatsApp permissions")
        sys.exit(1)
    
    if not server_ok:
        print("[WARNING] Server is not running")
        print("   - Start server to receive webhooks")
        print("   - Command: uvicorn main:app --reload --port 8000")
    
    print("[SUCCESS] Basic setup is correct!")
    print()
    print("Next steps:")
    print("1. Start your server: uvicorn main:app --reload --port 8000")
    print("2. Start ngrok: .\\ngrok.exe http 8000")
    print("3. Configure webhook in Meta Dashboard:")
    print("   - URL: https://your-ngrok-url.ngrok.io/bot/whatsapp/webhook")
    print("   - Verify Token: (your WHATSAPP_VERIFY_TOKEN)")
    print("4. Subscribe to 'messages' field")
    print("5. Send a test message to your WhatsApp Business number")
    print()

if __name__ == "__main__":
    main()
