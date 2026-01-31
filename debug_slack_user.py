import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

def debug_user_1():
    print(f"Connecting to {DB_HOST}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check User Connection
        print("\n--- Checking slack_user_connections for user_id='1' ---")
        cursor.execute("SELECT * FROM public.slack_user_connections WHERE user_id = '1'")
        user_row = cursor.fetchone()
        
        if not user_row:
            print("❌ No row found for user_id='1'")
        else:
            print("✅ User Row Found:")
            print(dict(user_row))
            if not user_row['is_connected']:
                print("⚠️  User exists but is_connected = False")

            # 2. Check Workspace
            workspace_id = user_row['workspace_id']
            print(f"\n--- Checking slack_workspaces for id={workspace_id} ---")
            cursor.execute("SELECT * FROM public.slack_workspaces WHERE id = %s", (workspace_id,))
            team_row = cursor.fetchone()
            
            if not team_row:
                print(f"❌ No workspace found for id={workspace_id}")
            else:
                print("✅ Workspace Row Found:")
                safe_team = dict(team_row)
                safe_team['access_token'] = safe_team['access_token'][:10] + "..." if safe_team['access_token'] else "None"
                safe_team['refresh_token'] = safe_team['refresh_token'][:10] + "..." if safe_team['refresh_token'] else "None"
                print(safe_team)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    debug_user_1()
