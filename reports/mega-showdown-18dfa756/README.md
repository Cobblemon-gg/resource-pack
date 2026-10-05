# Mega Showdown 18dfa756 asset fixes

Ported 57 upstream model sets into 66 existing geometry assets: eye effect locators and visible-bound fixes for Mega Alakazam, Mega Gallade and both Raikou aliases. Original artwork, cubes, UVs, textures, resolver selections and custom skin dependencies are unchanged.

The frozen baseline is unchanged. Both packs were rebuilt. Nothing was uploaded or deployed.

## Validation

- All original cubes, UVs, textures and resolver bytes preserved; no asset deletions or Crowned/Primal changes.
- Eye-bearing parent geometry and all ancestor transforms must match before copying coordinates. Ancestor artwork may differ because it does not affect child coordinates.
- 19,903 resolved renderer states compared with identical current jars before/after: zero new findings, identical asset selections. Existing findings remain; this is not a claim that every pre-existing asset is crash-free.
- Skin guards, baseline/overlay hash reconstruction and changed-file checksums in both packs pass.
- [136 spawn commands across 50 species](spawn-commands.txt), including shiny/custom/aura states. Check world movement, alpha eye effects, battle previews and /skindex. These force visual aspects, not transformation mechanics.
- Three historical IDs (golurk_mega, floette_eternal, wochien) are not selected in current declared states; their active alias or official replacement is selected instead.

## Artifacts

- `resource-pack.zip`: 1,343,069 bytes; SHA-256 `2400fa6651ebb38e07a76e77b382db315bc447bfa0fccffc5b5fb67be46871f2`.
- `resource-pack-full.zip`: 60,940,609 bytes; SHA-256 `988a319c1dddfa2d3aa13342c58f0afe0a34a77c112791a6d35549b61e03ea7f`.

## Updated assets

