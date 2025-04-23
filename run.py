from waitress import serve
from app import app  # Ensure 'app' is your Flask instance

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8081)
