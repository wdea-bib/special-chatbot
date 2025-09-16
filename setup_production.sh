#!/bin/bash

# Production Setup Script
# إعداد الإنتاج للشات بوت التعليمي

echo "🔧 إعداد البيئة للإنتاج"
echo "========================="

# إنشاء ملف gunicorn.conf.py للإنتاج
cat > gunicorn.conf.py << 'EOF'
# Gunicorn configuration file

bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Process naming
proc_name = "educational_chatbot"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
EOF

# إنشاء مجلد السجلات
mkdir -p logs

# إنشاء systemd service file
cat > educational_chatbot.service << 'EOF'
[Unit]
Description=Educational Chatbot FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/educational_chatbot
Environment="PATH=/path/to/educational_chatbot/venv/bin"
ExecStart=/path/to/educational_chatbot/venv/bin/gunicorn main:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# إنشاء nginx config
cat > nginx.conf << 'EOF'
server {
    listen 80;
    server_name your_domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Static files
    location /static/ {
        alias /path/to/educational_chatbot/static/;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }

    location /frontend/ {
        alias /path/to/educational_chatbot/frontend/;
        expires 1d;
    }

    # API endpoints
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# HTTPS configuration (after SSL certificate setup)
# server {
#     listen 443 ssl http2;
#     server_name your_domain.com;
#     
#     ssl_certificate /path/to/ssl/certificate.pem;
#     ssl_certificate_key /path/to/ssl/private.key;
#     
#     # Rest of configuration same as above
# }
EOF

echo "✅ تم إنشاء ملفات الإعداد للإنتاج"
echo ""
echo "📝 الخطوات التالية للإنتاج:"
echo "1. تعديل المسارات في الملفات المُنشأة"
echo "2. نسخ educational_chatbot.service إلى /etc/systemd/system/"
echo "3. تكوين nginx باستخدام nginx.conf"
echo "4. تثبيت SSL certificate"
echo "5. تشغيل الخدمة: systemctl start educational_chatbot"
