import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus

import requests

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class GoogleNewsScraper(BaseScraper):
    """Scraper using Google News RSS for Kenya crime stories.

    Google News provides public RSS feeds for search queries.
    This captures articles from Nation, Star, and any other Kenyan outlet
    that Google indexes — solving the 403 problem with those sites.
    """

    SOURCE_NAME = "Google News KE"

    # Search queries targeting our crime categories in Kenya
    SEARCH_QUERIES = [
        "gender based violence Kenya",
        "sexual assault Nairobi",
        "domestic violence Kenya",
        "stalking harassment Kenya",
        "fraud scam Kenya",
        "assault crime Nairobi",
        "robbery mugging Nairobi",
        "kidnapping abduction Kenya",
        "GBV Kenya",
        "sextortion Kenya",
    ]

    def scrape(self):
        articles = []

        for query in self.SEARCH_QUERIES:
            encoded = quote_plus(query)
            rss_url = (
                f"https://news.google.com/rss/search?"
                f"q={encoded}&hl=en-KE&gl=KE&ceid=KE:en"
            )

            try:
                resp = self.session.get(rss_url, timeout=30)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)

                for item in root.iter("item"):
                    title = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    pub_date_str = item.findtext("pubDate", "")
                    source_el = item.find("source")
                    source_name = (
                        source_el.text.strip() if source_el is not None else ""
                    )

                    if not title or not link:
                        continue

                    # Use the original source name if available
                    summary = f"Via {source_name}" if source_name else ""
                    pub_date = self._parse_rss_date(pub_date_str)

                    article = self._build_article(title, link, summary, pub_date)
                    if article:
                        # Tag the actual outlet in the summary
                        if source_name:
                            article["summary"] = f"Source: {source_name}"
                        articles.append(article)

            except (requests.RequestException, ET.ParseError) as e:
                logger.error("Google News query '%s' failed: %s", query, e)
                continue

        # Dedupe by URL
        seen = set()
        unique = []
        for a in articles:
            if a["url"] not in seen:
                seen.add(a["url"])
                unique.append(a)

        logger.info("Google News KE: found %d relevant articles", len(unique))
        return unique

    def _parse_rss_date(self, date_str):
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S",
        ):
            try:
                return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=None)
            except (ValueError, TypeError):
                continue
        return None
