
import sys
from main import app
from fastapi.routing import APIRoute

with open("registered_routes.txt", "w") as f:
    f.write("REGISTERED ROUTES:\n")
    f.write("="*50 + "\n")
    for route in app.routes:
        if isinstance(route, APIRoute):
            f.write(f"{route.methods} {route.path}\n")
    f.write("="*50 + "\n")

print("Routes written to registered_routes.txt")
