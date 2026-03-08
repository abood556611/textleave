# دليل التثبيت السريع - TextLeaf

## المتطلبات الأساسية

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python وأدوات البناء
sudo apt install python3 python3-pip python3-venv -y

# تثبيت FFmpeg (ضروري لـ MoviePy)
sudo apt install ffmpeg -y

# التحقق من التثبيت
python3 --version
ffmpeg -version
```

## التثبيت المحلي

```bash
# 1. الانتقال إلى مجلد المشروع
cd /home/user/webapp

# 2. إنشاء بيئة افتراضية
python3 -m venv venv

# 3. تفعيل البيئة الافتراضية
source venv/bin/activate

# 4. تثبيت المكتبات
pip install --upgrade pip
pip install -r requirements.txt

# 5. إعداد ملف البيئة
cp .env.example .env
# قم بتعديل .env بالإعدادات المناسبة

# 6. اختبار التطبيق
python test.py

# 7. تشغيل التطبيق
python app.py
```

التطبيق سيعمل على: http://localhost:5000

## التثبيت على الإنتاج (Hostinger)

### الطريقة الأوتوماتيكية

```bash
# 1. رفع الملفات إلى السيرفر
scp -r /home/user/webapp user@your-server:/tmp/

# 2. الاتصال بالسيرفر
ssh user@your-server

# 3. نقل المشروع
sudo mv /tmp/webapp /var/www/textleaf
cd /var/www/textleaf

# 4. تشغيل سكريبت النشر
sudo bash deploy.sh
```

### الطريقة اليدوية

```bash
# 1. الاتصال بالسيرفر
ssh user@your-server

# 2. تثبيت المتطلبات
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv ffmpeg nginx git -y

# 3. نسخ المشروع
cd /var/www
sudo git clone <repository-url> textleaf
cd textleaf

# 4. إعداد البيئة
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 5. إعداد Gunicorn Service
sudo nano /etc/systemd/system/textleaf.service
```

أضف المحتوى التالي:

```ini
[Unit]
Description=TextLeaf Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/textleaf
Environment="PATH=/var/www/textleaf/venv/bin"
ExecStart=/var/www/textleaf/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 --timeout 300 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# 6. إعداد Nginx
sudo nano /etc/nginx/sites-available/textleaf
```

أضف المحتوى التالي:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    location /static {
        alias /var/www/textleaf/static;
        expires 30d;
    }
}
```

```bash
# 7. تفعيل الموقع
sudo ln -s /etc/nginx/sites-available/textleaf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 8. ضبط الصلاحيات
sudo chown -R www-data:www-data /var/www/textleaf
sudo chmod -R 755 /var/www/textleaf

# 9. تشغيل الخدمات
sudo systemctl daemon-reload
sudo systemctl enable textleaf
sudo systemctl start textleaf
sudo systemctl restart nginx

# 10. التحقق من الحالة
sudo systemctl status textleaf
sudo systemctl status nginx
```

### إضافة SSL (اختياري لكن موصى به)

```bash
# تثبيت Certbot
sudo apt install certbot python3-certbot-nginx -y

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# التجديد التلقائي
sudo certbot renew --dry-run
```

## إدارة التطبيق

### عرض السجلات

```bash
# سجلات التطبيق
sudo journalctl -u textleaf -f

# سجلات Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### إعادة التشغيل

```bash
# إعادة تشغيل التطبيق
sudo systemctl restart textleaf

# إعادة تشغيل Nginx
sudo systemctl restart nginx
```

### تحديث التطبيق

```bash
cd /var/www/textleaf
sudo git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart textleaf
```

## استكشاف الأخطاء

### التطبيق لا يعمل

```bash
# التحقق من الحالة
sudo systemctl status textleaf

# عرض الأخطاء
sudo journalctl -u textleaf -n 50

# التحقق من المنافذ
sudo netstat -tlnp | grep 8000
```

### مشاكل FFmpeg

```bash
# التحقق من التثبيت
which ffmpeg
ffmpeg -version

# إعادة التثبيت
sudo apt remove ffmpeg -y
sudo apt install ffmpeg -y
```

### مشاكل الصلاحيات

```bash
# إصلاح الصلاحيات
sudo chown -R www-data:www-data /var/www/textleaf
sudo chmod -R 755 /var/www/textleaf
sudo chmod -R 777 /var/www/textleaf/uploads
sudo chmod -R 777 /var/www/textleaf/output
```

## المتغيرات البيئية (.env)

```bash
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=output
MAX_CONTENT_LENGTH=52428800
OXAPAY_API_KEY=your-oxapay-api-key
OXAPAY_MERCHANT_ID=your-merchant-id
WHATSAPP_NUMBER=+963958917677
APP_URL=https://your-domain.com
```

## الدعم

للمساعدة، تواصل عبر:
- WhatsApp: +963 958 917 677
- الموقع: https://textleaf.com (قريباً)
