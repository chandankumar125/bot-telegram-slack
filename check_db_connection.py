import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
dbname = os.getenv("DB_NAME")

print(f"Attempting connection to: {host}:{port} as {user} for DB '{dbname}'...")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=dbname,
        connect_timeout=5
    )
    print("✅ Connection Successful!")
    conn.close()
except psycopg2.OperationalError as e:
    print("❌ Connection Failed (OperationalError):")
    print(str(e))
    if "password authentication" in str(e):
        print("\n👉 ACTION REQUIRED: The password in your .env file is incorrect. Please update DB_PASSWORD.")
except Exception as e:
    print("❌ Connection Failed:")
    print(e)
