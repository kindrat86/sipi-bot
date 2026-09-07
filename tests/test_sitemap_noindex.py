"""Offline regression coverage for noindex pages entering the sitemap."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rebuild_sitemap_under_test', ROOT / 'scripts/rebuild_sitemap.py')
assert spec is not None and spec.loader is not None
sitemap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sitemap)


class SitemapNoindexTests(unittest.TestCase):
    def test_noindex_proof_is_omitted_without_changing_the_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / 'public'
            proof = public / 'proof' / 'pa_fixture' / 'index.html'
            proof.parent.mkdir(parents=True)
            source = '<html><head><meta name="robots" content="noindex,nofollow"></head><body>Private replay proof</body></html>'
            proof.write_text(source)
            output = public / 'sitemap.xml'
            with patch.multiple(sitemap, ROOT=str(root), PUBLIC=str(public), SITEMAP=str(output)):
                sitemap.build_sitemap()
            urls = {x.text for x in ET.parse(output).getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
            self.assertNotIn('https://sipi.bot/proof/pa_fixture/', urls)
            self.assertIn('https://sipi.bot/', urls)
            self.assertEqual(proof.read_text(), source)


    def test_noindex_variants_and_served_mirrors_are_excluded(self):
        cases = {
            'public/private-google/index.html': '<meta CONTENT="NoIndex, follow" NAME="GoogleBot"/>',
            'public/private-none/index.html': '<meta name=robots content=none>',
            'public/private-late/index.html': '<!--' + 'x' * 20000 + '--><meta name=robots content=noindex>',
            'learn/private-root/index.html': '<meta name=robots content=noindex>',
            'learn/mirror/index.html': '<meta name=robots content=index>',
            'public/learn/mirror/index.html': '<meta name=robots content=noindex>',
            'public/open/index.html': '<meta name=robots content="index,follow">',
            'public/comment/index.html': '<!-- <meta name=robots content=noindex> -->',
            'public/script/index.html': '<script>const example = \'<meta name=robots content=noindex>\';</script>',
            'public/nofollow/index.html': '<meta name=robots content=nofollow>',
            'public/other-bot/index.html': '<meta name=bingbot content=noindex>',
            'public/text/index.html': '<p>Documentation about noindex and none.</p>',
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, source in cases.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source)
            output = root / 'public/sitemap.xml'
            with patch.multiple(sitemap, ROOT=str(root), PUBLIC=str(root / 'public'), SITEMAP=str(output)):
                sitemap.build_sitemap()
            # The XML is generated locally above from controlled test fixtures.
            urls = {x.text for x in ET.parse(output).getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
            for path in ('private-google/', 'private-none/', 'private-late/', 'learn/private-root', 'learn/mirror', 'learn/mirror/'):
                self.assertNotIn('https://sipi.bot/' + path, urls)
            for path in ('open/', 'comment/', 'script/', 'nofollow/', 'other-bot/', 'text/'):
                self.assertIn('https://sipi.bot/' + path, urls)
            for rel, source in cases.items():
                self.assertEqual((root / rel).read_text(), source)


if __name__ == '__main__':
    unittest.main()
