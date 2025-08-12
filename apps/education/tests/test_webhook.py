import json
import hmac
import hashlib
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.my_profile.models import Profile
from apps.education.models import ConversationalExamSession, ExamSessionTag


@override_settings(RETELL_WEBHOOK_SECRET='testsecret')
class RetellWebhookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username='alice', email='alice@example.com', password='pass1234')
        self.profile = Profile.objects.create(user=self.user, external_id='ext-alice')
        self.url = reverse('education_api:retell_exam_completed')

    def _payload(self, session_id='sess-1'):
        now = timezone.now()
        return {
            "session_id": session_id,
            "agent_id": "agent_trauck_cdl_v1",
            "user_external_id": self.profile.external_id,
            "channel": "web",
            "started_at": now.isoformat(),
            "ended_at": (now + timezone.timedelta(minutes=5)).isoformat(),
            "duration_seconds": 300,
            "exam": {
                "type": "cdl-mock",
                "score_total": 87.5,
                "score_scale": "percentage",
                "section_breakdown": [
                    {"section": "Regulations", "score": 45},
                    {"section": "Safety", "score": 42.5}
                ],
                "strengths": ["Regulations"],
                "weaknesses": ["Safety"]
            },
            "artifacts": {
                "transcript_url": "https://example.com/t/1",
                "recording_url": "https://example.com/r/1"
            },
            "communication": {"thread_id": "thread-123"},
            "tags": [
                {"key": "lang", "value": "en"},
                {"key": "level", "value": "advanced"}
            ]
        }

    def _sign(self, body_bytes: bytes) -> str:
        return hmac.new(b'testsecret', body_bytes, hashlib.sha256).hexdigest()

    def test_invalid_signature(self):
        body = json.dumps(self._payload()).encode('utf-8')
        res = self.client.post(self.url, data=body, content_type='application/json',
                               HTTP_X_RETELL_SIGNATURE='invalidsig')
        self.assertEqual(res.status_code, 401)

    def test_valid_signature_and_persistence(self):
        body = json.dumps(self._payload()).encode('utf-8')
        sig = self._sign(body)
        res = self.client.post(self.url, data=body, content_type='application/json',
                               HTTP_X_RETELL_SIGNATURE=sig)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(ConversationalExamSession.objects.count(), 1)
        session = ConversationalExamSession.objects.first()
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.profile, self.profile)
        self.assertEqual(session.tags.count(), 2)

    def test_idempotency(self):
        payload = self._payload(session_id='sess-unique')
        body = json.dumps(payload).encode('utf-8')
        sig = self._sign(body)
        res1 = self.client.post(self.url, data=body, content_type='application/json', HTTP_X_RETELL_SIGNATURE=sig)
        self.assertEqual(res1.status_code, 201)
        res2 = self.client.post(self.url, data=body, content_type='application/json', HTTP_X_RETELL_SIGNATURE=sig)
        self.assertIn(res2.status_code, (200, 201))
        self.assertEqual(ConversationalExamSession.objects.filter(retell_session_id='sess-unique').count(), 1)

    def test_read_endpoints_authenticated(self):
        payload = self._payload(session_id='sess-read')
        body = json.dumps(payload).encode('utf-8')
        sig = self._sign(body)
        self.client.post(self.url, data=body, content_type='application/json', HTTP_X_RETELL_SIGNATURE=sig)
        self.client.login(username='alice', password='pass1234')
        list_url = reverse('education_api:my_sessions')
        res = self.client.get(list_url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) >= 1)
        session_id = res.json()[0]['id']
        detail_url = reverse('education_api:session_detail', kwargs={'id': session_id})
        res_d = self.client.get(detail_url)
        self.assertEqual(res_d.status_code, 200)
