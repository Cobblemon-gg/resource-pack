---
name: add-skins
description: Add new Pokemon skins to the Cobblemon resource pack from a Downloads folder. Deploys models, textures, aura geos, resolvers, and generates config entries. Use when the user says to add skins from a folder.
---

# Add Pokemon Skins to Resource Pack

You are adding new Pokemon skin sets to the Cobblemon resource pack. The user will provide a folder path (usually in ~/Downloads) containing skin assets.

Use `$ARGUMENTS` as the folder path. If not provided, ask the user for the folder path.

## Step 1: Scan the Source Folder

List all Pokemon folders in the source. Each Pokemon folder typically contains:
- `{name}_medieval/{name}_medieval.geo.json` — base model geo
- `{name}_medieval/{name}_medieval.png` — base texture
- `{name}_medieval/{name}_shiny_medieval.png` — shiny texture
- `{name}_medieval/ef_{name}_medieval/ef_{name}_medieval_1.json` — aura1 geo
- `{name}_medieval/ef_{name}_medieval/ef_{name}_medieval_2.json` — aura2 geo
- Shared aura textures in `ef_{theme}/ef_{theme}_1/` and `ef_{theme}_2/` (8 PNG frames each)

The theme name (e.g., "medieval", "cyberpunk", "masquerade") is derived from the skin subfolder names. Replace "medieval" above with the actual theme.

**Important variant detection:**
- Folders like `{name}_alola_{theme}` = alolan regional form (aspect: `["alolan"]`)
- Folders like `{name}_hisuian_{theme}` = hisuian regional form (aspect: `["hisuian"]`)
- Folders like `{name}_male_{theme}` = male gender form (aspect: `["male"]`)
- Folders like `{name}_mega_{theme}` = mega evolution (goes in `megas/` folder)
- If a Pokemon's ef folder contains `.png` files alongside `.json`, it has **custom aura textures** (not shared)

## Step 2: Map Pokemon to Generations

