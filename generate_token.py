
import jwt
import os
from dotenv import load_dotenv

# Load your actual .env file so we use the REAL secret
load_dotenv()

# Get secret from env (or fallback to what's in config.py)
SECRET = os.getenv("JWT_SECRET", "JWT_SECRET") 
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Create a token for User ID 1
payload = {"sub": "1"}
token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

print("\n" + "="*60)
print("🔑 YOUR GENERATED JWT TOKEN:")
print("-" * 60)
print(token)
print("-" * 60)
print("Copy the string above and paste it into Postman Authorization.")
print("="*60 + "\n")
