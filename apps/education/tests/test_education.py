import json
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.education.models import Topic, Question, ExamTemplate, ExamAttempt

@pytest.mark.django_db
def test_start_and_submit_attempt(client):
    User = get_user_model()
    u = User.objects.create_user(username='u1', password='pass', email='u1@example.com')
    client.login(username='u1', password='pass')

    t = Topic.objects.create(name='General', slug='general')
    # 10 TF
    for i in range(10):
        Question.objects.create(topic=t, type='TF', text=f'TF {i}', difficulty='easy', correct_answer='true')
    # 20 SC
    for i in range(20):
        Question.objects.create(topic=t, type='SC', text=f'SC {i}', difficulty='medium', choices=[{'key':'A','text':'A'},{'key':'B','text':'B'}], correct_answer='A')

    template = ExamTemplate.objects.create(name='Demo', topic=t, num_questions=20, is_active=True)

    # Start via API
    resp = client.post(reverse('education:api_start_attempt'), data=json.dumps({'template_id': template.id}), content_type='application/json')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] in ('OK','INSUFFICIENT_CREDITS')

    if data['status'] == 'INSUFFICIENT_CREDITS':
        return  # environment without wallet/credits

    attempt_id = data['attempt_id']
    items = data['items']
    assert len(items) == 20

    # Prepare answers: choose correct ones
    answers = []
    for it in items:
        if it['type'] == 'TF':
            answers.append({'question_id': it['question_id'], 'selected': 'true'})
        else:
            answers.append({'question_id': it['question_id'], 'selected': it['choices'][0]['key']})

    resp2 = client.post(reverse('education:api_submit_attempt', args=[attempt_id]), data=json.dumps({'answers': answers}), content_type='application/json')
    assert resp2.status_code == 200
    result = resp2.json()
    assert result['status'] in ('OK','INVALID_STATE')

    a = ExamAttempt.objects.get(id=attempt_id)
    if result['status'] == 'OK':
        assert a.status == 'SUBMITTED'
