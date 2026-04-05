# WatchTower KE

Crime intelligence web scraper for Kenya — tracking GBV, assault, fraud, stalking, and scams from major Kenyan news sources. Built with Flask for [SheSafe Africa](https://shessafe.africa/).

## Features

- Scrapes 4 Kenyan news outlets: Nation Africa, The Standard, Citizen Digital, The Star
- Auto-classifies articles into 10 crime categories (GBV, sexual assault, domestic violence, stalking, harassment, assault, fraud, scam, robbery, kidnapping)
- Extracts location data (Nairobi neighborhoods, major Kenyan towns)
- Dashboard with charts (category breakdown, source distribution, top locations)
- Filterable reports page with search
- REST API for integration with shessafe.africa
- Background scheduler runs scrapers every 6 hours

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python run.py
```

Open http://127.0.0.1:5000 — then click **"Run Scraper Now"** on the Dashboard to populate data.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/articles` | GET | List articles (filters: `category`, `location`, `source`, `q`, `limit`) |
| `/api/stats` | GET | Dashboard statistics |
| `/api/scrape` | POST | Trigger a manual scrape |

## Project Structure

```
WatchTower-KE/
├── app.py              # Flask app factory + routes
├── config.py           # Configuration & crime keywords
├── models.py           # SQLAlchemy models (Article, ScrapeLog)
├── scraper_engine.py   # Orchestrates all scrapers
├── run.py              # Entry point
├── scrapers/
│   ├── base.py         # Base scraper with classification logic
│   ├── nation.py       # Nation Africa scraper
│   ├── standard.py     # The Standard scraper
│   ├── citizen.py      # Citizen Digital scraper
│   └── star.py         # The Star scraper
├── templates/          # Jinja2 HTML templates
├── static/css/         # Stylesheet
└── requirements.txt
```

## Crime Categories

| Category | Keywords tracked |
|---|---|
| GBV | gender-based violence, femicide, violence against women |
| Sexual Assault | rape, defilement, sexual offence, molestation |
| Domestic Violence | spouse abuse, intimate partner violence |
| Stalking | stalking, cyberstalking, online harassment |
| Harassment | street/workplace/sexual harassment |
| Assault | physical attacks, stabbings |
| Fraud | con artists, identity theft, pyramid schemes |
| Scam | MPesa scams, sextortion, romance scams |
| Robbery | mugging, phone snatching, carjacking |
| Kidnapping | abduction, missing persons |
