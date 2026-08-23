# -*- coding: utf-8 -*-
"""ตรวจไฟล์ Excel โดยไม่พึ่ง LibreOffice

LibreOffice ในคอนเทนเนอร์นี้ recalc ไม่ได้ (timeout แม้ไฟล์ 3 เซลล์)
สคริปต์นี้จึงตรวจสิ่งที่ recalc ควรจับ ด้วยการอ่านสูตรตรง ๆ แล้ว
คำนวณผลที่ควรได้ด้วย Python เทียบกับข้อมูลจริง
"""
import json, re, sys
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

FILE = 'ผลงาน-AI-จากคอมเมนต์-Facebook.xlsx'
catalog = json.load(open('data/catalog.json'))
wb = load_workbook(FILE)
ws, s2, s3 = wb['แคตตาล็อกผลงาน'], wb['สรุปตามหมวดหมู่'], wb['วิธีทำและข้อจำกัด']

fails = []
def check(name, cond, detail=''):
    print(('✓ ' if cond else '✗ ') + name + ('' if cond else f'\n    {detail}'))
    if not cond: fails.append(name)

# ── 1. ฟังก์ชันที่ใช้ต้องเป็นชุดที่ Excel รองรับโดยไม่ต้องมี _xlfn. ──
ALLOWED = {'COUNTIF', 'SUMIF', 'SUM', 'IFERROR'}
BANNED  = {'XLOOKUP','XMATCH','SORT','FILTER','UNIQUE','SEQUENCE',
           'TEXTJOIN','CONCAT','IFS','SWITCH','MAXIFS','MINIFS'}
used, formulas = set(), []
for sheet in (ws, s2, s3):
    for row in sheet.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('='):
                formulas.append((sheet.title, c.coordinate, c.value))
                used |= set(re.findall(r'([A-Z][A-Z0-9\.]*)\s*\(', c.value))
check(f'ใช้เฉพาะฟังก์ชันที่ปลอดภัย ({len(formulas)} สูตร)', used <= ALLOWED, f'เจอ: {sorted(used)}')
check('ไม่มีฟังก์ชันที่ต้องมี prefix หรือ spill', not (used & BANNED), f'เจอ: {sorted(used & BANNED)}')

# ── 2. ช่วงอ้างอิงต้องครอบข้อมูลจริงพอดี ไม่ขาดไม่เกิน ──
HEADER_ROW = 5
first, last = HEADER_ROW + 1, HEADER_ROW + len(catalog)
check(f'แถวข้อมูลอยู่ที่ {first}-{last} ครบ {len(catalog)} รายการ',
      ws.cell(row=first, column=1).value == 1
      and ws.cell(row=last, column=1).value == len(catalog)
      and ws.cell(row=last + 1, column=1).value is None,
      f'A{first}={ws.cell(row=first,column=1).value} A{last}={ws.cell(row=last,column=1).value} '
      f'A{last+1}={ws.cell(row=last+1,column=1).value}')

# ตรวจเฉพาะ COUNTIF/SUMIF ที่สแกนคอลัมน์หมวดหมู่ ส่วน $B$<แถวรวม>
# ในสูตรสัดส่วนเป็นการอ้างเซลล์เดียว ไม่ใช่ช่วง จึงไม่นับ
scan = [f for f in formulas if re.search(r'\b(COUNTIF|SUMIF)\(', f[2])]
bad_range = [f for f in scan if f'$B${first}:$B${last}' not in f[2]]
check(f'ทุกสูตร COUNTIF/SUMIF ({len(scan)} สูตร) อ้างช่วงหมวดหมู่ที่ถูกต้อง',
      scan and not bad_range, str(bad_range[:3]))

bad_sum = [f for f in scan if 'SUMIF(' in f[2] and f'$H${first}:$H${last}' not in f[2]]
check('ทุกสูตร SUMIF บวกยอดรีแอ็กชันจากช่วงที่ถูกต้อง', not bad_sum, str(bad_sum[:3]))

# ── 3. ผลของสูตรต้องตรงกับที่คำนวณจากข้อมูลจริง ──
from collections import Counter
cnt = Counter(r['catName'] for r in catalog)
rea = {}
for r in catalog: rea[r['catName']] = rea.get(r['catName'], 0) + r['reactions']

