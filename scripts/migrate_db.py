import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
# this is for test pupose for postgress

def run_migration():
    print("Running database migration...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # 1. Drop existing strict unique constraints
        print("- Dropping strict unique constraints...")
        cursor.execute("ALTER TABLE slack_user_connections DROP CONSTRAINT IF EXISTS slack_user_connections_user_id_key;")
        cursor.execute("ALTER TABLE slack_user_connections DROP CONSTRAINT IF EXISTS slack_user_connections_slack_user_id_key;")
        
        # 2. Add partial unique indexes (Ensures only ONE active connection per user/slack_id)
        # This allows history (many is_connected = FALSE rows) but only one active.
        print("- Creating partial unique indexes...")
        cursor.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'idx_active_user') THEN
                    CREATE UNIQUE INDEX idx_active_user ON slack_user_connections (user_id) WHERE is_connected = TRUE;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'idx_active_slack') THEN
                    CREATE UNIQUE INDEX idx_active_slack ON slack_user_connections (slack_user_id) WHERE is_connected = TRUE;
                END IF;
            END $$;
        """)
        
        conn.commit()
        print("✅ Migration successful!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    run_migration()
