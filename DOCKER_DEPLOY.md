# 🐳 دليل نشر TextLeaf عبر Docker على Hostinger

## المتطلبات الأساسية

- ✅ VPS من Hostinger (Ubuntu 20.04 أو أحدث)
- ✅ Docker و Docker Compose مثبتين
- ✅ اتصال SSH بالسيرفر
- ✅ اسم نطاق (Domain) موجه إلى السيرفر

---

## 🚀 التثبيت السريع (5 دقائق)

### الخطوة 1: الاتصال بالسيرفر

```bash
ssh root@your-server-ip
```

### الخطوة 2: تثبيت Docker و Docker Compose

```bash
# تحديث النظام
apt update && apt upgrade -y

# تثبيت المتطلبات الأساسية
apt install -y curl git

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# تثبيت Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# التحقق من التثبيت
docker --version
docker-compose --version
```

### الخطوة 3: نسخ المشروع

```bash
# إنشاء مجلد للمشروع
mkdir -p /opt/textleaf
cd /opt/textleaf

# نسخ الملفات (اختر إحدى الطريقتين)

# الطريقة 1: عبر Git
git clone <your-repository-url> .

# الطريقة 2: عبر SCP من جهازك المحلي
# على جهازك المحلي، نفذ:
# scp -r /home/user/webapp/* root@your-server-ip:/opt/textleaf/
```

### الخطوة 4: إعداد المتغيرات البيئية

```bash
# نسخ ملف البيئة
cp .env.docker .env

# تعديل الملف بمحرر nano
nano .env
```

عدّل المتغيرات التالية:

```env
FLASK_ENV=production
SECRET_KEY=اكتب-مفتاح-سري-قوي-هنا-32-حرف-على-الأقل
APP_URL=https://textleaf.com
OXAPAY_API_KEY=مفتاح-oxapay-الخاص-بك
OXAPAY_MERCHANT_ID=معرف-التاجر-الخاص-بك
WHATSAPP_NUMBER=+963958917677
```

احفظ بـ `Ctrl+O` ثم `Enter`، واخرج بـ `Ctrl+X`

### الخطوة 5: بناء وتشغيل Docker

```bash
# بناء الصورة
docker-compose build

# تشغيل التطبيق
docker-compose up -d

# التحقق من الحالة
docker-compose ps
docker-compose logs -f textleaf
```

### الخطوة 6: اختبار التطبيق

```bash
# اختبار محلي
curl http://localhost:8000/

# اختبار API
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"duration": 10}'
```

يجب أن تحصل على استجابة JSON!

---

## 🌐 إعداد اسم النطاق والـ SSL

### الخطوة 1: تحديث nginx.conf

```bash
nano nginx.conf
```

في قسم HTTPS، عدّل `server_name`:

```nginx
server_name your-domain.com www.your-domain.com;
```

### الخطوة 2: الحصول على شهادة SSL (Let's Encrypt)

```bash
# تثبيت Certbot
apt install -y certbot

# إيقاف Nginx مؤقتاً
docker-compose stop nginx

# الحصول على الشهادة
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# نسخ الشهادات لـ Docker
mkdir -p ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/

# إعادة تشغيل Nginx
docker-compose up -d nginx
```

### الخطوة 3: تفعيل HTTPS في nginx.conf

```bash
nano nginx.conf
```

أزل التعليق (`#`) من قسم HTTPS server، ثم:

```bash
docker-compose restart nginx
```

---

## 📋 أوامر إدارة Docker المفيدة

### إدارة الخدمات

```bash
# تشغيل جميع الخدمات
docker-compose up -d

# إيقاف جميع الخدمات
docker-compose down

# إعادة تشغيل خدمة محددة
docker-compose restart textleaf

# إعادة بناء الصورة بعد تعديل الكود
docker-compose build --no-cache
docker-compose up -d
```

### عرض السجلات (Logs)

```bash
# جميع السجلات
docker-compose logs

# سجلات خدمة محددة
docker-compose logs textleaf
docker-compose logs nginx

# متابعة السجلات في الوقت الفعلي
docker-compose logs -f

# آخر 100 سطر
docker-compose logs --tail=100
```

### حالة الخدمات

```bash
# حالة الـ containers
docker-compose ps

# استخدام الموارد
docker stats

# فحص صحة الـ container
docker inspect textleaf-app | grep -A 10 Health
```

### الدخول إلى الـ Container

```bash
# فتح shell داخل الـ container
docker-compose exec textleaf bash

# تشغيل أمر معين
docker-compose exec textleaf python test.py
```

