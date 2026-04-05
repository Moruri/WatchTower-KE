import logging
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from config import Config

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for all news scrapers."""

    SOURCE_NAME = "unknown"
    BASE_URL = ""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": Config.USER_AGENT})

    def fetch_page(self, url):
        """Fetch a page and return a BeautifulSoup object."""
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except requests.RequestException as e:
            logger.error("Failed to fetch %s: %s", url, e)
            return None

    def classify_article(self, text):
        """Determine crime category from article text. Returns the best match."""
        text_lower = text.lower()
        scores = {}
        for category, keywords in Config.CRIME_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        if not scores:
            return None
        return max(scores, key=scores.get)

    def extract_location(self, text):
        """Try to extract a Kenya location from the text."""
        text_lower = text.lower()
        for loc in Config.LOCATION_KEYWORDS:
            pattern = r"\b" + re.escape(loc) + r"\b"
            if re.search(pattern, text_lower):
                return loc.title()
        return None

    def scrape(self):
        """Scrape articles. Must be implemented by subclasses.

        Should return a list of dicts with keys:
            title, url, source, summary, category, location, published_date
        """
        raise NotImplementedError

    def _build_article(self, title, url, summary, published_date=None):
        """Helper to build an article dict with auto-classification."""
        combined_text = f"{title} {summary}"
        category = self.classify_article(combined_text)
        if not category:
            return None

        location = self.extract_location(combined_text)

        return {
            "title": title.strip(),
            "url": url.strip(),
            "source": self.SOURCE_NAME,
            "summary": summary.strip()[:1000] if summary else "",
            "category": category,
            "location": location,
            "published_date": published_date,
        }