Use Pokedex numbers from folder names (e.g., `0065_alakazam` = #65 = Gen 1). Map to generation folders:
- 01_generation: #1-151
- 02_generation: #152-251
- 03_generation: #252-386
- 04_generation: #387-493
- 05_generation: #494-649
- 06_generation: #650-721
- 07_generation: #722-809
- 08_generation: #810-905
- 09_generation: #906-1025

For unnumbered folders, look up the Pokedex number.

## Step 3: Deploy Files

For each skin, using a Python script for efficiency:

### 3a. Shared Aura Textures
Copy to: `assets/cobblemon/textures/pokemon/auras/{theme}/`
- `ef_{theme}_1_{1-8}.png` and `ef_{theme}_2_{1-8}.png`

### 3b. Model Geos
Destination: `assets/cobblemon/bedrock/pokemon/models/{gen}/{pokemon}/` (or `megas/{dex}/` for megas)

- Copy base geo: `{name}_{theme}.geo.json`
- Copy + rename aura geos: `ef_{name}_{theme}_1.json` -> `{name}_{theme}_aura1.geo.json`
- Copy + rename aura geos: `ef_{name}_{theme}_2.json` -> `{name}_{theme}_aura2.geo.json`

**CRITICAL: Update geometry identifiers** in all geo files:
- Base: `geometry.{name}_{theme}`
- Aura1: `geometry.{name}_{theme}_aura1`
- Aura2: `geometry.{name}_{theme}_aura2`

### 3c. Textures
Destination: `assets/cobblemon/textures/pokemon/{gen}/{pokemon}/` (or `megas/{dex}/` for megas)
- `{name}_{theme}.png` (base)
- `{name}_shiny_{theme}.png` (shiny)

### 3d. Custom Aura Textures (if applicable)
If a Pokemon has custom aura PNGs in its ef folder, copy to:
`assets/cobblemon/textures/pokemon/{gen}/{pokemon}/auras/`

### 3e. Resolvers
Destination: `assets/cobblemon/bedrock/pokemon/resolvers/pokemon/{gen}/{dex_folder}/` (or `megas/{dex}/`)

**CRITICAL PATH CONSTRUCTION — DO NOT DOUBLE THE GENERATION:**

The texture path in the resolver must be: `cobblemon:textures/pokemon/{gen}/{pokemon}/{file}.png`

For example: `cobblemon:textures/pokemon/01_generation/alakazam/alakazam_medieval.png`

**NOT** `cobblemon:textures/pokemon/01_generation/01_generation/alakazam/...` (WRONG - doubled generation)

For megas: `cobblemon:textures/pokemon/megas/{dex}/{file}.png`

**NOT** `cobblemon:textures/pokemon/megas/megas/{dex}/...` (WRONG - doubled megas)

When building the path in a script, construct the full texture path directly rather than nesting a `tex_base` that already contains the generation inside another generation prefix:
```python
# CORRECT:
tex_path = f"cobblemon:textures/pokemon/{gen}/{pokemon_folder}/{filename}.png"

# WRONG - leads to doubled path:
tex_base = f"{gen}/{pokemon_folder}"
tex_path = f"cobblemon:textures/pokemon/{gen}/{tex_base}/{filename}.png"
```

Each resolver has 6 variations:
```json
{
  "species": "cobblemon:{species_id}",
  "order": 3,
  "variations": [
    { "aspects": ["{theme}"], "model": "cobblemon:{name}_{theme}.geo", "texture": "cobblemon:textures/pokemon/{gen}/{pokemon}/{name}_{theme}.png" },
    { "aspects": ["{theme}", "shiny"], "model": "cobblemon:{name}_{theme}.geo", "texture": "cobblemon:textures/pokemon/{gen}/{pokemon}/{name}_shiny_{theme}.png" },
    { "aspects": ["{theme}-aura1"], "model": "cobblemon:{name}_{theme}_aura1.geo", "texture": "cobblemon:textures/pokemon/{gen}/{pokemon}/{name}_{theme}.png", "layers": [AURA_LAYER_1] },
    { "aspects": ["{theme}-aura1", "shiny"], "model": "cobblemon:{name}_{theme}_aura1.geo", "texture": "cobblemon:textures/pokemon/{gen}/{pokemon}/{name}_shiny_{theme}.png", "layers": [AURA_LAYER_1] },
    { "aspects": ["{theme}-aura2"], "model": "cobblemon:{name}_{theme}_aura2.geo", "texture": "cobblemon:textures/pokemon/{gen}/{pokemon}/{name}_{theme}.png", "layers": [AURA_LAYER_2] },
    { "aspects": ["{theme}-aura2", "shiny"], "model": "cobblemon:{name}_{theme}_aura2.geo", "texture": "cobblemon:textures/pokemon/{gen}/{pokemon}/{name}_shiny_{theme}.png", "layers": [AURA_LAYER_2] }
  ]
}
```

Where `{gen}` is e.g. `01_generation` and `{pokemon}` is the pokemon folder name (e.g. `alakazam`). These are separate variables — never nest one inside the other.

For regional/gender variants, prepend the form aspect (e.g., `["alolan", "{theme}"]`).

**CRITICAL: Form variant resolvers MUST have a higher `order` than the base form resolver.** If both have the same order, the more specific form won't display. Use:
- Base skin: `"order": 3`
- Form variants (alolan, hisuian, male, phony, etc.): `"order": 4`

**CRITICAL: Mega skin resolvers must have a higher `order` than the existing mega resolver for that Pokemon.** Check the existing mega resolver's order first, then set the new skin's order to be +1 higher. For example, if the existing `falinks_mega.json` has `"order": 7`, then `falinks_mega_medieval.json` must be `"order": 8`. Always read the existing mega order before assigning — do NOT use a hardcoded value.

Aura layer format:
```json
{
  "name": "aura",
  "texture": {
    "frames": ["cobblemon:textures/pokemon/auras/{theme}/ef_{theme}_{aura_num}_{1-8}.png"],
    "fps": 10,
    "loop": true
  },
  "emissive": true,
  "translucent": true
}
```

For custom aura textures, point frames to the Pokemon-specific aura path instead.

## Step 4: Species ID Reference

**CRITICAL: Cobblemon species IDs are lowercase with NO underscores, NO hyphens, NO spaces — just concatenated letters.**

The species ID in the resolver `"species"` field must have no separators:
- `cobblemon:mrmime` (NOT `mr_mime` or `mr-mime`)
- `cobblemon:chienpao` (NOT `chien_pao` or `chien-pao`)
- `cobblemon:kommoo` (NOT `kommo-o` or `kommo_o`)
- `cobblemon:sirfetchd` (NOT `sirfetch'd`)
- `cobblemon:tapulele`, `cobblemon:ironvaliant`, `cobblemon:ironleaves`, `cobblemon:ironbundle`, `cobblemon:ironhands`, `cobblemon:ironcrown`, `cobblemon:roaringmoon`, `cobblemon:fluttermane`

Note: File/folder names CAN have underscores (e.g., `mr_mime_medieval.geo.json`), but the `"species"` value in the resolver JSON must NOT. The species ID is always a single concatenated word.

## Step 5: Generate Config Entries

After deploying files, output the skin config YAML entries for the user to paste:
```yaml
  {pokemon}_{theme}:
    name: "&#HEX&l{Theme} {Pokemon}"
    aspect: "{theme}"
    pokemon: "{species_id}"
```

Use vibrant hex colors that fit the theme. Only list unique Pokemon (skip form variants like alola/hisuian/mega).

## Naming Conventions Summary

| Item | Pattern |
|------|---------|
| Geo file | `{pokemon}_{theme}.geo.json` |
| Geo identifier | `geometry.{pokemon}_{theme}` |
| Aura geo file | `{pokemon}_{theme}_aura{1,2}.geo.json` |
| Aura geo identifier | `geometry.{pokemon}_{theme}_aura{1,2}` |
| Model reference | `cobblemon:{pokemon}_{theme}.geo` |
| Texture path | `cobblemon:textures/pokemon/{gen}/{pokemon}/{pokemon}_{theme}.png` |
| Resolver file | `3_{pokemon}_{theme}.json` |
| Aspect in resolver | `{theme}` (hyphenated: `st-patricks`, `lunar-new-year`) |
| Resolver folder | `{gen}/{dex_number}_{pokemon}/` |
