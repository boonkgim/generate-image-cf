"""Offline CLI regression checks; never call the live inference API."""
import base64
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

spec = importlib.util.spec_from_file_location(
    'generate_image', Path(__file__).resolve().parents[1] / 'scripts/generate_image.py'
)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class GenerateImageTests(unittest.TestCase):
    def run_cli(self, response=None, error=None, model=None):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'output.png'
            args = ['generate_image.py', 'A red fox', str(output)]
            if model:
                args.append(model)
            with patch.object(app.sys, 'argv', args), patch.dict(
                app.os.environ,
                {'CLOUDFLARE_ACCOUNT_ID': 'test-account', 'CLOUDFLARE_API_TOKEN': 'test-token'},
                clear=True,
            ), patch.object(app, 'call_model', return_value=response, side_effect=error) as call:
                if error:
                    with self.assertRaises(SystemExit) as result:
                        app.main()
                    self.assertFalse(output.exists())
                    message = str(result.exception)
                else:
                    with patch('sys.stdout', new_callable=io.StringIO):
                        app.main()
                    message = output.read_bytes()
                call.assert_called_once_with(
                    'test-account', 'test-token', model or app.DEFAULT_MODEL, 'A red fox'
                )
                return message

    def test_quota_exhaustion_does_not_retry_default_or_explicit_model(self):
        for model in [None, '@cf/example/explicit-model']:
            with self.subTest(model=model):
                error = HTTPError('https://example.invalid', 429, 'quota', {}, io.BytesIO(
                    json.dumps({'errors': [{'code': 4006}]}).encode()
                ))
                message = self.run_cli(error=error, model=model)
                self.assertIn('allocation exhausted', message)
                self.assertIn('No fallback was attempted', message)

    def test_other_errors_are_reported_without_retry(self):
        for status, body in [(429, b'{"errors":[{"code":9999}]}'),
                             (401, b'unauthorised'), (429, b'not JSON')]:
            with self.subTest(status=status, body=body):
                message = self.run_cli(error=HTTPError(
                    'https://example.invalid', status, 'error', {}, io.BytesIO(body)
                ))
                self.assertIn(f'Cloudflare API error ({status})', message)

    def test_raw_image_is_saved(self):
        self.assertEqual(self.run_cli(response=('image/png', b'image-bytes')), b'image-bytes')

    def test_base64_image_is_saved(self):
        body = json.dumps({'success': True, 'result': {
            'image': base64.b64encode(b'image-bytes').decode()
        }}).encode()
        self.assertEqual(self.run_cli(response=('application/json', body)), b'image-bytes')


if __name__ == '__main__':
    unittest.main()
