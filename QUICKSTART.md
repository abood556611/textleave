# 🚀 دليل البدء السريع - TextLeaf

## ⚡ تشغيل التطبيق محلياً (5 دقائق)

### الخطوة 1: تثبيت المتطلبات

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip ffmpeg -y

# macOS
brew install python3 ffmpeg

# Windows
# قم بتثبيت Python من python.org
# قم بتثبيت FFmpeg من ffmpeg.org
```

### الخطوة 2: إعداد المشروع

```bash
# انتقل إلى مجلد المشروع
cd /home/user/webapp

# أنشئ بيئة افتراضية
python3 -m venv venv

# فعّل البيئة الافتراضية
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# ثبت المكتبات
pip install Flask Pillow moviepy requests python-dotenv
```

### الخطوة 3: إعداد الإعدادات

```bash
# أنسخ ملف البيئة
cp .env.example .env

# لا حاجة لتعديل شيء للتجربة المحلية!
```

### الخطوة 4: تشغيل التطبيق

```bash
python app.py
```

🎉 **التطبيق يعمل الآن على:** http://localhost:5000

---

## 🧪 اختبار التطبيق

```bash
# تشغيل الاختبارات
python test.py
```

---

## 📦 هيكل المشروع

```
webapp/
├── 🐍 Backend
│   ├── app.py              # Flask application
│   ├── config.py           # الإعدادات
│   ├── image_generator.py  # محرك الصور
│   ├── video_generator.py  # محرك الفيديو
│   ├── oxapay_service.py   # نظام الدفع
│   └── database.py         # قاعدة البيانات
│
├── 🎨 Frontend
│   ├── templates/
│   │   ├── index.html      # الصفحة الرئيسية
│   │   ├── 404.html        # خطأ 404
│   │   └── 500.html        # خطأ 500
│   └── static/
│       ├── css/style.css   # التصميم
│       ├── js/app.js       # المنطق
│       ├── backgrounds/    # صور الخلفيات
│       └── audio/          # ملفات الصوت
│
├── 📚 Documentation
│   ├── README.md           # الدليل الرئيسي
│   ├── API.md              # توثيق API
│   ├── INSTALL.md          # دليل التثبيت
│   └── PROJECT_SUMMARY.md  # ملخص المشروع
│
├── 🔧 Configuration
│   ├── requirements.txt    # المكتبات المطلوبة
│   ├── .env.example        # نموذج البيئة
│   ├── .gitignore          # ملفات مستبعدة
│   └── deploy.sh           # سكريبت النشر
│
└── 📁 Data
    ├── uploads/            # رفع الملفات
    └── output/             # الفيديوهات المولدة
```

---

## 🎬 كيفية استخدام التطبيق

### 1. توليد فيديو بسيط

1. افتح http://localhost:5000
2. اكتب نصك في حقل "النص الرئيسي"
3. اختر المدة (5، 10، أو 15 ثانية)
4. اختر FPS (30 أو 60)
5. اختر الأبعاد (9:16 للفيديو العمودي)
6. انقر "توليد الفيديو"
7. انتظر حتى ينتهي (شاهد شريط التقدم)
8. حمل الفيديو!

### 2. توليد فيديو مع صوت

1. نفس الخطوات أعلاه
2. قبل "توليد الفيديو"، ارفع ملف صوتي (MP3، WAV، إلخ)
3. الصوت سيتكرر تلقائياً ليتناسب مع طول الفيديو

### 3. توليد فيديو Premium (بدون علامة مائية)

1. فعّل مفتاح "وضع Premium"
2. أكمل باقي الخطوات
3. سيكون الفيديو بدقة 1080p وبدون علامة مائية

---

## 🔌 استخدام API

### مثال Python

```python
import requests
import time

# 1. توليد الفيديو
response = requests.post('http://localhost:5000/api/generate', data={
    'main_text': 'مرحباً بالعالم!',
    'duration': 10,
    'fps': 30,
    'resolution': '9:16',
    'premium': 'false'
})

