"""
Common URL handling utilities
"""
def validate_url(url: str) -> bool:
    """
    Validate if the URL is a valid YouTube playlist URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is a valid YouTube playlist URL
    """
    return "youtube.com" in url and "playlist" in url

def clean_url(url: str) -> str:
    """
    Clean YouTube URL by removing unnecessary parameters.
    
    Args:
        url (str): URL to clean
        
    Returns:
        str: Cleaned URL
    """
    base_url = url.split('&')[0] if '&' in url else url
    return base_url
