
from main import app
from fastapi.routing import APIRoute

print("\n" + "="*50)
print("REGISTERED ROUTES:")
print("="*50)
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"{route.methods} {route.path}")
print("="*50 + "\n")
