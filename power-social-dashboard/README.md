# Power Social Dashboard (Facebook, YouTube, Instagram)

แดชบอร์ดสำหรับวิเคราะห์คอนเทนต์สาธารณะบน Social Network (Facebook, YouTube, Instagram) แบบรวดเร็ว เหมาะสำหรับทีมการตลาด/คอนเทนต์ที่ต้องการภาพรวมการเคลื่อนไหวของเพจ/แชนแนล/บัญชี และเปรียบเทียบประสิทธิภาพคอนเทนต์

## คุณสมบัติหลัก
- ดึงข้อมูลคอนเทนต์สาธารณะจาก YouTube (API Key), Facebook/Instagram (ต้องมี Access Token) หรือใช้ข้อมูลตัวอย่างได้ทันที
- รวมข้อมูลจากหลายแพลตฟอร์มให้อยู่ในสโกีมารวมเดียวกัน (normalized)
- วิเคราะห์ KPI พื้นฐาน: จำนวนโพสต์, ยอดมีส่วนร่วม (likes/comments/shares), ยอดวิว, Engagement Rate โดยประมาณ
- กรองช่วงเวลา/แพลตฟอร์ม/ช่องทาง และดู Top Posts
- แสดงผลด้วยกราฟโต้ตอบแบบเรียลไทม์ด้วย Streamlit + Plotly

## โครงสร้างโปรเจกต์
```
power-social-dashboard/
  ├─ app.py
  ├─ requirements.txt
  ├─ .env.example
  ├─ ingest/
  │   ├─ __init__.py
  │   ├─ youtube.py
  │   ├─ facebook.py
  │   └─ instagram.py
  ├─ utils/
  │   ├─ __init__.py
  │   └─ processing.py
  └─ data/
      ├─ sample_youtube.json
      ├─ sample_facebook.json
      └─ sample_instagram.json
```

## การติดตั้งและเริ่มต้นใช้งาน
1) สร้างไฟล์สภาพแวดล้อม
```
cp .env.example .env
```
แก้ไขค่าในไฟล์ `.env` ตามที่คุณมี (ใส่เฉพาะอันที่ต้องการใช้งานจริง):
- `YOUTUBE_API_KEY`
- `FACEBOOK_ACCESS_TOKEN`
- `INSTAGRAM_ACCESS_TOKEN`

2) ติดตั้งไลบรารี
```
pip install -r requirements.txt
```

3) รันแอป Streamlit
```
streamlit run app.py
```
จากนั้นเปิดลิงก์ที่ปรากฏในเทอร์มินัล

หากยังไม่มีคีย์/โทเคน คุณสามารถติ๊ก “ใช้ข้อมูลตัวอย่าง” ในแอปเพื่อดูหน้าตาแดชบอร์ดและฟีเจอร์ต่างๆ ได้ทันที

## การตั้งค่า API Key/Access Token (อย่างย่อ)
- YouTube Data API: สร้าง Project และ API Key จาก Google Cloud Console แล้วเปิดใช้ YouTube Data API v3
- Facebook/Instagram Graph API: ต้องมี Facebook App และขอสิทธิ์ที่เกี่ยวข้อง (เช่น pages_read_engagement, instagram_basic, instagram_manage_insights) พร้อม Access Token ที่ถูกต้อง

หมายเหตุ: การดึงข้อมูลแบบ Live จาก Facebook/Instagram มีข้อกำหนดสิทธิ์และขอบเขตกว้างขวาง โปรเจกต์นี้จึงมีโหมด “ตัวอย่าง” ให้ทดลองใช้งานได้ทันที หากต้องการใช้งานจริง โปรดเตรียม App และ Token ที่ถูกต้อง

## ข้อจำกัดและแนวทางต่อยอด
- โมดูล Facebook/Instagram ในโปรเจกต์นี้เป็นโครงร่างพร้อมจัดการข้อผิดพลาด แต่การดึงข้อมูลจริงขึ้นกับสิทธิ์ของ App และ Token
- สามารถเพิ่มมุมมอง/กราฟเพิ่มเติม เช่น Word Cloud, Hashtag Analysis, หรือ Sentiment (ไทย/อังกฤษ) เมื่อพร้อมเพิ่มโมเดลที่เหมาะสม
- หากต้องการใช้งานในองค์กร แนะนำให้เพิ่มงาน ETL/กำหนดเวลารวบรวมข้อมูล (cron) และฐานข้อมูลถาวร (เช่น PostgreSQL/BigQuery)