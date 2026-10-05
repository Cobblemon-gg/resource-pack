# Base texture report — 11 September 2026

Reported normal Pokémon: Noibat, Eelektross, Arbok, Primarina, Skarmory, Dustox, Galarian Yamask, Beautifly.

Confirmed legacy overrides: Dustox and Beautifly still selected old pack models/textures and a poser requesting missing head_ai. Imported the complete official 1.8 graph under existing atlas_sweep18 aliases: four male/female geometries, two posers, two animation groups, two guarded resolvers, six normal/shiny/alpha textures. No assets removed. No client baseline/jar changes.

The six other species already select isolated r84 assets. Verified the actual GitHub r84 ZIP: model geometry matches official 1.8 (apart from intentional unique identifier), and included textures are byte-identical. This establishes asset provenance, not that the reported appearance is resolved. Need a screenshot and confirmation of a successful resourcepackupdate if those remain visibly wrong. Do not mark the six fresh reports resolved by static checks alone.

Manual checks (normal and shiny, standing/moving plus GUI preview):

```mcfunction
/spawnpokemon noibat
/spawnpokemon eelektross
/spawnpokemon arbok
/spawnpokemon primarina
/spawnpokemon skarmory
/spawnpokemon yamask galarian
/spawnpokemon dustox gender=male
/spawnpokemon dustox gender=female
/spawnpokemon beautifly gender=male
/spawnpokemon beautifly gender=female
```

Repeat with shiny=true. No in-game render session performed by the agent.

Validation: full Modrinth and CurseForge installed-modpack audits each covered 1,026 resolver sets / 20,485 states; zero critical/missing-asset states, zero unclassified posers, zero parse errors. Existing unrelated animation warnings remain. Overlay diff vs r84: exactly 16 additions, zero removals.
