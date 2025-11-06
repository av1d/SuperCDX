# Flask Wayback CDX - Deployment & Migration Guide

## Complete File Listing

This Flask application consists of the following files:

### Core Application Files
1. **app.py** - Main Flask application with all routes and logic
2. **requirements.txt** - Python dependencies (Flask, requests)
3. **README.md** - User documentation

### Template Files (templates/)
4. **base.html** - Base template with common HTML structure
5. **index.html** - Home page with search form and intro
6. **interface.html** - Error page template
7. **results.html** - Search results display page
8. **help.html** - Help documentation page
9. **slow_down.html** - Anti-bot page with 15-second timer

### Static Files (static/)
10. **static/css/style.css** - Main stylesheet
11. **static/js/no-bs-tooltips.js** - Tooltip functionality

### Assets Required (user must provide)
12. **static/images/logo.png** - Your site logo
13. **static/images/favicon.png** - Favicon
14. **static/images/memphis.png** - Background pattern for help page
15. **static/images/quickstart.png** - Screenshot for help page

## Setup Instructions

### 1. Create Directory Structure

```bash
mkdir flask-wayback-cdx
cd flask-wayback-cdx

# Create subdirectories
mkdir -p templates
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p logs
```

### 2. Copy Files to Correct Locations

Place each file in its appropriate directory:

```
flask-wayback-cdx/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── interface.html
│   ├── results.html
│   ├── help.html
│   └── slow_down.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── no-bs-tooltips.js
    └── images/
        ├── logo.png
        ├── favicon.png
        ├── memphis.png
        └── quickstart.png
```

### 3. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Secret Key (Important for Production!)

```bash
# Generate a secure random key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Set it as environment variable
export SECRET_KEY='your-generated-key-here'
```

Or edit app.py and replace the default secret key.

### 5. Run the Application

**Development mode:**
```bash
python app.py
```
Visit: http://localhost:5000

**Production mode with Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Key Differences from PHP Version

### Removed Features
- ✗ News feed system (news.json)
- ✗ Database session tracking (SQLite)
- ✗ User count statistics
- ✗ Database logging

### Added Features
- ✓ Simple query logging to logs/queries.txt
- ✓ Flask session-based anti-bot protection
- ✓ Simplified deployment structure

### Preserved Features
- ✓ All search functionality and logic
- ✓ CDX API integration
- ✓ URL processing and validation
- ✓ Search term parsing (quoted phrases, etc.)
- ✓ Result filtering and display
- ✓ Client-side export to text file
- ✓ Share functionality (copy URL)
- ✓ Tooltip system
- ✓ Anti-bot timer page
- ✓ Help documentation

## Migration Notes

### Sessions
PHP's `$_SESSION` → Flask's `session` object
- Anti-bot check now uses Flask sessions
- No database storage needed

### Routes
- `index.php` → `/` route in Flask
- `search.php` → `/search` route in Flask
- `help.php` → `/help` route in Flask
- `interface.php` → Integrated into templates as `interface.html`

### Templates
PHP includes → Jinja2 templates
- `<?php include('file.php'); ?>` → `{% include 'file.html' %}`
- `<?php echo $var; ?>` → `{{ var }}`

### HTTP Requests
PHP cURL → Python requests library
- Same timeout handling (120 seconds)
- Same error status code checking
- Same JSON parsing

### Query Logging
Instead of database logging, queries are appended to `logs/queries.txt`:
```python
def log_query(url):
    with open('logs/queries.txt', 'a') as f:
        f.write(f"{url}\n")
```

## Production Deployment Checklist

- [ ] Set unique SECRET_KEY environment variable
- [ ] Set Flask environment to production: `export FLASK_ENV=production`
- [ ] Use a production WSGI server (Gunicorn, uWSGI)
- [ ] Set up reverse proxy (Nginx, Apache)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up log rotation for logs/queries.txt
- [ ] Add your logo, favicon, and images to static/images/
- [ ] Customize CSS in static/css/style.css
- [ ] Test all routes: /, /search, /help, /slow_down
- [ ] Test search with various query patterns
- [ ] Test export functionality
- [ ] Test share (copy URL) functionality

## Troubleshooting

### "No such file or directory: logs/queries.txt"
The logs directory is auto-created. If you see this error, manually create:
```bash
mkdir logs
```

### Templates not found
Ensure all .html files are in the `templates/` directory.

### Static files not loading
Ensure static files are in the correct subdirectories under `static/`.

### CDX API timeouts
This is normal behavior - the Wayback Machine API can be slow. The 120-second timeout is intentional.

## Testing

Test each route:
```bash
# Home page
curl http://localhost:5000/

# Search (should redirect first time due to anti-bot)
curl -c cookies.txt http://localhost:5000/

# Search with session
curl -b cookies.txt "http://localhost:5000/search?url=example.com"

# Help page
curl http://localhost:5000/help
```

## License & Credits

This is a Flask port of the original PHP Wayback CDX search engine.
The core logic, algorithms, and UI design are preserved from the original production at [superscape.org](https://superscape.org).
