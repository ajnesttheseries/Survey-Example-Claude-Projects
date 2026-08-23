/*
 * fb-comment-extractor.js
 *
 * ดึงคอมเมนต์ทั้งหมดจากโพสต์ Facebook (รวม reply) โดยรันใน DevTools Console
 * ของเบราว์เซอร์ที่ล็อกอิน Facebook อยู่ และเปิดหน้าโพสต์นั้นค้างไว้
 *
 * วิธีใช้ดูใน tools/README.md
 *
 * ผลลัพธ์:
 *   - ดาวน์โหลด fb-comments-<postId>.csv และ .json อัตโนมัติ
 *   - เก็บผลไว้ที่ window.__FB_COMMENTS ด้วย (เผื่ออยากเล่นต่อใน console)
 *
 * หมายเหตุสำคัญ: Facebook เปลี่ยนโครงสร้าง DOM และชื่อ class บ่อยมาก
 * สคริปต์นี้จึงยึดกับ ARIA role/label เป็นหลัก (เสถียรกว่า class) แต่ก็ยัง
 * มีโอกาสพังเมื่อ Facebook ปรับ UI ถ้าดึงได้ 0 คอมเมนต์ ให้ดู
 * "การแก้ปัญหา" ใน README
 */

(async () => {
  'use strict';

  // ---------- ตั้งค่า ----------
  const CFG = {
    pauseMs: 1100,        // หน่วงหลังกดปุ่มขยาย/เลื่อนจอ ให้ Facebook โหลดทัน
    maxRounds: 500,       // กันลูปไม่รู้จบ เพิ่มได้ถ้าโพสต์คอมเมนต์เยอะมาก
    idleRoundsToStop: 3,  // ถ้าไม่มีอะไรเพิ่มติดกันกี่รอบถึงหยุด
    verbose: true,
  };

  const log = (...a) => CFG.verbose && console.log('%c[fb-extract]', 'color:#1877f2;font-weight:bold', ...a);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ---------- ข้อความปุ่มที่ต้องกด (ไทย + อังกฤษ) ----------
  // ใช้ตัวพิมพ์เล็กเทียบแบบ "มีคำนี้อยู่ในปุ่ม"
  const EXPAND_PATTERNS = [
    // โหลดคอมเมนต์เพิ่ม
    'ดูความคิดเห็นเพิ่มเติม', 'ดูความคิดเห็นก่อนหน้า', 'ความคิดเห็นเพิ่มเติม',
    'view more comments', 'view previous comments', 'more comments',
    'previous comments',
    // โหลด reply
    'ดูการตอบกลับ', 'การตอบกลับ', 'ตอบกลับทั้งหมด',
    'reply', 'replies',
    // ขยายข้อความที่ถูกตัด
    'ดูเพิ่มเติม', 'see more',
  ];

  // ปุ่มที่ห้ามกดเด็ดขาด (กันเผลอกดถูกใจ/แชร์/เขียนตอบกลับ)
  const FORBIDDEN_PATTERNS = [
    'ถูกใจ', 'แชร์', 'ซ่อน', 'ลบ', 'รายงาน', 'เขียนตอบกลับ', 'แสดงความคิดเห็น',
    'like', 'share', 'hide', 'delete', 'report', 'write a reply', 'comment as',
  ];

  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const lower = (s) => norm(s).toLowerCase();
  // innerText ให้ผลดีกว่าในเบราว์เซอร์ (เคารพ <br> และ element ที่ซ่อน)
  // แต่บาง environment ไม่มี จึงถอยไปใช้ textContent
  const txt = (el) => {
    if (!el) return '';
    return norm(el.innerText != null ? el.innerText : el.textContent);
  };

  function isExpandButton(el) {
    const t = lower(txt(el));
    if (!t || t.length > 60) return false;
    if (FORBIDDEN_PATTERNS.some((p) => t.includes(p))) return false;
    return EXPAND_PATTERNS.some((p) => t.includes(p));
  }

  function visible(el) {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  // ---------- ขั้นที่ 1: กดขยายทุกอย่างจนหมด ----------
  const clicked = new WeakSet();

  async function expandAll() {
    let idle = 0;
    for (let round = 1; round <= CFG.maxRounds; round++) {
      const buttons = Array.from(
        document.querySelectorAll('div[role="button"], span[role="button"], a[role="button"]')
      ).filter((el) => !clicked.has(el) && visible(el) && isExpandButton(el));

      const before = countComments();

      if (buttons.length === 0) {
        // ไม่มีปุ่มให้กดแล้ว ลองเลื่อนจอกระตุ้น lazy-load
        window.scrollBy(0, window.innerHeight * 0.8);
        await sleep(CFG.pauseMs);
      } else {
        for (const b of buttons) {
          clicked.add(b);
          try { b.click(); } catch (e) { /* ปุ่มหลุดจาก DOM ระหว่างกด — ข้าม */ }
          await sleep(120);
        }
        await sleep(CFG.pauseMs);
      }

      const after = countComments();
      log(`รอบ ${round}: กด ${buttons.length} ปุ่ม | คอมเมนต์ ${before} -> ${after}`);

      if (after === before && buttons.length === 0) {
        idle++;
        if (idle >= CFG.idleRoundsToStop) {
          log('ไม่มีอะไรเพิ่มแล้ว หยุดขยาย');
          return;
        }
      } else {
        idle = 0;
      }
    }
    log('ชนเพดาน maxRounds แล้ว — ผลอาจยังไม่ครบ ลองเพิ่ม CFG.maxRounds');
  }

  // ---------- ขั้นที่ 2: อ่านคอมเมนต์ออกจาก DOM ----------

  // คอมเมนต์แต่ละอันคือ article ที่มี aria-label ขึ้นต้นว่า "ความคิดเห็นโดย"/"Comment by"
  // ส่วนตัวโพสต์เองก็เป็น article เหมือนกัน จึงต้องกรองด้วย aria-label
  const COMMENT_LABEL_RE = /^(ความคิดเห็นโดย|comment by|ตอบกลับโดย|reply by)/i;

  function commentNodes() {
    return Array.from(document.querySelectorAll('div[role="article"]')).filter((el) => {
      const label = el.getAttribute('aria-label') || '';
      return COMMENT_LABEL_RE.test(norm(label));
    });
  }

  function countComments() {
    return commentNodes().length;
  }

  // ระดับความลึก: คอมเมนต์หลัก = 0, reply = 1, reply ของ reply = 2
  function depthOf(node, allNodes) {
    let d = 0;
    let p = node.parentElement;
    while (p) {
      if (p.getAttribute && p.getAttribute('role') === 'article' && allNodes.includes(p)) d++;
      p = p.parentElement;
    }
    return d;
  }

  function extractAuthor(node) {
    // ชื่อผู้คอมเมนต์อยู่ใน aria-label ของ article อยู่แล้ว — เชื่อถือได้ที่สุด
    const label = norm(node.getAttribute('aria-label') || '');
    const m = label.match(/^(?:ความคิดเห็นโดย|comment by|ตอบกลับโดย|reply by)\s+(.+?)(?:\s+\d|$)/i);
    if (m && m[1]) return m[1].trim();

    // สำรอง: ลิงก์โปรไฟล์อันแรกในคอมเมนต์
    const a = node.querySelector('a[role="link"][href*="facebook.com/"], a[role="link"][href^="/"]');
    return a ? txt(a) : '';
  }

  function extractProfileUrl(node) {
    const a = node.querySelector('a[role="link"][href]');
    if (!a) return '';
    try {
      const u = new URL(a.href, location.origin);
      // ตัด tracking params ที่ Facebook แปะมา (__cft__, __tn__ ฯลฯ)
      [...u.searchParams.keys()]
        .filter((k) => k.startsWith('__') || k === 'comment_id' || k === 'reply_comment_id')
        .forEach((k) => u.searchParams.delete(k));
      return u.toString();
    } catch (e) {
      return '';
    }
  }

  function extractPermalinkAndTime(node) {
    // ลิงก์เวลาของคอมเมนต์จะมี comment_id อยู่ใน query string
    const a = Array.from(node.querySelectorAll('a[href]')).find((x) =>
      /comment_id=|reply_comment_id=/.test(x.href)
    );
    if (!a) return { permalink: '', relTime: '', commentId: '' };

    let commentId = '';
    try {
      const u = new URL(a.href, location.origin);
      commentId = u.searchParams.get('reply_comment_id') || u.searchParams.get('comment_id') || '';
    } catch (e) { /* URL แปลก ๆ — ปล่อยว่าง */ }

    return { permalink: a.href, relTime: txt(a), commentId };
  }

  function extractText(node, allNodes) {
    // เนื้อความอยู่ใน div[dir="auto"] แต่ต้องกัน 3 อย่าง:
    //  1. ข้อความที่อยู่ใน reply ซ้อน (article ลูก)
    //  2. ชื่อผู้เขียน
    //  3. แถบปุ่ม ถูกใจ/ตอบกลับ/เวลา
    const author = extractAuthor(node);
    const parts = [];

    for (const d of node.querySelectorAll('div[dir="auto"]')) {
      // ข้ามถ้าอยู่ใน article ลูก (คือ reply ของคอมเมนต์นี้)
      const owner = d.closest('div[role="article"]');
      if (owner !== node) continue;

      // ข้ามถ้าอยู่ในปุ่ม
      if (d.closest('[role="button"]')) continue;

      const t = txt(d);
      if (!t) continue;
      if (t === author) continue;
      if (/^(ถูกใจ|ตอบกลับ|แชร์|like|reply|share)$/i.test(t)) continue;

      parts.push(t);
    }

    // ลบส่วนที่ซ้ำกัน (Facebook มัก nest div[dir=auto] ซ้อนกันหลายชั้น)
    const uniq = parts.filter((p, i) => !parts.some((q, j) => j < i && q.includes(p)));
    return uniq.join('\n').trim();
  }

  function extractReactionCount(node) {
    const el = node.querySelector('[aria-label*="ความรู้สึก"], [aria-label*="reaction"]');
    if (!el) return '';
    const m = norm(el.getAttribute('aria-label')).match(/[\d,]+/);
    return m ? m[0].replace(/,/g, '') : '';
  }

  function scrape() {
    const nodes = commentNodes();
    return nodes.map((node, i) => {
      const { permalink, relTime, commentId } = extractPermalinkAndTime(node);
      return {
        index: i + 1,
        depth: depthOf(node, nodes),
        author: extractAuthor(node),
        profileUrl: extractProfileUrl(node),
        text: extractText(node, nodes),
        relativeTime: relTime,
        reactions: extractReactionCount(node),
        commentId,
        permalink,
      };
    });
  }

  // ---------- ขั้นที่ 3: ส่งออกไฟล์ ----------

  function toCsv(rows) {
    const cols = ['index', 'depth', 'author', 'text', 'relativeTime', 'reactions', 'commentId', 'profileUrl', 'permalink'];
    const esc = (v) => {
      const s = v === null || v === undefined ? '' : String(v);
      return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    };
    const lines = [cols.join(',')];
    for (const r of rows) lines.push(cols.map((c) => esc(r[c])).join(','));
    // BOM เพื่อให้ Excel เปิดภาษาไทยไม่เป็นตัวยึกยือ
    return '﻿' + lines.join('\r\n');
  }

  function download(filename, content, mime) {
    const blob = new Blob([content], { type: mime + ';charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }

  function postIdFromUrl() {
    const u = new URL(location.href);
    const mp = u.searchParams.get('multi_permalinks');
    if (mp) return mp;
    const m = u.pathname.match(/\/posts\/(\d+)/);
    return m ? m[1] : 'unknown';
  }

  // ---------- ทางออกสำหรับ unit test (Node) ----------
  // เวลารันในเบราว์เซอร์ module จะไม่มี จึงข้ามบล็อกนี้แล้วรันจริงต่อไป
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      commentNodes, countComments, depthOf, extractAuthor, extractProfileUrl,
      extractPermalinkAndTime, extractText, extractReactionCount, scrape,
      toCsv, isExpandButton, postIdFromUrl,
    };
    return;
  }

  // ---------- รัน ----------
  console.clear();
  log('เริ่มขยายคอมเมนต์ทั้งหมด — อย่าเลื่อนจอหรือปิดแท็บระหว่างนี้');
  log('ถ้าจะหยุดกลางคัน กด Esc หรือรีโหลดหน้า');

  await expandAll();

  const rows = scrape();
  const postId = postIdFromUrl();

  window.__FB_COMMENTS = rows;

  if (rows.length === 0) {
    console.warn(
      '[fb-extract] ดึงได้ 0 คอมเมนต์ — โครงสร้าง DOM อาจเปลี่ยน\n' +
      'ลองดูวิธีแก้ในส่วน "การแก้ปัญหา" ของ tools/README.md'
    );
    return;
  }

  download(`fb-comments-${postId}.csv`, toCsv(rows), 'text/csv');
  download(`fb-comments-${postId}.json`, JSON.stringify(rows, null, 2), 'application/json');

  const top = rows.filter((r) => r.depth === 0).length;
  log(`เสร็จแล้ว: ${rows.length} รายการ (คอมเมนต์หลัก ${top}, ตอบกลับ ${rows.length - top})`);
  log('ดาวน์โหลด CSV + JSON แล้ว | ดูข้อมูลดิบได้ที่ window.__FB_COMMENTS');
  console.table(rows.slice(0, 20).map((r) => ({
    '#': r.index, ระดับ: r.depth, ผู้เขียน: r.author,
    ข้อความ: r.text.slice(0, 60), เวลา: r.relativeTime,
  })));
})();
