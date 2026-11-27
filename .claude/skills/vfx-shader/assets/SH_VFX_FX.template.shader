// __NAME__ — shader-only VFX (vfx-shader skill). Mobile: Built-in + URP, one unlit pass, UnityCG only.
// Look: __ONE_LINE_DESCRIPTION__
// Cost: 2 noise samples (scroll UVs computed in the vertex shader), no loops, no atan2/pow/sin per pixel.
// Particle inputs (enable with VfxShaderBuild.UseFxStreams): vertex color = tint * alpha,
//   TEXCOORD0.xy = UV, TEXCOORD0.z = Custom1.x progress 0..1, TEXCOORD0.w = Custom1.y random seed.
// Without a particle (MeshRenderer): progress = _Progress, seed = 0.
Shader "VFX/FX/__NAME__"
{
    Properties
    {
        [HDR] _ColorA ("Edge Color", Color) = (1, 0.35, 0.08, 1)
        [HDR] _ColorB ("Core Color", Color) = (1, 0.9, 0.6, 1)
        _Radius ("Radius", Range(0, 1)) = 0.7
        _Width ("Ring Half-Width (0 = filled disc)", Range(0, 0.5)) = 0.12
        _Soft ("Edge Softness", Range(0.001, 0.3)) = 0.04
        _GrowStart ("Radius Scale At Start", Range(0, 1)) = 0.35

        _NoiseTex ("Noise (tileable, linear; R and G used)", 2D) = "gray" {}
        _NoiseScroll ("Noise Scroll (xy = R, zw = G)", Vector) = (0, 0.35, 0.12, -0.2)
        [Toggle(_DISTORT)] _UseDistort ("Noise Distortion", Float) = 1
        _DistortAmount ("Distortion Amount", Range(0, 0.4)) = 0.08
        [Toggle(_DISSOLVE)] _UseDissolve ("Dissolve With Progress", Float) = 1
        _DissolveSoft ("Dissolve Softness", Range(0.001, 0.5)) = 0.08

        _Progress ("Progress (MeshRenderer only)", Range(0, 1)) = 0
        [Toggle(_USE_PARTICLE_DATA)] _UseParticle ("Progress From Particle Custom1", Float) = 1

        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend ("Src Blend", Float) = 5   // SrcAlpha
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend ("Dst Blend (1 Add, 10 Alpha)", Float) = 1
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
            #pragma target 2.0
            #pragma shader_feature_local _DISTORT
            #pragma shader_feature_local _DISSOLVE
            #pragma shader_feature_local _USE_PARTICLE_DATA
            #include "UnityCG.cginc"
            #include "Assets/VFX/_Shared/Shaders/VfxShaderLib.cginc"

            half4 _ColorA, _ColorB;
            half _Radius, _Width, _Soft, _GrowStart, _DistortAmount, _DissolveSoft, _Progress;
            sampler2D _NoiseTex;
            float4 _NoiseTex_ST;
            float4 _NoiseScroll;

            struct appdata
            {
                float4 vertex : POSITION;
                fixed4 color : COLOR;
                float4 uv : TEXCOORD0;      // xy UV, z progress, w seed
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                fixed4 color : COLOR;
                float3 uv : TEXCOORD0;      // xy UV, z progress
                float4 nuv : TEXCOORD1;     // two scrolled noise UVs
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.color = v.color;
            #if _USE_PARTICLE_DATA
                float progress = v.uv.z, seed = v.uv.w;
            #else
                float progress = _Progress, seed = 0;
            #endif
                o.uv = float3(v.uv.xy, progress);
                float2 baseUV = TRANSFORM_TEX(v.uv.xy, _NoiseTex) + seed;   // seed shifts the noise per particle
                float t = _Time.y;
                o.nuv.xy = baseUV + _NoiseScroll.xy * t;
                o.nuv.zw = baseUV * 1.7 + _NoiseScroll.zw * t;
                return o;
            }

            half4 frag(v2f i) : SV_Target
            {
                half progress = i.uv.z;
                half2 n = half2(tex2D(_NoiseTex, i.nuv.xy).r, tex2D(_NoiseTex, i.nuv.zw).g);

                float2 p = vfxCentered(i.uv.xy);
            #if _DISTORT
                p += (n - 0.5h) * (2.0h * _DistortAmount);
            #endif

                half r = _Radius * lerp(_GrowStart, 1.0h, vfxEaseOut(progress));
                half d = _Width > 0.0001h ? vfxSdRing(p, r, _Width * r) : vfxSdCircle(p, r);
                half shape = vfxFill(d, _Soft);

                half alpha = shape;
            #if _DISSOLVE
                alpha *= vfxDissolve(n.x, progress, _DissolveSoft);
            #endif

                half3 col = lerp(_ColorA.rgb, _ColorB.rgb, shape * shape);
                alpha *= i.color.a * _ColorA.a;
                return half4(col * i.color.rgb, alpha);
            }
            ENDCG
        }
    }
    Fallback Off
}
