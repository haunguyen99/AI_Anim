// vfx-code: phát lại effect trong scene demo — tự lặp sau mỗi `interval` giây, phím Space phát lại ngay.
// Cài: Assets/VFX/_VfxCode/Runtime/VfxCodeReplay.cs (KHÔNG nằm trong Editor/).
using UnityEngine;

namespace VfxCode
{
    public class VfxCodeReplay : MonoBehaviour
    {
        [Tooltip("Giây giữa 2 lần phát (one-shot). Effect loop thì đặt 0 = không phát lại tự động.")]
        public float interval = 1.2f;
        public KeyCode key = KeyCode.Space;

        ParticleSystem[] systems;
        float timer;

        void Awake() { systems = GetComponentsInChildren<ParticleSystem>(true); }

        void Start() { Replay(); }

        void Update()
        {
            timer += Time.deltaTime;
            if ((interval > 0f && timer >= interval) || Input.GetKeyDown(key)) Replay();
        }

        public void Replay()
        {
            timer = 0f;
            foreach (var ps in systems) { ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear); ps.Clear(true); }
            foreach (var ps in systems) ps.Play(true);
        }
    }
}
