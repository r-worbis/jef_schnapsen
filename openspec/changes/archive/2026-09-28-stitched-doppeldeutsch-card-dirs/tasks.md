# Tasks

## 1. Doppeldeutsche Tell faces

- [x] 1.1 Download the twenty `{PI|KR|HE|KA}{02|03|04|10|11}.png` files from `https://schnopsn.com/images/ddeutsch/` (not the `_2` crops). Using the mapping in `design.md`, write `schnapsen/static/cards/doppeldeutsch/{token}.png`: if the bitmap is taller than 300px, copy it unchanged; otherwise paste it above a 180° rotation of itself with no gap and no scaling. Delete the twenty `.svg` files in that directory. Do not add Pillow to `requirements.txt`; it is only a build tool. Verify a test in `tests/test_card_faces.py` that this directory's files are exactly the twenty `{token}.png` names, that `Pik-König.png` is 290×434, that the lower half of `Pik-Bube.png` matches its upper half rotated 180°, and that `python -m unittest tests.test_card_faces.CardFaceFilesTests` passes.
- [x] 1.2 In `schnapsen/static/cards/ATTRIBUTION.md`, replace the doppeldeutsch Wikimedia section with `https://schnopsn.com/doppeldeutsche-karten`, the image base `https://schnopsn.com/images/ddeutsch/`, the token mapping, and a note that the page does not publish a reuse license. Leave the French Bellot section and `LICENSE` in place. Verify the attribution test still requires Bellot and the LGPL, requires the schnopsn.com page, does not require CC BY-SA or Mfrasca for this pack, and that `python -m unittest tests.test_card_faces.CardFaceFilesTests` passes.

## 2. French directory and face URLs

- [x] 2.1 Move the twenty French `{token}.svg` files from `schnapsen/static/cards/` into `schnapsen/static/cards/french/`. Leave `back.svg`, `LICENSE`, `ATTRIBUTION.md`, and `preview.html` in the parent directory. Verify a test that `french/*.svg` is exactly the twenty engine tokens, that the parent's `*.svg` set is exactly `back.svg`, and that `python -m unittest tests.test_card_faces.CardFaceFilesTests` passes.
- [x] 2.2 In `schnapsen/page.html` and `schnapsen/static/cards/preview.html`, load French faces from `french/{token}.svg` and doppeldeutsche faces from `doppeldeutsch/{token}.png`. Keep the back at `back.svg`, the `schnapsen-deck` choice, and the Schelle-Ober caption. Verify a test that both files contain `french/` and `doppeldeutsch/` with `.png`, that the page no longer builds a top-level `/{token}.svg` face URL, and that `python -m unittest tests.test_card_faces` passes, including a static fetch of `french/Herz-Ass.svg` as `image/svg+xml`, `doppeldeutsch/Karo-Dame.png` as `image/png`, and `back.svg`.

## 3. Preview and table

- [x] 3.1 In the browser, open the deck preview and confirm Französisch shows the faces from `french/` plus the shared back, then Doppeldeutsch shows twenty full faces from `doppeldeutsch/` (Pik Bube reads upright and upside down) and not the French faces. On the table, switch to Doppeldeutsch during a deal and confirm the hand and trump use those faces while the cards, scores, and turn stay put; switch back to Französisch and confirm the French faces return.
