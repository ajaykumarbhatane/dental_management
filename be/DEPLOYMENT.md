"""
Deployment Guide for Production

This document covers deploying the Dental Clinic Management System to production.
"""

# ============================================================================
# PRE-DEPLOYMENT CHECKLIST
# ============================================================================

## Code Review
- [ ] All tests passing
- [ ] No debug print statements
- [ ] No hardcoded secrets/passwords
- [ ] Code follows project standards
- [ ] Security vulnerabilities checked

## Environment Setup
- [ ] Production .env configured
- [ ] Database created and backed up
- [ ] Secret key generated (use django-insecure to generate)
- [ ] ALLOWED_HOSTS configured
- [ ] CORS origins configured

## Database
- [ ] PostgreSQL installed and running
- [ ] Database user created with least privileges
- [ ] Database backed up
- [ ] Migrations tested

## Static & Media
- [ ] S3 bucket created (if using AWS)
- [ ] Static files configured
- [ ] Media upload directory permissions set

## Security
- [ ] HTTPS/SSL configured
- [ ] Security headers configured
- [ ] CSRF enabled
- [ ] Password requirements set
- [ ] File upload validation in place


# ============================================================================
# DEPLOYMENT STEPS
# ============================================================================

## Step 1: Prepare Server

```bash
# Install system dependencies
sudo apt update && sudo apt upgrade
sudo apt install python3.9 python3-pip python3-venv
sudo apt install postgresql postgresql-contrib
sudo apt install redis-server
sudo apt install git

# Create deploy user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG sudo deploy
```

## Step 2: Clone Repository

```bash
cd /var/www/
sudo git clone <your-repo-url> dental-clinic
cd dental-clinic/be
sudo chown -R deploy:deploy /var/www/dental-clinic
```

## Step 3: Setup Virtual Environment

```bash
sudo -u deploy python3 -m venv venv
sudo -u deploy source venv/bin/activate
sudo -u deploy pip install --upgrade pip
sudo -u deploy pip install -r requirements.txt
sudo -u deploy pip install gunicorn
```

## Step 4: Configure Environment

```bash
# Copy and configure .env
sudo -u deploy cp .env.example .env
sudo -u deploy nano .env
```

Example production .env:
```
DEBUG=False
SECRET_KEY=<generate-secure-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=dental_clinic_db
DB_USER=dental_user
DB_PASSWORD=<secure-password>
DB_HOST=127.0.0.1
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/0
JWT_SECRET_KEY=<generate-secure-key>

CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

USE_S3=True
AWS_STORAGE_BUCKET_NAME=dental-clinic-media
AWS_S3_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
```

## Step 5: Setup PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE dental_clinic_db;

# Create user
CREATE USER dental_user WITH PASSWORD 'secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dental_clinic_db TO dental_user;

# Exit psql
\q
```

Test connection:
```bash
psql -U dental_user -d dental_clinic_db -h 127.0.0.1
```

## Step 6: Run Migrations

```bash
cd /var/www/dental-clinic/be
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Step 7: Configure Gunicorn

Create `/var/www/dental-clinic/be/gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
keepalive = 5
timeout = 30
accesslog = "/var/www/dental-clinic/be/logs/access.log"
errorlog = "/var/www/dental-clinic/be/logs/error.log"
loglevel = "info"
```

Create systemd service file `/etc/systemd/system/dental-clinic.service`:

```ini
[Unit]
Description=Dental Clinic Management System
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=deploy
Group=deploy
WorkingDirectory=/var/www/dental-clinic/be
Environment="PATH=/var/www/dental-clinic/be/venv/bin"
EnvironmentFile=/var/www/dental-clinic/be/.env
ExecStart=/var/www/dental-clinic/be/venv/bin/gunicorn \
    --config /var/www/dental-clinic/be/gunicorn_config.py \
    config.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dental-clinic
sudo systemctl start dental-clinic
sudo systemctl status dental-clinic
```

## Step 8: Configure Nginx

Create `/etc/nginx/sites-available/dental-clinic`:

```nginx
upstream dental_clinic {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/dental-clinic-access.log;
    error_log /var/log/nginx/dental-clinic-error.log;
    
    # Proxy settings
    location / {
        proxy_pass http://dental_clinic;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_redirect off;
    }
    
    # Static files
    location /static/ {
        alias /var/www/dental-clinic/be/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/dental-clinic/be/media/;
        expires 7d;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/dental-clinic /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 9: SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

## Step 10: Configure Firewall

```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

## Step 11: Setup Monitoring and Logging

Monitor service status:
```bash
sudo journalctl -u dental-clinic -f
tail -f /var/www/dental-clinic/be/logs/error.log
```


# ============================================================================
# POST-DEPLOYMENT VERIFICATION
# ============================================================================

## Health Checks

```bash
# Check service is running
sudo systemctl status dental-clinic

# Test API endpoint
curl -X GET https://yourdomain.com/api/docs/

# Check logs for errors
sudo journalctl -u dental-clinic -n 50

# Verify database connection
python manage.py dbshell
```

## Performance Baseline

```bash
# Check response times
curl -w "Total time: %{time_total}s\n" https://yourdomain.com/api/docs/

# Load test (optional)
# ab -n 1000 -c 10 https://yourdomain.com/api/docs/
```

## Security Verification

- [ ] HTTPS working
- [ ] Redirects HTTP to HTTPS
- [ ] Security headers present
- [ ] CORS properly configured
- [ ] Admin panel requires authentication


# ============================================================================
# CONTINUOUS DEPLOYMENT
# ============================================================================

## Automated Deployments

Create deployment script `/var/www/dental-clinic/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "Dental Clinic - Deployment Script"

cd /var/www/dental-clinic
git pull origin main

cd be
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart dental-clinic

echo "✅ Deployment completed successfully"
```

Make executable:
```bash
chmod +x /var/www/dental-clinic/deploy.sh
```


# ============================================================================
# BACKUP AND RECOVERY
# ============================================================================

## Database Backups

Create daily backup script `/usr/local/bin/backup-dental-clinic.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/dental-clinic"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump dental_clinic_db | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Backup media files
tar czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" /var/www/dental-clinic/be/media/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

Add to crontab:
```bash
0 2 * * * /usr/local/bin/backup-dental-clinic.sh
```

## Disaster Recovery

To restore from backup:

```bash
# Stop application
sudo systemctl stop dental-clinic

# Restore database
gunzip < /var/backups/dental-clinic/db_TIMESTAMP.sql.gz | psql dental_clinic_db

# Restore media files
tar xzf /var/backups/dental-clinic/media_TIMESTAMP.tar.gz -C /

# Start application
sudo systemctl start dental-clinic
```


# ============================================================================
# MONITORING AND ALERTS
# ============================================================================

### Key Metrics to Monitor

- CPU Usage
- Memory Usage
- Disk Space
- Database Connection Pool
- Redis Memory
- API Response Times
- Error Rates
- Failed Login Attempts

### Recommended Monitoring Tools

- Prometheus + Grafana
- DataDog
- New Relic
- Sentry (for error tracking)

### Scaling Considerations

For high-traffic scenarios:
- Horizontal scaling with load balancer (nginx or HAProxy)
- Database read replicas
- Cache layer optimization
- CDN for static files


---

For questions or issues, refer to:
- Django Deployment Documentation
- Gunicorn Documentation
- Nginx Documentation
- PostgreSQL Administration Guide
