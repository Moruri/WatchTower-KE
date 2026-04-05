import logging
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class StandardScraper(BaseScraper):
    """Scraper for The Standard (standardmedia.co.ke).

    Uses their public RSS feed as the primary source — it's reliable
    and returns ~30 recent articles with titles, descriptions, and dates.
    Falls back to HTML scraping on the crime section page.
    """

    SOURCE_NAME = "The Standard"
    BASE_URL = "https://www.standardmedia.co.ke"
    RSS_URL = "https://www.standardmedia.co.ke/rss/headlines.php"
    SECTION_URLS = [
        "https://www.standardmedia.co.ke/category/763/crime-and-justice",
        "https://www.standardmedia.co.ke/category/588/national",
    ]

    def scrape(self):
        articles = []

        # ── Primary: RSS feed ────���───────────────────────────────
        articles.extend(self._scrape_rss())

        # ── Secondary: HTML sections ─────────────────────────────
        articles.extend(self._scrape_html())

        # Dedupe by URL
        seen = set()
        unique = []
        for a in articles:
            if a["url"] not in seen:
                seen.add(a["url"])
                unique.append(a)

        logger.info("The Standard: found %d relevant articles", len(unique))
        return unique

    def _scrape_rss(self):
        articles = []
        try:
            resp = self.session.get(self.RSS_URL, timeout=30)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)

            for item in root.iter("item"):
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                desc = item.findtext("description", "").strip()
                pub_date_str = item.findtext("pubDate", "")

                if not title or not link:
                    continue

                pub_date = self._parse_rss_date(pub_date_str)
                article = self._build_article(title, link, desc, pub_date)
                if article:
                    articles.append(article)

        except (requests.RequestException, ET.ParseError) as e:
            logger.error("Standard RSS failed: %s", e)

        return articles

    def _scrape_html(self):
        articles = []
        for section_url in self.SECTION_URLS:
            soup = self.fetch_page(section_url)
            if not soup:
                continue

            for link_tag in soup.select("a[href*='/article/']"):
                title_tag = link_tag.select_one("h3, h4, h2")
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                href = link_tag.get("href", "")
                if not href.startswith("http"):
                    href = self.BASE_URL + href

                article = self._build_article(title, href, "", None)
                if article:
                    articles.append(article)

        return articles

    def _parse_rss_date(self, date_str):
        """Parse RSS pubDate format: 'Mon, 05 Apr 2026 10:30:00 +0300'."""
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
        ):
            try:
                return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=None)
            except (ValueError, TypeError):
                continue
        return None
