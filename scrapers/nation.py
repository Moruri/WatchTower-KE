import logging
from datetime import datetime

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class NationScraper(BaseScraper):
    """Scraper for Nation Africa (nation.africa) — Kenya's largest news outlet."""

    SOURCE_NAME = "Nation Africa"
    BASE_URL = "https://nation.africa"
    SEARCH_URLS = [
        "https://nation.africa/kenya/news/gender-violence",
        "https://nation.africa/kenya/news/crime",
        "https://nation.africa/kenya/counties",
    ]

    def scrape(self):
        articles = []
        for section_url in self.SEARCH_URLS:
            soup = self.fetch_page(section_url)
            if not soup:
                continue

            # Nation uses article teaser cards
            for card in soup.select("article, .story-teaser, .article-collection-item"):
                link_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, .title-medium, .title-small")
                summary_tag = card.select_one("p, .article-summary, .story-summary")

                if not link_tag or not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                href = link_tag["href"]
                if not href.startswith("http"):
                    href = self.BASE_URL + href

                summary = summary_tag.get_text(strip=True) if summary_tag else ""

                # Try to get date
                date_tag = card.select_one("time, .date, .article-date")
                pub_date = None
                if date_tag:
                    date_str = date_tag.get("datetime") or date_tag.get_text(strip=True)
                    pub_date = self._parse_date(date_str)

                article = self._build_article(title, href, summary, pub_date)
                if article:
                    articles.append(article)

        logger.info("Nation Africa: found %d relevant articles", len(articles))
        return articles

    def _parse_date(self, date_str):
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%B %d, %Y", "%d %B %Y"):
            try:
                return datetime.strptime(date_str[:19], fmt)
            except (ValueError, TypeError):
                continue
        return None
