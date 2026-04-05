import logging
from datetime import datetime

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class StarScraper(BaseScraper):
    """Scraper for The Star Kenya (the-star.co.ke)."""

    SOURCE_NAME = "The Star"
    BASE_URL = "https://www.the-star.co.ke"
    SEARCH_URLS = [
        "https://www.the-star.co.ke/news/",
        "https://www.the-star.co.ke/counties/nairobi/",
        "https://www.the-star.co.ke/news/crime/",
    ]

    def scrape(self):
        articles = []
        for section_url in self.SEARCH_URLS:
            soup = self.fetch_page(section_url)
            if not soup:
                continue

            for card in soup.select(
                "article, .article-item, .post-item, .teaser, .node--type-article"
            ):
                link_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, .field--name-title")
                summary_tag = card.select_one("p, .field--name-body, .teaser-text")

                if not link_tag or not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                href = link_tag["href"]
                if not href.startswith("http"):
                    href = self.BASE_URL + href

                summary = summary_tag.get_text(strip=True) if summary_tag else ""

                date_tag = card.select_one("time, .date, .field--name-created")
                pub_date = None
                if date_tag:
                    date_str = date_tag.get("datetime") or date_tag.get_text(strip=True)
                    pub_date = self._parse_date(date_str)

                article = self._build_article(title, href, summary, pub_date)
                if article:
                    articles.append(article)

        logger.info("The Star: found %d relevant articles", len(articles))
        return articles

    def _parse_date(self, date_str):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%B %d, %Y",
            "%a, %d %b %Y",
        ):
            try:
                return datetime.strptime(date_str[:19], fmt)
            except (ValueError, TypeError):
                continue
        return None
