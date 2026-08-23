# -*- coding: utf-8 -*-
"""สร้างหน้าเว็บ Gallery จาก data/catalog.json"""
import json, re
from urllib.parse import urlparse

catalog = json.load(open('data/catalog.json'))
POST = 'https://www.facebook.com/groups/1745892855948687/posts/2323047211566579/'

order, seen = [], set()
for r in catalog:
    if r['catName'] not in seen:
        seen.add(r['catName']); order.append(r['catName'])

def domain(u):
    try:
        h = urlparse(u).netloc.replace('www.', '')
        return h or ''
    except Exception:
        return ''

items = [{
    'no': r['no'], 'cat': r['catName'], 'name': r['name'], 'desc': r['desc'],
    'author': r['author'], 'url': r['url'], 'domain': domain(r['url']),
    'extras': r['extras'], 'reactions': r['reactions'],
    'ok': r['linkStatus'] == 'ใช้ได้', 'src': r['permalink'],
} for r in catalog]

DATA = json.dumps({'rooms': order, 'items': items}, ensure_ascii=False, separators=(',', ':'))

HTML = r'''<title>นิทรรศการผลงาน AI ไทย</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Trirong:wght@400;500;600&family=IBM+Plex+Sans+Thai:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --paper:#EFEFEA; --card:#F7F7F4; --ink:#16181A; --ink-soft:#3D4247;
  --muted:#6B7075; --rule:#D6D6CF; --rule-soft:#E3E3DC;
  --blue:#2438D9; --rose:#E8455F; --cover:#E7E7E0;
  --shadow:0 1px 0 rgba(22,24,26,.06), 0 12px 28px -22px rgba(22,24,26,.5);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#0D0F12; --card:#161A20; --ink:#E9E9E3; --ink-soft:#B9BCC0;
    --muted:#8B9096; --rule:#2A2F37; --rule-soft:#20242B;
    --blue:#8C99FF; --rose:#FF7E93; --cover:#1B2028;
    --shadow:0 1px 0 rgba(0,0,0,.4), 0 14px 30px -24px #000;
  }
}
:root[data-theme="dark"]{
  --paper:#0D0F12; --card:#161A20; --ink:#E9E9E3; --ink-soft:#B9BCC0;
  --muted:#8B9096; --rule:#2A2F37; --rule-soft:#20242B;
  --blue:#8C99FF; --rose:#FF7E93; --cover:#1B2028;
  --shadow:0 1px 0 rgba(0,0,0,.4), 0 14px 30px -24px #000;
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:"IBM Plex Sans Thai",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:15px; line-height:1.65; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px; margin:0 auto; padding:0 24px}
a{color:var(--blue)}
:focus-visible{outline:2px solid var(--blue); outline-offset:3px; border-radius:2px}

/* ── หัวนิทรรศการ ── */
.mast{padding:64px 0 40px; border-bottom:1px solid var(--rule)}
.eyebrow{
  font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.18em;
  text-transform:uppercase; color:var(--rose); margin:0 0 18px;
}
.mast h1{
  font-family:Trirong,Georgia,serif; font-weight:500; font-size:clamp(2.4rem,6.2vw,4.1rem);
  line-height:1.08; letter-spacing:-.015em; margin:0 0 20px; text-wrap:balance; max-width:16ch;
}
.deck{font-size:1.06rem; color:var(--ink-soft); max-width:62ch; margin:0 0 28px}
.prov{
  font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--muted);
  display:flex; flex-wrap:wrap; gap:8px; align-items:baseline;
}
.stats{
  display:flex; flex-wrap:wrap; gap:0; margin-top:34px;
  border-top:1px solid var(--rule); padding-top:22px;
}
.stat{padding-right:44px}
.stat b{
  display:block; font-family:"IBM Plex Mono",monospace; font-weight:500;
  font-size:1.85rem; line-height:1.1; font-variant-numeric:tabular-nums;
}
.stat span{font-size:12px; color:var(--muted); letter-spacing:.02em}

/* ── แถบควบคุม ── */
.index{padding:34px 0 4px; border-bottom:1px solid var(--rule)}
.index h2{
  font-family:"IBM Plex Mono",monospace; font-size:11px; font-weight:500;
  letter-spacing:.18em; text-transform:uppercase; color:var(--muted); margin:0 0 14px;
}
.bar{
  position:sticky; top:0; z-index:20; background:var(--paper);
  border-bottom:1px solid var(--rule); padding:12px 0;
}
.bar-in{display:flex; flex-wrap:wrap; gap:12px; align-items:center}
.active-filter{
  display:none; align-items:center; gap:8px; font-family:"IBM Plex Mono",monospace;
  font-size:12px; background:var(--ink); color:var(--paper);
  border:0; border-radius:999px; padding:6px 8px 6px 14px; cursor:pointer; font-weight:400;
}
.active-filter[data-on="1"]{display:inline-flex}
.active-filter b{font-weight:500}
.active-filter span{
  display:grid; place-items:center; width:17px; height:17px; border-radius:50%;
  background:rgba(255,255,255,.22); font-size:13px; line-height:1;
}
.search{
  flex:1 1 240px; min-width:200px; display:flex; align-items:center; gap:9px;
  border:1px solid var(--rule); background:var(--card); border-radius:2px; padding:8px 12px;
}
.search svg{flex:none; opacity:.5}
.search input{
  border:0; background:none; color:var(--ink); font:inherit; font-size:14px;
  width:100%; outline:none;
}
select{
  font:inherit; font-size:13px; color:var(--ink); background:var(--card);
  border:1px solid var(--rule); border-radius:2px; padding:9px 11px;
}
.chips{display:flex; flex-wrap:wrap; gap:6px; padding:0 0 18px}
.chip{
  font:inherit; font-size:12.5px; color:var(--ink-soft); cursor:pointer;
  background:none; border:1px solid var(--rule); border-radius:999px; padding:5px 13px;
  transition:background .12s, color .12s, border-color .12s;
}
.chip:hover{border-color:var(--ink-soft)}
.chip[aria-pressed="true"]{background:var(--ink); border-color:var(--ink); color:var(--paper)}
.chip i{font-family:"IBM Plex Mono",monospace; font-style:normal; opacity:.55; margin-left:6px}
.count{font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--muted);
  margin:0 0 0 auto; white-space:nowrap}
/* เผื่อที่ให้แถบ sticky ตอนกระโดดไปยังหัวห้อง */
html{scroll-padding-top:96px}
.room{scroll-margin-top:96px}

/* ── ห้องจัดแสดง ── */
.room{padding:52px 0 8px}
.room-head{
  display:flex; align-items:baseline; gap:14px; margin-bottom:26px;
  border-bottom:1px solid var(--rule); padding-bottom:12px;
}
.room-no{
  font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--rose);
  letter-spacing:.1em; flex:none;
}
.room-head h2{
  font-family:Trirong,Georgia,serif; font-weight:500; font-size:1.55rem;
  margin:0; letter-spacing:-.01em; flex:1;
}
.room-n{font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--muted); flex:none}

.grid{
  display:grid; gap:30px 26px;
  grid-template-columns:repeat(auto-fill,minmax(268px,1fr));
}

/* ── แผ่นป้ายแคตตาล็อก ── */
.plate{display:flex; flex-direction:column; min-width:0}
.cover{
  position:relative; display:block; aspect-ratio:16/10; background:var(--cover);
  border:1px solid var(--rule); overflow:hidden; text-decoration:none;
  box-shadow:var(--shadow); transition:transform .18s ease, box-shadow .18s ease;
}
a.cover:hover{transform:translateY(-3px); box-shadow:0 1px 0 rgba(22,24,26,.06), 0 20px 34px -22px rgba(22,24,26,.55)}
.cover canvas{display:block; width:100%; height:100%}
.cover-no{
  position:absolute; left:12px; bottom:8px; font-family:"IBM Plex Mono",monospace;
  font-size:2.6rem; font-weight:500; line-height:1; color:var(--ink);
  mix-blend-mode:multiply; opacity:.88; font-variant-numeric:tabular-nums;
}
:root[data-theme="dark"] .cover-no{mix-blend-mode:screen}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .cover-no{mix-blend-mode:screen}}
.cover-dom{
  position:absolute; right:11px; bottom:11px; font-family:"IBM Plex Mono",monospace;
  font-size:10.5px; color:var(--ink); opacity:.6; max-width:62%; overflow:hidden;
  text-overflow:ellipsis; white-space:nowrap; direction:rtl; text-align:right;
}
.label{padding:14px 2px 0; display:flex; flex-direction:column; gap:7px; flex:1}
.label h3{
  font-family:Trirong,Georgia,serif; font-weight:500; font-size:1.15rem; line-height:1.3;
  margin:0; letter-spacing:-.005em; text-wrap:balance;
}
.label h3 a{color:var(--ink); text-decoration:none; background-image:linear-gradient(var(--blue),var(--blue));
  background-size:0 1px; background-repeat:no-repeat; background-position:0 100%; transition:background-size .2s}
.label h3 a:hover{background-size:100% 1px; color:var(--blue)}
.by{font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted);
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.desc{font-size:13.5px; line-height:1.6; color:var(--ink-soft); margin:0}
.foot{
  margin-top:auto; padding-top:11px; display:flex; align-items:center; gap:12px;
  border-top:1px solid var(--rule-soft); font-family:"IBM Plex Mono",monospace; font-size:11px;
}
.foot a{color:var(--blue); text-decoration:none}
.foot a:hover{text-decoration:underline}
.foot .sep{color:var(--rule); }
.rea{margin-left:auto; color:var(--muted); font-variant-numeric:tabular-nums}
.warn{
  display:inline-block; font-family:"IBM Plex Mono",monospace; font-size:10.5px;
  color:var(--rose); border:1px solid currentColor; border-radius:999px; padding:1px 8px;
}
.cover--dead{cursor:default}

.empty{padding:80px 0; text-align:center; color:var(--muted)}
.empty p{margin:0 0 6px}

/* ── ท้ายเล่ม ── */
.colophon{margin-top:76px; border-top:1px solid var(--rule); padding:44px 0 72px}
.colophon h2{
  font-family:Trirong,Georgia,serif; font-weight:500; font-size:1.35rem; margin:0 0 22px;
}
.notes{display:grid; gap:22px 40px; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); max-width:980px}
.note dt{
  font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--rose); margin-bottom:5px;
}
.note dd{margin:0; font-size:13.5px; line-height:1.62; color:var(--ink-soft)}

@media (max-width:640px){
  .wrap{padding:0 18px}
  .mast{padding:44px 0 32px}
  .grid{grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:26px 18px}
  .stat{padding-right:30px}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none !important; animation:none !important}
}
</style>

<header class="mast">
  <div class="wrap">
    <p class="eyebrow">นิทรรศการออนไลน์ · รวบรวมจากคอมเมนต์สาธารณะ</p>
    <h1>ผลงานที่คนไทยสร้างด้วย AI</h1>
    <p class="deck">
      โพสต์เดียวในกลุ่ม Facebook ชวนให้คนเอาผลงานที่สร้างด้วย AI มาแบ่งกัน
      แล้วคอมเมนต์ก็ทะลักเป็นพันอัน หน้านี้คัดเฉพาะผลงานที่เจ้าของแนบลิงก์ไว้จริง
      จัดเป็นหมวดหมู่ และเรียงเป็นแคตตาล็อกให้กดเข้าไปดูของจริงได้ทุกชิ้น
    </p>
    <p class="prov">
      <span>ที่มา</span>
      <a href="__POST__" target="_blank" rel="noopener">โพสต์ต้นทางบน Facebook</a>
    </p>
    <div class="stats">
      <div class="stat"><b id="s-works">0</b><span>ผลงาน</span></div>
      <div class="stat"><b id="s-rooms">0</b><span>หมวดหมู่</span></div>
      <div class="stat"><b>1,329</b><span>คอมเมนต์ที่อ่าน</span></div>
      <div class="stat"><b id="s-live">0</b><span>ลิงก์ที่กดเข้าได้</span></div>
    </div>
  </div>
</header>

<section class="index" aria-label="สารบัญนิทรรศการ">
  <div class="wrap">
    <h2>สารบัญนิทรรศการ</h2>
    <div class="chips" id="chips"></div>
  </div>
</section>

<nav class="bar" aria-label="ค้นหาและกรองผลงาน">
  <div class="wrap">
    <div class="bar-in">
      <label class="search">
        <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.5"/>
          <path d="M11 11l4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <input id="q" type="search" placeholder="ค้นหาชื่อผลงาน คำอธิบาย หรือผู้สร้าง" autocomplete="off">
      </label>
      <select id="sort" aria-label="เรียงลำดับ">
        <option value="room">เรียงตามหมวดหมู่</option>
        <option value="rea">เรียงตามยอดรีแอ็กชัน</option>
        <option value="name">เรียงตามชื่อผลงาน</option>
      </select>
      <button class="active-filter" id="clear" type="button" data-on="0">
        <b id="clear-name"></b><span aria-hidden="true">&times;</span>
      </button>
      <p class="count" id="count"></p>
    </div>
  </div>
</nav>

<main class="wrap" id="main"></main>

<footer class="colophon">
  <div class="wrap">
    <h2>ที่มาและข้อจำกัด</h2>
    <dl class="notes">
      <div class="note">
        <dt>เก็บข้อมูลอย่างไร</dt>
        <dd>ดึงคอมเมนต์จากหน้าโพสต์ด้วยสคริปต์ที่รันในเบราว์เซอร์ของเจ้าของบัญชีเอง
            เพราะ Facebook ปิด Groups API สำหรับอ่านคอมเมนต์มาตั้งแต่ปี 2020
            รันสามครั้งแล้วนำผลมารวมและตัดซ้ำด้วยรหัสคอมเมนต์ เหลือ 1,329 คอมเมนต์</dd>
      </div>
      <div class="note">
        <dt>คัดเข้าแคตตาล็อกอย่างไร</dt>
        <dd>เลือกเฉพาะคอมเมนต์ที่เจ้าของนำเสนอผลงานของตัวเองพร้อมลิงก์
            คอมเมนต์หลักกับคอมเมนต์เสริมของคนเดียวกันถูกยุบเป็นผลงานเดียว
            ส่วนคอมเมนต์ที่โชว์หลายผลงานคนละเรื่องถูกแยกเป็นคนละรายการ</dd>
      </div>
      <div class="note">
        <dt>ภาพปกไม่ใช่ภาพหน้าจอจริง</dt>
        <dd>เป็นภาพพิมพ์ริโซกราฟที่วาดขึ้นด้วยโค้ด โดยสุ่มลวดลายจากชื่อผลงานแต่ละชิ้น
            ผลงานเดิมจะได้ลายเดิมเสมอ แต่ไม่ได้สะท้อนหน้าตาเว็บหรือแอปจริง
            เพราะเครื่องที่ประมวลผลไม่มีสิทธิ์ออกอินเทอร์เน็ตไปเก็บภาพ</dd>
      </div>
      <div class="note">
        <dt>ลิงก์ที่กดไม่ได้</dt>
        <dd id="n-dead"></dd>
      </div>
      <div class="note">
        <dt>ยอดรีแอ็กชัน</dt>
        <dd>เป็นค่า ณ เวลาที่ดึงข้อมูล ไม่ใช่ค่าปัจจุบัน คอมเมนต์ที่ไม่มีรีแอ็กชันนับเป็นศูนย์</dd>
      </div>
      <div class="note">
        <dt>ความครบถ้วน</dt>
        <dd>คอมเมนต์ที่ Facebook ซ่อนหรือกรองเป็นสแปมจะไม่อยู่ในหน้าเว็บ จึงเก็บมาไม่ได้
            ผลงานบางชิ้นอาจตกหล่น และคำอธิบายทั้งหมดสรุปจากข้อความที่เจ้าของเขียนเอง
            ไม่ได้เข้าไปทดลองใช้จริง</dd>
      </div>
    </dl>
  </div>
</footer>

<script>
const DATA = __DATA__;
const {rooms, items} = DATA;

/* ── ภาพปกริโซกราฟ: สุ่มจากชื่อผลงาน ผลงานเดิมได้ลายเดิมเสมอ ── */
function seedOf(s){
  let h = 2166136261;
  for (let i = 0; i < s.length; i++){ h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function rng(seed){
  let a = seed;
  return () => { a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
function css(v){ return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }

function blob(ctx, r, cx, cy, rad){
  const pts = 6 + Math.floor(r() * 3);
  ctx.beginPath();
  for (let i = 0; i <= pts; i++){
    const ang = (i / pts) * Math.PI * 2;
    const rr = rad * (0.62 + r() * 0.55);
    const x = cx + Math.cos(ang) * rr, y = cy + Math.sin(ang) * rr * 0.82;
    if (i === 0) ctx.moveTo(x, y);
    else {
      const pa = ((i - 0.5) / pts) * Math.PI * 2, pr = rad * (0.72 + r() * 0.5);
      ctx.quadraticCurveTo(cx + Math.cos(pa) * pr, cy + Math.sin(pa) * pr * 0.82, x, y);
    }
  }
  ctx.closePath(); ctx.fill();
}

function paint(cv){
  const w = cv.clientWidth || 300, h = cv.clientHeight || 188;
  if (!w || !h) return;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
  const ctx = cv.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  const r = rng(seedOf(cv.dataset.seed));
  ctx.fillStyle = css('--cover'); ctx.fillRect(0, 0, w, h);

  // หมึกสองสีพิมพ์ทับกัน เยื้องกันเล็กน้อยแบบงานพิมพ์จริง
  const inks = [css('--blue'), css('--rose')];
  const dark = document.documentElement.getAttribute('data-theme') === 'dark'
    || (!document.documentElement.getAttribute('data-theme')
        && matchMedia('(prefers-color-scheme: dark)').matches);
  ctx.globalCompositeOperation = dark ? 'screen' : 'multiply';

  // เลือกลายจากค่าสุ่มของผลงานนั้น ให้แต่ละใบหน้าตาไม่ซ้ำกัน
  const motif = Math.floor(r() * 3);
  ctx.globalAlpha = dark ? 0.42 : 0.56;

  for (let layer = 0; layer < 2; layer++){
    ctx.fillStyle = ctx.strokeStyle = inks[layer];
    // เยื้องกันเล็กน้อยแบบพิมพ์ผิดทะเบียนในงานริโซจริง
    const ox = layer * 3.5, oy = layer * 2.5;

    if (motif === 0){            // ก้อนหมึกทับกัน
      const n = 2 + Math.floor(r() * 2);
      for (let i = 0; i < n; i++)
        blob(ctx, r, w * (0.18 + r() * 0.7) + ox, h * (0.16 + r() * 0.68) + oy,
             Math.min(w, h) * (0.2 + r() * 0.3));

    } else if (motif === 1){     // แถบหมึกแนวนอน หนาบางไม่เท่ากัน
      const n = 3 + Math.floor(r() * 3);
      for (let i = 0; i < n; i++){
        const y = h * r(), th = h * (0.05 + r() * 0.19);
        const x = -w * 0.1 + w * r() * 0.5, wd = w * (0.4 + r() * 0.75);
        ctx.fillRect(x + ox, y + oy, wd, th);
      }

    } else {                     // วงแหวนซ้อนศูนย์กลาง
      const cx = w * (0.3 + r() * 0.42), cy = h * (0.28 + r() * 0.44);
      const n = 3 + Math.floor(r() * 3);
      for (let i = 0; i < n; i++){
        ctx.lineWidth = Math.min(w, h) * (0.035 + r() * 0.075);
        ctx.beginPath();
        ctx.arc(cx + ox, cy + oy, Math.min(w, h) * (0.12 + i * (0.09 + r() * 0.06)),
                r() * 6.28, r() * 6.28 + 2.2 + r() * 4);
        ctx.stroke();
      }
    }
  }

  // เม็ดหมึกและรอยเกรน
  ctx.globalAlpha = dark ? 0.15 : 0.2;
  ctx.fillStyle = inks[Math.floor(r() * 2)];
  for (let i = 0; i < 260; i++){
    const s = 0.6 + r() * 1.5;
    ctx.fillRect(r() * w, r() * h, s, s);
  }
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  cv.dataset.painted = '1';
}

const io = new IntersectionObserver((es) => {
  es.forEach(e => { if (e.isIntersecting && !e.target.dataset.painted) paint(e.target); });
}, {rootMargin: '260px'});

/* ── สร้างการ์ด ── */
const pad = n => String(n).padStart(3, '0');
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function plate(it){
  const el = document.createElement('article');
  el.className = 'plate';
  const cover = it.ok
    ? `<a class="cover" href="${esc(it.url)}" target="_blank" rel="noopener"
          aria-label="เปิด ${esc(it.name)} ในแท็บใหม่">`
    : `<div class="cover cover--dead">`;
  const coverEnd = it.ok ? '</a>' : '</div>';

  el.innerHTML = cover +
      `<canvas data-seed="${esc(it.name + it.no)}" aria-hidden="true"></canvas>` +
      `<span class="cover-no">${pad(it.no)}</span>` +
      (it.domain ? `<span class="cover-dom">${esc(it.domain)}</span>` : '') +
      coverEnd +
    `<div class="label">
       <h3>${it.ok ? `<a href="${esc(it.url)}" target="_blank" rel="noopener">${esc(it.name)}</a>`
                   : esc(it.name)}</h3>
       <p class="by">${esc(it.author)}</p>
       <p class="desc">${esc(it.desc)}</p>
       <div class="foot">
         ${it.ok ? `<a href="${esc(it.url)}" target="_blank" rel="noopener">เข้าชมผลงาน</a>`
                 : `<span class="warn">ลิงก์ไม่สมบูรณ์</span>`}
         <span class="sep">/</span>
         <a href="${esc(it.src)}" target="_blank" rel="noopener">คอมเมนต์</a>
         ${it.reactions ? `<span class="rea">${it.reactions.toLocaleString('th-TH')} รีแอ็กชัน</span>` : ''}
       </div>
     </div>`;
  el.querySelectorAll('canvas').forEach(c => io.observe(c));
  return el;
}

/* ── สถานะและการเรนเดอร์ ── */
let room = null, q = '', sort = 'room';
const main = document.getElementById('main');

function visible(){
  const t = q.trim().toLowerCase();
  return items.filter(it => {
    if (room && it.cat !== room) return false;
    if (!t) return true;
    return (it.name + ' ' + it.desc + ' ' + it.author + ' ' + it.cat + ' ' + it.domain)
      .toLowerCase().includes(t);
  });
}

function render(){
  const list = visible();
  main.textContent = '';

  document.getElementById('count').textContent =
    (room || q.trim())
      ? `แสดง ${list.length} จาก ${items.length} ผลงาน`
      : `ทั้งหมด ${items.length} ผลงาน ใน ${rooms.length} หมวดหมู่`;

  if (!list.length){
    const d = document.createElement('div');
    d.className = 'empty';
    d.innerHTML = '<p>ไม่พบผลงานที่ตรงกับที่ค้นหา</p><p>ลองใช้คำสั้นลง หรือกดหมวด “ทั้งหมด”</p>';
    main.appendChild(d);
    return;
  }

  if (sort === 'room'){
    rooms.forEach((name, i) => {
      const group = list.filter(it => it.cat === name);
      if (!group.length) return;
      const sec = document.createElement('section');
      sec.className = 'room';
      sec.innerHTML =
        `<div class="room-head">
           <span class="room-no">ห้อง ${pad(i + 1).slice(1)}</span>
           <h2>${esc(name)}</h2>
           <span class="room-n">${group.length} ผลงาน</span>
         </div>`;
      const g = document.createElement('div');
      g.className = 'grid';
      group.forEach(it => g.appendChild(plate(it)));
      sec.appendChild(g);
      main.appendChild(sec);
    });
  } else {
    const sorted = list.slice().sort(
      sort === 'rea' ? (a, b) => b.reactions - a.reactions
                     : (a, b) => a.name.localeCompare(b.name, 'th'));
    const sec = document.createElement('section');
    sec.className = 'room';
    const g = document.createElement('div');
    g.className = 'grid';
    sorted.forEach(it => g.appendChild(plate(it)));
    sec.appendChild(g);
    main.appendChild(sec);
  }
}

/* ── ปุ่มกรองหมวด ── */
const chips = document.getElementById('chips');
function chip(label, value, n){
  const b = document.createElement('button');
  b.className = 'chip'; b.type = 'button';
  b.setAttribute('aria-pressed', String(room === value));
  b.innerHTML = esc(label) + (n != null ? `<i>${n}</i>` : '');
  b.onclick = () => {
    room = (room === value) ? null : value;
    syncFilter();
    render();
    // เลื่อนไปต้นผลลัพธ์ ไม่ให้ผู้ใช้ค้างอยู่กลางหน้าเดิม
    main.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 'auto' : 'smooth', block: 'start'});
  };
  b.dataset.v = value ?? '';
  return b;
}
chips.appendChild(chip('ทั้งหมด', null, items.length));
rooms.forEach(name => chips.appendChild(chip(name, name, items.filter(i => i.cat === name).length)));

const clearBtn = document.getElementById('clear');
function syncFilter(){
  chips.querySelectorAll('.chip').forEach(c =>
    c.setAttribute('aria-pressed', String(c.dataset.v === (room ?? ''))));
  clearBtn.dataset.on = room ? '1' : '0';
  document.getElementById('clear-name').textContent = room || '';
}
clearBtn.onclick = () => { room = null; syncFilter(); render(); };

document.getElementById('q').addEventListener('input', e => { q = e.target.value; render(); });
document.getElementById('sort').addEventListener('change', e => { sort = e.target.value; render(); });

/* ── ตัวเลขสรุปและหมายเหตุ ── */
const dead = items.filter(i => !i.ok).length;
document.getElementById('s-works').textContent = items.length;
document.getElementById('s-rooms').textContent = rooms.length;
document.getElementById('s-live').textContent = items.length - dead;
document.getElementById('n-dead').textContent =
  `${dead} จาก ${items.length} รายการ เพราะ Facebook ตัดข้อความลิงก์ยาวด้วยจุดไข่ปลา ` +
  `และสคริปต์เก็บได้เฉพาะข้อความที่แสดง ลิงก์ App Store กู้คืนได้จากเลขรหัสแอป ` +
  `แต่ Play Store กับ Chrome Web Store กู้ไม่ได้ รายการเหล่านี้ทำเครื่องหมายไว้ว่า “ลิงก์ไม่สมบูรณ์”`;

render();

/* วาดปกใหม่เมื่อธีมเปลี่ยน เพราะสีหมึกและโหมดผสมสีต่างกันคนละธีม */
function repaint(){
  document.querySelectorAll('canvas[data-painted]').forEach(c => { delete c.dataset.painted; });
  document.querySelectorAll('canvas').forEach(c => {
    const r = c.getBoundingClientRect();
    if (r.top < innerHeight + 300 && r.bottom > -300) paint(c);
  });
}
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', repaint);
new MutationObserver(repaint).observe(document.documentElement, {attributes:true, attributeFilter:['data-theme']});
addEventListener('resize', () => { clearTimeout(window.__rz); window.__rz = setTimeout(repaint, 220); });
</script>
'''

out = HTML.replace('__DATA__', DATA).replace('__POST__', POST)
path = '/tmp/claude-0/-home-user-Survey-Example-Claude-Projects/ebb5aee4-0d70-5b59-8b13-f3af22750c3e/scratchpad/gallery/index.html'
open(path, 'w', encoding='utf-8').write(out)
print('written', len(out), 'bytes ->', path)
