# Mega Showdown 837be205 asset follow-up

Updated four standard model sets: Hoopa Confined, Hoopa Unbound, Mega Skarmory and G-Max Flapple. Replaced nine Rolycoly/Carkol/Coalossal normal/shiny/emissive alias textures with current Cobblemon 1.8 core textures after upstream removed its obsolete overrides.

No deployment, frozen client baseline change, species/hitbox change or Crowned/Primal change. The recent tag image edits and every unrelated authoring asset are preserved byte-for-byte.

| Model | Manual checks | Legacy skins/forms preserved |
| --- | --- | --- |
| hoopa confined | [ ] normal/shiny; idle, movement, cry, battle, faint, portrait/profile | `molten`, `spectrum`, `spectrum-aura1`, `spectrum-aura2` |
| unbound hoopa | [ ] normal/shiny; idle, movement, cry, battle, faint, portrait/profile | `molten`, `spectrum`, `spectrum-aura1`, `spectrum-aura2` |
| mega skarmory | [ ] normal/shiny; idle, movement, cry, battle, faint, portrait/profile | `monochrome`, `monochrome-aura1`, `monochrome-aura2` |
| gmax flapple | [ ] normal/shiny; idle, movement, cry, battle, faint, portrait/profile | None currently defined |
| Rolycoly | [ ] normal/shiny/emissive/alpha eyes | Existing legacy graph unchanged |
| Carkol | [ ] normal/shiny/emissive/alpha eyes | Existing legacy graph unchanged |
| Coalossal | [ ] normal/shiny/emissive/alpha eyes | Existing legacy graph unchanged |

## Hoopa scale and priorities

Both legacy Hoopa resolver files use order 0. Two new, explicitly higher-priority guarded standard resolvers avoid depending on their unspecified same-order ordering. These are deliberate additional resolvers; no old resolver was renamed or changed. Molten, spectrum and aura skins cause the new standard resolvers to stop matching, preserving their complete original asset graph. Normal Unbound is excluded from the confined override.

The native poser schema supports `transformedParts` root-bone scaling. Every new Confined pose scales its zero-pivot `hoopa_confined` root by 0.7; every new Unbound pose scales its zero-pivot `hoopa_unbound` root by 2. This matches upstream visual scale while retaining species baseScale 1 for old skins. The original geometry and all custom-skin posers are untouched. Root bones exist and no imported animations independently animate those root bones.

Global Hoopa species scale/hitboxes remain unchanged. Test world visual size, interaction/collision, sendout, portrait/profile framing and form switching. Neither new Hoopa geometry defines ride seat locators; riding support is not introduced here.

Mega Skarmory uses the native 1.8 Skarmory poser and animations with new geometry. Its `seat_1` locator exists at `[0,23.25,0.25]`; verify seat alignment and takeoff/flying/landing ingame. Monochrome/aura skins retain their old geometry/poser.

G-Max Flapple intentionally reuses the matched upstream G-Max Appletun model/poser/textures, as specified by the new upstream resolver.

## References, removals and validation

Hoopa Unbound requires the upstream `pokemon.hoopaunbound.cry` sound event, which core Cobblemon does not provide. Its event and actual OGG were imported; existing sound definitions were retained. No unresolved new literal animation/model/poser/texture/sound references remain.

Upstream texture deletions for Cherubi/Cherrim, Rockruff/Lycanroc, Applin/Flapple/Appletun and Duraludon/Dipplin/Archaludon/Hydrapple were not blindly copied: our legacy skins retain their assets. Previously isolated Rolycoly/Carkol/Coalossal standard sets already use core 1.8 geometry, so only their nine obsolete standard alias textures were updated to core bytes. Their existing alpha textures already match core and are unchanged.

Automated checks: all 27 imported model/poser sets, 61 variations, 342 literal animation references and 13 sound events resolve; 217 legacy variations remain protected across the full port. This follow-up compares 88 skin states before/after, verifies Hoopa pose root scales, and proves every pre-existing asset outside the declared 35 changed paths remains byte-identical. All four builder/guard regression tests pass. ZIPs reconstruct the complete authoring tree; the frozen baseline checksum remains unchanged.

Three earlier missing textures remain: `textures/pokemon/skins/abyss/zygarde_abyss.png`, `textures/pokemon/skins/abyss/zygarde_abyss_emissive.png`, `textures/pokemon/megas/0003_venusaur/venusaurmega_movie.png`. These are not introduced by this update.

Use the normal `python3 tools/msd18_skin_guards.py --refresh` and `python3 tools/build_pack.py build` workflow for future skin/form additions. The paired overlay is `dist/resource-pack.zip`; full fallback is `dist/resource-pack-full.zip`. Do not freeze a new baseline.

Exact hashes/provenance and pre-edit asset hashes: `mega-showdown-1.8-837be205-port.json`. Validation: `mega-showdown-1.8-837be205-validation.json`.
