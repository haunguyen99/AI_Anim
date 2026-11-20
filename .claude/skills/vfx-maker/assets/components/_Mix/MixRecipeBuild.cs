#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;
using static VfxKit.VfxBuildKit;

namespace VfxEffects
{
    /// <summary>
    /// Builds a VFX prefab from a Mix Lab recipe (Docs/VFX/_Recipes/&lt;name&gt;.json, exported by the web Mix Lab):
    ///   each item = an unpacked copy of a component prefab (Assets/VFX/_Components/*/Prefabs/CMP_&lt;id&gt;.prefab) with
    ///   delay (added to every Start Delay), duration (simulation speed = component length / duration), size (scale),
    ///   intensity (alpha multiplier), rotation (Y), offset (m). The palette replaces the standard slot colours
    ///   (Core / Mid / Outer / Dust) wherever a component uses them (start colours and Color over Lifetime keys).
    /// Output: Assets/VFX/Mixes/&lt;name&gt;/VFX_&lt;name&gt;.prefab + demo scene; Docs/VFX/&lt;name&gt;/ previews + report (Review Lab).
    /// Batch: -executeMethod VfxEffects.MixRecipeBuild.BuildBatch -recipe Docs/VFX/_Recipes/&lt;name&gt;.json
    /// </summary>
    public static class MixRecipeBuild
    {
        [System.Serializable] class Palette { public string Core, Mid, Outer, Dust; }
        [System.Serializable] class Item { public string id; public float delay, duration = -1f, size = 1f, intensity = 1f, rotation; public float[] offset; }
        [System.Serializable] class Recipe { public string name; public int version; public Palette palette; public Item[] items; }

        [MenuItem("VFX/Components/Build From Recipe...")]
        public static void BuildMenu()
        {
            string p = EditorUtility.OpenFilePanel("Recipe (Mix Lab)", "Docs/VFX/_Recipes", "json");
            if (!string.IsNullOrEmpty(p) && ConfirmSceneSwitch()) Build(p);
        }

