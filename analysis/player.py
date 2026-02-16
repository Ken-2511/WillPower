import http.server
import json
import os
import sys
from pathlib import Path
from urllib.parse import unquote

SCREEN_DIR = Path("D:/screenCap")
CAMERA_DIR = Path("D:/cameraCap")

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Player</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #1a1a1a; color: #eee; font-family: sans-serif; }
#images { display: flex; gap: 4px; padding: 4px; height: calc(100vh - 80px); }
#images img { object-fit: contain; background: #000; }
#cam { width: 20%; }
#scr1, #scr2 { width: 40%; }
#controls { display: flex; align-items: center; gap: 12px; padding: 8px 12px;
  background: #222; position: fixed; bottom: 0; width: 100%; height: 44px; }
#progress { flex: 1; cursor: pointer; }
#time { font-size: 13px; min-width: 60px; }
select, button { background: #333; color: #eee; border: 1px solid #555;
  padding: 4px 8px; cursor: pointer; font-size: 13px; }
#dateSelect { margin-left: auto; }
</style></head><body>
<div id="images">
  <img id="cam"><img id="scr1"><img id="scr2">
</div>
<div id="controls">
  <button id="playBtn" onclick="toggle()">Play</button>
  <input id="progress" type="range" min="0" value="0" step="1">
  <span id="time">0/0</span>
  <select id="speed" onchange="skip=+this.value">
    <option value="1" selected>1x</option>
    <option value="2">2x</option>
    <option value="4">4x</option>
    <option value="8">8x</option>
    <option value="16">16x</option>
    <option value="32">32x</option>
  </select>
  <select id="dateSelect" onchange="loadDate(this.value)"></select>
</div>
<script>
let frames=[], idx=0, timer=null, skip=1;
const cam=document.getElementById('cam'), scr1=document.getElementById('scr1'),
  scr2=document.getElementById('scr2'), prog=document.getElementById('progress'),
  timeEl=document.getElementById('time'), playBtn=document.getElementById('playBtn'),
  dateSel=document.getElementById('dateSelect');

async function init() {
  const dates = await (await fetch('/api/dates')).json();
  dateSel.innerHTML = dates.map(d => '<option>'+d+'</option>').join('');
  if (dates.length) { dateSel.value = dates[dates.length-1]; loadDate(dateSel.value); }
}

async function loadDate(date) {
  stop();
  frames = await (await fetch('/api/frames?date='+date)).json();
  idx = 0;
  prog.max = Math.max(0, frames.length - 1);
  prog.value = 0;
  if (frames.length) show(0);
  update();
}

function show(i) {
  idx = i;
  const f = frames[i];
  cam.src = '/img/' + f.cam;
  scr1.src = '/img/' + f.scr[0];
  scr2.src = '/img/' + f.scr[1];
  prog.value = i;
  update();
}

function update() { timeEl.textContent = (idx+1)+'/'+frames.length; }

function toggle() { timer ? stop() : play(); }
function play() {
  if (!frames.length) return;
  playBtn.textContent = 'Pause';
  timer = setInterval(() => {
    let next = idx + skip;
    if (next >= frames.length) { stop(); return; }
    show(next);
  }, 1000);
}
function stop() { clearInterval(timer); timer = null; playBtn.textContent = 'Play'; }

prog.addEventListener('input', e => { stop(); show(+e.target.value); });

document.addEventListener('keydown', e => {
  if (e.code === 'Space') { e.preventDefault(); toggle(); }
  else if (e.code === 'ArrowLeft' && idx > 0) { stop(); show(idx - 1); }
  else if (e.code === 'ArrowRight' && idx < frames.length - 1) { stop(); show(idx + 1); }
});

init();
</script></body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = unquote(self.path)
        if path == "/":
            self._html(HTML)
        elif path == "/api/dates":
            dates = sorted(d.name for d in SCREEN_DIR.iterdir() if d.is_dir())
            self._json(dates)
        elif path.startswith("/api/frames?date="):
            date = path.split("=", 1)[1]
            self._json(self._get_frames(date))
        elif path.startswith("/img/"):
            self._serve_file(path[5:])
        else:
            self.send_error(404)

    def _get_frames(self, date):
        screen_dir = SCREEN_DIR / date
        camera_dir = CAMERA_DIR / date
        # Group screenshots by timestamp
        screens = {}
        if screen_dir.exists():
            for f in sorted(screen_dir.iterdir()):
                ts = f.name.split("_____")[0]
                screens.setdefault(ts, []).append(f.name)
        frames = []
        for ts, files in sorted(screens.items()):
            if len(files) < 2:
                continue
            cam_file = ts + ".jpg"
            cam_path = camera_dir / cam_file
            if not cam_path.exists():
                continue
            frames.append({
                "cam": f"cameraCap/{date}/{cam_file}",
                "scr": [f"screenCap/{date}/{f}" for f in sorted(files)[:2]],
            })
        return frames

    def _serve_file(self, rel_path):
        full = Path("D:/") / rel_path
        if not full.exists():
            self.send_error(404)
            return
        ext = full.suffix.lower()
        ct = {".png": "image/png", ".jpg": "image/jpeg", ".bmp": "image/bmp"}.get(ext, "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Cache-Control", "max-age=86400")
        self.end_headers()
        with open(full, "rb") as f:
            while chunk := f.read(65536):
                self.wfile.write(chunk)

    def _html(self, content):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode())

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        pass  # suppress logs


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
print(f"http://localhost:{port}")
http.server.HTTPServer(("", port), Handler).serve_forever()
