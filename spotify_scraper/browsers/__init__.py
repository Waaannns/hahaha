"""
Browser factory module for SpotifyScraper.

This module provides factory functions for creating browser instances.
"""

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import BrowserError


def create_browser(browser_type: str = "auto", **kwargs) -> Browser:
    """
    Create appropriate browser instance.

    Args:
        browser_type: Type of browser ('requests', 'selenium', or 'auto')
        **kwargs: Additional arguments to pass to browser constructor

    Returns:
        Configured browser instance

    Raises:
        BrowserError: If browser creation fails
        ValueError: If browser_type is invalid
    """
    # Import implementation classes here to avoid circular imports
    from spotify_scraper.browsers.requests_browser import RequestsBrowser


    # Create browser based on type
    if browser_type == "requests":
        return RequestsBrowser(**kwargs)

    elif browser_type == "auto":
        # Try requests first, fallback to selenium if needed
        try:
            browser = RequestsBrowser(**kwargs)
            # Test browser with a simple request
            browser.get_page_content("https://open.spotify.com")
            return browser
        except Exception as e:
            raise BrowserError("Failed to create any browser instance") from e

    else:
        raise ValueError(f"Unknown browser type: {browser_type}")