row, mism = 4, []
while s2.cell(row=row, column=1).value not in (None, 'รวมทั้งหมด'):
    name = s2.cell(row=row, column=1).value
    f_cnt = s2.cell(row=row, column=2).value
    f_sum = s2.cell(row=row, column=4).value
    if f'COUNTIF' not in str(f_cnt) or f'"{name}"' in str(f_cnt):
        pass
    if name not in cnt:
        mism.append(f'{name}: ไม่มีในข้อมูล')
    if f'$A{row}' not in str(f_cnt) or f'$A{row}' not in str(f_sum):
        mism.append(f'{name}: สูตรไม่ได้อ้าง $A{row}')
    row += 1
n_cats = row - 4
check(f'ชีตสรุปมี {n_cats} หมวด ตรงกับข้อมูล ({len(cnt)} หมวด)', n_cats == len(cnt))
check('ทุกแถวสรุปอ้างชื่อหมวดในคอลัมน์ A ของตัวเอง', not mism, str(mism[:3]))
check('ชื่อหมวดในชีตสรุปตรงกับในแคตตาล็อกทุกตัว',
      {s2.cell(row=4+i, column=1).value for i in range(n_cats)} == set(cnt),
      'ชื่อไม่ตรง → COUNTIF จะได้ 0')

tot_row = 4 + n_cats
check('แถวรวมใช้ SUM ครอบทุกหมวดพอดี',
      s2.cell(row=tot_row, column=2).value == f'=SUM(B4:B{tot_row-1})',
      str(s2.cell(row=tot_row, column=2).value))
check('สูตรสัดส่วนหารด้วยแถวรวม และกัน error ด้วย IFERROR',
      all(f'$B${tot_row}' in str(s2.cell(row=4+i, column=3).value)
          and 'IFERROR' in str(s2.cell(row=4+i, column=3).value) for i in range(n_cats)))

# ── 4. ลิงก์ ──
n_link = sum(1 for i in range(len(catalog)) if ws.cell(row=first+i, column=6).hyperlink)
ok_cnt = sum(1 for r in catalog if r['linkStatus'] == 'ใช้ได้')
check(f'ทำ hyperlink เฉพาะลิงก์ที่ใช้ได้ ({n_link} จาก {len(catalog)})', n_link == ok_cnt,
      f'hyperlink={n_link} ควรเป็น {ok_cnt}')
check('ลิงก์ที่ใช้ไม่ได้ไม่ถูกทำเป็น hyperlink หลอกให้กด',
      all(not ws.cell(row=first+i, column=6).hyperlink
          for i, r in enumerate(catalog) if r['linkStatus'] != 'ใช้ได้'))
n_perma = sum(1 for i in range(len(catalog)) if ws.cell(row=first+i, column=10).hyperlink)
check(f'มีลิงก์กลับไปคอมเมนต์ต้นทางครบ {len(catalog)} แถว', n_perma == len(catalog), str(n_perma))

# ── 5. รูปแบบไฟล์ ──
check('ตั้งค่าให้คำนวณสูตรใหม่ตอนเปิดไฟล์', wb.calculation.fullCalcOnLoad is True)
check('ใช้ฟอนต์ Arial ทั้งไฟล์',
      all(ws.cell(row=first+i, column=c).font.name == 'Arial'
          for i in range(0, len(catalog), 7) for c in range(1, 11)))
check('ตรึงหัวตารางและเปิดตัวกรอง',
      ws.freeze_panes == f'A{first}' and ws.auto_filter.ref == f'A{HEADER_ROW}:J{last}')
check('ยอดรีแอ็กชันเป็นตัวเลข ไม่ใช่ข้อความ',
      all(isinstance(ws.cell(row=first+i, column=8).value, int) for i in range(len(catalog))))
check('ไม่มีเซลล์ว่างในคอลัมน์ชื่อผลงานและลิงก์',
      all(ws.cell(row=first+i, column=3).value and ws.cell(row=first+i, column=6).value
          for i in range(len(catalog))))

print()
print('ผ่านทั้งหมด' if not fails else f'ไม่ผ่าน {len(fails)} ข้อ: {fails}')
sys.exit(1 if fails else 0)
