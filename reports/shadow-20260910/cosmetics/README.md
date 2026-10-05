# Shadow cosmetic additions

Imported only the requested 19 cosmetics into the resource pack. No client bundle changes and no live config changes or deployment.

- Shadow Slayer: wings, hat, hoe, pickaxe, axe, sword, shovel, bow, hammer as mace.
- Shadow Bat: wings, hoe, pickaxe, axe, sword, shovel, bow, battle axe as mace.
- Shadowsteel: wings and hat.

The original head transforms and texture animation metadata are preserved. Bow draw stages are registered at pull 0, 0.65 and 0.9. Tool overrides cover wooden, stone, iron, golden, diamond and netherite variants. Existing vanilla item override order was preserved; additions inserted before higher custom-model-data predicates.

## Additions-only configuration

Merge the entries under `content:` into the existing files; **do not replace the entire live files**. These snippets were checked against the current dev spawn configs and Atlas parsers.

- `../config-additions/cosmetic.additions.yml`: 19 cosmetic definitions.
- `../config-additions/pokemon-skin.additions.yml`: 24 base-species shadow skin definitions. Shinies and the six supplied Mega forms share these skins automatically through resolver aspects.
- `../config-additions/skin-dex.additions.yml`: one new `shadow-2026` collection, with both auras. The existing nine-skin Shadow collection remains intact, because it lacks the new aura models.

The new collection follows the existing completion reward convention: Aura I is awarded for completion. Aura II is registered for previews/use but no additional acquisition source is invented.

## Verification

Required asset references and model JSON element bounds/rotation checks passed. 7728 existing item states are unchanged; 81 new item states passed. All 117 touched asset hashes match the built ZIP. The ordinary baseline/overlay builder passed. In-game wing positioning, hat fit and bow poses still require visual testing.

Current combined pack (shadow skins plus cosmetics and earlier pending changes): `dist/resource-pack.zip`, 3182524 bytes. SHA-256: `3d1f830b86692db22a8037be65332da869da0528a1df84efa4a3d243a725a26d`.

## Item mappings

| Cosmetic | Item | Custom Model Data |
|---|---|---|
| shadow-slayer-wings | flint | 128 |
| shadow-slayer-hat | flint | 129 |
| shadow-slayer-hoe | netherite_hoe | 36 |
| shadow-slayer-pickaxe | netherite_pickaxe | 42 |
| shadow-slayer-axe | netherite_axe | 37 |
| shadow-slayer-sword | netherite_sword | 46 |
| shadow-slayer-shovel | netherite_shovel | 32 |
| shadow-slayer-bow | bow | 30 |
| shadow-slayer-mace | mace | 19 |
| shadow-bat-wings | flint | 130 |
| shadow-bat-hoe | netherite_hoe | 37 |
| shadow-bat-pickaxe | netherite_pickaxe | 43 |
| shadow-bat-axe | netherite_axe | 38 |
| shadow-bat-sword | netherite_sword | 47 |
| shadow-bat-shovel | netherite_shovel | 33 |
| shadow-bat-bow | bow | 31 |
| shadow-bat-mace | mace | 20 |
| shadowsteel-wings | flint | 131 |
| shadowsteel-hat | flint | 132 |
