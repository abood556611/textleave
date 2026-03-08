#!/bin/bash

################################################################################
# TextLeaf - Docker Deployment Script for Hostinger VPS
# This script automates the entire deployment process
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="textleaf"
PROJECT_DIR="/opt/$PROJECT_NAME"
DOMAIN="your-domain.com"  # Change this!
EMAIL="your-email@example.com"  # Change this for SSL

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "هذا السكريبت يجب أن يعمل بصلاحيات root"
        echo "استخدم: sudo bash docker-deploy-auto.sh"
        exit 1
    fi
}

################################################################################
# Main Installation Steps
################################################################################

print_header "🚀 TextLeaf - Docker Deployment"
echo "سيتم تثبيت التطبيق على: $PROJECT_DIR"
echo "اسم النطاق: $DOMAIN"
echo ""
read -p "هل تريد المتابعة؟ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

check_root

# Step 1: Update system
print_header "[1/10] تحديث النظام"
apt update && apt upgrade -y
print_success "تم تحديث النظام"

# Step 2: Install dependencies
print_header "[2/10] تثبيت المتطلبات الأساسية"
apt install -y curl git apt-transport-https ca-certificates software-properties-common
print_success "تم تثبيت المتطلبات"

# Step 3: Install Docker
print_header "[3/10] تثبيت Docker"
if command -v docker &> /dev/null; then
    print_warning "Docker مثبت بالفعل"
    docker --version
else
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    print_success "تم تثبيت Docker"
fi

# Step 4: Install Docker Compose
print_header "[4/10] تثبيت Docker Compose"
if command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose مثبت بالفعل"
    docker-compose --version
else
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_success "تم تثبيت Docker Compose"
fi

# Step 5: Create project directory
print_header "[5/10] إعداد مجلد المشروع"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Check if files already exist
if [ -f "docker-compose.yml" ]; then
    print_warning "المشروع موجود بالفعل. سيتم تحديثه."
    docker-compose down 2>/dev/null || true
else
    print_success "تم إنشاء مجلد المشروع: $PROJECT_DIR"
fi

# Step 6: Copy/Clone files
print_header "[6/10] نسخ ملفات المشروع"
print_warning "يجب نسخ ملفات المشروع إلى $PROJECT_DIR"
print_warning "إذا كانت الملفات غير موجودة، استخدم:"
echo "  scp -r /path/to/webapp/* root@server:$PROJECT_DIR/"
echo "  أو"
echo "  git clone <repository-url> $PROJECT_DIR"
echo ""
read -p "هل الملفات موجودة في $PROJECT_DIR؟ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "قم بنسخ الملفات أولاً ثم أعد تشغيل السكريبت"
    exit 1
fi

# Step 7: Setup environment
print_header "[7/10] إعداد المتغيرات البيئية"
if [ ! -f ".env" ]; then
    if [ -f ".env.docker" ]; then
        cp .env.docker .env
        print_success "تم نسخ .env من .env.docker"
    else
        print_warning "ملف .env غير موجود. سيتم إنشاء ملف افتراضي"
        cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
APP_URL=https://$DOMAIN
OXAPAY_API_KEY=
OXAPAY_MERCHANT_ID=
WHATSAPP_NUMBER=+963958917677
MAX_CONTENT_LENGTH=52428800
EOF
    fi
    print_warning "⚠️  لا تنسى تعديل ملف .env بإعداداتك الخاصة!"
    echo "استخدم: nano .env"
else
    print_success "ملف .env موجود بالفعل"
fi

# Step 8: Create necessary directories
print_header "[8/10] إنشاء المجلدات المطلوبة"
mkdir -p uploads output static/backgrounds static/audio ssl
chmod -R 755 uploads output static
print_success "تم إنشاء المجلدات"

# Step 9: Build and start containers
print_header "[9/10] بناء وتشغيل Docker Containers"
print_warning "هذه الخطوة قد تستغرق عدة دقائق..."

docker-compose build
print_success "تم بناء الصور"

docker-compose up -d
print_success "تم تشغيل الـ containers"

# Wait for services to start
echo "انتظار بدء الخدمات..."
sleep 10

# Step 10: Verify installation
print_header "[10/10] التحقق من التثبيت"

# Check container status
if docker-compose ps | grep -q "Up"; then
    print_success "الـ containers تعمل بنجاح"
    docker-compose ps
else
    print_error "هناك مشكلة في الـ containers"
    docker-compose logs --tail=50
    exit 1
fi

# Test application
if curl -s http://localhost:8000/ > /dev/null; then
    print_success "التطبيق يستجيب بنجاح"
else
    print_warning "التطبيق لا يستجيب بعد، قد يحتاج وقتاً إضافياً"
fi

################################################################################
# Post-Installation Instructions
################################################################################

print_header "✅ تم التثبيت بنجاح!"

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  التطبيق يعمل الآن!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "📍 روابط الوصول:"
echo "   - المحلي: http://localhost:8000"
echo "   - الخارجي: http://$(curl -s ifconfig.me):80"
echo ""

echo "🔧 الخطوات التالية:"
echo ""
echo "1️⃣  تعديل إعدادات التطبيق:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2️⃣  إعداد SSL (اختياري لكن موصى به):"
echo "   # تثبيت Certbot"
echo "   apt install -y certbot"
echo "   # إيقاف Nginx مؤقتاً"
echo "   docker-compose stop nginx"
echo "   # الحصول على الشهادة"
echo "   certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN"
echo "   # نسخ الشهادات"
echo "   cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $PROJECT_DIR/ssl/"
echo "   cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $PROJECT_DIR/ssl/"
echo "   # تفعيل HTTPS في nginx.conf وإعادة التشغيل"
echo "   nano $PROJECT_DIR/nginx.conf"
echo "   docker-compose up -d nginx"
echo ""
echo "3️⃣  إعداد Firewall:"
echo "   ufw allow 22/tcp"
echo "   ufw allow 80/tcp"
echo "   ufw allow 443/tcp"
echo "   ufw enable"
echo ""
echo "4️⃣  مراقبة السجلات:"
echo "   docker-compose logs -f"
echo ""
echo "5️⃣  إعادة التشغيل:"
echo "   docker-compose restart"
echo ""

echo "📚 للمزيد من المعلومات، راجع:"
echo "   $PROJECT_DIR/DOCKER_DEPLOY.md"
echo ""

echo -e "${YELLOW}⚠️  تذكير: لا تنسى تحديث الإعدادات في ملف .env${NC}"
echo ""

print_success "🎉 TextLeaf جاهز للاستخدام!"
echo ""
