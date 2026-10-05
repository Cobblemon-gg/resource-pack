# Mega Showdown 53022919 (v1.1.3+1.8) asset follow-up

Ported upstream `18dfa756..53022919` into eleven isolated `atlas_msd18_*` sets: Mega Absol remodel, Mega Absol Z, Lucario VGU base, Mega Lucario, Mega Lucario Z, Mega Golisopod, Frigibax, Arctibax, Baxcalibur, Mega Baxcalibur and Chi-Yu. Replaced seven stock-blob textures whose local geometry has identical cube UVs (Mega Charizard X/Y shiny, Cobalion alias, Okidogi alias, Mega Delphox alias shiny) and added the upstream ride-seat locators to the Mega Delphox alias.

No deployment, no client baseline change, no `data/` change, no Primal/Crowned change, nothing under `assets/flourish/` or `assets/minecraft/models/item/paper.json`. Every legacy rig, poser, animation, texture and skin variation is byte-identical; the 17 edited existing files are backed up under `mega-showdown-1.8-53022919-before/`.

MSD `mega_z`/`mega_x`/`mega_y` aspects were translated to this pack's `mega-z`/`mega-x`/`mega-y` flag aspects. No upstream resolver was copied wholesale.

## Per-species decisions

| Species / form | Decision | Reason |
| --- | --- | --- |
| Mega Absol | guarded import (`atlas_msd18_absol_mega`) | legacy `absol_mega` poser/model are inherited by greek-2026/masquerade mega skins |
| Mega Absol Z | guarded import (`atlas_msd18_absol_mega_z`) | pack already had a custom `absol_mega_z` set with greek-2026/masquerade skins and a `glow` layer (disabled on the new set) |
| Lucario (base) | guarded import (`atlas_msd18_lucario`, resolver `atlas_msd18/120_lucario.json`) | sits above the existing `atlas_sweep18` official-1.8 resolver (order 110); poser needs core `lucario` + upstream `lucario_mega` groups |
| Mega Lucario | guarded import (`atlas_msd18_lucario_mega`, emissive + alpha layers) | `skel` mega skin is texture-only on the legacy `lucario_mega.geo`; egyptian/movie/summer inherit the legacy poser |
| Mega Lucario Z | guarded import (`atlas_msd18_lucario_mega_z`) | pack already had a custom `lucario_mega_z` set with skel/shears/movie/summer/egyptian skins |
| Mega Garchomp Z | already synced | pack geo/poser/animation/textures are byte-identical to HEAD; resolver already uses `mega-z` |
| Mega Golisopod | guarded import (`atlas_msd18_golisopod_mega`, alpha layer) | anniversary mega skins inherit the legacy poser; pack geo lacked the HEAD eye locators/UV fix |
| Frigibax / Arctibax / Baxcalibur | guarded import (`atlas_msd18_<name>`) | pack bases are custom community rigs (Cobblemon core has none); medieval Baxcalibur skin inherits the legacy poser; upstream rigs carry more animations |
| Mega Baxcalibur | guarded import (`atlas_msd18_baxcalibur_mega`, resolver `atlas_msd18/100_baxcalibur_mega.json`) | two legacy resolvers (`0901_`, `0998_`) share order 7; a higher-order resolver avoids their tie |
| Chi-Yu | guarded import (`atlas_msd18_chiyu`, emissive layers) | st-patricks skins inherit the legacy poser |
| G-Max Corviknight | skipped | G-Max visuals ship from the MSD jar; the pack has no corviknight gmax assets to duplicate |
| Mega Delphox | alias patched | `locator_seat_1/2` bones and `visible_bounds_width` 10 added to `atlas_msd18_delphoxmega.geo.json`; alias shiny texture replaced; legacy skel/valentines/silk-scarf assets untouched |
| Mega Charizard X/Y shiny | replaced | stock blobs; local geometry has 134/166 cubes with identical UVs to HEAD |
| Cobalion, Okidogi | alias textures replaced | stock blobs, identical UVs; legacy `05_generation`/`09_generation` copies retained |
| Mega Slowbro | skipped | local stock rig predates upstream's remodel (0 cubes in common); texture alone is UV-incompatible; full-set update candidate |
| Latias / Latios | skipped | pack base uses core `latias.geo`/`latios.geo`; MSD textures target its `latias2`/`latios2` rigs (0 cubes in common) |
| Kyogre / Groudon (+Primal), Zamazenta (+Crowned) | skipped | historically protected; base textures excluded with them |
| Kubfu / Urshifu | skipped | custom pack rigs with 0 cubes in common (Urshifu 128px vs 256px upstream) |
| Mega Diancie textures | retained | deleted upstream but still referenced by `0_diancie_base.json` |
| Charizard/Corviknight gigantamax textures | skipped | provided by the MSD jar |
| Pikachu cosplay alola-bias (regionbiasmsd) | skipped | not used by this pack |
| Mega stones / Arceus plates (`assets/flourish/`) | not applied | out of bounds; all 23 mapped files are stock blobs, five stones already equal HEAD, 17 plates would update, `legendplate.png` has no local file |

## Manual test checklist

For every row test normal and shiny, idle/walk/run, sleep, battle entry/attacks/recoil/faint, GUI portrait/profile, cry and form switching; test each listed skin in normal/shiny plus aura variants.

