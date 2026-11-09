"""No network is used; provider request shape is validated with a fake transport."""
import json
import os
import unittest
from unittest.mock import patch
from factory_control.providers import OpenAITextProvider, GeminiInteractionProvider


class FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, limit): return json.dumps({'output': [{'content': [{'type': 'output_text', 'text': 'Review ready'}]}]}).encode()


class ProviderTests(unittest.TestCase):
    def test_key_required(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'OPENAI_MODEL'):
                OpenAITextProvider()
        with patch.dict(os.environ, {'OPENAI_MODEL': 'test-model'}, clear=True):
            with self.assertRaisesRegex(ValueError, 'OPENAI_API_KEY'):
                OpenAITextProvider()

    @patch('factory_control.providers.urllib.request.urlopen')
    def test_opt_in_text_only_request(self, opener):
        opener.return_value = FakeResponse()
        p = OpenAITextProvider(model='test-model', api_key='test-key')
        generated = p.generate('research', 'draft plan', 'objective', 'context')
        self.assertEqual(generated.text, 'Review ready')
        self.assertFalse(generated.simulated)
        request = opener.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(body['store'], False)
        self.assertNotIn('tools', body)
        self.assertEqual(body['max_output_tokens'], 900)
        self.assertEqual(request.full_url, 'https://api.openai.com/v1/responses')


class FakeGeminiResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, limit):
        return json.dumps({'steps': [{'type': 'model_output', 'content': [{'type': 'text', 'text': 'Gemini draft'}]}]}).encode()


class GeminiProviderTests(unittest.TestCase):
    @patch('factory_control.providers.urllib.request.urlopen')
    def test_gemini_interactions_api_stateless_and_no_tools(self, opener):
        opener.return_value = FakeGeminiResponse()
        provider = GeminiInteractionProvider(model='test-model', api_key='test-key')
        out = provider.generate('research', 'review', 'objective', 'context')
        self.assertEqual(out.text, 'Gemini draft')
        self.assertFalse(out.simulated)
        req = opener.call_args.args[0]
        self.assertEqual(req.full_url, 'https://generativelanguage.googleapis.com/v1beta/interactions')
        data = json.loads(req.data)
        self.assertEqual(data['store'], False)
        self.assertNotIn('tools', data)
        self.assertEqual(data['model'], 'test-model')
        self.assertIn('X-goog-api-key', req.headers)

    def test_gemini_missing_secrets_and_model_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'GEMINI_MODEL'):
                GeminiInteractionProvider()
            with self.assertRaisesRegex(ValueError, 'GEMINI_API_KEY'):
                GeminiInteractionProvider(model='test-model')
            with self.assertRaisesRegex(ValueError, 'GEMINI_MODEL'):
                GeminiInteractionProvider(model='../../invalid', api_key='dummy')


if __name__ == '__main__': unittest.main()
