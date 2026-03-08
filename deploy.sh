#!/bin/bash

# TextLeaf Deployment Script for Hostinger VPS
# This script automates the deployment process

set -e

echo "====================================="
echo "TextLeaf Deployment Script"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="textleaf"
APP_DIR="/var/www/$APP_NAME"
DOMAIN="your-domain.com"  # Change this
EMAIL="your-email@example.com"  # Change this for SSL

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}Please run as root (use sudo)${NC}"
   exit 1
fi

echo -e "${GREEN}[1/9] Updating system packages...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}[2/9] Installing required packages...${NC}"
apt install -y python3-pip python3-venv ffmpeg nginx git

echo -e "${GREEN}[3/9] Creating application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

echo -e "${GREEN}[4/9] Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}[5/9] Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo -e "${GREEN}[6/9] Creating systemd service...${NC}"
cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=TextLeaf Video Generator Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 --timeout 300 app:app

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}[7/9] Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
    }

    location /output {
        alias $APP_DIR/output;
        expires 1h;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo -e "${GREEN}[8/9] Setting permissions...${NC}"
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

echo -e "${GREEN}[9/9] Starting services...${NC}"
systemctl daemon-reload
systemctl enable $APP_NAME
systemctl start $APP_NAME
systemctl restart nginx

echo ""
echo -e "${GREEN}====================================="
echo "Deployment Complete!"
echo "====================================="
echo ""
echo "Application is running on http://$DOMAIN"
echo ""
echo -e "${YELLOW}Optional: Install SSL certificate${NC}"
echo "Run these commands:"
echo "  apt install certbot python3-certbot-nginx -y"
echo "  certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --no-eff-email"
echo ""
echo "Check service status:"
echo "  systemctl status $APP_NAME"
echo ""
echo "View logs:"
echo "  journalctl -u $APP_NAME -f"
echo ""
