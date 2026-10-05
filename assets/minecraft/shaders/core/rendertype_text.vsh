#version 150

#moj_import <fog.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;

uniform sampler2D Sampler0;
uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform mat3 IViewRotMat;
uniform int FogShape;
uniform float GameTime;

out float vertexDistance;
out vec4 vertexColor;
flat out vec4 baseColor;
out vec2 texCoord0;
out vec2 corner;
out vec4 screenPos;
flat out float isGui;
flat out float isShadow;
flat out float isWorldText;
noperspective out vec3 worldPos;

// No noperspective varyings — UV bounds use texCoord0 + estimated bounds.

#moj_import<text_effects.glsl>

bool shouldApplyTextEffects() {
    uint vertexColorId = colorId(floor(round(textData.color.rgb * 255.0) / 4.0) / 255.0);
    if(textData.isShadow) { vertexColorId = colorId(textData.color.rgb);}
    switch(vertexColorId) {
        case 16777215u:

#moj_import<text_effects_config.glsl>

        return true;
    }
    return false;
}


const vec2[] corners = vec2[](
    vec2(-1.0, +1.0), vec2(-1.0, -1.0), vec2(+1.0, -1.0), vec2(+1.0, +1.0)
);

void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);
    corner = corners[gl_VertexID % 4];

    isShadow = 0.0;//fract(Position.z) < 0.01 ? 1.0 : 0.0;

    // Detect if this is GUI text or world text
    // World text is rendered with perspective and has depth, GUI text is flat
    // Check if ModelViewMat has rotation (world) or is axis-aligned (GUI)
    // Also check ProjMat - GUI uses orthographic (ProjMat[3][3] == 1), world uses perspective (ProjMat[3][3] == 0)
    // Additionally, GUI text typically has Position.z == 0 or very small depth values
    bool isPerspective = ProjMat[3][3] == 0.0;
    bool hasDepth = abs(Position.z) > 0.001;
    isWorldText = (isPerspective && hasDepth) ? 1.0 : 0.0;

    isGui = 1.0;

    textData.isShadow = isShadow > 0.5;
    textData.color = Color;

    bool hasEffect = shouldApplyTextEffects();

    if(!hasEffect) {
        isShadow = 0.0;
        if(Position.z == 0.0 && textData.isShadow) {
            textData.isShadow = false;
            if(shouldApplyTextEffects()) {
                isShadow = 0.0;
            }else {
                isGui = 0.0;
            }
        }else{
            isGui = 0.0;
        }
    }

    // No quad expansion — outline renders within the font atlas's built-in glyph padding.

    screenPos = gl_Position;
    worldPos = Position;
    vertexDistance = 1.0;//fog_distance(IViewRotMat * Position, FogShape);
    vertexColor = Color * texelFetch(Sampler2, UV2 / 16, 0);
    baseColor = Color;
    texCoord0 = UV0;
}
