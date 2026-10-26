import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qx_audit', ROOT / 'tools/check_qx_config.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class QXValidationTests(unittest.TestCase):
    def test_native_rules_accept_supported_network_modifiers(self):
        self.assertEqual(audit.validate_filters(
            'host-suffix, example.com, Test\n'
            'ip-cidr, 192.0.2.0/24, direct, via-interface=%TUN%\n'
            'final, Test\n', local=True, policies={'Test'}), 3)

    def test_foreign_filter_types_and_options_are_not_accepted(self):
        for text in ['PROCESS-NAME, com.apple.Maps, direct',
                     'URL-REGEX, /path, reject',
                     'AND,((PROTOCOL,UDP),(DOMAIN-SUFFIX,example.com)),reject',
                     'ip-cidr, 192.0.2.0/24, direct, no-resolve']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                audit.validate_filters(text)

    def test_policy_reference_and_final_position_are_checked(self):
        with self.assertRaisesRegex(ValueError, 'undefined'):
            audit.validate_filters('host, example.com, Missing', policies={'Test'})
        for text in ['host, example.com, direct',
                     'final, direct\nhost, example.com, direct',
                     'final, direct\nfinal, proxy']:
            with self.assertRaisesRegex(ValueError, 'exactly one final'):
                audit.validate_filters(text, local=True)

    @unittest.skipUnless(shutil.which('node'), 'Node.js required for parser execution')
    def test_conversion_warnings_fail_even_when_remaining_output_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            config = directory / 'qx.conf'
            config.write_text('[general]\nresource_parser_url=https://example.com/parser.js\n'
                              '[policy]\nstatic=Test,direct\n[filter_remote]\n'
                              'https://example.com/rules, force-policy=Test, opt-parser=true\n'
                              '[filter_local]\nfinal, Test\n')
            parser = directory / 'parser.js'
            parser.write_text('$notify("Unsupported PROCESS-NAME", "", "");'
                              '$done({content:"host, example.com, direct"});')
            rules = directory / 'rules.txt'
            rules.write_text('DOMAIN,example.com\nPROCESS-NAME,Example\n')
            def downloaded(url, _cache):
                path = parser if url.endswith('.js') else rules
                return {'url': url, 'snapshot': str(path), 'status': 200}
            with patch.object(audit, 'download', side_effect=downloaded):
                result = audit.audit(config, directory / 'cache')
            self.assertEqual(result['passed'], 0)
            self.assertEqual(result['resources'][0]['notifications'][0][0],
                             'Unsupported PROCESS-NAME')

    @unittest.skipUnless(shutil.which('node'), 'Node.js required for parser execution')
    def test_parser_context_has_no_file_or_network_capabilities(self):
        import subprocess
        result = subprocess.run(['node', str(ROOT / 'tools/parse_qx_resources.cjs')],
                                input=json.dumps({
                                    'parser': 'if(typeof require!=="undefined" || typeof fetch!=="undefined" || typeof process!=="undefined") throw Error("I/O exposed"); $done({content:$resource.content});',
                                    'resources': [{'url': 'https://example.com', 'tag': 'Test',
                                                   'parser': True, 'content': 'host, example.com, direct'}],
                                }), capture_output=True, text=True, check=True)
        self.assertIsNone(json.loads(result.stdout)[0]['error'])


if __name__ == '__main__':
    unittest.main()
