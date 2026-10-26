"""Video reference -> per-frame 3D pose (pose.json).

Runs MediaPipe Pose Landmarker on every frame of a video and writes a JSON file
that `apply_motion.py` (Blender) consumes.

Coordinates in the output are already converted to Blender convention:
  metres, Z up, -Y = towards the camera, +X = image right.
"world" landmarks are hip-centred (MediaPipe world space); "image" landmarks are
normalised 2D (u, v in 0..1, v down) and are used to estimate root translation.

Usage:
  .venv/Scripts/python tools/extract_pose.py ref.mp4 -o work/pose.json --preview work/preview
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner",
    "right_eye", "right_eye_outer", "left_ear", "right_ear", "mouth_left",
    "mouth_right", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky", "left_index",
    "right_index", "left_thumb", "right_thumb", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle", "left_heel",
    "right_heel", "left_foot_index", "right_foot_index",
]

BONES_2D = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23), (12, 24),
    (23, 24), (23, 25), (25, 27), (24, 26), (26, 28), (27, 31), (28, 32),
    (27, 29), (28, 30), (15, 19), (16, 20), (0, 7), (0, 8),
]


def gaussian_smooth(arr, sigma):
    """Smooth along axis 0 (time) with a gaussian kernel, edge-padded."""
    if sigma <= 0 or len(arr) < 3:
        return arr
    radius = max(1, int(round(sigma * 3)))
    x = np.arange(-radius, radius + 1)
    k = np.exp(-0.5 * (x / sigma) ** 2)
    k /= k.sum()
    pad = np.pad(arr, [(radius, radius)] + [(0, 0)] * (arr.ndim - 1), mode="edge")
    out = np.zeros_like(arr)
    for i, w in enumerate(k):
        out += w * pad[i:i + len(arr)]
    return out


def fill_missing(arr, valid):
    """Linearly interpolate frames where valid is False (arr: T x ...)."""
    idx = np.flatnonzero(valid)
    if len(idx) == 0:
        return arr
    T = len(arr)
    flat = arr.reshape(T, -1)
    t = np.arange(T)
    for c in range(flat.shape[1]):
        flat[:, c] = np.interp(t, idx, flat[idx, c])
    return flat.reshape(arr.shape)


def draw_overlay(frame, image_lms, vis):
    h, w = frame.shape[:2]
    pts = [(int(u * w), int(v * h)) for u, v in image_lms]
    for a, b in BONES_2D:
        color = (0, 255, 0) if min(vis[a], vis[b]) > 0.5 else (0, 0, 255)
        cv2.line(frame, pts[a], pts[b], color, 2)
    for i, p in enumerate(pts):
        cv2.circle(frame, p, 3, (255, 255, 0) if vis[i] > 0.5 else (0, 0, 255), -1)
    return frame


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("-o", "--out", default="work/pose.json")
    ap.add_argument("--model", choices=["heavy", "full"], default="heavy")
    ap.add_argument("--start", type=float, default=0.0, help="start time (s)")
    ap.add_argument("--end", type=float, default=None, help="end time (s)")
    ap.add_argument("--smooth", type=float, default=1.5, help="gaussian sigma in frames (0 = off)")
    ap.add_argument("--preview", default=None, help="folder for skeleton-overlay PNGs")
    ap.add_argument("--preview-count", type=int, default=8)
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit(f"Cannot open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    first = int(round(args.start * fps))
    last = total - 1 if args.end is None else min(total - 1, int(round(args.end * fps)))
    cap.set(cv2.CAP_PROP_POS_FRAMES, first)

    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(ROOT, "models", f"pose_landmarker_{args.model}.task")),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    world, image, vis, valid, raw_frames = [], [], [], [], []
    n = last - first + 1
    preview_idx = set(np.linspace(0, n - 1, min(args.preview_count, n)).astype(int).tolist()) if args.preview else set()

    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        for k in range(n):
            ok, frame = cap.read()
            if not ok:
                n = k
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ts = int(round((first + k) * 1000.0 / fps))
            res = landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ts)
            if res.pose_world_landmarks:
                wl = res.pose_world_landmarks[0]
                il = res.pose_landmarks[0]
                # MediaPipe (x right, y down, z away from camera) -> Blender (x, z, -y)
                world.append([[p.x, p.z, -p.y] for p in wl])
                image.append([[p.x, p.y] for p in il])
                vis.append([float(p.visibility or 0.0) for p in il])
                valid.append(True)
            else:
                world.append([[0.0, 0.0, 0.0]] * 33)
                image.append([[0.5, 0.5]] * 33)
                vis.append([0.0] * 33)
                valid.append(False)
            if k in preview_idx:
                raw_frames.append((k, frame.copy()))
            if k % 50 == 0:
                print(f"  frame {k}/{n}", flush=True)
    cap.release()

    valid = np.array(valid[:n])
    if not valid.any():
        sys.exit("No person detected in the video.")
    world = fill_missing(np.array(world[:n], dtype=np.float64), valid)
    image = fill_missing(np.array(image[:n], dtype=np.float64), valid)
    world = gaussian_smooth(world, args.smooth)
    image = gaussian_smooth(image, args.smooth)
    vis = np.array(vis[:n])

    if args.preview:
        os.makedirs(args.preview, exist_ok=True)
        for k, frame in raw_frames:
            draw_overlay(frame, image[k], vis[k])
            cv2.imwrite(os.path.join(args.preview, f"ref_{k:05d}.png"), frame)

    out = {
        "source": os.path.abspath(args.video),
        "fps": fps,
        "width": width,
        "height": height,
        "first_frame": first,
        "frame_count": int(n),
        "detected_ratio": float(valid.mean()),
        "landmark_names": LANDMARK_NAMES,
        "frames": [
            {
                "world": np.round(world[k], 5).tolist(),
                "image": np.round(image[k], 5).tolist(),
                "vis": np.round(vis[k], 3).tolist(),
                "detected": bool(valid[k]),
            }
            for k in range(n)
        ],
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f)
    print(f"Wrote {args.out}: {n} frames @ {fps:.3f} fps, detected {valid.mean() * 100:.1f}%")


if __name__ == "__main__":
    main()
