# 🚀 تثبيت TextLeaf عبر Docker - دليل سريع

## ⚡ التثبيت بأمر واحد

### على السيرفر (Hostinger VPS):

```bash
# 1. نسخ المشروع إلى السيرفر
scp -r /home/user/webapp root@your-server-ip:/tmp/textleaf

# 2. الاتصال بالسيرفر
ssh root@your-server-ip

# 3. نقل المشروع إلى المكان الصحيح
mv /tmp/textleaf /opt/textleaf
cd /opt/textleaf

# 4. تشغيل سكريبت التثبيت التلقائي
bash docker-deploy-auto.sh
```

**هذا كل شيء! 🎉**

---

## 🎯 الأوامر الأساسية

### بعد التثبيت:

```bash
cd /opt/textleaf

# تشغيل التطبيق
docker-compose up -d

# إيقاف التطبيق
docker-compose down

# عرض السجلات
docker-compose logs -f

# إعادة التشغيل
docker-compose restart

# التحقق من الحالة
docker-compose ps
```

---

## 📝 تعديل الإعدادات

```bash
# تعديل ملف البيئة
nano /opt/textleaf/.env

# إعادة التشغيل بعد التعديل
docker-compose restart
```

الإعدادات المهمة:
- `SECRET_KEY` - مفتاح سري قوي
- `APP_URL` - رابط موقعك
- `OXAPAY_API_KEY` - مفتاح OxaPay
- `OXAPAY_MERCHANT_ID` - معرف التاجر

---

## 🔒 إضافة SSL (Let's Encrypt)

```bash
# تثبيت Certbot
apt install -y certbot

# إيقاف Nginx مؤقتاً
cd /opt/textleaf
docker-compose stop nginx

# الحصول على الشهادة
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# نسخ الشهادات
mkdir -p /opt/textleaf/ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/textleaf/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/textleaf/ssl/

# تفعيل HTTPS في nginx.conf (أزل # من قسم HTTPS)
nano /opt/textleaf/nginx.conf

# إعادة تشغيل Nginx
docker-compose up -d nginx
```

---

## 🔥 Firewall (الجدار الناري)

```bash
# تثبيت UFW
apt install -y ufw

# السماح بالمنافذ الضرورية
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS

# تفعيل Firewall
ufw enable

# التحقق
ufw status
```

---

## 📊 المراقبة

```bash
# استخدام الموارد
docker stats

# حالة الـ containers
docker-compose ps

# السجلات المباشرة
docker-compose logs -f textleaf

# آخر 100 سطر من السجلات
docker-compose logs --tail=100
```

---

## 🔄 التحديثات

```bash
cd /opt/textleaf

# سحب آخر التغييرات
git pull

# إعادة البناء والتشغيل
docker-compose build
docker-compose up -d

# التحقق
docker-compose logs -f
```

---

## 🆘 استكشاف الأخطاء

### التطبيق لا يعمل:

```bash
# عرض السجلات
docker-compose logs textleaf

# إعادة التشغيل
docker-compose restart textleaf

# إعادة البناء
docker-compose build --no-cache
docker-compose up -d
```

### Port مشغول:

```bash
# معرفة ما يستخدم Port 80
lsof -i :80

# إيقاف الخدمة أو تغيير Port في docker-compose.yml
```

### نفاد المساحة:

```bash
# تنظيف Docker
docker system prune -a -f

# حذف الملفات القديمة
rm -rf /opt/textleaf/output/*.mp4
```

---

## 📞 الدعم

- **WhatsApp**: +963 958 917 677
- **Documentation**: `/opt/textleaf/DOCKER_DEPLOY.md`

---

## ✅ Checklist

قبل الإطلاق، تأكد من:

- [ ] تم تعديل `.env` بالإعدادات الصحيحة
- [ ] تم إضافة SSL certificate
- [ ] تم تفعيل Firewall
- [ ] تم اختبار التطبيق
- [ ] تم إعداد النسخ الاحتياطي التلقائي
- [ ] تم إعداد التجديد التلقائي لـ SSL

---

## 🎉 انتهى!

التطبيق يعمل على:
- **HTTP**: http://your-domain.com
- **HTTPS**: https://your-domain.com

**استمتع بتطبيقك! 🚀**
