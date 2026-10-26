import importlib.util
from io import BytesIO
from pathlib import Path
import tempfile
from urllib.error import HTTPError
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('remote_rules', ROOT / 'tools/check_remote_rules.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Response(BytesIO):
    status = 200
    headers = {'Content-Type': 'text/plain'}


class RemoteRuleChecks(unittest.TestCase):
    def test_http_404_fails_even_when_a_local_resource_exists(self):
        path = next((ROOT / 'Rules').glob('Loon/SKK/*.list'))
        url = 'https://raw.githubusercontent.com/allen0039/proxy-resource-hub/main/' + str(path.relative_to(ROOT))
        with patch.object(checker, 'urlopen', side_effect=HTTPError(url, 404, 'missing', {}, None)) as request:
            result = checker.check_url(url)
        request.assert_called_once()
        self.assertFalse(result['ok'])
        self.assertEqual(result['status'], 404)

    def test_success_status_with_html_is_not_a_valid_rule(self):
        with patch.object(checker, 'urlopen', return_value=Response(b'<!DOCTYPE html><html>not found</html>')):
            self.assertFalse(checker.check_url('https://example.com/rules.list')['ok'])

    def test_native_text_and_yaml_are_downloaded_and_checked(self):
        for suffix, body in [('list', b'DOMAIN,example.com\n'), ('yaml', b'domain_set:\n  - example.com\n')]:
            with patch.object(checker, 'urlopen', return_value=Response(body)):
                self.assertTrue(checker.check_url('https://example.com/rules.' + suffix)['ok'])

    def test_undocumented_egern_fields_and_empty_payloads_are_rejected(self):
        for body in (b'process_name_set:\n  - Example\n', b'payload: []\n',
                     b'no_resolve: true\n', b'domain_set: example.com\n'):
            with patch.object(checker, 'urlopen', return_value=Response(body)):
                self.assertFalse(checker.check_url('https://example.com/rules.yaml')['ok'])

    def test_snapshot_is_the_downloaded_response_not_a_local_substitute(self):
        body = b'DOMAIN,live.example.com\n'
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(checker, 'urlopen', return_value=Response(body)) as request:
                result = checker.check_url('https://example.com/rules.list', cache_dir=directory)
            request.assert_called_once()
            self.assertEqual(Path(result['snapshot']).read_bytes(), body)
            self.assertEqual(len(result['sha256']), 64)

    def test_only_active_rule_sections_are_read(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'loon.lcf').write_text(
                '[Remote Proxy]\nhttps://private.example/nodes, enabled=true\n'
                '[Remote Rule]\nhttps://example.com/on.list, enabled=true\n'
                'https://example.com/off.list, enabled = false\n'
                '# https://example.com/comment.list\n')
            self.assertEqual(checker.collect_urls(directory),
                             {'https://example.com/on.list': ['loon.lcf']})


if __name__ == '__main__':
    unittest.main()
