"""Vendored Schnapsen card drawings and static serving."""

import unittest
from pathlib import Path
from urllib.request import urlopen

from schnapsen.cards import RANKS, SUITS
from schnapsen.engine import new_match
from schnapsen.server import Table, make_server

CARDS = Path(__file__).resolve().parents[1] / "schnapsen" / "static" / "cards"
TOKENS = [f"{suit}-{rank}" for suit in SUITS for rank in RANKS]


class CardFaceFilesTests(unittest.TestCase):
    def test_twenty_faces_and_back_and_no_other_ranks(self):
        names = {path.name for path in CARDS.glob("*.svg")}
        expected = {f"{token}.svg" for token in TOKENS} | {"back.svg"}
        self.assertEqual(names, expected)
        self.assertNotIn("Herz-2.svg", names)

    def test_license_and_attribution_name_the_source(self):
        license_text = (CARDS / "LICENSE").read_text(encoding="utf-8")
        attribution = (CARDS / "ATTRIBUTION.md").read_text(encoding="utf-8")
        self.assertIn("GNU LESSER GENERAL PUBLIC LICENSE", license_text)
        self.assertIn("Version 2.1", license_text)
        self.assertIn("Bellot", attribution)
        self.assertIn("SVG-cards", attribution)
        self.assertIn("GNU Lesser General Public License", attribution)

    def test_preview_lists_every_token(self):
        preview = (CARDS / "preview.html").read_text(encoding="utf-8")
        for token in TOKENS:
            self.assertIn(token, preview)
        self.assertIn("back.svg", preview)

    def test_table_page_uses_pack_art_and_keeps_play_ids(self):
        page = (CARDS.parents[1] / "page.html").read_text(encoding="utf-8")
        self.assertIn("/static/cards/", page)
        self.assertIn("back.svg", page)
        self.assertIn('el.dataset.id = clickId', page)
        self.assertIn('id = "play:" + label.replace(" ", "-")', page)


class StaticCardServingTests(unittest.TestCase):
    def setUp(self):
        self.server = make_server(Table(new_match()), 0)
        host, port = self.server.server_address[:2]
        self.base = f"http://{host}:{port}"
        self.thread = __import__("threading").Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_get_face_and_back(self):
        for name in ("Herz-Ass.svg", "back.svg"):
            with urlopen(f"{self.base}/static/cards/{name}") as response:
                self.assertEqual(response.status, 200)
                body = response.read()
                self.assertIn(b"<svg", body)
                self.assertEqual(response.headers.get_content_type(), "image/svg+xml")


if __name__ == "__main__":
    unittest.main()
