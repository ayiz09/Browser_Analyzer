from urllib.parse import urlparse

def extract_domain(url):
    """Extract domain from URL"""
    try:
        if not url:
            return ""
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except:
        return ""