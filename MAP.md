# MAP.md: Bản đồ dự án VFX_LIb

Đọc file này cùng `CLAUDE.md` ở đầu mỗi hội thoại. **Tạo / di chuyển / xoá file thì cập nhật dòng tương ứng ở đây.**

## Harness (khung làm việc cho Claude)

| Đường dẫn | Chứa gì |
|---|---|
| `CLAUDE.md` | Dự án là gì, skill, công cụ, quy tắc chính. Đọc đầu tiên. |
| `CLAUDE.local.md` | Sở thích cá nhân trên máy này. Không commit. |
| `AGENTS.md` | Quy tắc chung cho mọi agent / subagent / phiên song song. |
| `SPEC.md` | Mục tiêu, phạm vi, tiêu chí "xong" của thư viện VFX. |
| `MAP.md` | File này. |
| `contexte/` | Những gì đã học được về dự án, mỗi chủ đề một file (xem `contexte/README.md`). |
| `.claude/rules/` | Luật cứng của art lead, tự nạp vào mọi phiên. |
| `.claude/skills/` | Skill dự án: `vfx-maker`, `vfx-code`, `vfx-shader`. |
| `.claude/agents/vfx-artist.md` | Agent VFX artist: nhận brief, làm VFX theo luật + skill của project, bàn giao cho `vfx-director` review. |
| `tools/vfx_artist.py` | Bật / tắt / giữ chạy nhân viên VFX (`on`, `off`, `status`, `watch`). Tự chạy lại sau khi bật máy bằng `~/.config/systemd/user/vfx-artist.service` (ngoài repo; linger bật). |
| `tools/subsession/briefs/vfx_artist.md` | Brief phiên nhân viên VFX: nhận order HorusChat / WorkAI (profile `vfx`), gửi demo cho người order, nhận feedback, giao. Sổ order: `work/vfx_orders/<mã>/`. |
| `.claude/agents/vfx-director.md` | Agent reviewer VFX độc lập (chỉ đọc, chấm theo luật; brief ở `Docs/VFX/_ArtDirection/agent-review.md`). |
| `.claude/settings.local.json` | Quyền riêng máy (không commit). `settings.json` (quyền dùng chung) chưa tạo. |
| `.claude/launch.json` | Server xem web: `shape-lab` (8765), `review-lab` (8776). |
| `.mcp.json` | Công cụ kết nối: Blender MCP. |
| `.worktreeinclude` | File không có trong git nhưng cần chép theo mỗi worktree. |
| `.gitignore` | Chỉ cho tài liệu + code lên git (whitelist). Từ 2026-11-04 chỉ commit kiến thức + skill + `.md` (xem `CLAUDE.md`). |
| `tools/sync_knowledge.py` | Đồng bộ kiến thức lên git (2026-11-10): commit phạm vi kiến thức lên `master`, chép sang `main`, push `main`. Chạy bởi hook `Stop` + Task Scheduler 17:30 + tay (`--dry-run`). Lên git. Xem `contexte/git-sync.md`. |
| `tools/library_props.py` | Đo thuộc tính ảnh trong `Assets/Library` → `Docs/VFX/_Library/library_props.csv`; `--contact <nhóm>/<vai trò>` dựng contact sheet vào `Docs/VFX/_Library/_contact/` (2026-11-10, phục vụ "Luật chọn" của `LIBRARY.md`). Chỉ ở máy (`.py`). |
| `tools/auto_commit.ps1` | Vỏ gọi `sync_knowledge.py` (Task Scheduler `VFX_LIb Auto Commit` 17:30 trỏ vào file này); log `tools/auto_commit.log` (không lên git). Lên git. |
| `tools/fetch_library.py` | Tải thư viện texture `Assets/Library` từ Google Drive (`Library.tar.gz`) và giải nén vào `Assets/` (2026-11-20). `--force`, `--dry-run`; giải nén an toàn; đã có thì bỏ qua. Lên git. |
| `tools/make_tree.py` | Tạo lại cây thư mục trên máy khác (2026-11-19): `python -I tools/make_tree.py` tạo thư mục còn thiếu theo bảng `Docs/VFX/_Library/folder_tree.csv`; `--export` quét lại cây hiện tại ghi bảng; `--dry-run`. Bỏ qua Library/Temp/obj/Logs/UserSettings/.vs/tmp_gen. Lên git. |
| `.claude/skills/Sourcetree/` | Skill `/Sourcetree` (2026-11-19): bọc `tools/make_tree.py`, dựng lại / cập nhật cây thư mục. Lên git. |

