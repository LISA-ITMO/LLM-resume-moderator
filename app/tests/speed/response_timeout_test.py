import requests
import time

MODERATION_RULES = {
    "rules": [
    {
      "id": "rule_1",
      "condition": "Резюме должно содержать информацию о трудовой деятельности если желаемая должность требует опыта"
    },
    {
      "id": "rule_2",
      "condition": "Резюме должно содержать профессию/должность или должности, на которые претендует соискатель, должность должжна быть реальной профессией"
    },
    {
      "id": "rule_4",
      "condition": "Резюме должно быть заполнено на русском языке"
    },
    {
      "id": "rule_5",
      "condition": "Информация о работодателе не должна содержать сведений, не относящихся к работодателю, если работодатель ИП это не нарушение правил"
    },
    {
      "id": "rule_6",
      "condition": "Информация о резюме не должна содержать сведений, не относящихся к соискателю"
    },
    {
      "id": "rule_7",
      "condition": "Информация не должна содержать слова и выражения, не соответствующие нормам современного русского литературного языка, допустимы стилистические неточности, но главное чтобы не было матов и токсичности"
    }
    ],
    "moderation_model": "T_it_1_0"
}

API_URL = "http://localhost:8000/moderator/answer"

resumes = \
[
 {'Опыт_работы': '...',
  'ДПО': '...',
  'Образование': '...',
  'Должность': '...'},
 {'Опыт_работы': '...',
  'ДПО': '...',
  'Образование': '...',
  'Должность': '...'}]



def prepare_request(resume):
    return {
        **MODERATION_RULES,
        "resume": {
            "experience": resume.get("Опыт_работы", ""),
            "job_title": resume.get("Должность", ""),
            "education": resume.get("Образование", ""),
            "additional_education": resume.get("ДПО", "")
        }
    }

def test_moderation_speed(resumes):
    results = []
    total_time = 0
    
    for i, resume in enumerate(resumes):
        payload = prepare_request(resume)
        
        start_time = time.perf_counter()
        response = requests.post(API_URL, json=payload)
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time)
        total_time += duration_ms
        results.append((i, duration_ms))
        
        print(f"Резюме {i}: {duration_ms:.2f} с | Статус: {response.status_code}")
    
    avg_time = total_time / len(resumes) if resumes else 0
    
    with open("moderation_speed_results.txt", "w") as f:
        for idx, t in results:
            f.write(f"Запрос {idx}: {t:.2f} с\n")
        f.write(f"\nСреднее время: {avg_time:.2f} с")
    
    print(f"\nТестирование завершено. Результаты сохранены в moderation_speed_results.txt")
    print(f"Обработано резюме: {len(resumes)}")
    print(f"Среднее время ответа: {avg_time:.2f} с")

if __name__ == "__main__":
    test_moderation_speed(resumes)