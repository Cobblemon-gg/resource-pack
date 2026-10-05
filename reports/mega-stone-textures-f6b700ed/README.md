# Mega stone icons refreshed from Mega Showdown f6b700ed (2026-09-21)

Upstream re-drew every mega stone in one uniform style (orb + mega swirl emblem, PR "New Mega Stone
Textures"). All 92 Atlas mega stones that have an upstream counterpart now use that art.

* Each stone was resolved the way the game does: `mega.yml` customModelData -> `paper.json` override
  -> model json -> `layer0` texture. Seven stones display through a differently named model
  (`charizardite_x/_y`, `mewtwonite_x/_y`, `dragonitite`, `hawluchite`, `baxcaliburite`); the file the
  model actually points at is the one that was replaced.
* `chimechoite` (ours) maps to upstream `chimechite`.
* 61 of the replaced files were byte-identical to older upstream art. 31 were Atlas-made icons in the
  OLD upstream style (same palettes, no swirl). They were replaced too so the set stays uniform;
  every replaced file is kept under `before/` and listed with hashes in `port.json`.
* **Not updated: `rayquazanite`.** Mega Showdown has no Rayquaza stone (it mega evolves through Dragon
  Ascent), so there is no upstream icon. It is now the only old-style stone icon.
* Same-named leftover textures that no model references (e.g. `dragoninite.png`) were left alone.

Check in game: the stone reroll UI, raid shop, `/service give-mega` items and held-item icons in the
battle overlay. Only `assets/flourish/textures/item/*.png` changed; no models, ids or CMD values.