### Trợ lý cá nhân (chép từ AI_Anim `main`, 2026-11-17)

| Đường dẫn | Chứa gì |
|---|---|
| `tools/tro_ly.py` | Công cụ trợ lý: `on / off / status / room / wait / say / history / todo`. Luôn dùng danh tính `haunv`. Cờ tắt + mốc ở `work/store/_sys/watch/`, sổ việc `work/assistant/todo.json` (tạo khi chạy). |
| `tools/subsession/briefs/tro_ly_ca_nhan.md` | Brief (luật) của trợ lý. **Còn ghi tên chủ "Hậu" / `@haunv:localhost` và "dự án AI Animation": sửa thành chủ máy này** trước khi bật. |
| `.claude/skills/assistant/`, `assistant_on/`, `assistant_off/` | Skill `/assistant`, `/assistant_on`, `/assistant_off`. |
| `tools/identity.py`, `horuschat_cli.py`, `horuschat_watch.py`, `horuschat_daemon.py`, `workai_watch.py`, `workai_daemon.py`, `paseo_cmd.py`, `subsession/subsession.py` | Phụ thuộc của `tro_ly.py` (danh tính, CLI + bộ canh HorusChat / WorkAI, gọi Paseo). `paseo_cmd.py` đã sửa để tìm `paseo` trong PATH trên Linux. Toast của bộ canh dùng PowerShell nên trên Linux chỉ ghi log lỗi. |
| `tools/horuschat_mcp/`, `tools/workai/workai.py` | Client HorusChat (MCP) và WorkAI. Khoá điền tay vào `tools/horuschat_mcp/.env.haunv` và `tools/workai/.env.haunv` (không commit). |

## Unity

- **Dọn 2026-11-05 (art lead):** `Assets/` chỉ còn effect có trong scene Showcase + phần dùng chung. Đã xoá (vào Thùng rác Windows): `Assets/StrongExplosion_v1`, `Assets/Scenes`, `Assets/_Game`, `Assets/VFX/{BombBlast_Shader, CodeShockwaveGround, CodeSparkBurst, Explosion, FireStylized, FireballImpact, FireballLoop, FireballProjectile, Lightning_Impact, Lightning_Strike, Meteor, SmokeStylized, StylizedSlash, ThunderChainImpact, ThunderImpact, Shaders}`, 5 Mix cũ, `smoke.mat`, ảnh `tread_*.png` ở gốc. Tài liệu của chúng trong `Docs/VFX/` (kể cả `ThunderImpact/`, `ThunderChainImpact/`) và `contexte/` vẫn giữ; builder của ThunderImpact / ThunderChainImpact còn trong git (commit `b23b0b6`).

