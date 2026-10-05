# Cobblemon 1.8 model overlay hotfix — 10 September 2026

Updates normal/shiny/alpha models for Nidoking, Tyranitar, Garganacl, Druddigon, Typhlosion (Johto and Hisui), and Zoroark (Unova and Hisui). Uses official Cobblemon 1.8 model and texture bytes with isolated atlas_hotfix18 identifiers, and matching JSON posers/animation aliases where applicable. Prevents Journey Mounts 1.7.2 models or retained baseline rigs from inheriting incompatible 1.8 textures and compiled posers.

All 168 custom skin/form combinations checked retain the previous model, poser and texture selections. Managed skin guards are registered in tools/msd18-skin-guards.json; refresh with `python3 tools/msd18_skin_guards.py --refresh` when adding a skin, then build normally. Do not refresh the client baseline.

Validation: 200 states, including 32 standard states. No missing model/texture or identified strict poser crash paths remain among these states. Existing custom animation warnings are unchanged; upstream Garganacl has unused pointer channels. These checks do not replace an in-game render test.

Manual tests: spawn each below, repeat with `shiny=true`; inspect in world, PC, Skindex and reward previews. Test walking, battle and alpha eyes where applicable.

```
/spawnpokemon nidoking
/spawnpokemon tyranitar
/spawnpokemon garganacl
/spawnpokemon druddigon
/spawnpokemon typhlosion
/spawnpokemon typhlosion hisuian
/spawnpokemon zoroark
/spawnpokemon zoroark hisuian
```

Sneasler: production server Cobblemon species data specifies Hisuian Sneasel, holding Razor Claw, level-up during day. Ordinary Sneasel evolves into Weavile at night. No Sneasel override found in old/new main spawn shared datapacks. No evolution code or data changed.
