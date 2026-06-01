"""
config.py — All settings for the News Extraction Bot.
Each feed has a 'tags' list — saved to DB and CSV alongside every article.
"""

# ==========================================
# FETCH INTERVALS (minutes) — all run 24/7
# ==========================================
FETCH_INTERVAL_MARKET   = 5
FETCH_INTERVAL_NATIONAL = 10   # increased frequency for India
FETCH_INTERVAL_GLOBAL   = 30

ARTICLES_PER_FEED       = 10
REQUEST_TIMEOUT_SEC     = 15
MAX_RETRIES             = 3

# ==========================================
# DUPLICATE DETECTION
# ==========================================
SIMILARITY_THRESHOLD   = 0.68
SEEN_HEADLINES_MAX     = 10000
SEEN_HEADLINES_TTL_HRS = 24

# ==========================================
# STORAGE
# ==========================================
DB_FILE     = "news.db"
CSV_ENABLED = True
CSV_FILE    = "news_feed.csv"

# ==========================================
# KEYWORD FILTERS — leave empty to collect everything
# ==========================================
KEYWORDS = []

REAL_ESTATE_KEYWORDS = [
    "real estate",
    "estate",
    "property",
    "housing",
    "apartment",
    "flat",
    "villa",
    "residential",
    "commercial",
    "project",
    "land",
    "plot",
    "premises",
    "realty",
]

# ==========================================
# TOP 10 STOCK EXCHANGES
# ==========================================
STOCK_EXCHANGES = {
    "bse":      {"label": "BSE (Sensex)",          "keywords": ["bse", "sensex", "bombay stock exchange"]},
    "nse":      {"label": "NSE (Nifty)",            "keywords": ["nse", "nifty", "national stock exchange"]},
    "nyse":     {"label": "NYSE",                   "keywords": ["nyse", "new york stock exchange", "wall street"]},
    "nasdaq":   {"label": "NASDAQ",                 "keywords": ["nasdaq"]},
    "lse":      {"label": "LSE (FTSE)",             "keywords": ["lse", "ftse", "london stock exchange"]},
    "tse":      {"label": "Tokyo (Nikkei)",         "keywords": ["nikkei", "tokyo stock exchange", "tse", "jpx"]},
    "sse":      {"label": "Shanghai (CSI)",         "keywords": ["shanghai stock exchange", "sse", "csi 300"]},
    "hkex":     {"label": "Hong Kong (Hang Seng)",  "keywords": ["hkex", "hang seng", "hong kong exchange"]},
    "euronext": {"label": "Euronext (CAC/DAX)",     "keywords": ["euronext", "cac 40", "dax", "euro stoxx"]},
    "sgx":      {"label": "SGX (Singapore)",        "keywords": ["sgx", "straits times index", "singapore exchange"]},
}

# ==========================================
# AVAILABLE TAGS (reference)
# ==========================================
# world, politics, india, business, finance, market, stocks,
# ipo, economy, tech, science, sports, entertainment, crime,
# health, environment, startups

