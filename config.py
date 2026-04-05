import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "watchtower-ke-dev-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'watchtower.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Scraper settings
    SCRAPE_INTERVAL_HOURS = int(os.environ.get("SCRAPE_INTERVAL_HOURS", 1))
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    # Crime categories tracked
    CRIME_CATEGORIES = [
        "gbv",
        "sexual_assault",
        "domestic_violence",
        "stalking",
        "harassment",
        "assault",
        "fraud",
        "scam",
        "robbery",
        "kidnapping",
    ]

    # Keywords per category for matching articles
    CRIME_KEYWORDS = {
        "gbv": [
            "gender-based violence", "gender based violence", "gbv",
            "violence against women", "femicide",
        ],
        "sexual_assault": [
            "sexual assault", "rape", "defilement", "sexual offence",
            "sexual abuse", "molest",
        ],
        "domestic_violence": [
            "domestic violence", "wife beating", "husband beating",
            "spouse abuse", "intimate partner violence",
        ],
        "stalking": [
            "stalking", "stalker", "cyberstalking", "following",
            "online harassment",
        ],
        "harassment": [
            "harassment", "street harassment", "workplace harassment",
            "sexual harassment", "threatening messages",
        ],
        "assault": [
            "assault", "attack", "physical assault", "beaten",
            "stabbing", "machete",
        ],
        "fraud": [
            "fraud", "con artist", "fake", "impersonation",
            "identity theft", "pyramid scheme", "ponzi",
        ],
        "scam": [
            "scam", "scammer", "mpesa scam", "online scam",
            "sextortion", "catfishing", "romance scam",
        ],
        "robbery": [
            "robbery", "mugging", "phone snatching", "carjacking",
            "burglary", "break-in", "theft",
        ],
        "kidnapping": [
            "kidnapping", "abduction", "kidnap", "missing person",
            "abducted",
        ],
    }

    # Kenya-specific location keywords
    LOCATION_KEYWORDS = [
        "nairobi", "mombasa", "kisumu", "nakuru", "eldoret",
        "westlands", "kilimani", "langata", "karen", "kibera",
        "eastleigh", "kasarani", "embakasi", "ruaraka", "dagoretti",
        "mathare", "dandora", "kayole", "umoja", "south b", "south c",
        "hurlingham", "lavington", "kileleshwa", "parklands",
        "thika", "juja", "ruiru", "kitengela", "ongata rongai",
        "machakos", "kajiado", "nyeri", "nanyuki", "kenya",
    ]
