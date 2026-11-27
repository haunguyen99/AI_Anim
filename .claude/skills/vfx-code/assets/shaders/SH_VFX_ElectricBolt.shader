// SH_VFX_ElectricBolt — shader-only VFX (vfx-shader skill). Mobile: Built-in + URP, one unlit pass, UnityCG only.
// Look: toon electric bolt on a long quad, NO texture. The path is a jagged polyline made from hashed points
//   (linear value noise = straight segments, 2 octaves), pinned at both ends, with a thinner second strand.
//   Toon: white core + coloured rim with hard (anti-aliased) edges, faint outer glow. The shape re-rolls _Fps times a second.
// Quad: u = along the bolt (0..1), v = across. _Aspect = quad length / width (Stretched Billboard: lengthScale).
// Cost: 0 texture samples, ~10 hashes (frac/mul only), no loops, no sin/pow/atan2. target 3.0 (fwidth).
// Particle inputs (streams Position, Color, UV, Custom1XYZ): vertex color = tint (rgb) * alpha,
//   TEXCOORD0.z = Custom1.x thin 0..1 (0 full, 0.5 thin, 1 gone; from 0.5 the bolt also breaks into pieces),
//   TEXCOORD0.w = Custom1.y seed (random 0..1: each bolt a different shape),
//   TEXCOORD1.x = Custom1.z reach 0..1 (how far the bolt has travelled from its start end).
// Without a particle (MeshRenderer): _Thin, _Seed, _Reach.
Shader "VFX/FX/Electric Bolt"
{
    Properties
    {
        [HDR] _ColorCore ("Core Color", Color) = (1.4, 1.5, 1.6, 1)
        [HDR] _ColorRim ("Rim Color", Color) = (0.25, 0.6, 2.0, 1)
        _Aspect ("Quad Length / Width", Float) = 5
        _Segments ("Big Segments Along Length", Range(1, 24)) = 8
        _Amp ("Zigzag Amplitude (fraction of width)", Range(0, 0.45)) = 0.26
        _Detail ("Small Zigzag (x3 segments)", Range(0, 1)) = 0.35
        _Pin ("End Pinning (higher = only the tips pinned)", Range(2, 40)) = 12
        _CoreWidth ("Core Half Width", Range(0.002, 0.2)) = 0.025
        _RimWidth ("Rim Half Width", Range(0.004, 0.3)) = 0.07
        _TipThin ("Thinner Toward The End (0..1)", Range(0, 1)) = 0.4
        _Strand ("Second Strand Strength", Range(0, 1)) = 0.6
        _Glow ("Outer Glow", Range(0, 1)) = 0.25
        _GlowWidth ("Outer Glow Half Width", Range(0.02, 0.5)) = 0.22
        _Fps ("Shape Changes Per Second", Range(0, 30)) = 12
        _FlickerMin ("Flicker Min Brightness", Range(0, 1)) = 0.55
        [Toggle] _Flip ("Reach From The Other End", Float) = 0

        _Thin ("Thin (MeshRenderer only)", Range(0, 1)) = 0
        _Seed ("Seed (MeshRenderer only)", Range(0, 1)) = 0
        _Reach ("Reach (MeshRenderer only)", Range(0, 1)) = 1
        [Toggle(_USE_PARTICLE_DATA)] _UseParticle ("Data From Particle Custom1", Float) = 1

        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend ("Src Blend", Float) = 1   // One (colour is premultiplied)
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend ("Dst Blend", Float) = 1   // One = additive
    }

    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" "IgnoreProjector"="True" "PreviewType"="Plane" }
        Blend [_SrcBlend] [_DstBlend]
        ZWrite Off
        Cull Off

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.0
            #pragma shader_feature_local _USE_PARTICLE_DATA
            #include "UnityCG.cginc"
            #include "Assets/VFX/_Shared/Shaders/VfxShaderLib.cginc"

            half4 _ColorCore, _ColorRim;
            float _Aspect, _Segments, _Amp, _Detail, _Pin;
            half _CoreWidth, _RimWidth, _TipThin, _Strand, _Glow, _GlowWidth, _Fps, _FlickerMin, _Flip;
            half _Thin, _Seed, _Reach;

            struct appdata
            {
                float4 vertex : POSITION;
                fixed4 color : COLOR;
                float4 uv : TEXCOORD0;      // xy UV, z thin, w seed
                float uv2 : TEXCOORD1;      // reach
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                fixed4 color : COLOR;
                float4 uv : TEXCOORD0;      // xy UV, z thin, w seed
                float2 data : TEXCOORD1;    // x reach, y frame (shape re-roll index)
            };

            // sin-free hash (Dave Hoskins hash11): stable on mobile GPUs
            float hash11(float p)
            {
                p = frac(p * 0.1031);
                p *= p + 33.33;
                p *= p + p;
                return frac(p);
            }

            // linear value noise in -1..1 -> straight segments between hashed points; returns value and slope (per unit t)
            float2 zig(float t)
            {
                float i = floor(t);
                float a = hash11(i) * 2.0 - 1.0;
                float b = hash11(i + 1.0) * 2.0 - 1.0;
                return float2(lerp(a, b, t - i), b - a);
            }

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.color = v.color;
            #if _USE_PARTICLE_DATA
                float thin = v.uv.z, seed = v.uv.w, reach = v.uv2;
            #else
                float thin = _Thin, seed = _Seed, reach = _Reach;
            #endif
                o.uv = float4(v.uv.xy, thin, seed);
                o.data = float2(reach, floor(_Time.y * _Fps + seed * 17.0));
                return o;
            }

            // distance (in quad widths) from p to one strand
            float strand(float u, float y, float base, float amp, float pin)
            {
                float n = _Segments;
                float2 a = zig(u * n + base);
                float2 b = zig(u * n * 3.0 + base * 1.7 + 11.0);
                float off = (a.x + b.x * _Detail) * amp * pin;
                float slope = (a.y * n + b.y * n * 3.0 * _Detail) * amp * pin / _Aspect;   // d(off)/d(x), x in widths
                return abs(y - off) * rsqrt(1.0 + slope * slope);
            }

            half4 frag(v2f i) : SV_Target
            {
                float u = i.uv.x;
                float y = i.uv.y - 0.5;                       // across, in quad widths
                half thin = saturate(i.uv.z);
                float seed = i.uv.w;
                float frame = i.data.y;
                float base = seed * 97.0 + frame * 13.37;

                float pin = saturate(u * (1.0 - u) * _Pin);  // 0 at both ends -> pinned to A and B

                // main strand + thinner second strand (other shape, smaller amplitude)
                float d1 = strand(u, y, base, _Amp, pin);
                float d2 = strand(u, y, base + 41.0, _Amp * 0.8, pin);

                // widths: thinner toward the far end and as the bolt dies
                half w = (1.0h - _TipThin * u) * saturate(1.0h - thin * 1.4h);
                half wc = _CoreWidth * w, wr = _RimWidth * w;

                half aa1 = max(fwidth(d1), 1e-4);
                half core = 1.0h - smoothstep(wc - aa1, wc + aa1, d1);
                half rim = 1.0h - smoothstep(wr - aa1, wr + aa1, d1);
                half aa2 = max(fwidth(d2), 1e-4);
                half rim2 = (1.0h - smoothstep(wr * 0.45h - aa2, wr * 0.45h + aa2, d2)) * _Strand;
                half core2 = (1.0h - smoothstep(wc * 0.4h - aa2, wc * 0.4h + aa2, d2)) * _Strand;
                half glow = saturate(1.0h - d1 / _GlowWidth); glow *= glow * _Glow * w;

                // reach: the bolt travels from its start end; soft tip
                float ur = lerp(u, 1.0 - u, _Flip);
                half reach = 1.0h - smoothstep(i.data.x - 0.03h, i.data.x, ur);

                // death: from thin 0.5 the bolt breaks into pieces (whole small segments drop out)
                half cut = saturate((thin - 0.5h) * 2.0h);
                half keep = step(cut, hash11(floor(u * _Segments * 3.0) + base));

                half flicker = lerp(_FlickerMin, 1.0h, hash11(frame + seed * 31.0));

                half rimAll = max(rim, rim2);
                half coreAll = max(core, core2);
                half3 col = lerp(_ColorRim.rgb, _ColorCore.rgb, coreAll) * rimAll + _ColorRim.rgb * glow * (1.0h - rimAll);
                col *= reach * keep * flicker * i.color.rgb * i.color.a;
                return half4(col, 1.0h);
            }
            ENDCG
        }
    }
    Fallback Off
}