video_id = response.json()['video_id']
print(f"Video ID: {video_id}")

# 2. متابعة التقدم
while True:
    progress = requests.get(f'http://localhost:5000/api/progress/{video_id}').json()
    print(f"{progress['progress']}% - {progress['status']}")
    
    if progress['status'] == 'Complete!':
        break
    
    time.sleep(2)

# 3. تحميل الفيديو
video = requests.get(f'http://localhost:5000/api/download/{video_id}')
with open('my_video.mp4', 'wb') as f:
    f.write(video.content)

print("تم تحميل الفيديو بنجاح!")
```

### مثال cURL

```bash
# توليد فيديو
curl -X POST http://localhost:5000/api/generate \
  -F "main_text=Hello World" \
  -F "duration=10" \
  -F "fps=30" \
  -F "resolution=9:16" \
  -F "premium=false"

# الحصول على التقدم (استبدل VIDEO_ID)
curl http://localhost:5000/api/progress/VIDEO_ID

# تحميل الفيديو
curl -O http://localhost:5000/api/download/VIDEO_ID
```

---

## 🚀 النشر على Hostinger

### الطريقة السريعة

```bash
# 1. رفع الملفات
scp -r /home/user/webapp user@your-server:/tmp/

# 2. الاتصال بالسيرفر
ssh user@your-server

# 3. تشغيل سكريبت النشر
sudo mv /tmp/webapp /var/www/textleaf
cd /var/www/textleaf
sudo bash deploy.sh
```

### ملاحظات مهمة للنشر

1. **قبل النشر:**
   - غيّر `DOMAIN` في `deploy.sh`
   - غيّر `SECRET_KEY` في `.env`
   - أضف مفاتيح OxaPay للدفع

2. **بعد النشر:**
   - ثبت شهادة SSL
   - فعّل Firewall
   - راقب السجلات

---

## 🛠️ استكشاف الأخطاء

### المشكلة: "No module named 'moviepy'"

```bash
pip install moviepy
```

### المشكلة: "FFmpeg not found"

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### المشكلة: التطبيق لا يعمل

```bash
# تحقق من السجلات
python app.py

# أو في الإنتاج
sudo journalctl -u textleaf -f
```

### المشكلة: خطأ في توليد الفيديو

1. تأكد من تثبيت FFmpeg
2. تأكد من وجود مساحة كافية
3. تحقق من صلاحيات المجلدات

---

## 📞 الدعم

**لديك سؤال؟**

- 💬 WhatsApp: +963 958 917 677
- 📧 Email: support@textleaf.com
- 📖 التوثيق: اقرأ API.md و INSTALL.md

---

## 🎯 نصائح للاستخدام الأمثل

### للحصول على أفضل النتائج:

1. **النص الرئيسي:**
   - استخدم نصاً قصيراً (2-5 كلمات)
   - تجنب النصوص الطويلة جداً

2. **المدة:**
   - 5 ثواني: للنصوص القصيرة
   - 10 ثواني: الأفضل للاستخدام العام
   - 15 ثانية: للتأثير الدرامي

3. **FPS:**
   - 30 FPS: استخدام عادي، حجم أصغر
   - 60 FPS: حركة أكثر سلاسة، حجم أكبر

4. **الأبعاد:**
   - 9:16: Instagram Stories, TikTok
   - 16:9: YouTube, Facebook
   - 1:1: Instagram Feed

5. **الصوت:**
   - استخدم ملفات MP3 لأفضل توافق
   - تأكد من أن الصوت ليس طويلاً جداً
   - الصوت سيتكرر تلقائياً

---

## ✨ ابدأ الآن!

```bash
cd /home/user/webapp
source venv/bin/activate
python app.py
```

**افتح متصفحك:** http://localhost:5000

**استمتع بإنشاء فيديوهات Match Cut رائعة! 🎬✨**
