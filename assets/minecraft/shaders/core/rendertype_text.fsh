#version 150

#moj_import <fog.glsl>

uniform sampler2D Sampler0;

uniform vec4 ColorModulator;
uniform float FogStart;
uniform float FogEnd;
uniform vec4 FogColor;
uniform float GameTime;

in float vertexDistance;
in vec4 vertexColor;
flat in vec4 baseColor;
in vec2 corner;
flat in float isGui;
in vec4 screenPos;
flat in float isShadow;
flat in float isWorldText;
noperspective in vec3 worldPos;
in vec2 texCoord0;

// No noperspective varyings — UV bounds use texCoord0 + estimated bounds.

#define TEXT_EFFECTS_FSH
#moj_import<text_effects.glsl>

int applyTextEffects() {
    uint vertexColorId = colorId(floor(round(textData.color.rgb * 255.0) / 4.0) / 255.0);
    if(textData.isShadow) { vertexColorId = colorId(textData.color.rgb);}
    switch(vertexColorId) {
        case 16777215u:

    #moj_import<text_effects_config.glsl>

        return 0;
    }
    return 0;
}

out vec4 fragColor;

void main() {
    textData.isShadow = isShadow > 0.5;
    textData.backColor = vec4(0.0);
    textData.topColor = vec4(0.0);
    textData.doTextureLookup = true;

    if(isGui > 0.5 && isWorldText > 0.5) {
        // World text (holograms, nametags, etc.) - use simple path
        textData.uv = texCoord0;
        textData.color = baseColor;

        textData.uvMin = vec2(0.0);
        textData.uvMax = vec2(1.0);
        textData.uvCenter = vec2(0.5);
        textData.localPosition = texCoord0;

        textData.position = vec2(gl_FragCoord.x, 0.0);
        textData.characterPosition = vec2(gl_FragCoord.x, 0.0);

        applyTextEffects();

    } else if(isGui > 0.5) {
        textData.color = baseColor;

        // Use texCoord0 directly (always valid from GPU interpolation).
        // The noperspective trick for reconstructing UV bounds is unreliable —
        // the GPU's quad triangle decomposition is undefined and changes on F3+T.
        // Instead, use texCoord0 with conservative estimated bounds.
        // MC font atlas characters are ~5-8 texels wide on a 256x256 atlas.
        vec2 charEstimate = vec2(6.0 / 256.0);
        textData.uv = texCoord0;
        textData.uvMin = texCoord0 - charEstimate;
        textData.uvMax = texCoord0 + charEstimate;
        textData.uvCenter = texCoord0;
        textData.localPosition = vec2(0.5);
        textData.position = gl_FragCoord.xy;
        textData.characterPosition = gl_FragCoord.xy;

        applyTextEffects();
    } else {
        // No effects - passthrough
        textData.uv = texCoord0;
        textData.color = vertexColor;
    }

    vec4 textureSample = texture(Sampler0, textData.uv);
    if(!textData.doTextureLookup) textureSample = vec4(0.0);

    fragColor = mix(vec4(textData.backColor.rgb, textData.backColor.a * textData.color.a), textureSample * textData.color, textureSample.a);
    fragColor.rgb = mix(fragColor.rgb, textData.topColor.rgb, textData.topColor.a);
    fragColor *= ColorModulator;

    if (fragColor.a < 0.1) {
        discard;
    }
    fragColor = linear_fog(fragColor, vertexDistance, FogStart, FogEnd, FogColor);
}
