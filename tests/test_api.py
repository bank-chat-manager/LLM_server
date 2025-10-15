import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.anyio
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the LLM service."}

@pytest.mark.anyio
def test_get_summary():
     print("\n--- Testing Summary ---")
     with TestClient(app) as client:
        payload = [
            {"customer": "안녕하세요, 주택 담보 대출을 받으려고 하는데요. 필요 서류가 어떻게 되나요?"},
            {"agent": "네, 고객님. 주택 담보 대출 신청을 위해서는 신분증, 재직증명서, 그리고 소득증빙서류가 필요합니다."}
        ]
        response = client.post("/api/summary", json=payload)
        json_response = response.json()
        print(f"Response: {json_response}")
        assert response.status_code == 200
        assert "summary" in json_response


def test_get_tags():
    print("\n--- Testing Tagging ---")
    payload = [
        {"customer": "신용카드를 잃어버렸어요. 바로 분실 신고 좀 해주세요."},
        {"agent": "알겠습니다, 고객님. 즉시 분실 신고 처리해드리겠습니다. 카드 번호 뒤 4자리가 어떻게 되시나요?"}
    ]
    response = client.post("/api/tagging", json=payload)
    json_response = response.json()
    print(f"Response: {json_response}")
    assert response.status_code == 200
    assert "tags" in json_response

def test_get_emotion():
    print("\n--- Testing Emotion (Positive) ---")
    payload = [
        {"customer": "문제가 빨리 해결되어서 정말 다행이에요. 감사합니다!"},
        {"agent": "천만에요, 고객님. 다른 문의사항은 없으신가요?"}
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
        {"customer": "아니, 왜 수수료가 이렇게 많이 나왔죠? 이해가 안 가네요."},
        {"agent": "고객님, 죄송하지만 관련 규정에 따라 처리된 것으로 확인됩니다."}
    ]
    response = client.post("/api/emotion", json=payload)
    json_response = response.json()
    print(f"Response: {json_response}")
    assert response.status_code == 200
    assert "emotion" in json_response
    assert json_response["emotion"] == "부정"
