from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Article(db.Model):
    """A scraped news article about a crime incident."""

    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(1000), unique=True, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200))
    published_date = db.Column(db.DateTime)
    scraped_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "summary": self.summary,
            "category": self.category,
            "location": self.location,
            "published_date": (
                self.published_date.isoformat() if self.published_date else None
            ),
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }


class ScrapeLog(db.Model):
    """Tracks each scrape run for monitoring."""

    __tablename__ = "scrape_logs"

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    started_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    finished_at = db.Column(db.DateTime)
    articles_found = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="running")
    error_message = db.Column(db.Text)
