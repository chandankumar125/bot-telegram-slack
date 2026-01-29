
import requests
import json
import sys
import time

# CONFIGURATION
BASE_URL = "http://localhost:8000"
USER_ID = "VL_TEST_USER"  # Match your DB user
TEAM_NAME_EXPECTED = "Adsparkx"  # Match your expected team

def print_section(title):
    print("\n" + "#"*60)
    print(f"TEST SUITE: {title}")
    print("#"*60)

def print_step(name, status, detail=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name[:50]:<50} : {detail}")

# --- 1. HEALTH CHECK ---
def test_backend_health():
    print_section("Backend Connectivity")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_step("Backend Reachability", True, "200 OK")
        else:
            print_step("Backend Reachability", False, f"Status {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print_step("Backend Reachability", False, str(e))
        sys.exit(1)

# --- 2. AUTH FLOW TEST (REDIRECT) ---
def test_auth_redirect():
    print_section("Auth Flow Verification")
    url = f"{BASE_URL}/bot/slack/install?user_id={USER_ID}"
    try:
        # Don't follow redirect so we can check the 307
        response = requests.get(url, allow_redirects=False)
        
        if response.status_code == 307:
            location = response.headers.get('location', '')
            if "slack.com/oauth/v2/authorize" in location:
                print_step("/install Redirects to Slack", True, "Location header correct")
                if f"state={USER_ID}" in location:
                    print_step("State Parameter Preserved", True, f"Found {USER_ID} in url")
                else:
                    print_step("State Parameter Preserved", False, "User ID missing from state")
            else:
                print_step("/install Redirects to Slack", False, f"Wrong location: {location[:30]}...")
        else:
            print_step("Install Endpoint Status", False, f"Expected 307, got {response.status_code}")
            
    except Exception as e:
        print_step("Auth Flow Error", False, str(e))

# --- 3. CONNECTION STATUS TEST ---
def test_connection_status():
    print_section("Connection Status Check")
    url = f"{BASE_URL}/bot/slack/status?user_id={USER_ID}"
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("connected"):
            print_step("User Connected", True, f"Team: {data.get('team_name')}")
            # Verify data integrity
            if data.get("email") and data.get("slack_user_id"):
                 print_step("Data Integrity", True, "Email and Slack ID present")
            else:
                 print_step("Data Integrity", False, "Missing critical user info")
            
            # --- TOKEN ROTATION CHECK ---
            token = data.get("access_token")
            if token:
                if token.startswith("xoxe."):
                    print_step("Token Rotation Mode", True, "Enabled (Mode 2) - Token starts with xoxe.")
                else:
                    print_step("Token Rotation Mode", True, "Disabled (Mode 1) - Legacy Token (xoxb/xoxp)")
            else:
                print_step("Token Retrieval", False, "Access Token missing from status check")

            return True
        else:
            print_step("User Connected", False, "API says Not Connected")
            return False
            
    except Exception as e:
        print_step("Status Check Failed", False, str(e))
        return False

# --- 4. NOTIFICATION TEST ---
def test_notification_delivery():
    print_section("Notification Delivery System")
    url = f"{BASE_URL}/bot/notify"
    payload = {
        "user_id": USER_ID,
        "platform": "slack",
        "title": "Comprehensive Test",
        "summary": "This connects all the dots: Endpoints -> Logic -> Helper -> Slack API."
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if response.status_code == 200 and result.get("slack") == "sent":
            print_step("Send Notification", True, "Slack API received message")
        else:
             print_step("Send Notification", False, f"Result: {result}")
             
    except Exception as e:
        print_step("Notification Error", False, str(e))

# --- 5. DISCONNECT TEST (Dry Run / Optional) ---
def test_disconnect_logic():
    print_section("Disconnection Logic")
    # Note: We won't actually disconnect to preserve your test state, 
    # but we will check if the endpoint exists and accepts method.
    url = f"{BASE_URL}/bot/slack/disconnect"
    try:
        response = requests.options(url) # Check allowed methods or 405
        # FastAPI might return 405 for POST-only endpoints on OPTIONS, or 200.
        # Let's just try to hit it with a fake user to see if it responds correctly (404/False)
        
        fake_url = f"{BASE_URL}/bot/slack/disconnect?user_id=FAKE_USER_999"
        response = requests.post(fake_url)
        data = response.json()
        
        if response.status_code == 200 and data.get("ok") is False:
             print_step("Disconnect Endpoint Active", True, "Correctly handled non-existent user")
        else:
             print_step("Disconnect Endpoint Active", False, f"Unexpected response: {data}")

    except Exception as e:
         print_step("Disconnect Test Error", False, str(e))


if __name__ == "__main__":
    print(f"Running Comprehensive Slack Integration Tests on {BASE_URL}")
    print(f"Target User: {USER_ID}")
    
    test_backend_health()
    test_auth_redirect()
    
    is_connected = test_connection_status()
    
    if is_connected:
        test_notification_delivery()
        # test_disconnect_logic() # Uncomment to test disconnect logic safely
    else:
        print("\n🚫 Skipping Notification Test (User not connected)")
        print("👉 Please connect via Dashboard first to run full suite.")

    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