        public static void BuildBatch()
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, "-recipe");
            if (i < 0 || i + 1 >= args.Length) throw new System.ArgumentException("thiếu -recipe <đường dẫn recipe.json>");
            string path = args[i + 1];
            RunBatch(() => Build(path));
        }

        public static GameObject Build(string recipePath)
        {
            var r = JsonUtility.FromJson<Recipe>(File.ReadAllText(recipePath));
            if (r == null || r.items == null || r.items.Length == 0) throw new System.InvalidOperationException("recipe rỗng: " + recipePath);
            string name = Sanitize(string.IsNullOrEmpty(r.name) ? Path.GetFileNameWithoutExtension(recipePath) : r.name);
            string root = "Assets/VFX/Mixes/" + name, docs = "Docs/VFX/" + name;
            EnsureFolders(root, "Prefabs", "Scenes");
            Directory.CreateDirectory(docs);

            var map = SlotMap(r.palette);
            var go = new GameObject("VFX_" + name);
            var log = new StringBuilder();
            float end = 0f;
            for (int k = 0; k < r.items.Length; k++)
            {
                var it = r.items[k];
                var prefab = FindComponent(it.id);
                if (!prefab) { log.AppendLine("  ! bỏ qua " + it.id + ": không tìm thấy CMP_" + it.id); continue; }
                var inst = (GameObject)PrefabUtility.InstantiatePrefab(prefab, go.transform);
                PrefabUtility.UnpackPrefabInstance(inst, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                inst.name = k.ToString("00") + "_" + it.id;
                var systems = inst.GetComponentsInChildren<ParticleSystem>(true);
                float baseDur = MixCapture.Duration(systems);
                float dur = it.duration > 0f ? it.duration : baseDur;
                float speed = baseDur / dur;
                inst.transform.localPosition = it.offset != null && it.offset.Length == 3 ? new Vector3(it.offset[0], it.offset[1], it.offset[2]) : Vector3.zero;
                inst.transform.localRotation = Quaternion.Euler(0f, it.rotation, 0f) * inst.transform.localRotation;
                inst.transform.localScale = inst.transform.localScale * Mathf.Max(0.01f, it.size);
                foreach (var ps in systems)
                {
                    var m = ps.main;
                    m.startDelay = AddConst(m.startDelay, it.delay * speed);   // delay is in mix seconds; the system runs `speed` times faster
                    m.simulationSpeed *= speed;
                    m.scalingMode = ParticleSystemScalingMode.Hierarchy;
                    m.startColor = Recolor(m.startColor, map, it.intensity);
                    var col = ps.colorOverLifetime;
                    if (col.enabled) col.color = Recolor(col.color, map, 1f);
                }
                end = Mathf.Max(end, it.delay + dur);
                log.AppendLine($"  {inst.name,-34} delay {it.delay:0.###}  dur {dur:0.###} (gốc {baseDur:0.###}, speed ×{speed:0.##})  size {it.size:0.##}  int {it.intensity:0.##}  rot {it.rotation:0}  off {inst.transform.localPosition}");
            }

            var saved = SavePrefab(go, root + "/Prefabs/VFX_" + name + ".prefab");
            File.Copy(recipePath, docs + "/recipe.json", true);
            var times = Enumerable.Range(0, 8).Select(i => Mathf.Max(0.01f, (end + 0.1f) * i / 8f)).ToArray();
            var target = new Vector3(0f, 0.6f, 0f);
            const float d = 7f, a = 40f * Mathf.Deg2Rad;
            var gameCam = target + new Vector3(0f, Mathf.Sin(a) * d, -Mathf.Cos(a) * d);
            ComponentKit.Capture(new[] { saved }, Vector3.zero, times, docs + "/Preview_sheet.png", gameCam, target);
            ComponentKit.Capture(new[] { saved }, Vector3.zero, times, docs + "/Preview_side.png", new Vector3(0f, 1.1f, -d), new Vector3(0f, 1.1f, 0f));
            DemoScene(saved, root + "/Scenes/" + name + "_Demo.unity", gameCam, target, end + 1f);

            var errors = Validate(root, saved);
            var rep = new StringBuilder();
            rep.AppendLine("Mix: " + name + "   Recipe: " + recipePath + "   Unity: " + Application.unityVersion);
            rep.AppendLine("Built: " + System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
            rep.AppendLine("Preview times (s): " + string.Join(", ", times.Select(t => t.ToString("0.###"))));
            rep.AppendLine("Palette: Core " + r.palette?.Core + " · Mid " + r.palette?.Mid + " · Outer " + r.palette?.Outer + " · Dust " + r.palette?.Dust);
            rep.AppendLine();
            rep.AppendLine("Items:");
            rep.Append(log);
            rep.AppendLine();
            rep.AppendLine("Layers:");
            foreach (var ps in saved.GetComponentsInChildren<ParticleSystem>(true))
            {
                var rr = ps.GetComponent<ParticleSystemRenderer>(); var mt = rr.sharedMaterial;
                rep.AppendLine("  " + ps.transform.parent.name + "/" + ps.name + "  max=" + ps.main.maxParticles + "  life=" + ps.main.startLifetime.constantMax.ToString("0.##") +
                               "  mode=" + rr.renderMode + "  mat=" + (mt ? mt.name + " (" + mt.shader.name + ")" : "NONE"));
            }
            rep.AppendLine();
            rep.AppendLine(errors.Count == 0 ? "Errors: none" : "Errors:\n  " + string.Join("\n  ", errors));
            File.WriteAllText(docs + "/BuildReport.txt", rep.ToString());
            AssetDatabase.SaveAssets();
            Debug.Log("[Mix] built VFX_" + name + " from " + recipePath);
            return saved;
        }

        static GameObject FindComponent(string id)
        {
            foreach (var g in AssetDatabase.FindAssets("CMP_" + id + " t:Prefab", new[] { "Assets/VFX/_Components" }))
            {
                var p = AssetDatabase.GUIDToAssetPath(g);
                if (Path.GetFileNameWithoutExtension(p) == "CMP_" + id) return AssetDatabase.LoadAssetAtPath<GameObject>(p);
            }
            return null;
        }

        static string Sanitize(string s) => new string(s.Select(c => char.IsLetterOrDigit(c) || c == '_' ? c : '_').ToArray());

        static ParticleSystem.MinMaxCurve AddConst(ParticleSystem.MinMaxCurve c, float add)
        {
            if (add == 0f) return c;
            if (c.mode == ParticleSystemCurveMode.Constant) { c.constant += add; return c; }
            if (c.mode == ParticleSystemCurveMode.TwoConstants) { c.constantMin += add; c.constantMax += add; return c; }
            return new ParticleSystem.MinMaxCurve(c.Evaluate(0f) + add);
        }

        // ------------------------------------------------------------------ palette
        static List<(Color from, Color to)> SlotMap(Palette p)
        {
            var list = new List<(Color, Color)>();
            void Add(Color from, string hex) { if (!string.IsNullOrEmpty(hex) && ColorUtility.TryParseHtmlString(hex, out var c)) list.Add((from, c)); }
            if (p != null) { Add(ComponentKit.Core, p.Core); Add(ComponentKit.Mid, p.Mid); Add(ComponentKit.Outer, p.Outer); Add(ComponentKit.Dust, p.Dust); }
            return list;
        }

        static Color Map(Color c, List<(Color from, Color to)> map)
        {
            foreach (var (from, to) in map)
                if (Mathf.Abs(c.r - from.r) + Mathf.Abs(c.g - from.g) + Mathf.Abs(c.b - from.b) < 0.03f) return new Color(to.r, to.g, to.b, c.a);
            return c;
        }

        static Gradient Map(Gradient g, List<(Color, Color)> map)
        {
            var n = new Gradient { mode = g.mode };
            n.SetKeys(g.colorKeys.Select(k => new GradientColorKey(Map(k.color, map), k.time)).ToArray(), g.alphaKeys);
            return n;
        }

        static ParticleSystem.MinMaxGradient Recolor(ParticleSystem.MinMaxGradient g, List<(Color, Color)> map, float alphaMul)
        {
            Color A(Color c) { c = Map(c, map); c.a = Mathf.Clamp01(c.a * alphaMul); return c; }
            switch (g.mode)
            {
                case ParticleSystemGradientMode.Color: return new ParticleSystem.MinMaxGradient(A(g.color));
                case ParticleSystemGradientMode.TwoColors: return new ParticleSystem.MinMaxGradient(A(g.colorMin), A(g.colorMax));
                case ParticleSystemGradientMode.Gradient: { var n = Map(g.gradient, map); return new ParticleSystem.MinMaxGradient(Scale(n, alphaMul)); }
                case ParticleSystemGradientMode.TwoGradients: return new ParticleSystem.MinMaxGradient(Scale(Map(g.gradientMin, map), alphaMul), Scale(Map(g.gradientMax, map), alphaMul));
                default: return g;
            }
        }

        static Gradient Scale(Gradient g, float alphaMul)
        {
            if (Mathf.Approximately(alphaMul, 1f)) return g;
            var n = new Gradient { mode = g.mode };
            n.SetKeys(g.colorKeys, g.alphaKeys.Select(k => new GradientAlphaKey(Mathf.Clamp01(k.alpha * alphaMul), k.time)).ToArray());
            return n;
        }
    }
}
#endif
