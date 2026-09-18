struct TextData {
    vec4 color;
    vec4 topColor;
    vec4 backColor;
    vec2 position;
    vec2 characterPosition;
    vec2 localPosition;
    vec2 uv;
    vec2 uvMin;
    vec2 uvMax;
    vec2 uvCenter;
    bool isShadow;
    bool doTextureLookup;
};

TextData textData;

#define PI 3.14159265359
#define TAU 6.28318530718
#define EPSILON 0.0001

bool uvBoundsCheck(vec2 uv, vec2 uvMin, vec2 uvMax) {
    return uv.x < textData.uvMin.x + EPSILON || uv.y < textData.uvMin.y + EPSILON || uv.x > textData.uvMax.x - EPSILON || uv.y > textData.uvMax.y - EPSILON;
}

vec3 hsvToRgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec3 rgbToHsv(vec3 c)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec4 rgba(int r, int g, int b, int a) {
    return vec4(r / 255.0, g / 255.0, b / 255.0, a / 255.0);
}

vec3 rgb(int r, int g, int b) {
    return vec3(r / 255.0, g / 255.0, b / 255.0);
}

vec3 hsv(int h, int s, int v) {
    vec3 c = vec3(h / 255.0, s / 255.0, v / 255.0);
    return hsvToRgb(c);
}

uint colorId(vec3 col) {
    uint r = uint(round(col.r * 255.0));
    uint g = uint(round(col.g * 255.0));
    uint b = uint(round(col.b * 255.0));
    return (r << 16) | (g << 8) | (b);
}

float random(vec2 seed) {
    return fract(sin(dot(seed, vec2(12.9898,78.233))) * 43758.5453);
}

float random(float seed) {
    return fract(sin(seed)  * 43758.5453);
}

float noise(float n) {
    float i = floor(n);
    float f = fract(n);
    return mix(random(i), random(i + 1.0), smoothstep(0.0, 1.0, f));
}

float noise(vec2 p){
	vec2 ip = floor(p);
	vec2 u = fract(p);
	u = u*u*(3.0-2.0*u);

	float res = mix(
		mix(random(ip),random(ip+vec2(1.0,0.0)),u.x),
		mix(random(ip+vec2(0.0,1.0)),random(ip+vec2(1.0,1.0)),u.x),u.y);
	return res*res;
}

vec3 textSdf() {
    vec3 value = vec3(0.0, 0.0, 1.0);

    vec2 texelSize = 1.0 / vec2(256.0);
    for(int x = -1; x <= 1; x++) {
        for(int y = -1; y <= 1; y++) {
            vec2 uv = textData.uv + vec2(x, y) * texelSize;
            if(uvBoundsCheck(uv, textData.uvMin, textData.uvMax)) continue;

            vec4 s = texture(Sampler0, uv);
            if(s.a >= 0.1) {
                vec3 v = vec3(fract(uv * 256.0), 0.0);

                if(x == 0) v.x = 0.0;
                if(y == 0) v.y = 0.0;
                if(x > 0) v.x = 1.0-v.x;
                if(y > 0) v.y = 1.0-v.y;

                v.z = length(v.xy);

                if(v.z < value.z) value = v;
            }
        }
    }
    return value;
}

