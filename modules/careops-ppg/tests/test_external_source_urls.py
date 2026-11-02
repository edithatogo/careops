import unittest

from scripts.ppg_external_source_urls import official_source_url


class OfficialPublicationOrigins(unittest.TestCase):
    def test_explicit_exact_origins_preserve_paths_and_queries(self):
        url = 'https://updates.publisher.example/doc.pdf?record=A%2F1&v=2'
        with self.assertRaises(ValueError):
            official_source_url(url)
        self.assertEqual(official_source_url(url, ['updates.publisher.example']), url)
        self.assertEqual(official_source_url('https://meteor.aihw.gov.au/content/123'),
                         'https://meteor.aihw.gov.au/content/123')

    def test_unqualified_or_ambiguous_origins_are_refused(self):
        for url in ('https://updates.publisher.example.evil.test/file.pdf',
                    'https://other.publisher.example/file.pdf',
                    'https://user@updates.publisher.example/file.pdf',
                    'https://updates.publisher.example:444/file.pdf',
                    'http://updates.publisher.example/file.pdf',
                    'https://updates.publisher.example/file.pdf#fragment',
                    'https://updates.publisher.example/file.pdf ',
                    'https://updates.publisher.example/\tfile.pdf',
                    'https://updates.publisher.example/\x7ffile.pdf',
                    'https://updates.publisher.example/\\file.pdf'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                official_source_url(url, ['updates.publisher.example'])
        for value in (None, 1):
            with self.assertRaises(ValueError):
                official_source_url(value, ['updates.publisher.example'])
        with self.assertRaises(TypeError):
            official_source_url('https://publisher.example/a', 'publisher.example')
