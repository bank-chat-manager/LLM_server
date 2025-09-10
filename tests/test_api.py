import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the LLM service."}

def test_get_summary():
    print("\n--- Testing Summary ---")
    payload = [
        {"speaker": "customer", "text": "This is a long text to be summarized."},
        {"speaker": "agent", "text": "I will summarize it for you."}
    ]
    response = client.post("/api/summary", json=payload)
    json_response = response.json()
    print(f"Response: {json_response}")
    assert response.status_code == 200
    assert "summary" in json_response

def test_get_tags():
    print("\n--- Testing Tagging ---")
    payload = [
        {"speaker": "customer", "text": "This is a text about cars and engines."},
        {"speaker": "agent", "text": "Let me find the keywords."}
    ]
    response = client.post("/api/tagging", json=payload)
    json_response = response.json()
    print(f"Response: {json_response}")
    assert response.status_code == 200
    assert "tags" in json_response

def test_get_emotion():
    print("\n--- Testing Emotion (Positive) ---")
    payload = [
        {"speaker": "customer", "text": "I am so happy today!"},
        {"speaker": "agent", "text": "That's great to hear!"}
    ]
    response = client.post("/api/emotion", json=payload)
    json_response = response.json()
    print(f"Response: {json_response}")
    assert response.status_code == 200
    assert "emotion" in json_response
    assert json_response["emotion"] in ["긍정", "부정", "중립"]

def test_get_emotion_negative():
    print("\n--- Testing Emotion (Negative) ---")
    payload = [
        {"speaker": "customer", "text": "This is a very bad experience."},
        {"speaker": "agent", "text": "I am sorry to hear that."}
    ]
    response = client.post("/api/emotion", json=payload)
    json_response = response.json()
    print(f"Response: {json_response}")
    assert response.status_code == 200
    assert "emotion" in json_response
    assert json_response["emotion"] == "부정"
