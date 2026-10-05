# Rotom datapack overrides removed 2026-09-17

Rotom now uses Mega Showdown's own system (Rotom Catalogue + appliance blocks) on top of Cobblemon 1.8's native `appliance` feature and Rotom forms. These Atlas overrides were moved here (the pack's `data/` tree is untracked, so this is the only copy). Atlas lets the MSD jar's `species/generation4/rotom.json` and `spawn_pool_world/0479_rotom.json` through its filter instead. To restore: move the files back under `data/cobblemon/`.

`spawn_pool_world/0479_rotom.json` was NOT removed: it is an Atlas rarity tuning (weights 10x lower than upstream, one entry ultra-rare) and stays authoritative; MSD's Rotom spawn file remains filtered.
