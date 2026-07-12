import os

from fastapi.testclient import TestClient

os.environ["AI_MOCK_MODE"] = "true"

from edulearn.backend.main import app


client = TestClient(app)


def test_education_health_returns_healthy():
    response = client.get("/api/education/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "EduLearn AI Education Platform"


def test_generate_lesson_mock_happy_path():
    payload = {
        "learner_profile": {
            "learner_id": "smoke-1",
            "name": "Sam",
            "age": 9,
            "grade_level": "3rd",
        },
        "subject": "Math",
        "topic": "Addition",
        "duration_minutes": 20,
        "lesson_format": "visual",
    }

    response = client.post("/api/education/lesson/generate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["lesson"]["topic"] == "Addition"
