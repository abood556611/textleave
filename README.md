# TextLeaf - Match Cut Video Generator

مولد فيديوهات Match Cut احترافي يحاكي تقليب صفحات المجلات بسرعة.

## المميزات الرئيسية

- **توليد فيديوهات Match Cut**: فيديوهات واقعية تحاكي تقليب صفحات المجلات
- **تنوع بصري**: خلفيات ونصوص متنوعة لكل صفحة
- **تخصيص كامل**: تحكم بالمدة، FPS، والأبعاد
- **جودة عالية**: دعم 720p و 1080p
- **نظام اشتراكات**: خطط مجانية ومدفوعة

## المنطق الرياضي

### حسابات الفيديو
- **مدة الصفحة الواحدة**: 0.5 ثانية
- **عدد الصفحات**: `المدة الكلية ÷ 0.5`
- **مثال**: فيديو 10 ثواني = 20 صفحة

### تركيبة الصفحة
كل صفحة تحتوي على:
1. النص الرئيسي (مع تنويعات طفيفة في الموقع والحجم)
2. خلفية عشوائية من مكتبة الصور
3. نصوص ضبابية محيطة (Filler Text)
4. مستطيل تحديد بحواف مهتزة (Highlighter)

## التثبيت

### المتطلبات
- Python 3.8+
- pip
- FFmpeg (لتشغيل MoviePy)

### خطوات التثبيت

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd webapp
```

2. **إنشاء بيئة افتراضية**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows
```

3. **تثبيت المكتبات**
```bash
pip install -r requirements.txt
```

4. **تثبيت FFmpeg**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**MacOS:**
```bash
brew install ffmpeg
```

**Windows:**
قم بتحميل FFmpeg من الموقع الرسمي وإضافته إلى PATH

5. **إعداد الملفات البيئية**
```bash
cp .env.example .env
# قم بتعديل .env بالإعدادات المناسبة
```

6. **تشغيل التطبيق**
```bash
python app.py
```

التطبيق سيعمل على: http://localhost:5000

## البنية التقنية

```
webapp/
├── app.py                  # Flask application
├── config.py              # Configuration settings
├── image_generator.py     # Image generation engine
├── video_generator.py     # Video generation engine
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   ├── js/
│   │   └── app.js        # Frontend logic
│   ├── backgrounds/      # Background images
│   └── audio/            # Audio files
├── templates/
│   └── index.html        # Main template
├── uploads/              # Temporary uploads
└── output/               # Generated videos
```

## الاستخدام

### عبر الواجهة
1. افتح المتصفح على http://localhost:5000
2. أدخل النص الرئيسي
3. اختر المدة والإعدادات
4. اختياري: ارفع ملف صوتي
5. انقر "توليد الفيديو"
6. قم بتحميل الفيديو عند الانتهاء

### عبر API

**توليد فيديو:**
```bash
curl -X POST http://localhost:5000/api/generate \
  -F "main_text=النص الرئيسي" \
  -F "duration=10" \
  -F "fps=30" \
  -F "resolution=9:16" \
  -F "premium=false"
```

**متابعة التقدم:**
```bash
curl http://localhost:5000/api/progress/{video_id}
```

**تحميل الفيديو:**
```bash
curl -O http://localhost:5000/api/download/{video_id}
```

## الإعدادات

### config.py
- `PAGE_DURATION`: مدة عرض كل صفحة (افتراضي: 0.5 ثانية)
- `RESOLUTIONS`: الأبعاد المتاحة
- `POSITION_VARIANCE`: التنويع في موقع النص (افتراضي: ±5px)
- `SIZE_VARIANCE`: التنويع في حجم النص (افتراضي: ±2%)

## نموذج العمل

### المجاني
- علامة مائية
- دقة 720p
- جميع المدد والأبعاد

### الاشتراك الشهري ($5)
- بدون علامة مائية
- دقة 1080p
- خيار Green Screen
- أولوية المعالجة

### الاشتراك السنوي ($50)
- كل مميزات الشهري
- وفر $10 سنوياً
- دعم أولوية

## نشر على Hostinger

### المتطلبات
- VPS على Hostinger
- نظام Ubuntu/Debian
- اتصال SSH

### خطوات النشر

1. **الاتصال بالسيرفر**
```bash
ssh user@your-server-ip
```

2. **تحديث النظام**
```bash
sudo apt update && sudo apt upgrade -y
```

3. **تثبيت المتطلبات**
```bash
sudo apt install python3-pip python3-venv ffmpeg nginx -y
```

4. **نسخ المشروع**
```bash
cd /var/www
sudo git clone <repository-url> textleaf
cd textleaf
```

5. **إعداد البيئة**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

6. **إعداد Gunicorn**
```bash
sudo nano /etc/systemd/system/textleaf.service
```

محتوى الملف:
```ini
[Unit]
Description=TextLeaf Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/textleaf
Environment="PATH=/var/www/textleaf/venv/bin"
ExecStart=/var/www/textleaf/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

7. **إعداد Nginx**
```bash
sudo nano /etc/nginx/sites-available/textleaf
```

محتوى الملف:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /var/www/textleaf/static;
    }
}
```

8. **تفعيل الخدمات**
```bash
sudo ln -s /etc/nginx/sites-available/textleaf /etc/nginx/sites-enabled/
sudo systemctl start textleaf
sudo systemctl enable textleaf
sudo systemctl restart nginx
```

9. **إعداد SSL (اختياري)**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## الدعم

للدعم الفني، تواصل عبر واتساب:
+963 958 917 677

## الترخيص

جميع الحقوق محفوظة © 2024 TextLeaf
