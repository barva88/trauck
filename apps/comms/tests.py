from django.test import TestCase, Client, override_settings
from django.urls import reverse
import hmac, hashlib, json


def _sign(body: bytes, secret: str):
    return hmac.new(secret.encode('utf-8'), body, hashlib.sha256).hexdigest()


@override_settings(RETELL_WEBHOOK_SECRET='testsecret')
class RetellWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('comms:retell_webhook')

    def _payload(self, idem='k1'):
        return {
            'source': 'retell',
            'version': '1',
            'event': 'message_created',
            'conversation': {
                'conversation_id': 'conv-123',
                'agent_id': 'agent-1',
                'channel': 'chat',
                'language': 'es'
            },
            'message': {
                'message_id': 'm-1',
                'role': 'user',
                'text': 'hola',
                'timestamp_iso': '2024-01-01T00:00:00Z'
            },
            'meta': {'idempotency_key': idem}
        }

    def test_signature_fail(self):
        body = json.dumps(self._payload()).encode('utf-8')
        res = self.client.post(self.url, data=body, content_type='application/json', HTTP_X_SIGNATURE='bad')
        self.assertEqual(res.status_code, 401)

    def test_signature_ok_and_idempotent(self):
        body = json.dumps(self._payload('kA')).encode('utf-8')
        sig = _sign(body, 'testsecret')
        res1 = self.client.post(self.url, data=body, content_type='application/json', HTTP_X_SIGNATURE=sig)
        self.assertEqual(res1.status_code, 200)
        res2 = self.client.post(self.url, data=body, content_type='application/json', HTTP_X_SIGNATURE=sig)
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res2.json().get('duplicate'))
