// SH_VFX_GlowStar — shader-only VFX (vfx-shader skill). Mobile: Built-in + URP, one unlit pass, UnityCG only.
// Look: toon flash on a square quad, NO texture: hard white core disk + coloured rim + soft glow;
//   with _STAR, a 4-point spiky star (optionally 4 more thinner spikes at 45 deg), toon two-tone.
// Animate size / colour with the particle (Size / Color over Lifetime). Additive (One One, colour premultiplied by alpha).
// Cost: 0 texture samples, no loops, no sin/pow/atan2. target 3.0 (fwidth).
Shader "VFX/FX/Glow Star"
{
    Properties
    {
        [HDR] _ColorCore ("Core Color", Color) = (1.4, 1.5, 1.6, 1)
        [HDR] _ColorRim ("Rim Color", Color) = (0.25, 0.6, 2.0, 1)
        _CoreRadius ("Core Radius (0..1 of quad half)", Range(0, 1)) = 0.18
        _RimRadius ("Rim Radius", Range(0, 1)) = 0.3
        _Glow ("Soft Glow", Range(0, 2)) = 0.6
        [Toggle(_STAR)] _Star ("Spiky Star", Float) = 0
        _SpikeSharp ("Spike Thinness", Range(1, 60)) = 18
        _SpikeCore ("Spike Core Threshold", Range(0, 1)) = 0.55
        _SpikeRim ("Spike Rim Threshold", Range(0, 1)) = 0.3
        _Diagonal ("45 deg Spikes (0 none, 1 full)", Range(0, 1)) = 0.5

        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend ("Src Blend", Float) = 1
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend ("Dst Blend", Float) = 1
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
            #pragma shader_feature_local _STAR
            #include "UnityCG.cginc"
            #include "Assets/VFX/_Shared/Shaders/VfxShaderLib.cginc"

            half4 _ColorCore, _ColorRim;
            half _CoreRadius, _RimRadius, _Glow, _SpikeSharp, _SpikeCore, _SpikeRim, _Diagonal;

            struct appdata { float4 vertex : POSITION; fixed4 color : COLOR; float2 uv : TEXCOORD0; };
            struct v2f { float4 pos : SV_POSITION; fixed4 color : COLOR; float2 uv : TEXCOORD0; };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.color = v.color;
                o.uv = v.uv;
                return o;
            }

            // 0..1 field of a plus-shaped star: bright on the axes, falling off with distance
            half spikes(float2 p, half r)
            {
                half arms = abs(p.x) * abs(p.y) * _SpikeSharp;
                return saturate(1.0h - arms - r);
            }

            half4 frag(v2f i) : SV_Target
            {
                float2 p = vfxCentered(i.uv);
                half r = length(p);
                half aa = max(fwidth(r), 1e-4);

                half core = 1.0h - smoothstep(_CoreRadius - aa, _CoreRadius + aa, r);
                half rim = 1.0h - smoothstep(_RimRadius - aa, _RimRadius + aa, r);
                half glow = saturate(1.0h - r); glow *= glow * _Glow;

            #if _STAR
                half s = spikes(p, r);
                float2 q = float2(p.x - p.y, p.x + p.y) * 0.70710678;   // 45 deg
                s = max(s, spikes(q, r * 1.6h) * _Diagonal);
                half saa = max(fwidth(s), 1e-4);
                core = max(core, smoothstep(_SpikeCore - saa, _SpikeCore + saa, s));
                rim = max(rim, smoothstep(_SpikeRim - saa, _SpikeRim + saa, s));
            #endif

                half3 col = lerp(_ColorRim.rgb, _ColorCore.rgb, core) * rim + _ColorRim.rgb * glow * (1.0h - rim);
                return half4(col * i.color.rgb * i.color.a, 1.0h);
            }
            ENDCG
        }
    }
    Fallback Off
}
