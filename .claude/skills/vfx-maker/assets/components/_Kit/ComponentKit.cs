#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using VfxKit;
using static VfxKit.VfxBuildKit;

namespace VfxEffects
{
    /// <summary>
    /// Shared helpers for standardized VFX components (Docs/VFX/_ArtDirection/components/STANDARD.md):
    /// layer defaults, flipbook setup, standard preview (game 3/4 + side, 1 m grid, 2 m human, red hit-point marker) and report.
    /// Each component group has its own Assets/VFX/_Components/&lt;Group&gt;/Editor/&lt;Group&gt;ComponentsBuild.cs.
    /// </summary>
    public static class ComponentKit
    {
        // Standard default palette (fire orange): Core / Mid / Outer
        public static readonly Color Core = new Color(1f, 0.953f, 0.769f);   // #FFF3C4
        public static readonly Color Mid = new Color(1f, 0.604f, 0.235f);    // #FF9A3C
        public static readonly Color Outer = new Color(0.784f, 0.157f, 0.118f); // #C8281E
        // Dust slot (draft 2026-11-02, Alpha layers only): earthy grey-brown; the shadow tone comes from the texture
        public static readonly Color Dust = new Color(0.804f, 0.733f, 0.651f);  // #CDBBA6
        public const float TwoPi = Mathf.PI * 2f;

        public static Color WithAlpha(Color c, float a) { c.a = a; return c; }

        // Sorting table for every component (no ties, so Unity never falls back to distance; art lead 2026-11-03).
        // Plane first, then brightness: everything lying ON the ground sits under the upright smoke, which sits under the light.
        //   ground plane : Scorch body -9 / light -8 · Lightning ground arcs -7 · Glow ground pool -5 · Impact flat -4 · Ring (ground) -3
        //   upright      : Dust alpha -2 / fire glow -1 · Glow outer + halo 0 / inner 1 · Ring (air, dir) 2 · Sparks 3 · Lightning bolt 4
        //   front        : Impact flash, splash, spike 5 / core 6
        public static void Common(ParticleSystem ps, int order, float maxScreenSize = 3f)
        {
            var r = ps.GetComponent<ParticleSystemRenderer>();
            r.maxParticleSize = maxScreenSize;
            r.sortingOrder = order;
        }

        /// <summary>Flat on the ground without Horizontal Billboard: Billboard + Render Alignment Local, object rotated X 90.</summary>
        public static void GroundFlat(ParticleSystem ps, float y = 0.02f)
        {
            ps.transform.localPosition = new Vector3(0f, y, 0f);
            ps.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
            ps.GetComponent<ParticleSystemRenderer>().alignment = ParticleSystemRenderSpace.Local;
        }