| Model | Manual checks | Legacy skins/forms preserved |
| --- | --- | --- |
| mega absol | [ ] normal/shiny; idle, movement, cry, battle, faint, portrait/profile | `greek-2026`, `greek-2026-aura1`, `greek-2026-aura2`, `masquerade`, `masquerade-aura`, `plushie` |
| mega absol z | [ ] normal/shiny; glow layer must be absent on the new set; portrait/profile | `greek-2026`, `greek-2026-aura1`, `greek-2026-aura2`, `masquerade`, `masquerade-aura` |
| lucario | [ ] normal/shiny/alpha eyes; idle, walk, sleep, item hold, battle idle, cry, recoil | `cosmetic_item-shears`, `egyptian`, `galaxy`, `golden`, `movie`, `movie-aura1`, `movie-aura2`, `plushie2`, `skel`, `summer` |
| mega lucario | [ ] normal/shiny/alpha eyes; emissive layer; `lucario_aura` particles on cry/attack locators; quirks | `egyptian`, `movie`, `movie-aura1`, `movie-aura2`, `skel`, `summer` |
| mega lucario z | [ ] normal/shiny; idle/walk/run, sleep, quirks, portrait | `cosmetic_item-shears`, `egyptian`, `movie`, `movie-aura1`, `movie-aura2`, `skel`, `summer` |
| mega golisopod | [ ] normal/shiny/alpha eyes; ground + water idle/swim, faint, cry | `anniversary`, `anniversary-aura1`, `anniversary-aura2` |
| frigibax | [ ] normal/shiny/alpha eyes; idle, walk | None currently defined |
| arctibax | [ ] normal/shiny/alpha eyes; idle, walk | None currently defined |
| baxcalibur | [ ] normal/shiny/alpha eyes; idle, walk, battle idle | `medieval`, `medieval-aura1`, `medieval-aura2` |
| mega baxcalibur | [ ] normal/shiny; idle, walk, battle idle; confirm the new resolver wins over both legacy order-7 resolvers | None currently defined |
| chiyu | [ ] normal/shiny; emissive layer; idle | `st-patricks`, `st-patricks-aura1`, `st-patricks-aura2` |
| mega delphox | [ ] alias shiny colours; ride seat alignment if riding is enabled; legacy skins unchanged | `cosmetic_item-silk_scarf`, `skel`, `valentines` |
| mega charizard x / y | [ ] shiny textures only | wild-west variants use their own textures |
| cobalion, okidogi | [ ] alias normal/shiny textures | legacy copies unchanged |

Special checks:

- Mega Garchomp Z: regression only (no change); confirm `mega-z` still selects the pack set.
- Upstream Lucario/Golisopod animations name bones their geometry lacks (29/18/26/11 names, e.g. `jaw`, `dread_*`, `figner_*`, `toe_*`). This is upstream's shipped state and Cobblemon skips absent bones; watch for missing secondary motion rather than crashes.
- The Mega Lucario `lucario_aura` particle is a Cobblemon core particle (`cobblemon:lucario_aura`); no particle file was copied.
- Mega Slowbro is knowingly stale versus upstream (remodel predates this delta); decide separately whether to import its full set.

## Validation

`tools/verify_msd18_53022919.py`: 11 sets, 28 new variations, 442 legacy skin states resolve identically before/after, 31 new-variation texture references, 424 literal animation references, 19 sound events and 10 particle references resolve, 83 changed assets, 15,738 retained byte-identical, pack `client-baseline.json` unchanged. `msd18_skin_guards.py --refresh` was a no-op; `build_pack.py build` and both `tools/test_*.py` suites pass.

`tools/verify_msd18_port.py` fails on pre-existing stale hashes (13 paths edited in place by the 18dfa756/837be205 ports, e.g. `atlas_msd18_raikou.geo.json`); its structural checks are reproduced by the new verifier. The Atlas client archive `atlas/client/resource-pack/atlas-baseline.zip` (rewritten 2026-09-14) no longer matches this pack's manifest hash; that is outside this repository and was not touched.

Outputs: `dist/resource-pack.zip` 6,792,622 bytes, SHA-256 `194456ce96720b1d768c9822be44edfe5d656650a736acc493547d4cf20338cd`; `dist/resource-pack-full.zip` 66,299,937 bytes, SHA-256 `31492da7c4dd50fa27c51ae71e4337a8de94007c92bdb3bd4288ebd1897dc092`. Both need manual client testing before publication.

Exact hashes, pre-edit hashes, resolver snapshots, the per-upstream-file decision map and skip reasons: `mega-showdown-1.8-53022919-port.json`. Validation counts: `mega-showdown-1.8-53022919-validation.json`. Re-run `python3 tools/msd18_skin_guards.py --refresh` then `python3 tools/build_pack.py build` after adding skins for any species above.

## Arceus plate item textures (applied after the model sync)

The 17 `assets/flourish/textures/item/<type>plate.png` files were stock MSD blobs and were replaced with the reworked upstream 53022919 plate art (`legend_plate` has no local counterpart and was not added). Check the plate icons in the Arceus form-change UI and inventory tooltips.
