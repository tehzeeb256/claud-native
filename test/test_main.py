from fastapi.testclient import TestClient
from app.main import app

# Test client setup
client = TestClient(app)