| Upstream model | Local asset |
|---|---|
| venusaurmega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0003_venusaur/venusaurmega.geo.json` |
| beedrillmega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0015_beedrill/beedrillmega.geo.json` |
| pidgeot_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0018_pidgeot/pidgeot_mega.geo.json` |
| alakazam_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0065_alakazam/alakazam_mega.geo.json` |
| kangaskhan_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_kangaskhan_mega.geo.json` |
| starmie_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0121_starmie/starmie_mega.geo.json` |
| gyarados_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0130_gyarados/gyarados_mega.geo.json` |
| aerodactyl_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0142_aerodactyl/aerodactyl_mega.geo.json` |
| feraligatr_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_feraligatr_mega.geo.json` |
| ampharos_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0181_ampharos/ampharos_mega.geo.json` |
| heracross_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0214_heracross/heracross_mega.geo.json` |
| raikou.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_raikou.geo.json` |
| raikou.geo.json | `assets/cobblemon/bedrock/pokemon/models/02_generation/raikou/raikou.geo.json` |
| entei.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_entei.geo.json` |
| entei.geo.json | `assets/cobblemon/bedrock/pokemon/models/02_generation/entei/entei.geo.json` |
| suicune.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_suicune.geo.json` |
| suicune.geo.json | `assets/cobblemon/bedrock/pokemon/models/02_generation/suicune/suicune.geo.json` |
| tyranitar_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0248_tyranitar/tyranitar_mega.geo.json` |
| blaziken_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0257_blaziken/blaziken_mega.geo.json` |
| gardevoirmega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0282_gardevoir/gardevoirmega.geo.json` |
| aggron_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0306_aggron/aggron_mega.geo.json` |
| sharpedomega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0319_sharpedo/sharpedomega.geo.json` |
| camerupt_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0323_camerupt/camerupt_mega.geo.json` |
| absol_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0359_absol/absol_mega.geo.json` |
| glalie_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0362_glalie/glalie_mega.geo.json` |
| salamencemega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0373_salamence/salamencemega.geo.json` |
| metagross_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0376_metagross/metagross_mega.geo.json` |
| lopunny_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0428_lopunny/lopunny_mega.geo.json` |
| lucario_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0448_lucario/lucario_mega.geo.json` |
| snover.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0459_snover/snover.geo.json` |
| abomasnow.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0460_abomasnow/abomasnow.geo.json` |
| abomasnow_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0460_abomasnow/abomasnow_mega.geo.json` |
| gallade_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0475_gallade/gallade_mega.geo.json` |
| froslass_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0478_froslass/froslass_mega.geo.json` |
| rotom.geo.json | `assets/cobblemon/bedrock/pokemon/models/0479_rotom/rotom.geo.json` |
| rotom_fan.geo.json | `assets/cobblemon/bedrock/pokemon/models/0479_rotom/rotom_fan.geo.json` |
| rotom_frost.geo.json | `assets/cobblemon/bedrock/pokemon/models/0479_rotom/rotom_frost.geo.json` |
| rotom_heat.geo.json | `assets/cobblemon/bedrock/pokemon/models/0479_rotom/rotom_heat.geo.json` |
| rotom_mow.geo.json | `assets/cobblemon/bedrock/pokemon/models/0479_rotom/rotom_mow.geo.json` |
| rotom_wash.geo.json | `assets/cobblemon/bedrock/pokemon/models/0479_rotom/rotom_wash.geo.json` |
| scrafty_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0559_scrafty/scrafty_mega.geo.json` |
| scrafty_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0560_scrafty/scrafty_mega_karma.geo.json` |
| scrafty_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0560_scrafty/scrafty_mega_karma_aura1.geo.json` |
| scrafty_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0560_scrafty/scrafty_mega_karma_aura2.geo.json` |
| scrafty_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0560_scrafty/scrafty_mega.geo.json` |
| chandelure_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0609_chandelure/chandelure_mega.geo.json` |
| golurk_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0623_golurk/golurk_mega.geo.json` |
| golurk_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_golurk_mega.geo.json` |
| chesnaught_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0652_chesnaught/chesnaught_mega.geo.json` |
| delphoxmega.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_delphoxmega.geo.json` |
| floette_eternal.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0670_floette/floette_eternal.geo.json` |
| floette_eternal_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0670_floette/floette_eternal_mega.geo.json` |
| meowstic_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0678_meowstic/meowstic_mega.geo.json` |
| malamarmega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0687_malamar/malamarmega.geo.json` |
| barbaracle_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0689_barbaracle/barbaracle_mega.geo.json` |
| dragalge_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0691_dragalge/dragalge_mega.geo.json` |
| crabominable_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0740_crabominable/crabominable_mega.geo.json` |
| drampamega.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_drampamega.geo.json` |
| blipbug.geo.json | `assets/cobblemon/bedrock/pokemon/models/08_generation/blipbug/blipbug.geo.json` |
| dottler.geo.json | `assets/cobblemon/bedrock/pokemon/models/08_generation/dottler/dottler.geo.json` |
| orbeetle.geo.json | `assets/cobblemon/bedrock/pokemon/models/08_generation/orbeetle/orbeetle.geo.json` |
| appletun_gmax.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_appletun_gmax.geo.json` |
| falinks_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0870_falinks/falinks_mega.geo.json` |
| glimmora_mega.geo.json | `assets/cobblemon/bedrock/pokemon/models/megas/0970_glimmora/glimmora_mega.geo.json` |
| wochien.geo.json | `assets/cobblemon/bedrock/pokemon/models/09_generation/wochien/wochien.geo.json` |
| wochien.geo.json | `assets/cobblemon/bedrock/pokemon/models/atlas_msd18/atlas_msd18_wochien.geo.json` |

## Deliberate omissions

- Suicune adds two duplicate visible eye cube bones; these are unnecessary for the new locators and omitted. Suicune tail and Mega Eternal Floette root7 cleanup only removes zero cube rotations and irrelevant pivots; omitted as visual no-ops.
- `aegislash_blade2` is used only by the standalone MSD blade resolver, absent from our pack/Atlas. Official Cobblemon uses `aegislash` and its standard poses; unused MSD poser was not copied.
- Four deleted upstream Mega Metagross textures remain locally referenced and were retained.
- Crowned/Primal remain excluded.

| Omitted upstream model | Reason |
|---|---|
| charizard_gigantamax.geo.json | No matching local geometry; upstream form not imported |
| pikachu_belle.geo.json | No matching local geometry; upstream form not imported |
| pikachu_gigantamax.geo.json | No matching local geometry; upstream form not imported |
| pikachu_libre.geo.json | No matching local geometry; upstream form not imported |
| pikachu_phd.geo.json | No matching local geometry; upstream form not imported |
| pikachu_popstar.geo.json | No matching local geometry; upstream form not imported |
| pikachu_rockstar.geo.json | No matching local geometry; upstream form not imported |
| meowth_gmax.geo.json | No matching local geometry; upstream form not imported |
| victreebel_mega.geo.json | Different legacy rig; no matching eye parent and ancestor geometry |
| gengar_gmax.geo.json | No matching local geometry; upstream form not imported |
| gengar_mega.geo.json | Different legacy rig; no matching eye parent and ancestor geometry |
| kingler_gmax.geo.json | No matching local geometry; upstream form not imported |
| lapras_gmax.geo.json | No matching local geometry; upstream form not imported |
| eevee_gigantamax.geo.json | No matching local geometry; upstream form not imported |
| snorlax_gigantamax.geo.json | No matching local geometry; upstream form not imported |
| castform.geo.json | Different legacy rig; no matching eye parent and ancestor geometry |
| castform_rainy.geo.json | No matching local geometry; upstream form not imported |
| castform_snowy.geo.json | No matching local geometry; upstream form not imported |
| castform_sunny.geo.json | No matching local geometry; upstream form not imported |
| burmy.geo.json | No matching local geometry; upstream form not imported |
| burmy_sandy.geo.json | No matching local geometry; upstream form not imported |
| burmy_trash.geo.json | Different legacy rig; no matching eye parent and ancestor geometry |
| wormadam.geo.json | No matching local geometry; upstream form not imported |
| wormadam_sandy.geo.json | No matching local geometry; upstream form not imported |
| wormadam_trash.geo.json | Different legacy rig; no matching eye parent and ancestor geometry |
| mothim.geo.json | Different legacy rig; no matching eye parent and ancestor geometry |
| greninja_mega.geo.json | Different legacy rig; no matching eye parent and ancestor geometry |
| baile_oricorio.geo.json | No matching local geometry; upstream form not imported |
| pau_oricorio.geo.json | No matching local geometry; upstream form not imported |
| pompom_oricorio.geo.json | No matching local geometry; upstream form not imported |
| sensu_oricorio.geo.json | No matching local geometry; upstream form not imported |
| minior.geo.json | Different legacy rig; no matching eye parent and ancestor geometry |
| mimikyu_busted.geo.json | No matching local geometry; upstream form not imported |
| rillaboom_gigantamax.geo.json | No matching local geometry; upstream form not imported |
| cinderace_gigantamax.geo.json | No matching local geometry; upstream form not imported |
| gmax_orbeetle.geo.json | No matching local geometry; upstream form not imported |
| gmax_coalossal.geo.json | No matching local geometry; upstream form not imported |
| sandaconda_gigantamax.geo.json | No matching local geometry; upstream form not imported |
| cramorant_gulping.geo.json | No matching local geometry; upstream form not imported |
| cramorant_pikachu.geo.json | No matching local geometry; upstream form not imported |
| centiskorch_gmax.geo.json | No matching local geometry; upstream form not imported |
| hatterene_gmax.geo.json | No matching local geometry; upstream form not imported |
| grimmsnarl_gmax.geo.json | No matching local geometry; upstream form not imported |
| alcremie_gmax.geo.json | No matching local geometry; upstream form not imported |
| gmax_copperajah.geo.json | No matching local geometry; upstream form not imported |
| gmax_duraludon.geo.json | No matching local geometry; upstream form not imported |

[Provenance and snapshots](port.json), [validation](validation.json), [artifact hashes](artifacts.json).
