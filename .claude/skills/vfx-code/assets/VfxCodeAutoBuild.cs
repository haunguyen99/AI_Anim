// vfx-code: TỰ BUILD — khi lib/render.py ghi <name>.json vào Assets/VFX/<Effect>/Textures/,
// Unity tự nhập file và dựng prefab + scene demo (VfxCodeBuild.Build). Không cần bấm menu.
// Cài: Assets/VFX/_VfxCode/Editor/VfxCodeAutoBuild.cs. Bật / tắt: menu VFX/vfx-code/Auto Build (mặc định bật).
// Không chạy trong batchmode, Play mode, lúc đang compile. Chỉ nhận json có "sheets" + "space" (json của vfx-code).
#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace VfxCode
{
    [InitializeOnLoad]
    static class VfxCodeAutoBuild
    {
        const string PREF = "VfxCode.AutoBuild";
        const string MENU = "VFX/vfx-code/Auto Build";
        const double DEBOUNCE = 1.5;                      // giây chờ sau lần ghi cuối (render ghi PNG rồi json)

        static FileSystemWatcher watcher;
        static readonly object gate = new object();
        static readonly HashSet<string> pending = new HashSet<string>();
        static DateTime lastEvent;

        static bool Enabled { get => EditorPrefs.GetBool(PREF, true); set => EditorPrefs.SetBool(PREF, value); }

        static VfxCodeAutoBuild()
        {
            if (Application.isBatchMode) return;
            EditorApplication.delayCall += Watch;
            EditorApplication.update += Tick;
        }

        [MenuItem(MENU)]
        static void Toggle() { Enabled = !Enabled; Debug.Log("[vfx-code] Auto Build " + (Enabled ? "BẬT" : "TẮT")); }

        [MenuItem(MENU, true)]
        static bool ToggleCheck() { Menu.SetChecked(MENU, Enabled); return true; }

        static void Watch()
        {
            string dir = Path.Combine(Application.dataPath, "VFX");
            if (!Directory.Exists(dir)) return;
            watcher = new FileSystemWatcher(dir, "*.json")
            {
                IncludeSubdirectories = true,
                NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.FileName | NotifyFilters.Size,
            };
            watcher.Changed += OnFile;
            watcher.Created += OnFile;
            watcher.Renamed += (s, e) => OnFile(s, e);
            watcher.EnableRaisingEvents = true;
        }

        static void OnFile(object sender, FileSystemEventArgs e)    // luồng phụ: chỉ ghi nhận
        {
            string p = e.FullPath.Replace('\\', '/');
            if (!p.Contains("/Textures/")) return;
            lock (gate) { pending.Add(p); lastEvent = DateTime.UtcNow; }
        }

        static void Tick()                                          // luồng chính
        {
            List<string> todo;
            lock (gate)
            {
                if (pending.Count == 0 || (DateTime.UtcNow - lastEvent).TotalSeconds < DEBOUNCE) return;
                if (!Enabled) { pending.Clear(); return; }
                if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling || EditorApplication.isUpdating) return;
                todo = new List<string>(pending);
                pending.Clear();
            }
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..")).Replace('\\', '/') + "/";
            AssetDatabase.Refresh();
            foreach (string full in todo)
            {
                if (!full.StartsWith(root) || !File.Exists(full)) continue;
                string text = File.ReadAllText(full);
                if (!text.Contains("\"sheets\"") || !text.Contains("\"space\"")) continue;   // không phải json của vfx-code
                string asset = full.Substring(root.Length);
                try { VfxCodeBuild.Build(asset); Debug.Log("[vfx-code] Auto Build xong: " + asset); }
                catch (Exception ex) { Debug.LogError("[vfx-code] Auto Build lỗi " + asset + ": " + ex.Message); }
            }
        }
    }
}
#endif
