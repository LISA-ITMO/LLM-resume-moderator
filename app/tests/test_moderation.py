import pytest
from unittest.mock import patch

def test_moderation_success(client, mock_llm_response):
    with patch('manager.client.chat.completions.create', return_value=mock_llm_response):
        response = client.post(
            "/moderator/answer",
            json={
                "resume": {
                    "experience": "5 лет опыта работы Python разработчиком",
                    "job_title": "Senior Python Developer",
                    "education": "Высшее техническое образование",
                    "additional_education": "Курсы по машинному обучению"
                },
                "rules": None,
                "moderation_model": "T_it_1_0"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "OK"
        assert len(data["result"]["violated_rules"]) == 0
        assert "reasoning" in data

def test_moderation_violation(client, mock_llm_violation_response):
    with patch('manager.client.chat.completions.create', return_value=mock_llm_violation_response):
        response = client.post(
            "/moderator/answer",
            json={
                "resume": {
                    "experience": "",
                    "job_title": "Senior Python Developer",
                    "education": "Высшее техническое образование",
                    "additional_education": "Курсы по машинному обучению"
                },
                "rules": None,
                "moderation_model": "T_it_1_0"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "VIOLATION"
        assert len(data["result"]["violated_rules"]) == 1
        assert data["result"]["violated_rules"][0]["id"] == "rule_1"
        assert "reasoning" in data

def test_moderation_invalid_resume(client):
    response = client.post(
        "/moderator/answer",
        json={
            "resume": {
                "experience": "5 лет опыта работы Python разработчиком",
                "job_title": "Senior Python Developer",
                "education": "Высшее техническое образование"
                # missing additional_education field
            },
            "rules": None,
            "moderation_model": "T_it_1_0"
        }
    )
    
    assert response.status_code == 422  # Validation error

def test_moderation_invalid_model(client):
    response = client.post(
        "/moderator/answer",
        json={
            "resume": {
                "experience": "5 лет опыта работы Python разработчиком",
                "job_title": "Senior Python Developer",
                "education": "Высшее техническое образование",
                "additional_education": "Курсы по машинному обучению"
            },
            "rules": None,
            "moderation_model": "invalid_model"  # invalid model name
        }
    )
    
    assert response.status_code == 422
