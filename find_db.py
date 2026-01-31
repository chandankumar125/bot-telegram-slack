import psycopg2
import socket

def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

print("Scanning for PostgreSQL ports on localhost...")
found_port = None
for port in range(5430, 5440):
    if check_port('localhost', port):
        print(f"✅ Found open port: {port}")
        found_port = port
    else:
        pass
        # print(f"Closed: {port}")

if not found_port:
    print("❌ No open ports found in range 5430-5440 on localhost.")
    print("The database might be on a remote host (e.g., AWS RDS, Supabase) or a different IP.")
else:
    print(f"\nAttempting to connect to 'adscale' database on port {found_port}...")
    users = ['postgres', 'adsparkx', 'root', 'admin']
    passwords = ['root', 'password', 'postgres', 'adscale', 'admin']
    
    for user in users:
        for pwd in passwords:
            try:
                conn = psycopg2.connect(
                    host='localhost',
                    port=found_port,
                    user=user,
                    password=pwd,
                    database='adscale'
                )
                print(f"✅ SUCCESS! Connected with: User='{user}', Password='{pwd}', Port={found_port}, DB='adscale'")
                conn.close()
                exit()
            except psycopg2.OperationalError as e:
                # print(f"Failed with {user}/{pwd}: {e}")
                pass
            except Exception as e:
                print(e)

print("\n❌ Could not connect with common credentials. Please check PgAdmin Connection Properties.")
