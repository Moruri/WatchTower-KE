from scrapers.base import BaseScraper
from scrapers.standard import StandardScraper
from scrapers.citizen import CitizenScraper
from scrapers.google_news import GoogleNewsScraper

ALL_SCRAPERS = [StandardScraper, CitizenScraper, GoogleNewsScraper]

__all__ = [
    "BaseScraper",
    "StandardScraper",
    "CitizenScraper",
    "GoogleNewsScraper",
    "ALL_SCRAPERS",
]