void override_text_color(vec4 color) {
    textData.color = color;
    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void override_text_color(vec3 color) {
    textData.color.rgb = color;
    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void override_shadow_color(vec4 color) {
    if(textData.isShadow) textData.color = color;
}

void override_shadow_color(vec3 color) {
    if(textData.isShadow) textData.color.rgb = color;
}

void remove_text_shadow() {
    if(textData.isShadow) textData.color.a = 0.0;
}

void apply_waving_movement(float speed) {
    textData.uv.y += sin(textData.characterPosition.x * 0.1 - GameTime * 7500.0 * speed) / 256.0;
}

void apply_waving_movement() {
    apply_waving_movement(1.0);
}

void apply_shaking_movement() {
    float noiseX = noise(textData.characterPosition.x + textData.characterPosition.y + GameTime * 32000.0) - 0.5;
    float noiseY = noise(textData.characterPosition.x - textData.characterPosition.y + GameTime * 32000.0) - 0.5;

    textData.uv += vec2(noiseX, noiseY) / 256.0;
}

void apply_iterating_movement(float speed, float space) {
    float x = mod(textData.characterPosition.x * 0.4 - GameTime * 18000.0 * speed, (5.0 * space) * TAU);
    if(x > TAU) x = TAU;
    textData.uv.y += (-cos(x) * 0.5 + 0.5) / 256.0;
}

void apply_iterating_movement() {
    apply_iterating_movement(1.0, 1.0);
}

void apply_flipping_movement(float speed, float space) {
    float t = mod((textData.characterPosition.x * 0.4 - GameTime  * 18000.0 * speed) / TAU, 5.0 * space);
    textData.uv.x = textData.uvCenter.x + (textData.uv.x - textData.uvCenter.x) / (cos(TAU * min(t, 1.0)));
    textData.uv.y = textData.uvCenter.y + (textData.uv.y - textData.uvCenter.y) / (1.0 + 0.1 * sin(TAU * min(t, 1.0)));
}

void apply_flipping_movement() {
    apply_flipping_movement(1.0, 1.0);
}

void apply_skewing_movement(float speed) {
    float t = GameTime * 1600.0 * speed;

    textData.uv.x = mix(textData.uv.x, textData.uv.x + sin(TAU * t * 0.5) / 256.0, 1.0 - textData.localPosition.y);
    textData.uv.y = mix(textData.uv.y, textData.uvMax.y, -(0.3 + 0.5 * cos(TAU * t)));
}

void apply_skewing_movement() {
    apply_skewing_movement(1.0);
}

void apply_growing_movement(float speed) {
    vec2 offset = vec2(0.0, 5.0 / 256.0);
    textData.uv = (textData.uv - textData.uvCenter - offset) * (sin(GameTime * 12800.0 * speed) * 0.15 + 0.85) + textData.uvCenter + offset;
}

void apply_growing_movement() {
    apply_growing_movement(1.0);
}

void apply_outline(vec3 color) {
    if(textData.isShadow) {
        color *= 0.25;
        textData.color.rgb = color;
    }

    // Sample all 8 neighbors unconditionally (no bounds check needed).
    // texCoord0 is always valid, and MC's font atlas has sufficient padding
    // between characters to prevent cross-character bleed at ±1 texel.
    vec2 texelSize = 1.0 / vec2(256.0);

    for(int x = -1; x <= 1; x++) {
        for(int y = -1; y <= 1; y++) {
            if(x == 0 && y == 0) continue;

            vec4 s = texture(Sampler0, textData.uv + vec2(x, y) * texelSize);
            if(s.a >= 0.1) { textData.backColor = vec4(color, 1.0); return; }
        }
    }
}

void apply_thin_outline(vec3 color) {
    if(textData.isShadow) {
        color *= 0.25;
        textData.color.rgb = color;
    }

    vec2 texelSize = 1.0 / vec2(256.0);

    for(int x = -1; x <= 1; x++) {
        for(int y = -1; y <= 1; y++) {
            if(x == 0 && y == 0) continue;
            if(x != 0 && y != 0) continue; // cardinal directions only

            vec4 s = texture(Sampler0, textData.uv + vec2(x, y) * texelSize);
            if(s.a >= 0.1) { textData.backColor = vec4(color, 1.0); return; }
        }
    }
}

void apply_gradient(vec3 color1, vec3 color2) {
    textData.color.rgb = mix(color1, color2, (textData.uv.y - textData.uvMin.y) / (textData.uvMax.y - textData.uvMin.y));
    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_rainbow() {
    textData.color.rgb = hsvToRgb(vec3(0.005 * (textData.position.x + textData.position.y) - GameTime * 300.0, 0.8, 1.0));
    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_shimmer(float speed, float intensity) {
    if(textData.isShadow) return;
    float f = textData.localPosition.x + textData.localPosition.y - GameTime * 6400.0 * speed;
    if(mod(f, 5) < 0.75) textData.color.rgb = mix(textData.color.rgb, vec3(1.0), intensity);
}

void apply_shimmer(){
    apply_shimmer(1.0, 0.5);
}

void apply_chromatic_abberation() {
    float noiseX = noise(GameTime * 12000.0) - 0.5;
    float noiseY = noise(GameTime * 12000.0 + 19732.134) - 0.5;
    vec2 offset = vec2(0.5 / 256, 0.0) + vec2(0.5, 1.0) * vec2(noiseX, noiseY) / 256;

    vec2 uv = textData.uv + offset;
    vec4 s1 = texture(Sampler0, uv);
    s1.rgb *= s1.a;
    if(uvBoundsCheck(uv, textData.uvMin, textData.uvMax)) s1 = vec4(0.0);

    uv = textData.uv - offset;
    vec4 s2 = texture(Sampler0, uv);
    s2.rgb *= s2.a;
    if(uvBoundsCheck(uv, textData.uvMin, textData.uvMax)) s2 = vec4(0.0);

    textData.backColor = (s1 * vec4(1.0, 0.25, 0.0, 1.0)) + (s2 * vec4(0.0, 0.75, 1.0, 1.0));
    textData.backColor.rgb *= textData.color.rgb;
}

void apply_metalic(vec3 color) {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y > 3) textData.color.rgb = color * 0.7;
    if(y == 3) textData.color.rgb = color + 0.25;
    if(y < 3) textData.color.rgb = color;

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_fire() {
    if(textData.isShadow) return;

    float h = fract(textData.uv.y * 256.0);
    vec2 uv = textData.uv + vec2(0.0, 1.0 / 256);
    if(uvBoundsCheck(uv, textData.uvMin, textData.uvMax)) return;
    vec4 s = texture(Sampler0, uv);
    if(s.a > 0.1) {
        float f = noise(textData.localPosition * 32.0 + vec2(0.0, GameTime * 6400.0)) * 0.5 + 0.5;
        f -= (1.0 - sqrt(h)) * 0.8;

        if(f > 0.5)
        textData.backColor = vec4(mix(vec3(1.0, 0.2, 0.2), vec3(1.0, 0.7, 0.3), (f - 0.5) / 0.5), 1.0);
    }
}

void apply_fade(float speed) {
    textData.color.a = mix(textData.color.a, 0.0, sin(GameTime * 1200 * speed * PI) * 0.5 + 0.5);
}

void apply_fade() {
    apply_fade(1.0);
}

void apply_fade(vec3 color, float speed) {
    if(textData.isShadow) color *= 0.25;

    textData.color.rgb = mix(textData.color.rgb, color, sin(GameTime * 1200 * speed * PI) * 0.5 + 0.5);
}

void apply_fade(vec3 color) {
    apply_fade(color, 1.0);
}

void apply_blinking(float speed){
    if(sin(GameTime * 3200 * speed * PI) < 0.0) { textData.color.a = 0.0; textData.backColor.a = 0.0; textData.topColor.a = 0.0; }
}

void apply_blinking() {
    apply_blinking(1.0);
}

void apply_glowing() {
    if(textData.isShadow) textData.color = vec4(0.0);
    vec3 d = textSdf();
    textData.backColor = vec4(1.0, 1.0, 1.0, (1.0 - d.z) * (1.0 - d.z));
}

void apply_lesbian_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  3) textData.color.rgb = vec3(0.839, 0.161, 0.000);
    if(y == 3) textData.color.rgb = vec3(1.000, 0.608, 0.333);
    if(y == 4) textData.color.rgb = vec3(1.000, 1.000, 1.000);
    if(y == 5) textData.color.rgb = vec3(0.831, 0.384, 0.647);
    if(y >  5) textData.color.rgb = vec3(0.647, 0.000, 0.384);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_mlm_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  3) textData.color.rgb = vec3(0.000, 0.584, 0.525);
    if(y == 3) textData.color.rgb = vec3(0.412, 0.941, 0.686);
    if(y == 4) textData.color.rgb = vec3(1.000, 1.000, 1.000);
    if(y == 5) textData.color.rgb = vec3(0.510, 0.698, 1.000);
    if(y >  5) textData.color.rgb = vec3(0.271, 0.153, 0.627);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_bisexual_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  4) textData.color.rgb = vec3(0.843, 0.000, 0.443);
    if(y == 4) textData.color.rgb = vec3(0.612, 0.306, 0.592);
    if(y >  4) textData.color.rgb = vec3(0.000, 0.208, 0.663);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_transgender_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  3) textData.color.rgb = vec3(0.357, 0.812, 0.980);
    if(y == 3) textData.color.rgb = vec3(0.961, 0.671, 0.725);
    if(y == 4) textData.color.rgb = vec3(1.000, 1.000, 1.000);
    if(y == 5) textData.color.rgb = vec3(0.961, 0.671, 0.725);
    if(y >  5) textData.color.rgb = vec3(0.357, 0.812, 0.980);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  2) textData.color.rgb = vec3(1.000, 0.012, 0.012);
    if(y == 2) textData.color.rgb = vec3(1.000, 0.549, 0.000);
    if(y == 3) textData.color.rgb = vec3(1.000, 0.929, 0.000);
    if(y == 4) textData.color.rgb = vec3(0.000, 0.502, 0.149);
    if(y == 5) textData.color.rgb = vec3(0.000, 0.302, 1.000);
    if(y >  5) textData.color.rgb = vec3(0.459, 0.027, 0.529);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_pansexual_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  3) textData.color.rgb = vec3(1.000, 0.129, 0.549);
    if(y == 3) textData.color.rgb = vec3(1.000, 0.847, 0.000);
    if(y == 4) textData.color.rgb = vec3(1.000, 0.847, 0.000);
    if(y >  4) textData.color.rgb = vec3(0.129, 0.694, 1.000);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_asexual_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  3) textData.color.rgb = vec3(0.100, 0.100, 0.100);
    if(y == 3) textData.color.rgb = vec3(0.639, 0.639, 0.639);
    if(y == 4) textData.color.rgb = vec3(1.000, 1.000, 1.000);
    if(y >  4) textData.color.rgb = vec3(0.502, 0.000, 0.502);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_aromantic_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  3) textData.color.rgb = vec3(0.047, 0.655, 0.294);
    if(y == 3) textData.color.rgb = vec3(0.584, 0.796, 0.451);
    if(y == 4) textData.color.rgb = vec3(1.000, 1.000, 1.000);
    if(y == 5) textData.color.rgb = vec3(0.639, 0.639, 0.639);
    if(y >  5) textData.color.rgb = vec3(0.100, 0.100, 0.100);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

void apply_non_binary_pride() {
    int y = int(floor((textData.uv.y - textData.uvMin.y) * 256.0));

    if(y <  3) textData.color.rgb = vec3(1.000, 0.957, 0.173);
    if(y == 3) textData.color.rgb = vec3(1.000, 1.000, 1.000);
    if(y == 4) textData.color.rgb = vec3(0.616, 0.349, 0.824);
    if(y >  4) textData.color.rgb = vec3(0.100, 0.100, 0.100);

    if(textData.isShadow) textData.color.rgb *= 0.25;
}

#ifdef TEXT_EFFECTS_FSH

    #define TEXT_EFFECT(r, g, b) return 0; case ((uint(r/4) << 16) | (uint(g/4) << 8) | uint(b/4)):

#else

    #define TEXT_EFFECT(r, g, b) return true; case ((uint(r/4) << 16) | (uint(g/4) << 8) | uint(b/4)):

#endif