# ==========================================
# RSS FEEDS
# ==========================================
FEEDS = {

    # ------------------------------------------
    # GLOBAL — 14 sources
    # ------------------------------------------
    "global": [
        {"name": "BBC News",          "url": "http://feeds.bbci.co.uk/news/rss.xml",                               "tags": ["world", "politics", "business"]},
        {"name": "Reuters",           "url": "https://feeds.reuters.com/reuters/topNews",                           "tags": ["world", "business", "finance"]},
        {"name": "Al Jazeera",        "url": "https://www.aljazeera.com/xml/rss/all.xml",                           "tags": ["world", "politics"]},
        {"name": "The Guardian",      "url": "https://www.theguardian.com/world/rss",                               "tags": ["world", "politics", "environment"]},
        {"name": "Associated Press",  "url": "https://feeds.apnews.com/rss/apf-topnews",                            "tags": ["world", "politics", "business"]},
        {"name": "NPR News",          "url": "https://feeds.npr.org/1001/rss.xml",                                  "tags": ["world", "politics", "science"]},
        {"name": "TechCrunch",        "url": "https://techcrunch.com/feed/",                                        "tags": ["tech", "startups", "business"]},
        {"name": "Ars Technica",      "url": "https://feeds.arstechnica.com/arstechnica/index",                     "tags": ["tech", "science"]},
        {"name": "The Verge",         "url": "https://www.theverge.com/rss/index.xml",                              "tags": ["tech", "science", "entertainment"]},
        {"name": "Wired",             "url": "https://www.wired.com/feed/rss",                                      "tags": ["tech", "science", "business"]},
        {"name": "Bloomberg Markets", "url": "https://feeds.bloomberg.com/markets/news.rss",                        "tags": ["finance", "market", "economy", "business"]},
        {"name": "Financial Times",   "url": "https://www.ft.com/rss/home",                                         "tags": ["finance", "economy", "business"]},
        {"name": "The Economist",     "url": "https://www.economist.com/finance-and-economics/rss.xml",             "tags": ["finance", "economy", "world"]},
        {"name": "Forbes",            "url": "https://www.forbes.com/real-time/feed2/",                             "tags": ["business", "finance", "startups"]},
    ],

    # ------------------------------------------
    # INDIAN NATIONAL — 30 sources
    # Covers: mainstream, regional, TV, digital,
    #         sports, entertainment, health, tech
    # ------------------------------------------
    "national": [

        # --- Mainstream English dailies ---
        {"name": "Times of India",       "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",                    "tags": ["india", "politics", "world"]},
        {"name": "NDTV",                 "url": "https://feeds.feedburner.com/ndtvnews-top-stories",                             "tags": ["india", "politics", "world"]},
        {"name": "The Hindu",            "url": "https://www.thehindu.com/feeder/default.rss",                                   "tags": ["india", "politics", "world"]},
        {"name": "India Today",          "url": "https://www.indiatoday.in/rss/home",                                            "tags": ["india", "politics", "sports", "entertainment"]},
        {"name": "Hindustan Times",      "url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",               "tags": ["india", "politics", "crime"]},
        {"name": "Indian Express",       "url": "https://indianexpress.com/feed/",                                               "tags": ["india", "politics", "business"]},
        {"name": "Deccan Herald",        "url": "https://www.deccanherald.com/rss-feeds/national",                               "tags": ["india", "politics", "south-india", "karnataka"]},
        {"name": "Tribune India",        "url": "https://www.tribuneindia.com/rss/feed",                                         "tags": ["india", "politics", "north-india"]},
        {"name": "The Telegraph India",  "url": "https://www.telegraphindia.com/rss-feed/",                                      "tags": ["india", "politics", "east-india"]},
        {"name": "Deccan Chronicle",     "url": "https://www.deccanchronicle.com/rss_feed/",                                     "tags": ["india", "politics", "south-india", "karnataka"]},

        # --- TV & Digital news ---
        {"name": "News18",               "url": "https://www.news18.com/rss/india.xml",                                          "tags": ["india", "politics", "entertainment"]},
        {"name": "Zee News India",       "url": "https://zeenews.india.com/rss/india-national-news.xml",                         "tags": ["india", "politics", "business"]},
        {"name": "India TV News",        "url": "https://www.indiatvnews.com/rssfeed/news.xml",                                   "tags": ["india", "politics", "crime"]},
        {"name": "ABP Live",             "url": "https://news.abplive.com/feed",                                                  "tags": ["india", "politics", "entertainment"]},
        {"name": "Republic World",       "url": "https://www.republicworld.com/feeds/all/",                                       "tags": ["india", "politics", "world"]},
        {"name": "News9",                "url": "https://www.news9live.com/rss.xml",                                              "tags": ["india", "politics", "tech"]},

        # --- Independent & analytical ---
        {"name": "The Wire",             "url": "https://thewire.in/feed",                                                        "tags": ["india", "politics", "world"]},
        {"name": "Scroll.in",            "url": "https://scroll.in/feed",                                                         "tags": ["india", "politics", "tech"]},
        {"name": "The Print",            "url": "https://theprint.in/feed/",                                                      "tags": ["india", "politics", "world"]},
        {"name": "Firstpost",            "url": "https://www.firstpost.com/rss/india.xml",                                        "tags": ["india", "politics", "entertainment"]},
        {"name": "The Quint",            "url": "https://www.thequint.com/feeds/all-articles",                                    "tags": ["india", "politics", "entertainment"]},
        {"name": "Newslaundry",          "url": "https://www.newslaundry.com/feed",                                               "tags": ["india", "politics", "media"]},

        # --- Sports ---
        {"name": "Cricbuzz",             "url": "https://www.cricbuzz.com/rss-feeds/cricket-news",                                "tags": ["india", "sports", "cricket"]},
        {"name": "ESPN Cricinfo India",  "url": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",                     "tags": ["india", "sports", "cricket"]},
        {"name": "Sports Tak",           "url": "https://sportsTak.in/feed/",                                                     "tags": ["india", "sports"]},

        # --- Business & economy (India-focused) ---
        {"name": "YourStory",            "url": "https://yourstory.com/feed",                                                     "tags": ["india", "startups", "business", "tech"]},
        {"name": "Inc42",                "url": "https://inc42.com/feed/",                                                        "tags": ["india", "startups", "tech", "business"]},
        {"name": "VCCircle",             "url": "https://www.vccircle.com/feed/",                                                 "tags": ["india", "startups", "finance", "ipo"]},

        # --- Health & science ---
        {"name": "India Science Wire",   "url": "https://indiasciencewire.in/feed/",                                              "tags": ["india", "science", "health"]},

        # --- Regional English ---
        {"name": "The New Indian Express","url": "https://www.newindianexpress.com/nation/rssfeed/?id=164&getXmlFeed=true",       "tags": ["india", "politics", "south-india", "chennai"]},
    ],

    # ------------------------------------------
    # MARKET & STOCKS — 12 sources
    # ------------------------------------------
    "market": [
        {"name": "Economic Times",    "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",              "tags": ["market", "stocks", "finance", "india"]},
        {"name": "Moneycontrol",      "url": "https://www.moneycontrol.com/rss/latestnews.xml",                                   "tags": ["market", "stocks", "finance", "india"]},
        {"name": "Mint",              "url": "https://www.livemint.com/rss/markets",                                              "tags": ["market", "finance", "economy", "india"]},
        {"name": "Business Standard", "url": "https://www.business-standard.com/rss/markets-106.rss",                            "tags": ["market", "stocks", "business", "india"]},
        {"name": "Financial Express", "url": "https://www.financialexpress.com/market/feed/",                                     "tags": ["market", "finance", "economy", "india"]},
        {"name": "ET Markets",        "url": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",          "tags": ["stocks", "ipo", "market", "india"]},
        {"name": "Business Today",    "url": "https://www.businesstoday.in/rssfeeds/",                                            "tags": ["business", "economy", "india"]},
        {"name": "CNBCTV18",          "url": "https://www.cnbctv18.com/rss/marketsrss.xml",                                       "tags": ["market", "stocks", "finance", "india"]},
        {"name": "MarketWatch",       "url": "https://feeds.marketwatch.com/marketwatch/topstories/",                             "tags": ["market", "stocks", "finance", "world"]},
        {"name": "Seeking Alpha",     "url": "https://seekingalpha.com/market_currents.xml",                                      "tags": ["stocks", "finance", "market", "world"]},
        {"name": "Investing.com",     "url": "https://in.investing.com/rss/news.rss",                                             "tags": ["market", "stocks", "finance"]},
        {"name": "Yahoo Finance",     "url": "https://finance.yahoo.com/news/rssindex",                                           "tags": ["finance", "market", "business", "world"]},
    ],

    # ------------------------------------------
    # SPORTS — cricket, football, general
    # ------------------------------------------
    "sports": [
        {"name": "ESPN Cricinfo",        "url": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",                     "tags": ["sports", "cricket"]},
        {"name": "Cricbuzz",             "url": "https://www.cricbuzz.com/rss-feeds/cricket-news",                                "tags": ["sports", "cricket"]},
        {"name": "Sports Tak",           "url": "https://sportsTak.in/feed/",                                                     "tags": ["sports", "india"]},
        {"name": "ESPN",                 "url": "https://www.espn.com/espn/rss/news.xml",                                         "tags": ["sports", "world"]},
        {"name": "BBC Sport",            "url": "https://feeds.bbci.co.uk/sport/rss.xml",                                         "tags": ["sports", "world"]},
        {"name": "Sky Sports",           "url": "https://www.skysports.com/rss/12040",                                            "tags": ["sports", "world", "football"]},
        {"name": "Goal.com",             "url": "https://www.goal.com/feeds/en/news",                                             "tags": ["sports", "football", "world"]},
    ],

    # ------------------------------------------
    # ENTERTAINMENT — India (Bollywood, OTT, celebrity)
    # ------------------------------------------
    "entertainment_india": [
        {"name": "Bollywood Hungama",    "url": "https://www.bollywoodhungama.com/rss/news.xml",                                   "tags": ["entertainment", "bollywood", "india"]},
        {"name": "Pinkvilla",            "url": "https://www.pinkvilla.com/feed",                                                  "tags": ["entertainment", "bollywood", "india"]},
        {"name": "Filmfare",             "url": "https://www.filmfare.com/rss/news.xml",                                           "tags": ["entertainment", "bollywood", "india"]},
        {"name": "India Today - Ent",    "url": "https://www.indiatoday.in/rss/1206575",                                           "tags": ["entertainment", "india"]},
        {"name": "NDTV Movies",          "url": "https://feeds.feedburner.com/ndtvmovies",                                         "tags": ["entertainment", "bollywood", "india"]},
        {"name": "Koimoi",               "url": "https://www.koimoi.com/feed/",                                                    "tags": ["entertainment", "bollywood", "india"]},
        {"name": "Mid-Day Entertainment","url": "https://www.mid-day.com/rss/articles/latest",                                     "tags": ["entertainment", "india"]},
    ],

    # ------------------------------------------
    # ENTERTAINMENT — Global (Hollywood, music, TV)
    # ------------------------------------------
    "entertainment_global": [
        {"name": "Variety",              "url": "https://variety.com/feed/",                                                       "tags": ["entertainment", "hollywood", "world"]},
        {"name": "The Hollywood Reporter","url": "https://www.hollywoodreporter.com/feed/",                                        "tags": ["entertainment", "hollywood", "world"]},
        {"name": "Deadline",             "url": "https://deadline.com/feed/",                                                      "tags": ["entertainment", "hollywood", "world"]},
        {"name": "Rolling Stone",        "url": "https://www.rollingstone.com/music/music-news/feed/",                             "tags": ["entertainment", "music", "world"]},
        {"name": "Entertainment Weekly", "url": "https://ew.com/feed/",                                                            "tags": ["entertainment", "world"]},
        {"name": "IGN",                  "url": "https://feeds.feedburner.com/ign/all",                                            "tags": ["entertainment", "gaming", "world"]},
    ],

    # ------------------------------------------
    # ECONOMICS — India (macro, policy, RBI, budget)
    # ------------------------------------------
    "economics_india": [
        {"name": "Economic Times",       "url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",       "tags": ["economics", "economy", "india"]},
        {"name": "Mint - Economy",       "url": "https://www.livemint.com/rss/economy",                                            "tags": ["economics", "economy", "india"]},
        {"name": "Business Standard",    "url": "https://www.business-standard.com/rss/economy-policy-10301.rss",                  "tags": ["economics", "economy", "india"]},
        {"name": "Financial Express",    "url": "https://www.financialexpress.com/economy/feed/",                                   "tags": ["economics", "economy", "india"]},
        {"name": "The Hindu - Economy",  "url": "https://www.thehindu.com/business/Economy/?service=rss",                          "tags": ["economics", "economy", "india"]},
        {"name": "CNBCTV18 Economy",     "url": "https://www.cnbctv18.com/rss/economyrss.xml",                                     "tags": ["economics", "economy", "india"]},
    ],

    # ------------------------------------------
    # ECONOMICS — Global (IMF, Fed, trade, macro)
    # ------------------------------------------
    "economics_global": [
        {"name": "The Economist",        "url": "https://www.economist.com/finance-and-economics/rss.xml",                         "tags": ["economics", "economy", "world"]},
        {"name": "Bloomberg Economics",  "url": "https://feeds.bloomberg.com/economics/news.rss",                                  "tags": ["economics", "economy", "world"]},
        {"name": "Financial Times",      "url": "https://www.ft.com/rss/home/uk",                                                   "tags": ["economics", "economy", "world"]},
        {"name": "Reuters Economy",      "url": "https://feeds.reuters.com/reuters/businessNews",                                   "tags": ["economics", "economy", "world"]},
        {"name": "Project Syndicate",    "url": "https://www.project-syndicate.org/rss",                                            "tags": ["economics", "economy", "world"]},
        {"name": "IMF Blog",             "url": "https://www.imf.org/en/Blogs/RSS",                                                 "tags": ["economics", "economy", "world"]},
    ],
}