        /// <summary>Frame over Time that really is a straight line. VfxBuildKit.Curve builds keys with flat (0) tangents,
        /// which Unity plays as an S-curve: the flipbook stalls on the first frames (~12 % of the life) then rushes
        /// (found 2026-11-02 on Scorch: preview ~0.4 s late on a 2 s life).</summary>
        public static ParticleSystem.MinMaxCurve LinearFrames(float from, float to) =>
            new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0f, from, 1f, to));

        public static void SheetSequence(ParticleSystem ps, int cols, int rows)
        {
            var t = ps.textureSheetAnimation;
            t.enabled = true;
            t.mode = ParticleSystemAnimationMode.Grid;
            t.numTilesX = cols; t.numTilesY = rows;
            t.animation = ParticleSystemAnimationType.WholeSheet;
            t.frameOverTime = LinearFrames(0f, 0.999f);
            t.cycleCount = 1;
        }

        /// <summary>Each particle keeps one random cell for its whole life (cells are variants, not a sequence).</summary>
        public static void SheetRandomFrame(ParticleSystem ps, int cols, int rows)
        {
            var t = ps.textureSheetAnimation;
            t.enabled = true;
            t.mode = ParticleSystemAnimationMode.Grid;
            t.numTilesX = cols; t.numTilesY = rows;
            t.animation = ParticleSystemAnimationType.WholeSheet;
            t.frameOverTime = new ParticleSystem.MinMaxCurve(0f, 0.999f);
            t.cycleCount = 1;
        }

        public static Material Unlit(Color c)
        {
            var m = new Material(Shader.Find("Unlit/Color"));
            m.color = c;
            return m;
        }

        /// <summary>Saves the prefab, writes standard previews + report into docsRoot/id. companions: other prefabs shown together in Preview_combo.png.</summary>
        public static GameObject Save(GameObject go, string root, string docsRoot, string id, Vector3 previewPos, float[] times, params GameObject[] companions)
        {
            var prefab = SavePrefab(go, root + "/Prefabs/CMP_" + id + ".prefab");
            string docs = docsRoot + "/" + id;
            Directory.CreateDirectory(docs);
            var errors = Validate(root, prefab);

            var target = previewPos + new Vector3(0f, 0.2f, 0f);
            const float d = 6.5f, a = 40f * Mathf.Deg2Rad;
            var gameCam = target + new Vector3(0f, Mathf.Sin(a) * d, -Mathf.Cos(a) * d);
            Capture(new[] { prefab }, previewPos, times, docs + "/Preview_sheet.png", gameCam, target);
            Capture(new[] { prefab }, previewPos, times, docs + "/Preview_side.png", new Vector3(0f, 1.1f, -d), new Vector3(0f, 1.1f, 0f));
            if (companions != null && companions.Length > 0)
                Capture(new[] { prefab }.Concat(companions).ToArray(), previewPos, times, docs + "/Preview_combo.png", gameCam, target);
            DemoScene(prefab, root + "/Scenes/" + id + "_Demo.unity", gameCam, target, 1.5f);
            Report(docs + "/BuildReport.txt", id, prefab, times, errors, companions);
            if (errors.Count > 0) throw new System.InvalidOperationException(id + ": " + string.Join("\n", errors));
            return prefab;
        }

        public static void Capture(GameObject[] prefabs, Vector3 pos, float[] times, string outPng, Vector3 camPos, Vector3 lookAt, int size = 384)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var cam = new GameObject("Cam").AddComponent<Camera>();
            cam.transform.position = camPos; cam.transform.LookAt(lookAt);
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.08f, 0.085f, 0.1f, 1f);
            cam.fieldOfView = 40f;

            var grid = Unlit(new Color(0.2f, 0.21f, 0.24f));
            for (int i = -3; i <= 3; i++)
            {
                var x = GameObject.CreatePrimitive(PrimitiveType.Cube); x.GetComponent<Renderer>().sharedMaterial = grid;
                x.transform.position = new Vector3(i, 0f, 0f); x.transform.localScale = new Vector3(0.015f, 0.002f, 6f);
                var z = GameObject.CreatePrimitive(PrimitiveType.Cube); z.GetComponent<Renderer>().sharedMaterial = grid;
                z.transform.position = new Vector3(0f, 0f, i); z.transform.localScale = new Vector3(6f, 0.002f, 0.015f);
            }
            var human = GameObject.CreatePrimitive(PrimitiveType.Capsule);   // 2 m tall
            human.GetComponent<Renderer>().sharedMaterial = Unlit(new Color(0.3f, 0.31f, 0.35f));
            human.transform.position = new Vector3(-1.6f, 1f, 0.3f); human.transform.localScale = new Vector3(0.6f, 1f, 0.6f);
            var marker = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            marker.GetComponent<Renderer>().sharedMaterial = Unlit(new Color(1f, 0.15f, 0.15f));
            marker.transform.position = pos; marker.transform.localScale = Vector3.one * 0.07f;

            var systems = new List<ParticleSystem>();
            foreach (var p in prefabs)
            {
                var inst = (GameObject)PrefabUtility.InstantiatePrefab(p);
                inst.transform.position = pos;
                systems.AddRange(inst.GetComponentsInChildren<ParticleSystem>(true));
            }

            var rt = new RenderTexture(size, size, 24, RenderTextureFormat.ARGB32);
            var frame = new Texture2D(size, size, TextureFormat.RGB24, false);
            var sheet = new Texture2D(size * times.Length, size, TextureFormat.RGB24, false);
            cam.targetTexture = rt;
            try
            {
                for (int i = 0; i < times.Length; i++)
                {
                    foreach (var p in systems) p.Simulate(times[i], false, true, false);   // variable step: t = 0.01 must already show the burst
                    cam.Render();
                    RenderTexture.active = rt;
                    frame.ReadPixels(new Rect(0, 0, size, size), 0, 0); frame.Apply();
                    sheet.SetPixels(i * size, 0, size, size, frame.GetPixels());
                }
                sheet.Apply();
                File.WriteAllBytes(outPng, sheet.EncodeToPNG());
            }
            finally
            {
                RenderTexture.active = null; cam.targetTexture = null;
                rt.Release(); Object.DestroyImmediate(rt); Object.DestroyImmediate(frame); Object.DestroyImmediate(sheet);
            }
        }

        static void Report(string path, string id, GameObject prefab, float[] times, List<string> errors, GameObject[] companions)
        {
            var sb = new StringBuilder();
            sb.AppendLine("Component: " + id + "   Kit: " + VfxBuildKit.Version + "   Unity: " + Application.unityVersion + "   Pipeline: " + (IsURP ? "URP" : "Built-in"));
            sb.AppendLine("Built: " + System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
            sb.AppendLine("Preview times (s): " + string.Join(", ", times.Select(t => t.ToString("0.###"))));
            sb.AppendLine("Views: Preview_sheet = game 3/4 (40 deg down), Preview_side = side. Grid 1 m, capsule 2 m, red dot = hit point.");
            if (companions != null && companions.Length > 0)
                sb.AppendLine("Preview_combo = game 3/4 together with: " + string.Join(", ", companions.Select(c => c.name)));
            sb.AppendLine();
            sb.AppendLine("Layers:");
            foreach (var ps in prefab.GetComponentsInChildren<ParticleSystem>(true))
            {
                var r = ps.GetComponent<ParticleSystemRenderer>();
                var mt = r.sharedMaterial;
                sb.AppendLine("  " + prefab.name + "/" + ps.name + "  max=" + ps.main.maxParticles + "  life=" + ps.main.startLifetime.constantMax.ToString("0.##") +
                              "  mode=" + r.renderMode + (r.renderMode == ParticleSystemRenderMode.Billboard ? "/" + r.alignment : "") +
                              "  mat=" + (mt ? mt.name + " (" + mt.shader.name + ")" : "NONE"));
            }
            sb.AppendLine();
            sb.AppendLine(errors.Count == 0 ? "Errors: none" : "Errors:\n  " + string.Join("\n  ", errors));
            File.WriteAllText(path, sb.ToString());
        }
    }
}
#endif