---

## 🔧 استكشاف الأخطاء

### المشكلة: Container لا يعمل

```bash
# عرض السجلات للبحث عن الأخطاء
docker-compose logs textleaf

# إعادة تشغيل
docker-compose restart textleaf
```

### المشكلة: خطأ في الصلاحيات

```bash
# إصلاح صلاحيات المجلدات
chmod -R 755 uploads output static
chown -R 1000:1000 uploads output
```

### المشكلة: Port مستخدم بالفعل

```bash
# إيقاف الخدمة التي تستخدم Port 80 أو 8000
lsof -i :80
lsof -i :8000

# أو تغيير Port في docker-compose.yml
nano docker-compose.yml
# غيّر "80:80" إلى "8080:80" مثلاً
```

### المشكلة: نفاد مساحة القرص

```bash
# حذف الـ containers والصور غير المستخدمة
docker system prune -a

# حذف الـ volumes غير المستخدمة
docker volume prune
```

### المشكلة: خطأ في FFmpeg

```bash
# التحقق من تثبيت FFmpeg داخل الـ container
docker-compose exec textleaf ffmpeg -version
```

---

## 📊 المراقبة والأداء

### مراقبة الموارد

```bash
# استخدام CPU والذاكرة
docker stats

# حجم الـ containers والصور
docker system df
```

### النسخ الاحتياطي

```bash
# نسخ احتياطي لقاعدة البيانات
docker-compose exec textleaf cp textleaf.db /app/output/backup.db

# نسخ احتياطي للملفات المولدة
tar -czf backup-$(date +%Y%m%d).tar.gz output/ uploads/

# نقل النسخة الاحتياطية
scp backup-*.tar.gz user@backup-server:/backups/
```

---

## 🔄 التحديثات

### تحديث الكود

```bash
cd /opt/textleaf

# سحب آخر التغييرات
git pull

# إعادة بناء وتشغيل
docker-compose build
docker-compose up -d

# التحقق من السجلات
docker-compose logs -f textleaf
```

---

## 🔒 الأمان

### إعداد Firewall

```bash
# تثبيت UFW
apt install -y ufw

# السماح بـ SSH
ufw allow 22/tcp

# السماح بـ HTTP و HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# تفعيل Firewall
ufw enable

# التحقق من الحالة
ufw status
```

### تحديث الشهادات تلقائياً

```bash
# إضافة cron job للتجديد التلقائي
crontab -e

# أضف السطر التالي:
0 3 * * * certbot renew --quiet && docker-compose restart nginx
```

---

## 📈 التوسع (Scaling)

### زيادة عدد Workers

عدّل `docker-compose.yml`:

```yaml
services:
  textleaf:
    # ...
    command: gunicorn --bind 0.0.0.0:8000 --workers 8 --timeout 300 app:app
```

### إضافة Load Balancer

إذا احتجت لتشغيل عدة instances:

```yaml
services:
  textleaf:
    # ...
    deploy:
      replicas: 3
```

---

## ⚡ أوامر التثبيت الكاملة (نسخ ولصق)

```bash
#!/bin/bash
# TextLeaf Docker Deployment Script

# الخطوة 1: تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# الخطوة 2: تثبيت Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# الخطوة 3: إنشاء مجلد المشروع
mkdir -p /opt/textleaf
cd /opt/textleaf

# الخطوة 4: نسخ الملفات (استبدل بمسار repository الخاص بك)
# git clone <your-repo-url> .

# الخطوة 5: إعداد البيئة
cp .env.docker .env
echo "⚠️  لا تنسى تعديل ملف .env بإعداداتك!"

# الخطوة 6: بناء وتشغيل
docker-compose build
docker-compose up -d

# الخطوة 7: التحقق
docker-compose ps
docker-compose logs -f

echo "✅ تم! التطبيق يعمل على http://your-server-ip:80"
```

---

## 📞 الدعم

إذا واجهت أي مشاكل:

- **WhatsApp**: +963 958 917 677
- **GitHub Issues**: افتح issue في المستودع
- **السجلات**: أرسل نتيجة `docker-compose logs`

---

## 🎉 الخلاصة

تطبيق TextLeaf الآن:
- ✅ يعمل في Docker containers معزولة
- ✅ سهل النشر والإدارة
- ✅ قابل للتوسع (Scalable)
- ✅ محمي بـ Nginx و SSL
- ✅ جاهز للإنتاج!

**استمتع بنشر تطبيقك! 🚀**
