# Resource-pack authoring

Before changing skins, cosmetics, tags/fonts or inventory assets, read `README.md` (client baseline and server overlay workflow). Local Codex guidance also lives at `/Users/daniel/.codex/skills/cobblemon-ops/references/skins-and-resource-pack.md`.

Keep `assets/` as the complete authoring source. Routine updates use `python3 tools/build_pack.py build` and produce `dist/resource-pack.zip`; do not hand-update the legacy ZIP beside this repository. Do not freeze/replace the client baseline for routine updates. Preserve skin dependencies and complete resolver/model definitions. Font providers merge across layers; deleting an overlay provider does not remove its baseline glyph. The full fallback remains necessary until clients have the matching baseline.

For species in `reports/mega-showdown-1.8-model-test-list.md`, new normal/shiny sets use `atlas_msd18_*` aliases while custom skins retain legacy assets. After adding/changing skin/form aspects, run `python3 tools/msd18_skin_guards.py --refresh` before the normal overlay build; the builder rejects stale guards. Skins deliberately authored for new geometry must explicitly select the matching model, poser and texture/layers. Never remove existing skin protection to make a build pass.

## Installed-modpack model audit

For Pokémon model/poser/texture fixes, audit the actual installed Modrinth and CurseForge `mods/` directories, not only Cobblemon + Atlas. Journey Mounts 1.7.2 overrides hundreds of models and was the source of 1.8 root/UV conflicts. Run `python3 tools/audit_installed_models.py --profile "/path/to/instance" --overlay dist/resource-pack.zip --output /path/to/audit-output`. The scanner includes every mod, the Atlas baseline, generic posers and the overlay. The compiled poser inventory is tied to the official Cobblemon jar hash; update it when Cobblemon changes. Do not bypass a mismatch.

`atlas_hotfix18` and `atlas_sweep18` resolver/model/poser/animation aliases preserve official 1.8 standard sets while guarding legacy skins. Both are tracked by `tools/msd18-skin-guards.json`; run the existing guard refresh command after adding skins. Never remove those guards or overwrite the old custom rigs just to restore a standard model. See `reports/full-installed-model-scan-20260910.md` for scope, manual commands and remaining animation warnings. A zero critical-state count is not a guarantee of visually correct rendering or coverage of every dynamic Molang expression.
