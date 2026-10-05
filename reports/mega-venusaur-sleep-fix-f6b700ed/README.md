# Mega Venusaur sleep animation fix (Mega Showdown f6b700ed, 2026-09-21)

Upstream commit "Fixed Mega Venusaur sleep animation". Our file was semantically identical to the
previous upstream version, and upstream changed exactly one of its 17 animations:
`animation.venusaur_mega.sleep` now also poses `leaf_left_back`, `leaf_left_back2/3/4` (the old pose
forgot the left-back leaf, so it stuck out while asleep). The raw diff is large only because
upstream re-indented the file; the apply script asserts that no other animation differs.

Skins: the st-patricks, easter and movie Mega Venusaur skins (and their aura variants) use older
geometry without those four bones. That is safe: Cobblemon skips bone names a model lacks
(`BedrockAnimation`: `relevantPartsByName[boneName]` -> null -> skipped), and those skins already
run with 322 such unmatched references under the previous file (46 in `sleep`). Net effect: base
Mega Venusaur is fixed, skins behave exactly as before.

Check in game: Mega Venusaur (normal + shiny) asleep, plus one skin asleep as a regression check.
