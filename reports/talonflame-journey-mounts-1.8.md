# Talonflame compatibility with Journey Mounts 1.7.2

The official Cobblemon 1.8.0 model and its license are deliberately copied to
`assets/cobblemon/bedrock/pokemon/models/0663_talonflame/`.
Do not deduplicate this override against Cobblemon while Journey Mounts 1.7.2
remains supported: that mod replaces the same geometry resource with an older rig.
Cobblemon 1.8's poser requires `wing_open_left`, `wing_open_right`,
`wing_closed_left1`, and `wing_closed_right1`; the older rig lacks these bones,
causing the reported PC screen rendering crash. A server pack takes priority over
the mod's asset and restores the paired 1.8 rig without uninstalling Journey Mounts.
The Egyptian skin keeps its separate geometry, legacy poser, animation and textures.

Source: official `Cobblemon-fabric-1.8.0+1.21.1.jar` in the local Modrinth profile.
No client baseline refresh or server jar change is required. Players must load the
updated pack for the override to apply. This is a Cobblemon 1.8 pack change; do not
publish it to an older Cobblemon release as a standalone geometry swap.

The ordinary pack builder passed and both generated ZIPs contain identical source
model bytes. With Journey Mounts installed, static checks against the generated
overlay and Atlas client baseline pass normal, shiny, alpha, shiny alpha, Egyptian
and shiny Egyptian states. These checks cover the missing transformed-part bones;
they are not an in-game rendering or riding test.

Manual checks (with Journey Mounts still installed and the new pack loaded):

```text
/spawnpokemon talonflame
/spawnpokemon talonflame shiny
/spawnpokemon talonflame alpha
/spawnpokemon talonflame alpha shiny
/spawnpokemon talonflame egyptian
/spawnpokemon talonflame egyptian shiny
```

Also view these forms in the PC and Atlas previews, then test mounting, flight and
dismounting. Validation script and detailed results:
`atlas/output/talonflame-server-pack-20260910/check.py` and `result.json`.

Artifacts are built locally; this change has not been published to live delivery.
The generated overlay includes the repository's other pending changes as usual.

## Animation correction after in-game feedback

The initial geometry-only change stopped the crash, but the user reported the
normal model looking at the floor. `BedrockAnimationRepository.loadAnimations`
indexes groups by the animation **filename**, not the group portion of JSON keys.
Our Egyptian compatibility animations had legacy-prefixed keys but still occupied
`atlas_compat/talonflame.animation.json`, colliding with the official animation group.
The Egyptian poser also referenced a filename group that did not exist.

The legacy animation data now lives at
`atlas_compat/atlas_legacy_talonflame.animation.json`. The old compatibility path
contains the exact official 1.8 animation bytes, deliberately retained to override
already distributed Atlas client jars. Do not delete that path while those clients
are supported. Both files are mirrored into Atlas client source for its next build;
no client jar rebuild or baseline refresh is required to use the server-pack fix.

`check-animation-fix.py` additionally rejects differing resources with the same
animation group filename and checks each of the six states' Bedrock animation
references. It passes with the existing client jar, Journey Mounts and the rebuilt
server overlay. In-game posture, PC previews and riding must be retested.
