# Shadow skins and auras — 10 September 2026

Implemented in the resource-pack authoring tree only, under `atlas_shadow` asset directories. Atlas client sources, client jar and frozen baseline were not changed for this addition. Not published to live pack delivery; no server configuration, rewards, skindex or cosmetic registrations were changed.

Source: `/Users/daniel/Downloads/shadow/shadow`.

## Included

24 species, 30 model sets, 180 explicit combinations: `shadow`, `shadow-aura1`, `shadow-aura2`, each normal and shiny. Both auras animate the supplied 12 frames at 10 fps and use the supplied aura geometry. Armarouge uses its four supplied skin frames at 8 fps. Arceus uses the supplied normal/shiny emissive textures. No source artwork was repainted.

Species: amoonguss, arceus, archeops, armarouge, cyclizar, dragapult, emboar, flygon, gallade, granbull, greattusk, irontreads, krookodile, magearna, magmortar, marshadow, mewtwo, politoed, porygonz, slaking, staraptor, terrakion, vaporeon, xerneas.

Mega forms: mewtwo mega-x, mewtwo mega-y, staraptor mega, gallade mega, emboar mega, magearna mega.

[All 180 spawn commands](spawn-commands.txt). Example:

```text
/spawnpokemon vaporeon shadow
/spawnpokemon vaporeon shadow shiny
/spawnpokemon vaporeon shadow-aura1
/spawnpokemon vaporeon shadow-aura2 shiny
/spawnpokemon mewtwo mega-x shadow-aura1
```

## Compatibility

Each variant explicitly selects its geometry, poser and full texture definition. JSON posers and animation filename groups use isolated shadow IDs; compiled posers are retained where their required bones match. All inherited layer names are explicitly disabled before enabling the matching aura or Arceus emissive layer. Existing default and custom models are preserved. MSD skin guards were refreshed through the normal tool.

The isolated posers fix misspelled Mega Mewtwo `mmewtwo_...` special-animation groups and Mega Gallade's `head`/`Head` mismatch. Mega Staraptor's supplied aura root is renamed to match its skin root, preserving pivots, rotations, cubes and UVs. Archeops uses its existing cry animation for battle cry and omits an absent optional sleep quirk; Emboar omits an absent named faint override. These changes affect shadow variants only.

Some upstream animation channels address bones absent from the supplied rigs (including optional detail/locator bones). Those channels are recorded in `validation.json`; required poser bones and literal animation references resolve. This is static validation, not proof of visual correctness. Test walking, battle/attack animations, riding, PC/skindex previews and aura placement in-game, including both Mega Mewtwo forms and Mega Staraptor.

## Verification and artifacts

- Required model roots, transformed parts, animation factory bones and literal animation references passed for all 180 variants.
- 720 effective resolver states passed, including alpha/female combinations.
- 291 existing non-shadow states retained the same resolved assets/layers.
- 227 imported asset hashes verified in the actual generated overlay ZIP.
- Normal builder baseline reconstruction passed; frozen baseline was not refreshed.
- Server overlay: `dist/resource-pack.zip` — 2,961,288 bytes (about 2.96 MB).
- Full fallback: `dist/resource-pack-full.zip` — 62,558,828 bytes.
- Overlay SHA-256: `bd88c1efeab9f9e75534e9229f46a44a990f4b21526c170d278a3f5601f389aa`.

The overlay also includes other already pending resource-pack changes. Use the full fallback for clients without the paired Atlas baseline. Server-side registration/distribution is separate from these asset additions.

Audit/import scripts are retained alongside this report in `scripts/`; they read the local official client jar and source assets. `manifest.json` records imported paths, hashes, model/poser bindings and all variants.
