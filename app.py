"""WatchTower KE — Flask application for tracking crime reports in Kenya."""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template, request

from config import Config
from models import db, Article, ScrapeLog
from scraper_engine import run_all_scrapers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ── Background scheduler ─────────────────────────────────────────
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: run_all_scrapers(app),
        trigger="interval",
        hours=Config.SCRAPE_INTERVAL_HOURS,
        id="scrape_job",
        next_run_time=None,  # don't run on startup; use /api/scrape to trigger
    )
    scheduler.start()

    # ── Page routes ──────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/reports")
    def reports():
        return render_template("reports.html")

    # ── API routes ───────────────────────────────────────────────────
    @app.route("/api/articles")
    def api_articles():
        """Return articles with optional filters: category, location, source, limit."""
        query = Article.query
        category = request.args.get("category")
        location = request.args.get("location")
        source = request.args.get("source")
        search = request.args.get("q")

        if category:
            query = query.filter(Article.category == category)
        if location:
            query = query.filter(Article.location.ilike(f"%{location}%"))
        if source:
            query = query.filter(Article.source == source)
        if search:
            query = query.filter(
                Article.title.ilike(f"%{search}%")
                | Article.summary.ilike(f"%{search}%")
            )

        limit = request.args.get("limit", 100, type=int)
        articles = (
            query.order_by(Article.scraped_at.desc()).limit(limit).all()
        )
        return jsonify([a.to_dict() for a in articles])

    @app.route("/api/stats")
    def api_stats():
        """Summary statistics for the dashboard."""
        total = Article.query.count()

        # Per-category counts
        categories = {}
        for cat in Config.CRIME_CATEGORIES:
            categories[cat] = Article.query.filter_by(category=cat).count()

        # Per-source counts
        sources = {}
        for row in (
            db.session.query(Article.source, db.func.count(Article.id))
            .group_by(Article.source)
            .all()
        ):
            sources[row[0]] = row[1]

        # Top locations
        locations = {}
        for row in (
            db.session.query(Article.location, db.func.count(Article.id))
            .filter(Article.location.isnot(None))
            .group_by(Article.location)
            .order_by(db.func.count(Article.id).desc())
            .limit(15)
            .all()
        ):
            locations[row[0]] = row[1]

        # Last scrape time
        last_log = ScrapeLog.query.order_by(ScrapeLog.finished_at.desc()).first()
        last_scrape = last_log.finished_at.isoformat() if last_log and last_log.finished_at else None

        return jsonify(
            {
                "total_articles": total,
                "categories": categories,
                "sources": sources,
                "top_locations": locations,
                "last_scrape": last_scrape,
            }
        )

    @app.route("/api/scrape", methods=["POST"])
    def api_scrape():
        """Manually trigger a scrape run."""
        new_count = run_all_scrapers(app)
        return jsonify({"status": "ok", "new_articles": new_count})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
