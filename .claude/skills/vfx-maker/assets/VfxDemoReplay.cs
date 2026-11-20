using UnityEngine;

namespace VfxKit
{
    /// <summary>Demo-scene helper: replays the target effect every <see cref="interval"/> seconds, or on Space.</summary>
    public class VfxDemoReplay : MonoBehaviour
    {
        public GameObject target;
        public float interval = 3f;
        float timer;

        void Update()
        {
            if (target == null) return;
            timer += Time.deltaTime;
            if (timer >= interval || Input.GetKeyDown(KeyCode.Space)) Replay();
        }

        void Replay()
        {
            timer = 0f;
            foreach (var ps in target.GetComponentsInChildren<ParticleSystem>(true))
            {
                if (ps.transform.parent != null && ps.transform.parent.GetComponentInParent<ParticleSystem>() != null) continue;
                ps.Clear(true);
                ps.Play(true);
            }
        }
    }
}
