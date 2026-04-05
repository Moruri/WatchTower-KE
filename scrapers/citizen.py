import logging
from datetime import datetime

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class CitizenScraper(BaseScraper):
    """Scraper for Citizen Digital (citizen.digital).

    Uses partial attribute selectors to survive CSS Module hash changes.
    No dedicated crime section — scrapes the general /news page.
    """

    SOURCE_NAME = "Citizen Digital"
    BASE_URL = "https://www.citizen.digital"
    SEARCH_URLS = [
        "https://www.citizen.digital/news",
    ]

    def scrape(self):
        articles = []
        for section_url in self.SEARCH_URLS:
            soup = self.fetch_page(section_url)
            if not soup:
                continue

            # Citizen uses CSS Modules with hashed class names like
            # card__title_bawh2, featured__title_2EbQO, article__title_2udc-
            # Use partial attribute selectors to match them.

            # Strategy 1: Find all article links with titles via partial selectors
            for card in soup.select(
                '[class*="card__"], [class*="featured__"], [class*="article__"]'
            ):
                link_tag = card.select_one("a[href]") if card.name != "a" else card
                if not link_tag or not link_tag.get("href"):
                    continue

                # Find title within the card
                title_el = card.select_one(
                    '[class*="title"], h2, h3, h4'
                )
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                if not title:
                    continue

                href = link_tag["href"]
                if not href.startswith("http"):
                    href = self.BASE_URL + href

                # Excerpt / summary
                excerpt_el = card.select_one('[class*="excerpt"], p')
                summary = excerpt_el.get_text(strip=True) if excerpt_el else ""

                # Time
                time_el = card.select_one('[class*="time"], time')
                pub_date = None
                if time_el:
                    date_str = time_el.get("datetime") or time_el.get_text(strip=True)
                    pub_date = self._parse_date(date_str)

                article = self._build_article(title, href, summary, pub_date)
                if article:
                    articles.append(article)

            # Strategy 2: Fallback — find any <a> tags linking to news articles
            if not articles:
                for a_tag in soup.select("a[href*='/news/']"):
                    title = a_tag.get_text(strip=True)
                    href = a_tag["href"]
                    if not title or len(title) < 15:
                        continue
                    if not href.startswith("http"):
                        href = self.BASE_URL + href
                    article = self._build_article(title, href, "", None)
                    if article:
                        articles.append(article)

        # Dedupe
        seen = set()
        unique = []
        for a in articles:
            if a["url"] not in seen:
                seen.add(a["url"])
                unique.append(a)

        logger.info("Citizen Digital: found %d relevant articles", len(unique))
        return unique

    def _parse_date(self, date_str):
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%B %d, %Y"):
            try:
                return datetime.strptime(date_str[:19], fmt)
            except (ValueError, TypeError):
                continue
        return None
