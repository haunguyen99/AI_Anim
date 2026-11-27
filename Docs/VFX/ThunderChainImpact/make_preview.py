from pathlib import Path
from PIL import Image
import base64

p = Path(__file__).resolve().parent
frames = [Image.open(f).convert('RGB').resize((640,480), Image.Resampling.LANCZOS) for f in sorted((p/'Frames').glob('*.png'))]
frames[0].save(p/'Preview.gif', save_all=True, append_images=frames[1:]+[frames[-1]]*20, duration=33, loop=0)
frames[20].save(p/'Preview_peak.png')
sheet = Image.new('RGB', (640*9,480*6))
for i,frame in enumerate(frames): sheet.paste(frame,(i%9*640,i//9*480))
sheet.save(p/'Playback_sheet.jpg',quality=90)
data=base64.b64encode((p/'Playback_sheet.jpg').read_bytes()).decode()
html='''<!doctype html><html lang="vi"><meta charset="utf-8"><title>Thunder Chain Impact</title>
<style>body{margin:32px auto;max-width:980px;background:#10151f;color:#e8edf5;font:16px system-ui}h1{color:#ffd471}canvas{width:100%;border-radius:14px;background:#242a32}button,select{padding:9px 16px;margin:10px 8px 10px 0;background:#27354a;color:white;border:1px solid #58687e;border-radius:8px}input{width:65%}small{color:#aab7c9}</style>
<h1>Thunder Chain Impact</h1><p>Sét đánh tại tâm → mục tiêu 01 → 02 → 03. Góc 60°, vàng–trắng.</p>
<canvas id="c" width="640" height="480"></canvas><br><button id="play">Tạm dừng</button><button id="reset">Phát lại</button><select id="speed"><option value="1">1×</option><option value="0.5">0.5×</option><option value="0.25">0.25×</option></select><br><input id="seek" type="range" min="0" max="53" value="0"><span id="time"></span>
<p><small>54 khung hình render bằng Unity 2022.3, 30 fps. Scene demo tự lặp 2,8 s; Space để phát lại. Chưa đo hiệu năng mobile.</small></p>
<script>const im=new Image(),ctx=c.getContext('2d');let running=true,t=0,last=0;im.src='data:image/jpeg;base64,DATA';function draw(){let i=Math.min(53,Math.floor(t*30));ctx.drawImage(im,i%9*640,Math.floor(i/9)*480,640,480,0,0,640,480);seek.value=i;document.getElementById('time').textContent=(i/30).toFixed(2)+' s'}im.onload=()=>requestAnimationFrame(tick);function tick(ms){if(last&&running)t=(t+(ms-last)/1000*Number(speed.value))%2.5;last=ms;draw();requestAnimationFrame(tick)}play.onclick=()=>{running=!running;play.textContent=running?'Tạm dừng':'Tiếp tục'};reset.onclick=()=>{t=0;running=true;play.textContent='Tạm dừng'};seek.oninput=()=>{t=Number(seek.value)/30;running=false;play.textContent='Tiếp tục';draw()};</script></html>'''.replace('DATA',data)
(p/'Preview.html').write_text(html,encoding='utf-8')
