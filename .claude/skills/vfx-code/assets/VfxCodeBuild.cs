// vfx-code: dựng prefab từ <name>.json do lib/render.py xuất (1 particle chạy cả flipbook).
// Cài: Assets/VFX/_VfxCode/Editor/VfxCodeBuild.cs (trong Editor/) + Assets/VFX/_VfxCode/Runtime/VfxCodeReplay.cs (ngoài Editor/).
// Dùng: menu VFX/vfx-code/Build From Json... (prefab + scene demo) · Make Demo Scene... (chỉ scene) · hoặc batchmode:
//   Unity.exe -batchmode -projectPath <p> -executeMethod VfxCode.VfxCodeBuild.BuildBatch -vfxjson Assets/VFX/<Effect>/Textures/<name>.json -quit
// Built-in pipeline: Mobile/Particles/Additive · Mobile/Particles/Alpha Blended (URP: đổi tên shader ở SHADER_*).
#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

#pragma warning disable 0649   // trường do JsonUtility gán
namespace VfxCode
{
    public static class VfxCodeBuild
    {
        const string SHADER_ADD = "Mobile/Particles/Additive";
        const string SHADER_ALPHA = "Mobile/Particles/Alpha Blended";

        [Serializable] class Space { public string context, plane, camera, anchor, background; public float width_m; }
        [Serializable] class Info
        {
            public string name, blend; public float duration; public bool loop;
            public int frames, cols, rows; public float[] size, pivot; public string[] sheets; public Space space;
        }

        [MenuItem("VFX/vfx-code/Build From Json...")]
        static void BuildMenu()
        {
            string p = PickJson();
            if (p == null) return;
            Build(p);
            OfferOpen(p);
        }

        [MenuItem("VFX/vfx-code/Make Demo Scene...")]
        static void SceneMenu()
        {
            string p = PickJson();
            if (p == null) return;
            var info = Load(p);
            string fxDir = FxDir(p);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(fxDir + "/Prefabs/VFX_" + Path.GetFileName(fxDir) + ".prefab");
            if (prefab == null) { Debug.LogError("[vfx-code] chưa có prefab — chạy Build From Json trước"); return; }
            MakeDemoScene(info, fxDir, prefab);
            OfferOpen(p);
        }

        static string PickJson()
        {
            string p = EditorUtility.OpenFilePanel("vfx-code json", "Assets/VFX", "json");
            if (string.IsNullOrEmpty(p)) return null;
            string root = Path.GetFullPath(Application.dataPath + "/..").Replace('\\', '/') + "/";
            p = p.Replace('\\', '/');
            if (!p.StartsWith(root)) { Debug.LogError("[vfx-code] json phải nằm trong project"); return null; }
            return p.Substring(root.Length);
        }

        static Info Load(string jsonAssetPath) => JsonUtility.FromJson<Info>(File.ReadAllText(jsonAssetPath));
        static string FxDir(string jsonAssetPath) => Path.GetDirectoryName(Path.GetDirectoryName(jsonAssetPath)).Replace('\\', '/');
        static string ScenePath(string fxDir) => fxDir + "/Scenes/" + Path.GetFileName(fxDir) + "_Demo.unity";