| Đường dẫn | Chứa gì |
|---|---|
| `Assets/VFX/<Tên>/` | **Sản phẩm (livrables)**: mỗi effect một thư mục: `Prefabs/`, `Textures/`, `Materials/`, `Scripts/`. |
| `Assets/VFX/_Showcase/` | Scene chung `VFX_Showcase.unity` + UI chuyển effect (`VfxShowcase.cs`, `VfxShowcaseBuild.cs`).  Môi trường thực tế (trời hoàng hôn, nắng + bóng, sương, đất, sàn đá, đá tảng, cột vỡ) do `VfxShowcaseEnvironment.cs` dựng; texture / mesh sinh tự động ở `_Showcase/Textures`, `/Meshes`, `/Materials`. Ảnh xem thử: `Docs/VFX/_Showcase/env_*.png`. Build Scene chỉ thêm effect mới, giữ setup; bản sao scene tự lưu ở `_Showcase/Scenes/_Backup/` (5 bản gần nhất). Đèn demo (chỉ lúc Play trong Showcase, không trong prefab): bảng trong `Runtime/VfxShowcaseLights.cs`. |
| `Assets/VFX/_Components/` | Thành phần chuẩn để mix: Impact / Glow / Ring / Sparks / Dust. |
| `Assets/VFX/Mixes/` | Effect đã mix từ thành phần: `IceSpike_Impact`, `LightningStrike_Ground`, `LightningStrike_Impact`, `_Palettes`. |
| `Assets/VFX/fx_t_smoke_02.png` | Texture khói mặc định (luật art lead ghi cứng đường dẫn này, không dời). |
| `Assets/VFX/_Kit/` | Build kit dùng chung (`VfxBuildKit`, `ComponentKit`). |
| `Assets/VFX/_Shared/` | Shader dùng chung (`VfxShaderLib.cginc`, `SH_VFX_*`, `VFX_ArrowGlow` dời từ `VFX/Shaders` ngày 2026-11-05), noise texture. |
| `Assets/VFX/_Imported/` | Asset nhập: `Mesh/` (56 `SM_VFX_*`, mới: `SM_VFX_ArchTunnel` 2026-11-18, vòm hầm 20 tris, 2×2×3 m, UV U dọc vòm / V theo chiều sâu, chỉ mặt trong, làm bằng Blender MCP), `RpgGame/` (shader Coloso…). |
| `Assets/VFX/_VfxCode/` | Builder của skill `vfx-code`. |
| `Assets/VFX/LightningStrike/`, `ThunderSpear/`, `LightningTrail/`, `AuraGauntlet/` | 4 VFX điện (builder trong `Editor/`, menu `VFX/<Tên>/Build`), học từ rpg-game; số liệu: `.claude/skills/vfx-shader/references/thunder-core.md` và `lightning-set.md`. |
| `Assets/VFX/GroundBlast/`, `MushroomBlast/` | Nổ tại đất stylized; khói = khối cầu ăn mòn `VFX/FX/Erode Sphere` (luật khói vụ nổ). MushroomBlast: cột + đầu nấm + vành đất, texture từ `Assets/Library/`. Kế hoạch ở `Docs/VFX/<Tên>/Plan.md`. |
| `Assets/VFX/BlenderBlast/` | Thử vụ nổ bằng Blender (2026-11-11): mesh hoạt hình FBX/GLB (`Mesh/`), sheet 8×8 từ Mantaflow (hỏng) và 3 VDB JangaFX CC0 (`Textures/T_VDB_*`); nguồn `.blend` + script render ở `Source~/`. VDB gốc ở `D:\Game_prj\_VDB\`. Plan + preview ở `Docs/VFX/BlenderBlast/`; bài học `contexte/blender-vdb.md`. Chưa có prefab. |
| `Assets/VFX/FireballThrow/` | Cầu lửa ném vòng cung 8 m / 0.8 s rồi nổ tại chân mục tiêu (2026-11-05). Một prefab tự chạy: hạt thân vẽ cung, chết khi chạm thì kích lớp nổ (sub-emitter Death). Builder `Editor/FireballThrowBuild.cs` (menu `VFX/FireballThrow/Build`), kế hoạch `Docs/VFX/FireballThrow/Plan.md`. |
| `Assets/VFX/VioletThunder/` | Sét tím-hồng đánh xuống đất (2026-11-05): tích điện 0.4 s → tia toon (sheet `Lightnings_Electrics_026` cắt lại nằm ngang + bản viền mờ) + chớp + impact đất (vùng sáng, sao gai, 2 vành sóng) + dòng điện bò tồn ~1.4 s (`_020`). Builder `Editor/VioletThunderBuild.cs` (menu `VFX/VioletThunder/Build`), kế hoạch `Docs/VFX/VioletThunder/Plan.md`. |
| `Assets/VFX/WindTornado/` | Lốc xoáy gió 3,6 m (v3, 2026-11-06): làm lại layer theo layer từ `Stupid_Tornado_Projectile` của rpg-game: vành gió `fbx_fx_cylinder_03` + Shader Graph `Fx_dissolve_particle_apb` trên sheet đóng gói kênh, ống `Tornado_vertical`, cột sương, sương chân, khói, vụn. Builder `Editor/WindTornadoBuild.cs` (menu `VFX/WindTornado/Build`); kế hoạch + ảnh / dump bản gốc `Docs/VFX/WindTornado/`. Mesh `SM_VFX_WindBand_*` (v1) không còn dùng. v2 (2026-11-18): Beam bùng ~0.1 s rồi tan; v3: pivot cột ở gốc (pivot.y = lengthScale/2) + texture cột `trail_streak_001` lật ngang; v4: cột đứng yên, bùng tại chỗ rồi tan; đã giao cho Hậu 2026-11-18, ghi chú dùng ở `work/vfx_orders/20261118_haunv_thu1/giao/`. Chưa vào `Included`. |
| `Assets/VFX/FireTornado/` | Lốc lửa 4,5 m (2026-11-06): thân = một phễu `tornado_mesh` + shader Thrust tông ấm, dải lửa dựng đứng (Graph, sheet ô 6) leo lên thân, lửa chân, tàn lửa + đợt bắn khi sụp, khói nhiệt, quầng cháy đất. Làm bằng quy trình `vfx-shader/references/tornado.md`, không có prefab tham chiếu. Builder `Editor/FireTornadoBuild.cs` (menu `VFX/FireTornado/Build`), kế hoạch `Docs/VFX/FireTornado/Plan.md`. Đã thêm vào `Included` của Showcase. |
| VioletThunder đợt 2026-11-13 | Thêm `Editor/VioletThunderToxicBuild.cs`, `VioletThunderGoldBuild.cs` (biến thể), `VioletStormBuild.cs` (effect mới: loạt sét 3 điểm + tia cuối) và `VioletThunderKit.cs` (helper chung). Menu `VFX/VioletThunder/Build Toxic|Gold|Storm`. Đã build qua MCP, sheet tia riêng từng bản (`tools/make_bolt_sheet.py`). Ghi chú: cuối `Docs/VFX/VioletThunder/Plan_Variants.md`. |
| Biến thể 2026-11-09 | Mỗi loại trong Showcase có 2 biến thể mới (20 prefab), builder ở `Assets/VFX/<Loại>/Editor/<Loại><Biến thể>Build.cs` (menu `VFX/<Loại>/Build <Biến thể>`), prefab `VFX_<Loại>_<Biến thể>`, kế hoạch `Docs/VFX/<Loại>/Plan_Variants.md`. Slash360: Fire, Water; IceSpikeFan: Magma, Thorn; HealCircle: Holy, Nature; LightningStrike: Toxic, Frost; ThunderSpear: Frost, Flame; LightningTrail: Flame, Wind; AuraGauntlet: Fire, Poison; FireballThrow: Poison, Frost; VioletThunder: Crimson, Azure; FireTornado: Frost, Sand. **Chưa build / chưa compile trong Unity.** Kit phụ: `Slash360VariantKit.cs`, `IceSpikeVariantKit.cs`. |
| HealCircle_Arcane 2026-11-18 | Biến thể tím của HealCircle (order thử, chờ review): builder `Assets/VFX/HealCircle/Editor/HealCircleArcaneBuild.cs` (batch `VfxEffects.HealCircleArcaneBuild.BuildBatch`, phải chạy `-nographics=false`), prefab `VFX_HealCircle_Arcane`, texture rune chép từ Library `rune/circle` 003 + 008 qua `Docs/VFX/HealCircle_Arcane/prep_tex.py`, kế hoạch + preview ở `Docs/VFX/HealCircle_Arcane/`, sổ order `work/vfx_orders/20261118_haunv_thu1/`. Chưa vào `Included`. |
| `Assets/VFX/_Imported/RpgAura/` | Bản copy `VFX_Aura_Gauntlet_Prismatic` của rpg-game (hiện hồng: Shader Graph URP), để đọc setup. |
| `Assets/VFX/_Imported/RpgTornado/` | Bản copy `VFX_Book_Tornado` + `Stupid_Tornado_Projectile` (mesh / sheet texture dùng bởi WindTornado v3) của rpg-game + mesh / shader Thrust / texture (GUID gốc; copy bằng `tools/py/copy_closure.py`). Lớp gốc dùng Shader Graph URP nên hiện hồng. |
| `Assets/VFX/ElectricBolt/` | Tia điện nối A→B (2026-11-09): tay → ngực 8 m, một phát ~0.45 s, xanh-trắng toon, **hoàn toàn code + shader, không texture** (v2): shader mới `_Shared/Shaders/SH_VFX_ElectricBolt` (tia gấp khúc từ hash) + `SH_VFX_GlowStar` (chớp / sao), dùng lại `SH_VFX_Spark`. Builder `Editor/ElectricBoltBuild.cs` (menu `VFX/ElectricBolt/Build`). Tài liệu `Docs/VFX/ElectricBolt/` (`Research.md`, `Plan.md`); cách làm lưu vào skill `vfx-code` (`references/electric-bolt.md`, `assets/shaders/`, `assets/ElectricBoltBuild.example.cs`). Đã build v2, art lead duyệt, có trong `Included` + đèn demo Showcase. |
| `Assets/VFX/WindShellTrail/` | Trail gió cyan sau vật bay (2026-11-09, từ ảnh boomerang của art lead): vỏ cầu sóng mỗi 1.2 m bằng 2 lớp Billboard 2D (`ring_soft_004` bong bóng + `ring_soft_010` lưỡi liềm) + 2 ribbon gió (Trails Ribbon, `trail_ribbon_001/009`) + quầng lõi + sương; World space, root có `VfxPathMover`. Builder `Editor/WindShellTrailBuild.cs` (menu `VFX/WindShellTrail/Build`), kế hoạch `Docs/VFX/WindShellTrail/Plan.md`. Chỉ shader Additive mobile. v2 chưa build. |
| `Assets/VFX/_Imported/RpgThunder/` | Bản copy 100% `VFX_BossRaid_Knight_Thunder` của rpg-game (tham chiếu, giữ GUID gốc). |
| `Assets/VFX/_Imported/RpgGame/Lightning/` | Texture + mesh điện nhập từ rpg-game (Guardian_Lightning3, Gradient_lightning, sheet cung điện, nứt đất…). |
| `Assets/VFX/_Kit/Editor/VfxLightningKit.cs`, `_Kit/Runtime/VfxPathMover.cs` | Helper cho effect điện; mover cho effect có vệt (showcase). |
| `Docs/VFX/_Reference/rpg-game_Thunder/` | Ảnh render mẫu rpg-game (Thunder, Spear, Trail). |
| `Assets/shader_water/` | Shader nước (riêng). |
| `Assets/Library/` | Thư viện texture VFX đã phân loại (bản **sao chép** từ rpg-game + project, GUID mới). **Cây hiện tại, chia theo vai trò (2026-11-06, art lead tự chỉnh thêm):** `Slash/{Main_tex(Uvmesh),Onhit} shield/{fill,crack} (2026-11-19) glow/ spark/ impact/ ring/ lightning/ ground/ rune/ beam/ smoke/ noise/ mask/ trail/ water/`, mỗi thư mục con chứa ảnh tên `<cha>_<con>_NNN` (ví dụ `glow/soft_round/glow_soft_round_001.png`). Tra ngược tên cũ / tên gốc / nguồn: `Docs/VFX/_Library/library_index.csv`; bảng đổi tên: `rename_manifest.csv`, `reorganize_manifest.csv` (script `reorganize.py`, `rename_library.py`, đều có `--undo`). CLAUDE.md / luật / 3 skill đã trỏ cây mới (2026-11-09); **build script C# cũ trong Assets có thể còn trỏ đường dẫn cũ**. Bản đồ chọn texture: `Docs/VFX/_Library/LIBRARY.md`. `classify.csv` là bảng đời trước (tên cũ trước khi chia lại), dùng `library_index.csv` để tra. |
| `Assets/VFX/_Generated/ComfyUI/` | Texture tạo bằng ComfyUI MCP (Qwen Image 2.1), chưa đưa vào Library. Bản gốc ở `D:\GameProjects\VFX_LIb\`. `T_Impact_ComfyUI_01.png`: chớp impact xám trên nền đen (additive), 1024²; `_02`: bản 4 tia hình chữ thập (sửa từ `_01`); `_06`: 4 tia lệch, dài ngắn và góc khác nhau (ảnh ComfyUI `_04` đã xoá bớt 1 tia bằng script). |
| `Packages/`, `ProjectSettings/` | Cấu hình Unity. |

## Tài liệu

| Đường dẫn | Chứa gì |
|---|---|
| `Docs/VFX/_ArtDirection/PROGRESS.md` | **Trạng thái công việc / kế hoạch**: đọc trước khi làm VFX. |
| `Docs/VFX/_ArtDirection/` | Định hướng mỹ thuật, tools (Shape Lab), scripts, `_archive/` (bản lưu skill cũ). |
| `Docs/VFX/<Tên>/` | Plan, preview, GIF, BuildReport của từng effect. |
| `Docs/VFX/_Recipes/` | Recipe mix (json). |
| `Docs/VFX/_Components/` | Ảnh / dữ liệu chụp thành phần. |
| `Docs/VFX/_Review/` | Review Lab sinh ra (`index.html`). Không commit. |
| `Docs/VFX/_Tasks/` | Bảng giao việc vẽ texture (`VFX_Texture_Tasks.xlsx`, 2026-11-09): Impact đất / không, Bolt-Electric/Lightning, Shockwave; kéo vào Google Drive để thành Google Sheet. |
| `tools/py/` | Script phụ: `copy_closure.py` (copy prefab + phụ thuộc theo GUID), `RefRender.cs.txt` (bản sao của `vfx-shader/assets/RefRender.example.cs`). Bản chính thức nằm trong skill `vfx-shader`. |
| `tools/paseo-sdk/` | Gọi Claude bằng code. Mặc định gọi thẳng máy chủ API nội bộ: `gateway.mjs` (thư viện, stream), `ask.mjs`, `chat.mjs` (~1 s). Qua Paseo (`@getpaseo/client`, cần app mở): `paseo-ask.mjs`, `paseo-chat.mjs`, `providers.mjs`, `bench-reuse.mjs`, `check-default.mjs`, `fix-agent-models.mjs` (đổi agent dùng tên model sai sang tên máy chủ nhận). Xem `README.md` (gồm cấu hình model của app Paseo). |
| `tools/check_texture_plan.py` | Quét builder (`Assets/VFX/*/Editor/*Build.cs`), báo ảnh `Assets/Library/...` chưa được ghi tên trong plan `Docs/VFX/<Effect>*/*.md` hoặc không tồn tại (2026-11-13). Mặc định bỏ qua 21 builder cũ ở `tools/texture_plan_legacy.txt` (chỉ VFX tạo mới phải theo công thức), `--all` kiểm cả cũ, `--changed`, `--builder PATH`. Cùng đợt: `tools/make_bolt_sheet.py`, `tools/make_arc_glow.py`. |
| `Docs/VFX/_ArtDirection/agent-review.md` | Quy trình bàn giao (2026-11-13): agent khác review theo luật rồi mới chuyển art lead; brief mẫu cho agent review. |
| `Docs/VFX/_Anatomy/` | **Tạo hình chuẩn từng loại VFX** (2026-11-10, art lead): `README.md` (cách dùng, cách research, mẫu, chỉ mục) + một file mỗi loại (slash360, ice-spike-fan, heal-circle, lightning-strike, aura-gauntlet, fireball-throw, violet-thunder, violet-storm, tornado, waterfall, explosion, reward-burst, disintegrate) + `materials.md` (hình đặc trưng theo chất liệu). Mỗi file: cấu trúc, **Bất biến**, Được đổi, Lỗi biến thể đã gặp. Tra trước khi làm biến thể; chưa có thì research rồi lưu. |
| `Docs/VFX/Reward_StarDrop/` | Plan + preview của VFX reward kiểu Starr Drop (2026-11-18); prefab / builder nằm ở project `idle_farm_harvesting` (`Assets/Anim_VFX/`); thêm `VFX_Reveal_Sparkles`, `LabDemo_Swap` (Animator chuyển cảnh), `VFX_Lab_SlotFill` + `VFX_Lab_LightningLine` + demo UI `LabUIDemo` dùng sprite `_Game/Sprites/Laboratory` (Plan.md cuối file). |
| `Docs/VFX/_Library/` | Script phân loại texture (`classify.py`, chạy thử mặc định, `--apply` để chép) + bảng kết quả `classify.csv` + `LIBRARY.md` (bản đồ thành phần → thư mục Library, 2026-11-09) + `library_props.csv` (thuộc tính đo được từng ảnh: alpha / nền đen, xám / màu, chạm mép, **hướng** omni / dir / na) + `library_direction.csv` (nhãn hướng + sheet gán tay, nguồn sửa) + `components_by_effect.md` (thành phần texture của từng effect trong Showcase, 2026-11-06, làm cơ sở chia lại Library). |
| `Docs/VFX/Waterfall_Map6/` | Thác nước toon cho **airport-tycoon** scene S_Map6 (2026-11-12, làm qua Unity MCP): thân màu phẳng + viền trắng mép (theo video ref), cụm bọt trắng đặc trước đá chân thác, vòng gợn mảnh đứt đoạn. Asset nằm trong project kia (`Assets/Anim & VFX/`, builder `Editor/WaterfallMap6Build.cs`, menu `VFX/Waterfall/Build Map6 Waterfall`); ở đây chỉ có Plan + ảnh preview. |
| `Docs/VFX/Disintegrate/` | **Tan biến (HTML canvas 2D + WebAudio, 1 file `index.html`)** — order Cường 2026-11-18 (`work/vfx_orders/20261118_cuongdt_tanbien/`). v2: nhân vật đang tấn công dính chưởng rồi tan thành cát bụi đất kiểu Thanos, góc Diablo 2 (chọn 3/4 / top-down được); nhân vật / thùng / chữ, màu đất / xanh / tím; sound tự tổng hợp; 1 file offline. `Plan.md`; Anatomy `_Anatomy/disintegrate.md`. **Đã giao Cường 2026-11-18** (`Usage.md`, `Preview/tan_bien_final.gif`); chưa có prefab Unity; art lead chưa duyệt vào thư viện. Xem 1 khung: `index.html?t=1.0&ui=0`. |
| `Docs/VFX/Flamethrower/` | **Súng phun lửa (HTML canvas 2D + WebAudio, 1 file `index.html`)**: order Phong 2026-11-18 (`work/vfx_orders/20261118_phongdq_phunlua/`). Dòng lửa toon liên tục từ nòng ~5 m, bia cháy, cam đỏ / xanh / tím, sound tự tổng hợp. `Plan.md`; Anatomy `_Anatomy/flamethrower.md`. **Đã giao Cường 2026-11-18** (`Usage.md`, `Preview/tan_bien_final.gif`); chưa có prefab Unity; art lead chưa duyệt vào thư viện. Xem 1 khung: `index.html?t=1.6&ui=0`. |
| `Docs/VFX/PyroNova_Runner6/` | VFX hero Pyromancer + Nova của game **Run 6** (2026-11-16/17; project `/media/sondh/New Volume/Projects/runner6`, prefab ở `Assets/VFX_Library/Prefabs/`, scene `VFX_Scene`). `Plan.md` (kế hoạch, texture, trạng thái, bàn giao), `ref/` (khung ref animlibrary Projectile 25 / 6), `Preview/` (7 sheet chụp), `Source/` (builder `PyroNovaBuild.cs`, `PnPreview.cs`, `PyroNovaPlaceInScene.cs`, `prep_tex.py`). Brief từ `Run 6 - Work.xlsx` tab "Anim & VFX". 7 prefab: VFXHandFlame, VFXPyroCast, VFXPyroProjectile, NovaProjectile, NovaCast_1/2/3. Đã build ở project tạm và chép sang runner6; chưa review / chưa duyệt. Anatomy mới: `fire-hand-flame`, `fire-wave-cast`, `hero-projectile`, `laser-beam`. |
| `Docs/VFX/SHADERS.md` | Danh mục shader: kiểm tra trước khi viết shader mới. |
| `Docs/CannonLibraryAudit_v1/` | Kiểm kê thư viện Cannon VFX (có bản project Unity kiểm thử). |
| `Docs/StrongExplosion/`, `Docs/Meteor/`, `Docs/Models/`, `Docs/blender-mcp/` | Tài liệu từng chủ đề riêng. |

## Không đưa lên git

`Library/`, `Temp/`, `Logs/`, `obj/`, `.vs/`, `UserSettings/`, `*.csproj`, `*.sln`, texture / prefab / mesh / material / scene (chỉ ở máy này), `.env`, `CLAUDE.local.md`.
