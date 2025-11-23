# Skaters.com - Deployment Guide

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** November 23, 2025

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository>
cd skaters-python

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run development server
uvicorn app.main:app --reload --port 8000

# Visit: http://localhost:8000
```

---

## 📋 Prerequisites

- Python 3.9+
- SQLite (included) or PostgreSQL (production)
- Google Maps API key (for maps and photos)
- SMTP server (for emails - optional)

---

## ⚙️ Environment Configuration

### Required Variables:

```bash
# .env file

# Security (REQUIRED)
SECRET_KEY=<generate-with-command-below>
ENVIRONMENT=production  # or development
DEBUG=False  # True for development

# Database
DATABASE_URL=sqlite:///./skaters.db
# For PostgreSQL: postgresql://user:pass@localhost/skaters_db

# Google Maps API
GOOGLE_MAPS_API_KEY=your-api-key-here
```

### Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🗄️ Database Setup

### SQLite (Development):
```bash
# Database is created automatically
# Located at: skaters.db
```

### PostgreSQL (Production):
```bash
# 1. Create database
createdb skaters_db

# 2. Update .env
DATABASE_URL=postgresql://username:password@localhost/skaters_db

# 3. Run migrations (if using Alembic)
alembic upgrade head

# Or create tables directly
python -c "from app.database import engine, Base; Base.metadata.create_all(engine)"
```

---

## 🔐 Security Checklist

### Before Deployment:

- [ ] Set strong `SECRET_KEY` (32+ characters)
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Review user permissions
- [ ] Enable monitoring/logging

### Security Features Included:

- ✅ Password hashing (bcrypt)
- ✅ Session management
- ✅ CSRF protection ready
- ✅ XSS protection headers
- ✅ Clickjacking protection
- ✅ MIME sniffing protection
- ✅ Content Security Policy
- ✅ HTTPS enforcement (production)

---

## 🚀 Deployment Options

### Option 1: Traditional Server (Ubuntu/Debian)

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# 2. Clone repository
cd /var/www
git clone <repository> skaters
cd skaters

# 3. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit settings

# 5. Install Gunicorn
pip install gunicorn

# 6. Create systemd service
sudo nano /etc/systemd/system/skaters.service
```

**Service file (`/etc/systemd/system/skaters.service`):**
```ini
[Unit]
Description=Skaters.com FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/skaters
Environment="PATH=/var/www/skaters/venv/bin"
ExecStart=/var/www/skaters/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
# 7. Start service
sudo systemctl daemon-reload
sudo systemctl start skaters
sudo systemctl enable skaters

# 8. Configure Nginx
sudo nano /etc/nginx/sites-available/skaters
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name skaters.com www.skaters.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/skaters/app/static;
        expires 30d;
    }
}
```

```bash
# 9. Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/skaters /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 10. Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d skaters.com -d www.skaters.com
```

---

### Option 2: Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/skaters
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=skaters
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Deploy:**
```bash
docker-compose up -d
```

---

### Option 3: Cloud Platforms

#### Heroku:
```bash
# 1. Install Heroku CLI
# 2. Login
heroku login

# 3. Create app
heroku create skaters-com

# 4. Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# 5. Set environment variables
heroku config:set SECRET_KEY=<your-key>
heroku config:set ENVIRONMENT=production

# 6. Deploy
git push heroku main

# 7. Run migrations
heroku run alembic upgrade head
```

#### AWS Elastic Beanstalk:
```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize
eb init -p python-3.11 skaters-com

# 3. Create environment
eb create skaters-prod

# 4. Deploy
eb deploy
```

#### DigitalOcean App Platform:
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

---

## 📊 Monitoring & Logging

### Logs Location:
```
logs/
├── app.log      # All application logs
└── error.log    # Error logs only
```

### View Logs:
```bash
# Real-time
tail -f logs/app.log

# Errors only
tail -f logs/error.log

# Last 100 lines
tail -n 100 logs/app.log
```

### Log Rotation:
- Automatic rotation at 10MB
- 5 backup files kept
- Configurable in `app/logging_config.py`

---

## 🔧 Maintenance

### Database Backup:
```bash
# SQLite
cp skaters.db skaters_backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump skaters_db > backup_$(date +%Y%m%d).sql
```

### Update Application:
```bash
# 1. Pull latest code
git pull origin main

# 2. Update dependencies
pip install -r requirements.txt

# 3. Run migrations
alembic upgrade head

# 4. Restart service
sudo systemctl restart skaters
```

### Health Check:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"skaters.com"}
```

---

## 🐛 Troubleshooting

### Application won't start:
```bash
# Check logs
tail -f logs/app.log

# Check service status
sudo systemctl status skaters

# Check environment variables
printenv | grep SECRET_KEY
```

### Database connection errors:
```bash
# Test database connection
python -c "from app.database import engine; engine.connect()"

# Check DATABASE_URL
echo $DATABASE_URL
```

### Permission errors:
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/skaters

# Fix permissions
chmod -R 755 /var/www/skaters
```

---

## 📈 Performance Optimization

### Enable Caching:
```bash
# Install Redis
sudo apt install redis-server

# Update .env
REDIS_URL=redis://localhost:6379/0

# Install Python Redis
pip install redis aiocache
```

### Database Optimization:
```sql
-- Add indexes
CREATE INDEX idx_venues_city_state ON venues(city, state);
CREATE INDEX idx_venues_sport_type ON venues(sport_type);
CREATE INDEX idx_venues_rating ON venues(rating DESC);
```

### Static Files CDN:
- Upload `/app/static` to CDN
- Update `STATIC_URL` in settings

---

## 🔒 Security Best Practices

### 1. Regular Updates:
```bash
# Update dependencies
pip list --outdated
pip install -U <package>
```

### 2. Security Scanning:
```bash
# Install safety
pip install safety

# Check for vulnerabilities
safety check
```

### 3. SSL/TLS:
- Use Let's Encrypt for free SSL
- Force HTTPS redirects
- Enable HSTS headers (already configured)

### 4. Firewall:
```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

---

## 📞 Support

### Issues:
- GitHub Issues: <repository-url>/issues
- Email: support@skaters.com

### Documentation:
- API Docs: http://localhost:8000/docs
- Project Review: `PROJECT_REVIEW.md`
- Improvements: `IMPROVEMENTS_COMPLETED.md`

---

## 📝 License

[Your License Here]

---

**Deployed and maintained with ❤️**