        static void OfferOpen(string jsonAssetPath)
        {
            string sp = ScenePath(FxDir(jsonAssetPath));
            if (Application.isBatchMode || SceneManager.GetActiveScene().path == sp) return;
            if (EditorUtility.DisplayDialog("vfx-code", "Mở scene demo?\n" + sp, "Mở", "Không")
                && EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                EditorSceneManager.OpenScene(sp, OpenSceneMode.Single);
        }

        public static void BuildBatch()
        {
            string[] args = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(args, "-vfxjson");
            if (i < 0 || i + 1 >= args.Length) { Debug.LogError("[vfx-code] thiếu -vfxjson <Assets/...json>"); EditorApplication.Exit(2); return; }
            try { Build(args[i + 1]); EditorApplication.Exit(0); }
            catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }

        public static GameObject Build(string jsonAssetPath)
        {
            var info = Load(jsonAssetPath);
            if (info.space == null || info.space.width_m <= 0) throw new Exception("[vfx-code] json thiếu space.width_m — render lại bằng lib/render.py");
            string texDir = Path.GetDirectoryName(jsonAssetPath).Replace('\\', '/');          // Assets/VFX/<Effect>/Textures
            string fxDir = Path.GetDirectoryName(texDir).Replace('\\', '/');                  // Assets/VFX/<Effect>
            string effect = Path.GetFileName(fxDir);
            string matDir = fxDir + "/Materials", pfDir = fxDir + "/Prefabs";
            Directory.CreateDirectory(matDir); Directory.CreateDirectory(pfDir);

            float aspect = info.size[1] / info.size[0];                                        // cao / rộng của ô
            var root = new GameObject("VFX_" + effect);
            int order = 0;
            foreach (string sheet in info.sheets)
            {
                string texPath = texDir + "/" + sheet;
                ImportTexture(texPath);
                bool add = info.blend == "add" || sheet.Contains("_Light_");
                string layer = sheet.Contains("_Body_") ? "Body" : sheet.Contains("_Light_") ? "Light" : "Main";
                var mat = MakeMaterial(matDir + "/M_" + info.name + (layer == "Main" ? "" : "_" + layer) + ".mat",
                                       add ? SHADER_ADD : SHADER_ALPHA, AssetDatabase.LoadAssetAtPath<Texture2D>(texPath));
                MakeLayer(root.transform, layer, info, mat, aspect, order++);
            }
            string prefab = pfDir + "/VFX_" + effect + ".prefab";
            PrefabUtility.SaveAsPrefabAsset(root, prefab);
            UnityEngine.Object.DestroyImmediate(root);
            AssetDatabase.SaveAssets();
            Debug.Log($"[vfx-code] {prefab}: {info.sheets.Length} layer, {info.frames} frame {info.cols}x{info.rows}, {info.duration:0.###}s, plane {info.space.plane}, {info.space.width_m} m");
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(prefab);
            MakeDemoScene(info, fxDir, asset);
            return asset;
        }

        // Scene demo: effect đặt theo space, camera 3/4 nhìn xuống 40°, mặt đất theo nền, hình nhân 2 m so tỷ lệ,
        // VfxCodeReplay phát lại (Space). Dựng trong scene phụ rồi đóng → không đụng scene đang mở của người dùng.
        static string MakeDemoScene(Info info, string fxDir, GameObject prefab)
        {
            string path = ScenePath(fxDir);
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            bool isOpen = SceneManager.GetSceneByPath(path).isLoaded;
            if (isOpen && !Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return null;
            Scene prev = SceneManager.GetActiveScene();
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, isOpen ? NewSceneMode.Single : NewSceneMode.Additive);
            SceneManager.SetActiveScene(scene);

            var sp = info.space;
            float w = sp.width_m;
            float h = sp.context == "ground" ? 0f : 1.0f;                                      // air / dir: tầm trúng đòn ~1 m
            Color tone = sp.background == "light" ? new Color(0.72f, 0.72f, 0.70f)
                       : sp.background == "mixed" ? new Color(0.36f, 0.36f, 0.38f) : new Color(0.10f, 0.10f, 0.12f);

            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);                       // Plane 10 m
            ground.name = "Ground";
            ground.transform.localScale = Vector3.one * Mathf.Max(1f, w * 0.6f);
            ground.GetComponent<Renderer>().sharedMaterial = DemoMaterial("M_VfxCode_Ground_" + (sp.background ?? "dark"), tone);

            var human = GameObject.CreatePrimitive(PrimitiveType.Capsule);                      // cao 2 m
            human.name = "Ref_Human_2m";
            human.transform.position = new Vector3(-(w * 0.5f + 0.8f), 1f, 0.3f);
            human.transform.localScale = new Vector3(0.6f, 1f, 0.6f);
            human.GetComponent<Renderer>().sharedMaterial = DemoMaterial("M_VfxCode_Human", new Color(0.45f, 0.5f, 0.6f));

            var sun = new GameObject("Directional Light").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

            var demo = new GameObject("Demo_" + Path.GetFileName(fxDir));
            var rep = demo.AddComponent<VfxCodeReplay>();
            rep.interval = info.loop ? 0f : info.duration + 0.6f;
            var fx = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            fx.transform.SetParent(demo.transform, false);
            fx.transform.localPosition = new Vector3(0f, h, 0f);

            var cam = new GameObject("Main Camera").AddComponent<Camera>();
            cam.tag = "MainCamera";
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(tone.r * 0.8f, tone.g * 0.8f, tone.b * 0.8f, 1f);
            cam.fieldOfView = 30f;
            cam.transform.rotation = Quaternion.Euler(40f, 0f, 0f);                             // 3/4 nhìn xuống 40° (mặc định dự án)
            float dist = Mathf.Max(4f, (w + 2.2f) / (2f * Mathf.Tan(15f * Mathf.Deg2Rad)) * 0.85f);
            var target = new Vector3(-0.4f, Mathf.Max(h, 0.6f) * 0.8f, 0f);
            cam.transform.position = target - cam.transform.forward * dist;

            EditorSceneManager.SaveScene(scene, path);
            if (!isOpen)
            {
                if (prev.IsValid()) SceneManager.SetActiveScene(prev);
                EditorSceneManager.CloseScene(scene, true);
            }
            Debug.Log($"[vfx-code] scene {path}: camera 3/4 40°, nền {sp.background}, effect cao {h} m, hình nhân 2 m, Space = phát lại");
            return path;
        }

