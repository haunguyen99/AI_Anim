// VfxShaderLib.cginc — tiny shared helpers for shader-only VFX (vfx-shader skill).
// Lives in Assets/VFX/_Shared/Shaders/. Include with:
//   #include "Assets/VFX/_Shared/Shaders/VfxShaderLib.cginc"
// Everything is inline, branch-free and mobile friendly. Cost notes are per call.
#ifndef VFX_SHADER_LIB_INCLUDED
#define VFX_SHADER_LIB_INCLUDED

#define VFX_SHADER_LIB_VERSION 1

// ---------------------------------------------------------------- UV space

// UV 0..1 -> centered -1..1 (quad center = 0).
inline float2 vfxCentered(float2 uv) { return uv * 2.0 - 1.0; }

// Rotate a 2D point. Compute sin/cos in the vertex shader when the angle is per particle.
inline float2 vfxRotate(float2 p, float s, float c) { return float2(c * p.x - s * p.y, s * p.x + c * p.y); }

// Polar coords: x = radius, y = angle 0..1. atan2 is the most expensive call here — use only when the
// effect really needs angle (swirls, radial streaks). Add a tiny eps to avoid NaN at the center.
inline float2 vfxPolar(float2 p) { return float2(length(p), atan2(p.y, p.x + 1e-5) * 0.1591549 + 0.5); }

// ---------------------------------------------------------------- Shapes (signed distance, <0 inside)

inline half vfxSdCircle(float2 p, half r) { return length(p) - r; }
inline half vfxSdRing(float2 p, half r, half halfWidth) { return abs(length(p) - r) - halfWidth; }
inline half vfxSdBox(float2 p, half2 halfSize) { float2 d = abs(p) - halfSize; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
// Capsule / beam from a to b with radius r.
inline half vfxSdSegment(float2 p, float2 a, float2 b, half r)
{
    float2 pa = p - a, ba = b - a;
    float h = saturate(dot(pa, ba) / dot(ba, ba));
    return length(pa - ba * h) - r;
}

// Signed distance -> coverage 0..1 with soft edge (soft > 0).
inline half vfxFill(half d, half soft) { return 1.0h - smoothstep(-soft, soft, d); }

// ---------------------------------------------------------------- Value shaping

inline half vfxRemap01(half x, half a, half b) { return saturate((x - a) / (b - a)); }
// Hard-ish step around an edge (toon band). soft > 0.
inline half vfxBand(half x, half edge, half soft) { return smoothstep(edge - soft, edge + soft, x); }
// 3-tone toon ramp: dark below e1, mid between, light above e2.
inline half3 vfxRamp3(half v, half3 cDark, half3 cMid, half3 cLight, half e1, half e2, half soft)
{
    half3 c = lerp(cDark, cMid, vfxBand(v, e1, soft));
    return lerp(c, cLight, vfxBand(v, e2, soft));
}

// ---------------------------------------------------------------- Time / progress

// Dissolve keep factor. mask: high = stays longer. progress 0 = all visible, 1 = all gone. soft > 0.
inline half vfxDissolve(half mask, half progress, half soft)
{
    half t = lerp(-soft, 1.0h, saturate(progress));
    return smoothstep(t, t + soft, mask);
}

// Cheap ease-out for growth: 1-(1-x)^2.
inline half vfxEaseOut(half x) { x = saturate(x); return 1.0h - (1.0h - x) * (1.0h - x); }

// Fade in over [0,a], hold, fade out over [b,1] of a 0..1 life.
inline half vfxLifeFade(half life, half a, half b) { return saturate(life / max(a, 1e-3h)) * saturate((1.0h - life) / max(1.0h - b, 1e-3h)); }

#endif
