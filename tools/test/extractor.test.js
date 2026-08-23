/* ทดสอบ logic การอ่าน DOM ของ fb-comment-extractor.js ด้วย jsdom
 * รัน: node tools/test/extractor.test.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const html = fs.readFileSync(path.join(__dirname, 'fixture.html'), 'utf8');
const dom = new JSDOM(html, { url: 'https://www.facebook.com/groups/1745892855948687/?multi_permalinks=2323047211566579' });

global.window = dom.window;
global.document = dom.window.document;
global.URL = dom.window.URL;
global.Blob = dom.window.Blob;
global.location = dom.window.location;

const X = require('../fb-comment-extractor.js');

let failed = 0;
function check(name, actual, expected) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (!ok) { failed++; console.error(`✗ ${name}\n    ได้:   ${JSON.stringify(actual)}\n    ควรได้: ${JSON.stringify(expected)}`); }
  else console.log(`✓ ${name}`);
}
function checkTrue(name, cond, detail) {
  if (!cond) { failed++; console.error(`✗ ${name}${detail ? '\n    ' + detail : ''}`); }
  else console.log(`✓ ${name}`);
}

const rows = X.scrape();

check('เจอ 3 คอมเมนต์ (ไม่นับตัวโพสต์)', rows.length, 3);
check('ไม่ดึงเนื้อหาโพสต์หลักมา', rows.some(r => r.text.includes('เนื้อหาโพสต์หลัก')), false);

const [c1, reply, c2] = rows;

check('ชื่อผู้เขียนไทย ตัดเวลาออก', c1.author, 'สมชาย ใจดี');
check('ชื่อผู้เขียนอังกฤษ (ไม่มีเวลาต่อท้าย)', c2.author, 'Jane Doe');
check('ชื่อผู้ตอบกลับ', reply.author, 'มานี รักเรียน');

check('ความลึก: คอมเมนต์หลัก = 0', c1.depth, 0);
check('ความลึก: reply = 1', reply.depth, 1);
check('ความลึก: คอมเมนต์หลักที่สอง = 0', c2.depth, 0);

check('ข้อความไม่ซ้ำจาก div ซ้อนกัน', c1.text, 'ขอบคุณสำหรับข้อมูลครับ มีประโยชน์มาก');
check('ข้อความ reply ไม่รั่วเข้าคอมเมนต์แม่', c1.text.includes('เห็นด้วย'), false);
check('ปุ่ม ถูกใจ/ตอบกลับ ไม่ปนเข้าข้อความ', /ถูกใจ|ตอบกลับ/.test(c1.text), false);
check('ข้อความ reply', reply.text, 'เห็นด้วยค่ะ');

check('จำนวน reaction', c1.reactions, '12');
check('comment id', c1.commentId, '555');
check('reply_comment_id ชนะ comment_id', reply.commentId, '777');
check('เวลาแบบสัมพัทธ์', c1.relativeTime, '2 ชม.');

checkTrue('ตัด tracking param __cft__/__tn__ ออกจากลิงก์โปรไฟล์',
  !c1.profileUrl.includes('__cft__') && !c1.profileUrl.includes('__tn__'), c1.profileUrl);
checkTrue('ลิงก์โปรไฟล์ยังคง user id', c1.profileUrl.includes('/user/111/'), c1.profileUrl);

// --- CSV ---
const csv = X.toCsv(rows);
checkTrue('CSV มี BOM สำหรับ Excel ภาษาไทย', csv.charCodeAt(0) === 0xFEFF);
checkTrue('CSV escape เครื่องหมายคำพูดถูกต้อง', csv.includes('""quotes""'), csv.split('\r\n')[3]);
check('CSV จำนวนบรรทัด = header + 3', csv.split('\r\n').length, 4);

// --- ปุ่มขยาย ---
const btns = Array.from(document.querySelectorAll('div[role="button"]'));
const labels = btns.filter(b => X.isExpandButton(b)).map(b => b.textContent.trim());
check('เลือกเฉพาะปุ่มขยาย ไม่กดปุ่มถูกใจ', labels.sort(), ['View 3 replies', 'ดูความคิดเห็นเพิ่มเติม']);

// --- post id ---
check('อ่าน post id จาก multi_permalinks', X.postIdFromUrl(), '2323047211566579');

console.log(failed === 0 ? '\nผ่านทั้งหมด' : `\nไม่ผ่าน ${failed} ข้อ`);
process.exit(failed === 0 ? 0 : 1);