        static Material DemoMaterial(string name, Color c)
        {
            const string dir = "Assets/VFX/_VfxCode/Demo";
            Directory.CreateDirectory(dir);
            string p = dir + "/" + name + ".mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(p);
            if (m == null) { m = new Material(Shader.Find("Standard")); AssetDatabase.CreateAsset(m, p); }
            m.color = c;
            EditorUtility.SetDirty(m);
            return m;
        }

        static void ImportTexture(string path)
        {
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            var ti = AssetImporter.GetAtPath(path) as TextureImporter;
            if (ti == null) throw new Exception("[vfx-code] không import được " + path);
            ti.textureType = TextureImporterType.Default;
            ti.alphaIsTransparency = true;
            ti.mipmapEnabled = false;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.filterMode = FilterMode.Bilinear;
            ti.sRGBTexture = true;
            ti.SaveAndReimport();
        }

        static Material MakeMaterial(string path, string shaderName, Texture2D tex)
        {
            var sh = Shader.Find(shaderName);
            if (sh == null) throw new Exception("[vfx-code] không có shader " + shaderName);
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null) { m = new Material(sh); AssetDatabase.CreateAsset(m, path); }
            m.shader = sh;
            m.mainTexture = tex;
            EditorUtility.SetDirty(m);
            return m;
        }

        static void MakeLayer(Transform parent, string name, Info info, Material mat, float aspect, int order)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var ps = go.AddComponent<ParticleSystem>();
            ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
            var r = go.GetComponent<ParticleSystemRenderer>();
            float w = info.space.width_m;
            string plane = info.space.plane;

            var main = ps.main;
            main.duration = info.duration;
            main.loop = info.loop;
            main.startLifetime = info.duration;
            main.startSpeed = plane == "stretch" ? 0.01f : 0f;
            main.maxParticles = 1;
            main.simulationSpace = ParticleSystemSimulationSpace.Local;
            main.scalingMode = ParticleSystemScalingMode.Hierarchy;
            main.playOnAwake = true;
            main.startSize3D = plane != "stretch";
            if (plane == "stretch") main.startSize = w * aspect;                             // stretch: size = bề ngang, dài = size·lengthScale
            else { main.startSizeX = w; main.startSizeY = w * aspect; main.startSizeZ = 1f; }

            var em = ps.emission;
            em.rateOverTime = 0f;
            em.SetBursts(new[] { new ParticleSystem.Burst(0f, 1) });

            var sh = ps.shape;
            sh.enabled = plane == "stretch";
            if (plane == "stretch") { sh.shapeType = ParticleSystemShapeType.Cone; sh.angle = 0f; sh.radius = 0.0001f; }

            var tsa = ps.textureSheetAnimation;
            tsa.enabled = true;
            tsa.mode = ParticleSystemAnimationMode.Grid;
            tsa.numTilesX = info.cols;
            tsa.numTilesY = info.rows;
            tsa.animation = ParticleSystemAnimationType.WholeSheet;
            tsa.cycleCount = 1;
            float end = (float)info.frames / (info.cols * info.rows);
            var curve = AnimationCurve.Linear(0f, 0f, 1f, end);                                // TUYẾN TÍNH: tangent phẳng làm flipbook khựng
            tsa.frameOverTime = new ParticleSystem.MinMaxCurve(1f, curve);

            r.sharedMaterial = mat;
            r.sortingOrder = order;
            if (plane == "stretch")
            {
                r.renderMode = ParticleSystemRenderMode.Stretch;
                r.lengthScale = 1f / aspect;
                r.velocityScale = 0f;
            }
            else
            {
                r.renderMode = ParticleSystemRenderMode.Billboard;
                // ground = Billboard + alignment Local, quad nằm đất (KHÔNG dùng Horizontal Billboard)
                r.alignment = plane == "ground" ? ParticleSystemRenderSpace.Local : ParticleSystemRenderSpace.View;
                if (plane == "ground") go.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
                // pivot: đưa điểm gốc của ô (json pivot, y hướng xuống) về đúng vị trí hạt; +y = lên
                r.pivot = new Vector3(0.5f - info.pivot[0], info.pivot[1] - 0.5f, 0f);
            }
        }
    }
}
#endif
