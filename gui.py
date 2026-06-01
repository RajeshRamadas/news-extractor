import config
import storage
from pywebgui import WebGUIApp

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Extractor GUI</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f5f7fb;
      color: #1f2937;
    }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 0;
    }
    .sidebar {
      background: #111827;
      color: #e5e7eb;
      padding: 24px 20px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .brand {
      font-size: 1.25rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 16px;
    }
    .nav-button {
      width: 100%;
      text-align: left;
      border: none;
      border-radius: 12px;
      background: #1f2937;
      color: #e5e7eb;
      padding: 14px 16px;
      margin: 4px 0;
      cursor: pointer;
      transition: background 0.2s ease;
      font-size: 0.95rem;
    }
    .nav-button.active,
    .nav-button:hover {
      background: #2563eb;
      color: #fff;
    }
    .sidebar h2 {
      margin: 0;
      font-size: 1rem;
      color: #9ca3af;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .stats-card {
      background: #1f2937;
      padding: 16px;
      border-radius: 16px;
      display: grid;
      gap: 12px;
    }
    .stats-card strong {
      display: block;
      font-size: 1.1rem;
      margin-bottom: 4px;
      color: #fff;
    }
    .stats-list {
      display: grid;
      gap: 8px;
    }
    .stats-list div {
      display: flex;
      justify-content: space-between;
      color: #d1d5db;
      font-size: 0.95rem;
    }
    .main {
      padding: 24px 28px;
      overflow: auto;
    }
    .header-row {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }
    .header-row h1 {
      margin: 0;
      font-size: 2rem;
      color: #111827;
    }
    .subtitle {
      color: #6b7280;
      margin-top: 8px;
    }
    .panel {
      margin-top: 24px;
      background: #ffffff;
      border-radius: 28px;
      padding: 24px;
      box-shadow: 0 20px 60px rgba(15, 23, 42, 0.08);
    }
    .article-card {
      border: 1px solid #e5e7eb;
      border-radius: 18px;
      padding: 18px;
      margin-bottom: 16px;
      transition: border-color 0.2s ease, transform 0.2s ease;
      background: #fff;
    }
    .article-card:hover {
      transform: translateY(-1px);
      border-color: #cbd5e1;
    }
    .article-title {
      margin: 0;
      font-size: 1.05rem;
      line-height: 1.5;
    }
    .article-title a {
      color: #111827;
      text-decoration: none;
    }
    .article-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 10px;
      font-size: 0.9rem;
      color: #6b7280;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    .badge.breaker { background: #dbeafe; color: #1d4ed8; }
    .badge.duplicate { background: #fee2e2; color: #b91c1c; }
    .badge.source { background: #f3f4f6; color: #374151; }
    .empty-state {
      padding: 30px;
      text-align: center;
      color: #6b7280;
      font-size: 1rem;
    }
    .exchange-select {
      width: 100%;
      padding: 12px 14px;
      border-radius: 12px;
      border: none;
      background: #1f2937;
      color: #e5e7eb;
      font-size: 0.95rem;
      cursor: pointer;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%239ca3af' d='M6 8L0 0h12z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 14px center;
      padding-right: 36px;
    }
    .exchange-select:focus { outline: 2px solid #2563eb; }
    .exchange-select option { background: #1f2937; color: #e5e7eb; }
  </style>
</head>
<body>
  <aside class="sidebar">
    <div class="brand">News Extractor</div>
    <div>
      <h2>Main</h2>
      <div id="nav-buttons-main"></div>
    </div>
    <div>
      <h2>Stock Markets</h2>
      <select class="exchange-select" id="exchange-select">
        <option value="">— Select Exchange —</option>
        <option value="bse">BSE (Sensex)</option>
        <option value="nse">NSE (Nifty)</option>
        <option value="nyse">NYSE</option>
        <option value="nasdaq">NASDAQ</option>
        <option value="lse">LSE (FTSE)</option>
        <option value="tse">Tokyo (Nikkei)</option>
        <option value="sse">Shanghai (CSI)</option>
        <option value="hkex">Hong Kong (Hang Seng)</option>
        <option value="euronext">Euronext (CAC/DAX)</option>
        <option value="sgx">SGX (Singapore)</option>
      </select>
    </div>
    <div class="stats-card">
      <strong>Live Summary</strong>
      <div class="stats-list" id="summary-stats">
        <div><span>Total</span><span id="stat-total">0</span></div>
        <div><span>Breakers</span><span id="stat-breakers">0</span></div>
        <div><span>Duplicates</span><span id="stat-dups">0</span></div>
      </div>
    </div>
  </aside>
  <main class="main">
    <div class="header-row">
      <div>
        <h1>News Dashboard</h1>
        <div class="subtitle">Category: <strong id="selected-category">All</strong></div>
      </div>
    </div>
    <div class="panel">
      <div id="article-list"></div>
    </div>
  </main>
  <script>
    const categories = [
      { id: '', label: 'All', group: 'main' },
      { id: 'market', label: 'Market', group: 'main' },
      { id: 'national', label: 'National', group: 'main' },
      { id: 'global', label: 'Global', group: 'main' },
      { id: 'sports', label: 'Sports', group: 'main' },
      { id: 'entertainment_india', label: 'Entertainment (India)', group: 'main' },
      { id: 'entertainment_global', label: 'Entertainment (Global)', group: 'main' },
      { id: 'economics_india', label: 'Economics (India)', group: 'main' },
      { id: 'economics_global', label: 'Economics (Global)', group: 'main' }
    ];

    let currentCategory = '';
    let currentExchange = '';

    function createNav() {
      const mainNav = document.getElementById('nav-buttons-main');
      mainNav.innerHTML = '';
      categories.forEach(cat => {
        const button = document.createElement('button');
        button.className = 'nav-button';
        button.textContent = cat.label;
        button.dataset.category = cat.id;
        button.dataset.label = cat.label;
        button.addEventListener('click', () => {
          currentCategory = cat.id;
          currentExchange = '';
          document.getElementById('exchange-select').value = '';
          updateActiveButton();
          loadArticles();
        });
        mainNav.appendChild(button);
      });

      document.getElementById('exchange-select').addEventListener('change', (e) => {
        currentExchange = e.target.value;
        if (currentExchange) {
          currentCategory = '';
          updateActiveButton();
          loadArticles();
          const label = e.target.options[e.target.selectedIndex].text;
          document.getElementById('selected-category').textContent = label;
        }
      });
    }

    function updateActiveButton() {
      let label = 'All';
      document.querySelectorAll('.nav-button').forEach(button => {
        const active = button.dataset.category === currentCategory;
        button.classList.toggle('active', active);
        if (active) {
          label = button.dataset.label || 'All';
        }
      });
      document.getElementById('selected-category').textContent = label;
    }

    function renderArticles(articles) {
      const container = document.getElementById('article-list');
      if (!articles.length) {
        container.innerHTML = '<div class="empty-state">No articles found for this category yet.</div>';
        return;
      }

      container.innerHTML = articles.map(article => {
        const tags = article.tags || '';
        return `
          <div class="article-card">
            <h3 class="article-title"><a href="${article.link || '#'}" target="_blank" rel="noreferrer">${article.title}</a></h3>
            <div class="article-meta">
              <span class="badge source">${article.source}</span>
              <span>${new Date(article.saved_at).toLocaleString()}</span>
              <span>${tags}</span>
              ${article.is_breaker ? '<span class="badge breaker">Breaker</span>' : ''}
              ${article.is_duplicate ? '<span class="badge duplicate">Duplicate</span>' : ''}
            </div>
          </div>
        `;
      }).join('');
    }

    async function loadArticles() {
      let query = '';
      if (currentExchange) {
        query = `?exchange=${encodeURIComponent(currentExchange)}`;
      } else if (currentCategory) {
        query = `?category=${encodeURIComponent(currentCategory)}`;
      }
      const response = await fetch('/api/articles' + query);
      const data = await response.json();
      renderArticles(data.articles || []);
    }

    async function loadStats() {
      const response = await fetch('/api/stats');
      const data = await response.json();
      document.getElementById('stat-total').textContent = data.total;
      document.getElementById('stat-breakers').textContent = data.breakers;
      document.getElementById('stat-dups').textContent = data.duplicates;
    }

    async function refresh() {
      await Promise.all([loadArticles(), loadStats()]);
    }

    createNav();
    updateActiveButton();
    refresh();
    setInterval(refresh, 15000);
  </script>
</body>
</html>
"""


def _api_articles(query):
    category = query.get("category", [""])[0].strip() or None
    tag = query.get("tag", [""])[0].strip() or None
    exchange_id = query.get("exchange", [""])[0].strip() or None
    keyword_terms = None
    if exchange_id and exchange_id in config.STOCK_EXCHANGES:
        keyword_terms = config.STOCK_EXCHANGES[exchange_id]["keywords"]
    articles = storage.get_latest(limit=100, category=category, tag=tag, keyword_terms=keyword_terms)
    label = config.STOCK_EXCHANGES[exchange_id]["label"] if exchange_id and exchange_id in config.STOCK_EXCHANGES else (tag or category or "all")
    return {"articles": articles, "category": label}


def _api_stats(query):
    return storage.get_stats()


def main():
    storage.init_db()
    app = WebGUIApp(
        title="News Extractor GUI",
        html=HTML,
        route_handlers={
            "/api/articles": _api_articles,
            "/api/stats": _api_stats,
        },
    )
    app.run()


if __name__ == "__main__":
    main()
