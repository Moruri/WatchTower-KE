"""WatchTower KE — Flask application for tracking crime reports in Kenya."""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template, request, redirect, url_for

import threading

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

    # ── Background scheduler — runs every 1 hour ─────────────────────
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: run_all_scrapers(app),
        trigger="interval",
        hours=Config.SCRAPE_INTERVAL_HOURS,
        id="scrape_job",
    )
    scheduler.start()

    # Run an initial scrape on startup (in background thread so app boots fast)
    def _initial_scrape():
        import time
        time.sleep(3)  # let Flask finish starting
        logger.info("Running initial scrape on startup...")
        run_all_scrapers(app)

    threading.Thread(target=_initial_scrape, daemon=True).start()

    # ── Page routes ──────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template("reports.html")

    @app.route("/embed")
    def embed():
        """Standalone reports widget — no nav/footer, ready to iframe."""
        return render_template("embed.html")

    # ── Admin routes (not for public users) ──────────────────────────
    @app.route("/admin")
    def admin_home():
        return render_template("index.html")

    @app.route("/admin/dashboard")
    def admin_dashboard():
        return render_template("dashboard.html")

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
            query.order_by(
                Article.published_date.desc().nullslast(),
                Article.scraped_at.desc(),
            )
            .limit(limit)
            .all()
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

    # ── CORS — allow shessafe.africa to call the API ──────────────
    @app.after_request
    def add_cors(response):
        origin = request.headers.get("Origin", "")
        allowed = ["https://shessafe.africa", "http://localhost", "http://127.0.0.1"]
        if any(origin.startswith(o) for o in allowed):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
