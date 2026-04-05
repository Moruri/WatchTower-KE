"""Engine that runs all scrapers and saves results to the database."""

import logging
from datetime import datetime, timezone

from models import db, Article, ScrapeLog
from scrapers import ALL_SCRAPERS

logger = logging.getLogger(__name__)


def run_all_scrapers(app):
    """Run every registered scraper and persist new articles."""
    with app.app_context():
        total_new = 0
        for scraper_cls in ALL_SCRAPERS:
            scraper = scraper_cls()
            log = ScrapeLog(source=scraper.SOURCE_NAME)
            db.session.add(log)
            db.session.commit()

            try:
                articles = scraper.scrape()
                new_count = 0
                for data in articles:
                    # Skip duplicates by URL
                    exists = Article.query.filter_by(url=data["url"]).first()
                    if exists:
                        continue
                    article = Article(**data)
                    db.session.add(article)
                    new_count += 1

                db.session.commit()
                log.articles_found = new_count
                log.status = "success"
                total_new += new_count
                logger.info(
                    "%s: saved %d new articles", scraper.SOURCE_NAME, new_count
                )

            except Exception as e:
                db.session.rollback()
                log.status = "error"
                log.error_message = str(e)[:500]
                logger.exception("Scraper %s failed", scraper.SOURCE_NAME)

            finally:
                log.finished_at = datetime.now(timezone.utc)
                db.session.commit()

        logger.info("Scrape complete — %d new articles total", total_new)
        return total_new
