import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the LLM service."}

def test_get_summary():
    response = client.post("/api/summary", json={"text": "This is a long text to be summarized."})
    assert response.status_code == 200
    assert "summary" in response.json()

def test_get_tags():
    response = client.post("/api/tagging", json={"text": "This is a text about cars and engines."})
    assert response.status_code == 200
    assert "tags" in response.json()

def test_get_emotion():
    response = client.post("/api/emotion", json={"text": "I am so happy today!"})
    assert response.status_code == 200
    json_response = response.json()
    assert "emotion" in json_response
    assert json_response["emotion"] in ["긍정", "부정", "중립"]

def test_get_emotion_negative():
    response = client.post("/api/emotion", json={"text": "This is a very bad experience."})
    assert response.status_code == 200
    json_response = response.json()
    assert "emotion" in json_response
    assert json_response["emotion"] == "부정"
