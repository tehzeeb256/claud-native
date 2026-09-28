from fastapi.testclient import TestClient
from app.main import app

# Test client setup
client = TestClient(app)

# test root endpoint 
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "welcome" in data["message"].lower()
    