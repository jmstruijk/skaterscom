# Skaters.com - Professional Python Web Application

A comprehensive skating venue directory built with **Python FastAPI** for reliability, performance, and SEO optimization.

## 🚀 Why Python + FastAPI?

- **Reliability**: No framework quirks or routing issues
- **SEO Optimized**: Server-side rendering with Jinja2 templates
- **Performance**: FastAPI is one of the fastest Python frameworks
- **Type Safety**: Full Python type hints and Pydantic validation
- **Database**: SQLAlchemy ORM with PostgreSQL
- **Scalable**: Easy to deploy and scale

## 📁 Project Structure

```
skaters-python/
├── app/
│   ├── main.py              # Main application entry point
│   ├── models/              # Database models
│   │   └── venue.py         # Venue, User, Review models
│   ├── routes/              # API and page routes
│   │   ├── venues.py        # Venue pages
│   │   ├── search.py        # Search functionality
│   │   ├── auth.py          # Authentication
│   │   └── reviews.py       # Review system
│   ├── templates/           # HTML templates (Jinja2)
│   │   ├── base.html        # Base template
│   │   ├── index.html       # Homepage
│   │   └── venue_detail.html # Venue detail page
│   └── static/              # Static files
│       ├── css/             # Stylesheets
│       ├── js/              # JavaScript
│       └── images/          # Images
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Installation

### 1. Create Virtual Environment

```bash
cd /Users/johan/Projects/skaters-python
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Database

```bash
# Create PostgreSQL database
createdb skaters_db

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start Development Server

```bash
python -m app.main
# or
uvicorn app.main:app --reload --port 8000
```

Visit: **http://localhost:8000**

## 🎯 Features

### ✅ Implemented
- FastAPI application structure
- Database models (SQLAlchemy)
- Homepage with server-side rendering
- Responsive design (Tailwind CSS)
- SEO-optimized HTML templates
- Venue detail pages
- Professional header/footer

### 🚧 In Progress
- Database integration
- Search functionality
- User authentication
- Review system
- Admin panel
- Image uploads

### 📋 Planned
- Advanced filtering
- Geolocation search
- Email notifications
- Social features
- Mobile app API
- Analytics dashboard

## 🗄️ Database Schema

### Main Tables
- **venues** - Venue information
- **venue_photos** - Venue images
- **venue_amenities** - Facility features
- **venue_hours** - Operating hours
- **venue_pricing** - Admission/rental costs
- **users** - User accounts
- **reviews** - User reviews and ratings
- **saved_venues** - User saved venues

## 🔧 Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
ruff check app/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## 🚀 Deployment

### Production Server
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### With Nginx
```nginx
server {
    listen 80;
    server_name skaters.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/app/static;
    }
}
```

## 📊 Performance

- **Server-side rendering** for instant page loads
- **Database indexing** on key fields
- **Caching** with Redis (optional)
- **CDN** for static assets
- **Optimized images** with Pillow

## 🔒 Security

- **Password hashing** with bcrypt
- **JWT tokens** for authentication
- **SQL injection protection** via SQLAlchemy
- **XSS protection** in templates
- **CSRF tokens** on forms
- **Rate limiting** on API endpoints

## 📈 SEO Features

- Server-side rendered HTML
- Semantic HTML5 markup
- Meta tags and Open Graph
- XML sitemap generation
- Structured data (JSON-LD)
- Fast page load times
- Mobile-responsive design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file

## 📧 Contact

For questions or support, contact: support@skaters.com

---

**Built with ❤️ using Python, FastAPI, and modern web technologies**
