
import re
import httpx
import logging
import sys
import random
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import html2text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extensions to ignore in email regex/crawling
IGNORED_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.svg', '.woff', '.mp4', '.pdf', '.zip')

def extract_emails(text):
    """Robust email extraction."""
    if not text:
        return []
    # Basic regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(email_pattern, text)
    
    # Filter junk
    valid_emails = set()
    for email in matches:
        email_lower = email.lower()
        if any(email_lower.endswith(ext) for ext in IGNORED_EXTS):
            continue
        # Filter common false positives
        if email_lower in ['name@example.com', 'email@address.com', 'you@yourdomain.com']:
            continue
        valid_emails.add(email)
            
    return list(valid_emails)

def extract_social_media(soup):
    """Extract social media links."""
    socials = {}
    platforms = ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube', 'tiktok']
    
    if not soup:
        return socials
        
    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        for platform in platforms:
            if platform in href and platform not in socials:
                socials[platform] = a['href']
    return socials

def get_contact_pages(soup, base_url):
    """Find links to Contact, About, Team pages."""
    keywords = ['contact', 'about', 'team', 'staff', 'people', 'leadership']
    pages = set()
    
    if not soup:
        return []

    for a in soup.find_all('a', href=True):
        href = a['href']
        # Normalize
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        
        # Verify it's internal
        if parsed.netloc != urlparse(base_url).netloc:
            continue
            
        # Check keywords
        path_lower = parsed.path.lower()
        if any(k in path_lower for k in keywords):
            pages.add(full_url)
            
    return list(pages)[:4]  # Limit to 4 extra pages

def search_duckduckgo(query):
    """Search DuckDuckGo for missing emails."""
    try:
        from duckduckgo_search import DDGS
        logger.info(f"Searching DuckDuckGo for: {query}")
        
        # Simple text search to look for email-like patterns in snippets
        emails = set()
        with DDGS() as ddgs:
            # Get top 5 results
            results = [r for r in ddgs.text(query, max_results=5)]
            
            for res in results:
                # Check snippet for emails
                snippet_emails = extract_emails(res.get('body', ''))
                emails.update(snippet_emails)
                
        return list(emails)
        
    except ImportError:
        logger.warning("duckduckgo-search not found")
        return []
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return []

def scrape_website_contacts(url: str, business_name: str) -> dict:
    """
    Deep scrape: Home -> Contact Pages -> Search Engine
    """
    if not url:
        return {"error": "No URL provided"}
        
    if not url.startswith('http'):
        url = 'http://' + url
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    collected_emails = set()
    collected_socials = {}
    pages_scraped = 0
    search_enriched = False
    
    try:
        with httpx.Client(timeout=15, follow_redirects=True, verify=False) as client:
            
            # 1. Scrape Homepage
            logger.info(f"Fetching {url}")
            try:
                resp = client.get(url, headers=headers)
                resp.raise_for_status()
                pages_scraped += 1
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = html2text.html2text(resp.text)
                
                # Extract
                collected_emails.update(extract_emails(text))
                collected_socials.update(extract_social_media(soup))
                
                # 2. Find & Scrape Sub-pages
                sub_pages = get_contact_pages(soup, url)
                for sub_url in sub_pages:
                    logger.info(f"Fetching sub-page: {sub_url}")
                    try:
                        sub_resp = client.get(sub_url, headers=headers)
                        pages_scraped += 1
                        sub_text = html2text.html2text(sub_resp.text)
                        collected_emails.update(extract_emails(sub_text))
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.error(f"Main site fetch failed: {e}")

        # 3. Fallback: Search Engine Enrichment
        if business_name:
            # 3a. General Search
            if not collected_emails:
                search_query = f"{business_name} email contact"
                found_emails = search_duckduckgo(search_query)
                if found_emails:
                    collected_emails.update(found_emails)
                    search_enriched = True
            
            # 3b. Social Search (Facebook/Instagram/LinkedIn)
            # Try to find emails in social descriptions if standard methods failed
            if not collected_emails:
                logger.info(f"Running Social Search for {business_name}...")
                social_query = f'site:facebook.com OR site:instagram.com OR site:linkedin.com "{business_name}" email'
                social_emails = search_duckduckgo(social_query)
                if social_emails:
                    collected_emails.update(social_emails)
                    search_enriched = True
                
        # 4. Return Results
        return {
            "emails": list(collected_emails),
            "social_media": collected_socials,
            "owner_info": {},
            "team_members": [],
            "phone_numbers": [],
            "business_hours": "",
            "additional_contacts": [],
            "_pages_scraped": pages_scraped,
            "_search_enriched": search_enriched
        }
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        return {
            "error": str(e), 
            "emails": list(collected_emails),
            "_pages_scraped": pages_scraped
        }

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    name = sys.argv[2] if len(sys.argv) > 2 else "Test Business"
    print(scrape_website_contacts(url, name))
