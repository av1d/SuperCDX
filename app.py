from flask import Flask, render_template, request, session, redirect, url_for
import requests
import time
import re
import os
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Global variables for sharing data between functions
timestamps = []
domain = ""
start_time = 0

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

def log_query(url):
    """Log search queries to logs/queries.txt"""
    try:
        with open('logs/queries.txt', 'a', encoding='utf-8') as f:
            f.write(f"{url}\n")
    except Exception as e:
        print(f"Error logging query: {e}")

@app.route('/')
def index():
    """Home page - includes anti-bot check"""
    # Anti-bot check
    if 'visited' not in session:
        session['visited'] = True
        return redirect(url_for('slow_down'))

    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/slow_down')
def slow_down():
    """Anti-bot page"""
    return render_template('slow_down.html')

@app.route('/help')
def help_page():
    """Help documentation page"""
    return render_template('help.html')

@app.route('/search')
def search():
    """Main search endpoint"""
    global timestamps, domain, start_time

    start_time = time.time()
    timestamps = []

    # Get parameters
    url_param = request.args.get('url', '')
    query_param = request.args.get('query', '')

    if not url_param:
        return render_template('interface.html', error="Please enter a URL to search.")

    # Log the query
    log_query(url_param)

    # Validate and process URL
    domain = process_url(url_param)
    if not domain:
        return render_template('interface.html', error="Invalid URL format.")

    # Build CDX API URL
    cdx_url = build_cdx_url(domain)

    # Fetch data from Wayback CDX API
    try:
        data = fetch_cdx_data(cdx_url)
    except Exception as e:
        return render_template('interface.html', error=str(e), domain=domain)

    if not data or len(data) == 0:
        return render_template('interface.html', 
                             error="No results found for this domain.",
                             domain=domain)

    # Parse results
    urls = parse_results(data)

    if not urls:
        return render_template('interface.html', 
                             error="No results found.",
                             domain=domain)

    # Process search terms if provided
    processed_search_terms = None
    if query_param:
        processed_search_terms = build_word_list(query_param)

    # Calculate execution time
    execution_time = time.time() - start_time

    # Build and return results
    return build_results_response(urls, processed_search_terms, execution_time)

def process_url(url):
    """Process and validate URL"""
    url = url.strip()

    # Remove protocol if present
    url = re.sub(r'^https?://', '', url)

    # Remove trailing slash
    url = url.rstrip('/')

    # Basic validation
    if not url or ' ' in url:
        return None

    return url

def build_cdx_url(domain):
    """Build Wayback CDX API URL"""
    base_url = "https://web.archive.org/cdx/search/cdx"
    params = f"?url={quote(domain)}/*&output=json&fl=timestamp,original,statuscode&filter=statuscode:200&collapse=urlkey"
    return base_url + params

def fetch_cdx_data(cdx_url):
    """Fetch data from Wayback CDX API"""
    try:
        response = requests.get(cdx_url, timeout=120)

        if response.status_code == 503:
            raise Exception("Archive.org Wayback Machine is currently offline, please try again later.")
        elif response.status_code == 504:
            raise Exception("The connection to Archive.org Wayback Machine has timed out, please try again later.")
        elif response.status_code != 200:
            raise Exception(f"The API request to archive.org returned a non-200 HTTP status code: {response.status_code}")

        data = response.json()
        return data
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"There was an error fetching the data: {str(e)}")

def parse_results(data):
    """Parse CDX results into URLs list"""
    global timestamps
    urls = []

    for item in data:
        if isinstance(item, list) and len(item) >= 2:
            if item[0] != "timestamp" and item[1] != "original":
                timestamps.append(item[0])
                urls.append(item[1])

    return urls

def build_word_list(search_terms):
    """Build word list from search query, handling quoted phrases"""
    words = re.split(r'\s+', search_terms)
    word_list = []
    quoted = ""

    for word in words:
        if not quoted:
            if word.startswith("'"):
                if word.endswith("'"):
                    word_list.append(word)
                else:
                    quoted = word
            else:
                word_list.append(word)
        else:
            quoted += " " + word
            if word.endswith("'"):
                word_list.append(quoted)
                quoted = ""

    return word_list

def build_results_response(urls, processed_search_terms, execution_time):
    """Build and render search results"""
    global timestamps, domain

    total_results = len(urls)
    matched_link_counter = 0

    # Build result list
    results = []
    result_links_array = []

    for i, url in enumerate(urls):
        timestamp = timestamps[i]
        result_url = f"https://web.archive.org/web/{timestamp}/{url}"
        no_toolbar_url = f"https://web.archive.org/web/{timestamp}id_/{url}"

        css_class = 'even' if i % 2 == 0 else 'odd'

        # Check if URL matches search terms
        matched = False
        if processed_search_terms:
            lowercase_url = url.lower()
            for term in processed_search_terms:
                term_lower = term.lower().strip("'")
                if term_lower in lowercase_url:
                    matched = True
                    matched_link_counter += 1
                    break
        else:
            matched = True

        if matched:
            if processed_search_terms:
                result_num = matched_link_counter
            else:
                result_num = i + 1

            results.append({
                'num': result_num,
                'url': result_url,
                'no_toolbar_url': no_toolbar_url,
                'css_class': css_class
            })
            result_links_array.append(result_url)

    # Calculate final stats
    if processed_search_terms:
        display_count = matched_link_counter
        query_display = ' '.join(processed_search_terms)
    else:
        display_count = total_results
        query_display = None

    return render_template('results.html',
                         results=results,
                         result_links_array=result_links_array,
                         total_results=display_count,
                         domain=domain,
                         query_display=query_display,
                         execution_time=f"{execution_time:.2f}",
                         timestamp=datetime.utcnow().strftime('%B %d, %Y - %I:%M %p UTC'))

if __name__ == '__main__':
    app.run(debug=True)
