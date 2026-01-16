"""
Send test notification to WhatsApp
"""
import requests
import sys
from config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN

def send_test_notification(phone_number: str, title: str = "Test Notification", summary: str = "This is a test message"):
    """Send test notification via WhatsApp"""
    
    if not WHATSAPP_PHONE_NUMBER_ID or not WHATSAPP_ACCESS_TOKEN:
        print("ERROR: WhatsApp credentials are not set in .env file")
        print()
        print("Required:")
        print("  WHATSAPP_PHONE_NUMBER_ID=...")
        print("  WHATSAPP_ACCESS_TOKEN=...")
        return False
    
    # Format phone number (remove spaces, ensure + prefix)
    phone_number = phone_number.replace(" ", "").replace("-", "")
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    
    api_url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    message = f"*{title}*\n{summary}"
    
    print("=" * 60)
    print("Sending WhatsApp Test Notification")
    print("=" * 60)
    print()
    print(f"To: {phone_number}")
    print(f"Message: {message}")
    print()
    
    try:
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Message sent!")
            print()
            print(f"Message ID: {result.get('messages', [{}])[0].get('id', 'N/A')}")
            return True
        else:
            print(f"ERROR: Failed to send message")
            print(f"Status Code: {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Response: {response.text}")
            
            if response.status_code == 403:
                print()
                print("Possible issues:")
                print("  - Phone number not verified in Meta Dashboard")
                print("  - Access token expired or invalid")
                print("  - Phone number not in allowed list (for test mode)")
                print("  - Rate limit exceeded")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python send_test_notification_whatsapp.py <phone_number> [title] [summary]")
        print()
        print("Example:")
        print("  python send_test_notification_whatsapp.py +1234567890")
        print("  python send_test_notification_whatsapp.py +1234567890 'Server Alert' 'CPU usage is high'")
        print()
        print("Phone number format:")
        print("  - Include country code with + prefix")
        print("  - Example: +1234567890 (US) or +919876543210 (India)")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "Test Notification"
    summary = sys.argv[3] if len(sys.argv) > 3 else "This is a test message from your WhatsApp bot"
    
    success = send_test_notification(phone_number, title, summary)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
