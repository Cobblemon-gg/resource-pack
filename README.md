## CobblemonGG Server Resource Pack
Welcome to the official repository for the CobblemonGG Minecraft server resource pack! This resource pack is specially designed to enhance your gameplay experience on the CobblemonGG server.

## About CobblemonGG
CobblemonGG is a unique Minecraft server that offers a one-of-a-kind gameplay experience. Dive into a world where cobblestone reigns supreme, and embark on epic adventures with your friends!

## Features
- **Custom textures:** Enjoy a fresh look with specially designed textures that complement the CobblemonGG server theme.
- **Unique sounds:** Immerse yourself in the world of CobblemonGG with custom sound effects tailored to enhance your gaming experience.
- **Server-specific features:** This resource pack includes special features that are exclusive to the CobblemonGG server, providing you with a truly unique gameplay experience.

## Contributing
We welcome contributions from the community to improve the CobblemonGG resource pack. If you have any suggestions, bug reports, or feature requests, please feel free to open an issue or submit a pull request on GitHub.

## Support
For any questions, issues, or support related to the CobblemonGG resource pack, please visit our [GitHub Discussions](https://github.com/Cobblemon-gg/resource-pack/discussions) page. Feel free to ask questions, share your experiences, and engage with the community. Our team and fellow players are here to help!

## License
This resource pack is distributed under the [CobblemonGG Resource Pack License Agreement](https://github.com/Cobblemon-gg/resource-pack/blob/master/LICENSE), which outlines the terms and conditions for its use. By downloading and using this resource pack, you agree to be bound by the terms of this license agreement.

## Client baseline and small server updates (Cobblemon 1.8)

The editable `assets/` tree remains the complete source of truth, including current
skins, tags and inventories. Its stable runtime contents are frozen into Atlas
client's `client/resource-pack/atlas-baseline.zip`. This is embedded under
`resourcepacks/atlas_baseline/` and registered with Fabric as always enabled.
Fabric loads built-in mod packs above ordinary mod assets; the server pack has
higher priority and can replace the same resource paths. Authoring files,
Finder metadata, quarantines, Git files and `data/` are excluded from releases.

Publish the new Atlas client baseline **before** switching the server to the
small overlay. Existing clients require `dist/resource-pack-full.zip` until the
new client is mandatory. The baseline ID is recorded in `client-baseline.json`;
keep that manifest paired with the client release's `resource-pack/baseline.json`.

For a new skin/tag/inventory or an edit, update `assets/` normally and run:

```sh
python3 tools/build_pack.py build
```

Upload `dist/resource-pack.zip` to the existing server pack delivery mechanism.
`server-overrides.json` maps exact authoring asset paths to reasons for always
including them in the overlay, even when unchanged from the frozen baseline.
The temporary Rayquaza entry repairs clients that load the baseline below mod
defaults. Keep it until the client pack-order fix is required; do not refresh the
baseline or rename the resolver to force delivery. Missing override assets fail
the build.
Apart from these explicit overrides, it includes only files that changed or were added since the frozen client
baseline, so no client update is required. Font files and resolver JSONs must
contain the complete desired definition at their existing path; do not rename a
resolver when replacing it, since Cobblemon merges resolver sets across paths.
Deleting a custom-only authoring resource emits an exact `pack.mcmeta` resource
filter to hide the stale client copy. Filters affect **every lower pack**, not
only the client baseline. The baseline manifest records exact overlaps with
Cobblemon and vanilla: deleting those paths fails the build with an instruction
to copy the desired upstream fallback bytes to the same authoring path instead.
For a model or texture this publishes the fallback above the baseline without
hiding the upstream resource. No fallback artwork or model is guessed.

Fonts are additive across pack layers. Editing a font JSON to remove a provider
or glyph does not erase that provider from the frozen baseline; copying vanilla's
font JSON also does not erase extra baseline glyphs. New/changed tags can still
be pushed normally at the same glyph/path. To remove a glyph without refreshing
the client, explicitly override that glyph (for example with an intentional space
provider); otherwise refresh the baseline in a new client release. Deleting an
entire custom-only font file is masked correctly, but callers must also remove
references to that font. Do not manually filter `minecraft:font/default.json`:
that would hide vanilla's ordinary text providers as well. Removing a skin also
requires removing its resolver variation and other references.

`dist/resource-pack-full.zip` is a complete fallback pack. The build reconstructs
the effective baseline + overlay hashes and fails if they differ from the current
source tree. ZIP ordering/timestamps are deterministic so unchanged rebuilds keep
the same hash. The release workflow publishes both packs and the size report.

For a deliberate **new client release**, refresh the frozen snapshot:

```sh
python3 tools/build_pack.py freeze --baseline-id YOUR_NEW_CLIENT_RELEASE --replace-baseline
python3 tools/build_pack.py build
```

Freeze indexes the sibling Cobblemon assets and the cached Minecraft 1.21.1
client JAR. On another machine, pass `--upstream-source /path/to/assets-root`
and `--upstream-source /path/to/minecraft-client.jar`; repeat the option for other
lower-priority packs containing overlapping resources. Missing index sources
fail closed. Routine `build` uses only the saved inventory, so release CI does
not need those source checkouts or JARs. Recheck the inventory when changing the
supported upstream mods; unknown lower packs cannot be accounted for in advance.

For an existing snapshot, `python3 tools/build_pack.py annotate-upstream` adds
this inventory to the server manifest without changing its asset hashes,
baseline ID, client archive, or client checksum metadata. Builds with deletions
reject older manifests until they have this annotation.

Commit both `client-baseline.json` here and `client/resource-pack/` in Atlas, build
Atlas client, and distribute it before publishing overlays based on that new
manifest. Do not refresh the baseline for routine server skin/tag updates: older
clients still need those changed files in their overlay. Snapshot bytes are
checksum-verified by the Atlas build, which does not require this sibling repo.

See [the complete model test list](reports/cobblemon-1.8-model-test-list.md) and
[the machine-readable comparison](reports/cobblemon-1.8-audit.json). New upstream
geometry that still has a custom/legacy override is explicitly marked retained.
Texture-only skins that inherit changed geometry retain the paired old geometry,
poser, animation, textures and base resolver until they can be retargeted. This
avoids applying old UV skins to a new geometry layout.

Client bundling removes repeated transfer of baseline assets; Minecraft may still
reload all resource packs when joining a server. This does not promise to remove
all resource-reload time or GPU texture memory usage. In-game testing must cover
normal/shiny/forms, every affected custom skin, tags/fonts and inventory screens,
and a changed skin/tag delivered only via the server overlay.

## Mega Showdown 1.8 model updates and future skins

See [the updated models and every retained skin/form](reports/mega-showdown-1.8-model-test-list.md).
New normal/shiny sets use isolated `atlas_msd18_*` model/poser/animation IDs.
Existing custom skins retain the old complete asset graph through guarded extra
variations at the existing resolver paths. After adding or changing skin/form
aspects for these species, refresh these guards before the normal overlay build:

```sh
python3 tools/msd18_skin_guards.py --refresh
python3 tools/build_pack.py build
```

The builder rejects stale guards instead of silently putting a new legacy skin
on incompatible new UVs. Refresh changes only the imported fallback conditions,
never the custom skin's definition. A skin authored for the new model must
explicitly select its matching `atlas_msd18_*` model and poser plus complete
texture/layers at its normal higher resolver order. Test normal/shiny and aura
variants. Do not remove old skin protection or refresh the client baseline.

Layers merge by name in Cobblemon. When retargeting a skin, explicitly disable obsolete inherited layer names with `{"name": "OLD_NAME", "enabled": false}`; an empty `layers` array does not clear inherited layers. The new standard sets already disable unmatched old layers, including incompatible old alpha-eye layers.

The [837be205 follow-up](reports/mega-showdown-1.8-837be205-model-test-list.md) adds guarded Hoopa Confined/Unbound, Mega Skarmory and G-Max Flapple sets. Hoopa aliases use native poser root scaling; keep their species baseScale at 1 unless deliberately revising that compensation. Existing Hoopa and Skarmory custom skins retain legacy dependencies.

The [53022919 (v1.1.3+1.8) follow-up](reports/mega-showdown-1.8-53022919-model-test-list.md) adds guarded Mega Absol, Mega Absol Z, Lucario VGU base/Mega/Mega Z, Mega Golisopod, Frigibax line, Mega Baxcalibur and Chi-Yu sets, translating MSD `mega_z` aspects to this pack's `mega-z` flag. Base Lucario lives in `resolvers/atlas_msd18/120_lucario.json` above the `atlas_sweep18` resolver and Mega Baxcalibur in `resolvers/atlas_msd18/100_baxcalibur_mega.json` above two tied legacy resolvers; the MSD jar's own `bedrock/pokemon` and `textures/pokemon` assets are filtered by Atlas, so this pack remains the source of truth for non-G-Max visuals. Verify with `python3 tools/verify_msd18_53022919.py`.

## Legacy skin compatibility assets (September 2026)

The `atlas_compat`, `atlas_compat18` and `atlas_legacy18` asset directories contain
isolated compatibility graphs for retained skin rigs. Their uniquely named resolver
files deliberately merge after the historical skin definitions. Some also ship in
Atlas client resources so the old server pack remains usable during the 1.8 rollout.
Do not remove these files just because a source resolver still names the older model.

For a future skin correction, edit the matching compatibility resolver/asset at the
**same path in this authoring tree** and build the server overlay normally. The server
pack can override that client asset without requiring a client update. Preserve
other variants, aura layers and form guards. Mirror the authoritative assets into
`atlas/client/src/main/resources/assets/` when preparing the next client build;
never refresh the frozen baseline as part of an ordinary fix.

The root-wrapper model aliases preserve original cubes, UVs and named bones. Do not
replace them with upstream models unless the skin has been deliberately retargeted.
JSON posers address their selected root as `__root`; compiled posers may require an
actual named root. See Atlas `output/model-repairs-20260908/` for validation and tests.

## Whole-client model validation

Use [the installed-modpack scanner and test list](reports/full-installed-model-scan-20260910.md) for model/skin compatibility changes. Scan both distributed client profiles against the built server overlay; include every installed mod. The scanner exits unsuccessfully for missing model/texture assets and identified constructor/conditional-pose crash paths. Review its animation warnings separately and perform ingame checks. Static checks cannot certify every dynamic render or animation transition.
