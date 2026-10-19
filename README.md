# M82 Cluster Explorer

เว็บ Interactive สำหรับสำรวจกลุ่มดาวในสนาม M82 จากผล DBSCAN 2D, DBSCAN 3D และ HDBSCAN ที่บันทึกไว้ พร้อมภาพพื้นหลัง Hubble F435W

ใช้ HTML/CSS/JavaScript และ WebGL ไม่มีขั้นตอน npm install หรือ build ข้อมูลพร้อมแสดงผลรวมอยู่ใน `dist/` แล้ว ไม่ต้องมี Notebook, CSV ต้นทาง หรือ FITS เพื่อเปิดเว็บ

## เปิดในเครื่อง

ต้องมี Python 3 (แนะนำ 3.10 ขึ้นไป):

```sh
python server.py
```

บน Windows ใช้ `py -3 server.py` หรือดับเบิลคลิก `Start Explorer.cmd` ได้เช่นกัน เซิร์ฟเวอร์เปิดเฉพาะเครื่องนี้ที่ `http://127.0.0.1:8765` และจะลองพอร์ตถัดไปหากพอร์ตถูกใช้งาน กด Ctrl+C ใน terminal เพื่อหยุดเมื่อเปิดด้วยคำสั่ง

อย่าเปิด `dist/index.html` ผ่าน file:// โดยตรง เพราะเว็บต้อง fetch ไฟล์ข้อมูลผ่าน HTTP

## ใช้งาน

- เลือกวิธี 2D / 3D / HDBSCAN แล้วคลิกกลุ่มหรือค้นหา เช่น Y-1075
- ซูม เลื่อนแผนที่ เลือกประชากรดาว และเปิดวง RMS/ระยะสมาชิกไกลสุด
- กลุ่มสมาชิกเกิน 100 ดวงถูกซ่อนเริ่มต้น ปิดตัวกรองเพื่อดูทั้งหมดได้
- เปิด/ปิดพื้นหลัง Hubble และปรับความทึบได้
- ดู CMD เปรียบเทียบสมาชิกข้ามวิธี และส่งออก CSV/PNG
- URL เก็บวิธีและกลุ่ม เช่น `?method=2d&cluster=1075`

คำว่า cluster หมายถึงกลุ่มที่อัลกอริทึมจัดสมาชิกไว้ ไม่ใช่การยืนยันวัตถุทางกายภาพ ส่วน 3D หมายถึงตำแหน่งสองแกนร่วมกับสี ไม่ใช่ระยะลึกของดาว

## โครงสร้าง

```text
dist/                       เว็บไซต์พร้อมให้บริการ
  index.html
  app.js
  style.css
  data/                     ข้อมูล binary, catalog, ภาพ และ provenance
server.py                   เปิดเว็บด้วย Python standard library
prepare_data.py             สร้างข้อมูลเว็บจาก CSV ที่บันทึกไว้
prepare_background.py       สร้างภาพพื้นหลังจาก FITS
requirements-data.txt       แพ็กเกจเฉพาะการสร้างข้อมูลใหม่
docs/research-notes.md       รายละเอียดวิธีและข้อมูลของเว็บฉบับเดิม
DATA_SOURCES.md              แหล่งข้อมูลและขอบเขตผล
```

`dist/` เป็นโค้ดเว็บและข้อมูลที่ต้องติดตามด้วย Git ไม่ใช่ build cache ไฟล์ใหญ่สุดประมาณ 11 MB จึงไม่ได้ตั้ง Git LFS

## Push ขึ้น GitHub

repo นี้มี branch `main` และ commit เริ่มต้นแล้ว สร้าง repository ว่างบน GitHub โดยไม่เพิ่ม README หรือ .gitignore จากนั้นรันในโฟลเดอร์นี้ โดยเปลี่ยน OWNER และ REPOSITORY:

```sh
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

ยังไม่ได้ตั้ง remote หรือ push จากเครื่องนี้ และไม่ได้เปลี่ยนการเข้าถึงเว็บไซต์เดิม

## นำเว็บไปโฮสต์

นำเนื้อหาภายใน `dist/` ไปให้บริการด้วย static hosting ได้ทั้งหมด เว็บใช้พาธสัมพัทธ์และไม่เรียก API ภายนอก การ push repo อย่างเดียวไม่ได้ทำให้เว็บเผยแพร่โดยอัตโนมัติ หากใช้ GitHub Pages ต้องตั้งการเผยแพร่ให้ใช้ `dist/` เป็น artifact ของเว็บ

## สร้างข้อมูลใหม่ (ไม่จำเป็นสำหรับการเปิดเว็บ)

```sh
python -m pip install -r requirements-data.txt
python prepare_data.py --source "D:/research/m82-bfs-ff"
python prepare_background.py --source "D:/research/m82-bfs-ff/file"
```

คำสั่งแรกใช้ CSV เดิม 4 ไฟล์ที่ระบุใน `DATA_SOURCES.md` ไม่ได้รัน clustering ใหม่ คำสั่งที่สองใช้ FITS ทั้ง 6 สนาม ไฟล์ต้นทางไม่ได้รวมใน repo ผลที่สร้างจะเขียนทับไฟล์ใน `dist/data/` ควรตรวจ diff ก่อน commit

## สถานะข้อมูล

รวมดาว 408,213 แถว ผล 2D 510 กลุ่ม, 3D 49 กลุ่ม และ HDBSCAN 318 กลุ่ม ตัวเลือก 391 candidates ใช้รายการเดิมจากเล่ม ไม่ได้เปลี่ยนตามรายการแก้หลังสอบ รายละเอียดแหล่งข้อมูลและนิยามขนาดอยู่ใน `DATA_SOURCES.md` และ `docs/research-notes.md`

ยังไม่ได้กำหนด LICENSE สำหรับโค้ดใน repo นี้ เครดิตและ provenance ของข้อมูลวิจัยคงแยกจากการอนุญาตใช้โค้ด
