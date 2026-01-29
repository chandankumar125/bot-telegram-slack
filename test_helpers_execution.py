
import os
import sys
import logging
from dotenv import load_dotenv

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

# Load Env
load_dotenv()

# Import helpers
from helpers.telegram_api import get_telegram_me, send_telegram_message, set_telegram_webhook
from helpers.slack_api import publish_slack_message, verify_slack_request, get_slack_user_info
from helpers.whatsapp_api import verify_whatsapp_signature, send_whatsapp_message

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_results.log", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_telegram():
    logger.info("--- Testing Telegram Helper ---")
    try:
        # 1. Get Me
        logger.info("1. Testing get_telegram_me...")
        me = get_telegram_me()
        logger.info(f"   Success! Bot Name: {me.get('result', {}).get('username')}")

        # 2. Send Message (using ID from db.json if available)
        # Found in db.json: chat_id "5530989549"
        test_chat_id = "5530989549" 
        logger.info(f"2. Testing send_telegram_message to {test_chat_id}...")
        res = send_telegram_message(test_chat_id, "🔔 This is a test message from the new Helper API integration.")
        logger.info(f"   Success! Message ID: {res.get('result', {}).get('message_id')}")
        
    except Exception as e:
        logger.error(f"   Telegram Test Failed: {e}")

def test_slack():
    logger.info("\n--- Testing Slack Helper ---")
    try:
        # We need a token. We can use SLACK_BOT_TOKEN from env or the one from db.json
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            logger.warning("   Skipping Slack live calls: SLACK_BOT_TOKEN not found in env.")
        else:
            # 1. auth test (via user info?) 
            # We'll try to get info for the bot user itself if we knew 'U0A9H5GBUNL' or a user 'U0A8LC3ELP8'
            test_user_id = "U0A8LC3ELP8"
            logger.info(f"1. Testing get_slack_user_info for {test_user_id}...")
            user_info = get_slack_user_info(token, test_user_id)
            if user_info.get("ok"):
                logger.info(f"   Success! User: {user_info['user']['real_name']}")
            else:
                logger.error(f"   Failed to get user info: {user_info.get('error')}")

            # 2. Publish Message
            logger.info(f"2. Testing publish_slack_message to {test_user_id}...")
            res = publish_slack_message(token, test_user_id, "🔔 This is a test message from the new Helper API.")
            if res.get("ok"):
                logger.info(f"   Success! Timestamp: {res.get('ts')}")
            else:
                logger.error(f"   Failed to publish message: {res.get('error')}")

        # 3. Verify Signature (Local Check)
        logger.info("3. Testing verify_slack_request (Local logic)...")
        # specific dummy secret
        dummy_secret = "8f742231b10e8888abcd99yyy"
        # timestamp
        ts = str(int(1000000000)) # old timestamp
        # body
        body = "foo=bar"
        # We expect this to fail usually because timestamp is too old, or just verify the function returns boolean
        # Let's mock the timestamp check inside or just pass a current timestamp
        import time
        current_ts = str(int(time.time()))
        # calculate signature manually to verify 'True' case
        import hmac, hashlib
        basestring = f"v0:{current_ts}:{body}"
        sig = "v0=" + hmac.new(dummy_secret.encode(), basestring.encode(), hashlib.sha256).hexdigest()
        
        is_valid = verify_slack_request(body, current_ts, sig, signing_secret=dummy_secret)
        logger.info(f"   Signature Verification Result (Expected True): {is_valid}")

    except Exception as e:
        logger.error(f"   Slack Test Failed: {e}")

def test_whatsapp():
    logger.info("\n--- Testing WhatsApp Helper ---")
    try:
        # 1. Verify Signature (Local Check)
        logger.info("1. Testing verify_whatsapp_signature (Local logic)...")
        dummy_secret = "mysecret"
        body = '{"object":"whatsapp_business_account"}'
        import hmac, hashlib
        expected_sig = "sha256=" + hmac.new(dummy_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        
        is_valid = verify_whatsapp_signature(body, expected_sig, app_secret=dummy_secret)
        logger.info(f"   Signature Verification Result (Expected True): {is_valid}")
        
        # 2. Send Message (skip if no number)
        # We don't have a known safe number to spam. We will skip live send.
        logger.info("2. Skipping live send_whatsapp_message to avoid messaging random numbers.")

    except Exception as e:
        logger.error(f"   WhatsApp Test Failed: {e}")

if __name__ == "__main__":
    test_telegram()
    test_slack()
    test_whatsapp()
