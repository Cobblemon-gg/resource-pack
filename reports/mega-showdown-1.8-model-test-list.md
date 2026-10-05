# Mega Showdown 1.8 model and skin test list

Prepared from upstream `ced283c48914785b2ae0faf55e2edef1881e1dbd`. No assets were deployed and the frozen Atlas client baseline is unchanged.

The 14 requested new geometry sets and nine additional Mega/G-Max/texture corrections use isolated `atlas_msd18_*` models, posers and animation groups. Their textures live under `textures/pokemon/atlas_msd18/`. Existing custom skins keep their original models, posers, animation groups, UV layouts and layers. The old fallback variations remain at the same resolver path; additional normal/shiny variations exclude existing skin/form aspects with supported `q.has_aspect` conditions.

For every row: test normal and shiny, idle/walk/run, water/flying states where applicable, sleep, battle entry/attacks/recoil/faint, GUI portrait/profile and switching. Test every listed skin in normal/shiny and each listed aura form. These are manual checks, not completed ingame validation.

| Updated model/form | Existing skin/form aspects retained on legacy assets | Tested |
| --- | --- | --- |
| mega blastoise | `easter`, `movie`, `movie-aura1`, `movie-aura2`, `plushie`, `summer`, `superhero` | [ ] |
| raikou | `golden`, `greek-2026`, `greek-2026-aura1`, `greek-2026-aura2`, `lunar-new-year`, `plushie`, `plushie2` | [ ] |
| entei | `circus`, `circus-aura1`, `circus-aura2`, `golden`, `plushie`, `plushie2` | [ ] |
| suicune | `easter-2026`, `easter-2026-aura1`, `easter-2026-aura2`, `golden`, `plushie`, `plushie2` | [ ] |
| heatran | `mega`, `summer-2026`, `summer-2026-aura1`, `summer-2026-aura2` | [ ] |
| cobalion | `monochrome`, `monochrome-aura1`, `monochrome-aura2`, `plushie` | [ ] |
| terrakion | None currently defined | [ ] |
| virizion | `plushie`, `st-patricks`, `st-patricks-aura1`, `st-patricks-aura2` | [ ] |
| wochien | None currently defined | [ ] |
| chienpao | `christmas`, `cyberpunk`, `golden`, `plushie2` | [ ] |
| tinglu | `karma`, `karma-aura1`, `karma-aura2` | [ ] |
| okidogi | None currently defined | [ ] |
| munkidori | `plushie` | [ ] |
| fezandipiti | `masquerade`, `masquerade-aura` | [ ] |
| mega feraligatr | `golden`, `karma`, `karma-aura1`, `karma-aura2`, `plushie2`, `summer` | [ ] |
| mega golurk | `greek-2026`, `greek-2026-aura1`, `greek-2026-aura2`, `halloween` | [ ] |
| mega delphox | `cosmetic_item-silk_scarf`, `skel`, `valentines` | [ ] |
| mega drampa | `lunar-new-year` | [ ] |
| mega kangaskhan | `carnival`, `easter-2026`, `easter-2026-aura1`, `easter-2026-aura2`, `superhero` | [ ] |
| gmax garbodor | None currently defined | [ ] |
| rolycoly | None currently defined | [ ] |
| carkol | None currently defined | [ ] |
| coalossal | None currently defined | [ ] |

Special checks:

- Mega Blastoise: black glasses, wise glasses, alpha eyes, emissive layer and shiny.
- Mega Golurk: shiny emissive textures and physical attack variants.
- Mega Delphox, Drampa and Kangaskhan: corrected shiny colours; ensure legacy skins still use their original UV mapping.
- G-Max Garbodor: new complete matched set and movement.
- Rolycoly, Carkol and Coalossal: new texture/emissive/alpha layers against their matched 1.8 geometry.
- Entei, Raikou and Mega Kangaskhan: imported cry events now use valid native sound IDs; test cries.
- Entei and Ting-Lu: upstream refers to nonexistent faint clips. Those invalid overrides were removed; test ordinary Cobblemon faint behavior.
- Mega Venusaur: upstream only moved its animation directory. Animation IDs are unchanged and the existing valid animation is retained. Test Mega Venusaur normal/shiny and Easter, St Patrick’s, movie/aura skins as regression checks.

Crowned Zacian/Zamazenta, Primal Groudon/Kyogre, their assets and their behavior were not changed. Upstream-deleted Cherubi/Cherrim, Rockruff/Lycanroc, Applin-line and Duraludon-line legacy assets were retained.

Three existing missing textures remain: `skins/abyss/zygarde_abyss.png`, `skins/abyss/zygarde_abyss_emissive.png`, and `megas/0003_venusaur/venusaurmega_movie.png` (all under `textures/pokemon/`). They were not introduced by this port.

## Future skin additions

After adding/changing aspects for a species in this list, run `python3 tools/msd18_skin_guards.py --refresh` before `python3 tools/build_pack.py build`. The builder rejects stale guards. This keeps a new legacy skin from inheriting the new model/poser/layers. For a skin deliberately authored for the new model, explicitly set its matching `atlas_msd18_*` model and poser and the complete texture/layers at its normal higher resolver order; do not remove protection for existing skins. Check both normal and shiny. Do not freeze the client baseline.

## Automated validation

- 23 matched model/poser sets and 53 new normal/shiny/cosmetic variations.
- Original resolver variations retained exactly; 169 legacy custom/form variations protected.
- 295 literal animation references resolve; imported model/poser and texture references resolve.
- Four builder/guard tests pass. Overlay reconstruction matches the complete authoring source.
- See `mega-showdown-1.8-port.json` for exact paths/hashes and `mega-showdown-1.8-validation.json` for validation counts.
- Original changed resolver bytes are backed up under `reports/mega-showdown-1.8-before/`.

Use `dist/resource-pack.zip` with the matching Atlas client baseline; use `dist/resource-pack-full.zip` for clients without it. Both packs need manual client testing before publication.

Layers merge by name in Cobblemon. When retargeting a skin, explicitly disable obsolete inherited layer names with `{"name": "OLD_NAME", "enabled": false}`; an empty `layers` array does not clear inherited layers. The new standard sets already disable unmatched old layers, including incompatible old alpha-eye layers.

## Follow-up: upstream 837be205

[Four additional models, three texture corrections and every affected skin](mega-showdown-1.8-837be205-model-test-list.md) were updated. The combined inventory now has 27 imported model/poser sets; refer to that follow-up for Hoopa standard-only root scaling and the additional manual checks.
