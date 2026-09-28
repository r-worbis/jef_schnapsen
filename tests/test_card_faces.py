"""Vendored Schnapsen card drawings and static serving."""

import struct
import unittest
import zlib
from pathlib import Path
from urllib.request import urlopen

from schnapsen.cards import RANKS, SUITS
from schnapsen.engine import new_match
from schnapsen.server import Table, make_server

CARDS = Path(__file__).resolve().parents[1] / "schnapsen" / "static" / "cards"
TOKENS = [f"{suit}-{rank}" for suit in SUITS for rank in RANKS]


def png_size_and_rows(path):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a PNG")
    pos = 8
    width = height = color_type = None
    chunks = []
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk[:10])
            if bit_depth != 8 or color_type != 6:
                raise AssertionError(f"{path} is not 8-bit RGBA")
        elif kind == b"IDAT":
            chunks.append(chunk)
        elif kind == b"IEND":
            break
    raw = zlib.decompress(b"".join(chunks))
    stride = width * 4
    rows = []
    index = 0
    previous = bytearray(stride)

    def paeth(left, up, up_left):
        estimate = left + up - up_left
        distances = (abs(estimate - left), abs(estimate - up), abs(estimate - up_left))
        return (left, up, up_left)[distances.index(min(distances))]

    for _ in range(height):
        filter_type = raw[index]
        index += 1
        row = bytearray(raw[index : index + stride])
        index += stride
        for x in range(stride):
            left = row[x - 4] if x >= 4 else 0
            up = previous[x]
            up_left = previous[x - 4] if x >= 4 else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                predictor = paeth(left, up, up_left)
            else:
                raise AssertionError(f"unknown PNG filter {filter_type}")
            row[x] = (row[x] + predictor) & 255
        previous = row
        rows.append(bytes(row))
    return width, height, rows


def reversed_pixels(row, width):
    return b"".join(row[index : index + 4] for index in range((width - 1) * 4, -1, -4))


class CardFaceFilesTests(unittest.TestCase):
    def test_twenty_faces_and_back_and_no_other_ranks(self):
        french = {path.name for path in (CARDS / "french").glob("*.svg")}
        self.assertEqual(french, {f"{token}.svg" for token in TOKENS})
        self.assertNotIn("Herz-2.svg", french)
        parent = {path.name for path in CARDS.glob("*.svg")}
        self.assertEqual(parent, {"back.svg"})

    def test_license_and_attribution_name_the_source(self):
        license_text = (CARDS / "LICENSE").read_text(encoding="utf-8")
        attribution = (CARDS / "ATTRIBUTION.md").read_text(encoding="utf-8")
        self.assertIn("GNU LESSER GENERAL PUBLIC LICENSE", license_text)
        self.assertIn("Version 2.1", license_text)
        self.assertIn("Bellot", attribution)
        self.assertIn("SVG-cards", attribution)
        self.assertIn("GNU Lesser General Public License", attribution)
        self.assertIn("https://schnopsn.com/doppeldeutsche-karten", attribution)
        self.assertNotIn("CC BY-SA 3.0", attribution)
        self.assertNotIn("Mfrasca", attribution)

    def test_doppeldeutsche_faces_are_the_twenty_tokens(self):
        directory = CARDS / "doppeldeutsch"
        names = {path.name for path in directory.iterdir() if path.is_file()}
        self.assertEqual(names, {f"{token}.png" for token in TOKENS})
        self.assertNotIn("Herz-7.png", names)
        king_width, king_height, _ = png_size_and_rows(directory / "Pik-König.png")
        self.assertEqual((king_width, king_height), (290, 434))
        width, height, rows = png_size_and_rows(directory / "Pik-Bube.png")
        self.assertEqual(height % 2, 0)
        for y, row in enumerate(rows):
            self.assertEqual(rows[height - 1 - y], reversed_pixels(row, width))

    def test_preview_lists_every_token(self):
        preview = (CARDS / "preview.html").read_text(encoding="utf-8")
        for token in TOKENS:
            self.assertIn(token, preview)
        self.assertIn("back.svg", preview)
        self.assertIn("Französisch", preview)
        self.assertIn("Doppeldeutsch", preview)
        self.assertIn("french/", preview)
        self.assertIn("doppeldeutsch/", preview)
        self.assertIn(".png", preview)
        self.assertIn('src="french/Herz-Ass.svg"', preview)
        self.assertIn('src="doppeldeutsch/Karo-Dame.png"', preview)
        self.assertNotIn('src="Herz-Ass.svg"', preview)
        self.assertIn("Schelle-Ober", preview)
        self.assertIn("schnapsen-deck", preview)

    def test_table_page_uses_pack_art_and_keeps_play_ids(self):
        page = (CARDS.parents[1] / "page.html").read_text(encoding="utf-8")
        self.assertIn("/static/cards/", page)
        self.assertIn("back.svg", page)
        self.assertIn('el.dataset.id = clickId', page)
        self.assertIn('id = "play:" + label.replace(" ", "-")', page)
        self.assertIn("schnapsen-deck", page)
        self.assertIn('"/static/cards/french/" + token + ".svg"', page)
        self.assertIn('"/static/cards/doppeldeutsch/" + token + ".png"', page)
        self.assertNotIn('"/static/cards/" + prefix + token + ".svg"', page)
        self.assertNotIn('"/static/cards/" + token + ".svg"', page)
        self.assertIn("Schelle Ober", page)
        self.assertIn("Trumpf-Unter", page)
        self.assertIn("function isPlainPlay", page)
        self.assertIn("shouldShowActionButton(item.id)", page)
        self.assertIn("return /^play:[^:]+$/.test(id);", page)
        plain = __import__("re").compile(r"^play:[^:]+$")
        self.assertTrue(plain.match("play:Herz-Ass"))
        for kept in (
            "marry:Herz:Herz-König",
            "exchange:Herz-Bube",
            "close:Karo-Ass",
            "exchange-close:Karo-Ass",
            "close-marry:Karo:Karo-Dame",
            "exchange-marry:Herz:Herz-König",
            "seen",
            "next-deal",
        ):
            self.assertIsNone(plain.match(kept), f"{kept} must remain a text button")


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
        expected = {
            "french/Herz-Ass.svg": (b"<svg", "image/svg+xml"),
            "back.svg": (b"<svg", "image/svg+xml"),
            "doppeldeutsch/Karo-Dame.png": (b"\x89PNG", "image/png"),
        }
        for name, (marker, content_type) in expected.items():
            with urlopen(f"{self.base}/static/cards/{name}") as response:
                self.assertEqual(response.status, 200)
                body = response.read()
                self.assertIn(marker, body)
                self.assertEqual(response.headers.get_content_type(), content_type)


if __name__ == "__main__":
    unittest.main()
