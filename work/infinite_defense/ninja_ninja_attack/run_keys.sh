set -e
cd "/c/Users/Admin/Documents/AI_animation/work/infinite_defense/ninja_ninja_attack/keys"
"/c/Users/Admin/Documents/AI_animation/.venv/Scripts/python.exe" -I "/c/Users/Admin/Documents/AI_animation/tools/codex_img.py" prompts/k2.txt --out k2_ready_wind_r1.png --ref ../../ninja_idle/keys/k1r2_v1.png --timeout 600
"/c/Users/Admin/Documents/AI_animation/.venv/Scripts/python.exe" -I "/c/Users/Admin/Documents/AI_animation/tools/codex_img.py" prompts/k4.txt --out k4_release_r1.png --ref ../../ninja_idle/keys/k1r2_v1.png --ref k2_ready_wind_r1.png --timeout 600
"/c/Users/Admin/Documents/AI_animation/.venv/Scripts/python.exe" -I "/c/Users/Admin/Documents/AI_animation/tools/codex_img.py" prompts/k5.txt --out k5_follow_r1.png --ref ../../ninja_idle/keys/k1r2_v1.png --ref k4_release_r1.png --timeout 600
