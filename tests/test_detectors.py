import unittest

from ghsecret.detectors import scan_text


class DetectorTests(unittest.TestCase):
    def test_github_token(self):
        findings = scan_text('token = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"', 'x.py')
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].secret_type, 'GitHub Token')
        self.assertNotIn('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', findings[0].preview)

    def test_aws_key(self):
        findings = scan_text('AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF')
        self.assertEqual(findings[0].secret_type, 'AWS Access Key')

    def test_generic_secret(self):
        findings = scan_text('API_KEY = "this_is_a_long_secret_value_123"')
        self.assertEqual(len(findings), 1)

    def test_placeholder_is_ignored(self):
        findings = scan_text('API_KEY=your_api_key')
        self.assertEqual(findings, [])

    def test_private_key(self):
        findings = scan_text('-----BEGIN PRIVATE KEY-----')
        self.assertEqual(findings[0].secret_type, 'Privater Schlüssel')

    def test_jwt(self):
        findings = scan_text('token=eyJabcdefghij.klmnopqrst.uvwxyzABCDE')
        self.assertEqual(findings[0].secret_type, 'JWT')


if __name__ == '__main__':
    unittest.main()
