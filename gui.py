import config
import storage
from pywebgui import WebGUIApp

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Extractor</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
      --sidebar-bg: #0f172a;
      --accent: #3b82f6;
      --hot: #f97316;
      --bg: #f1f5f9;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
    }
    body {
      display: flex;
      height: 100vh;
      overflow: hidden;
      background: var(--bg);
      color: var(--text);
    }

    /* ── SIDEBAR ── */
    .sidebar {
      width: 252px;
      min-width: 252px;
      background: var(--sidebar-bg);
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .sidebar-header {
      padding: 18px 16px 14px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 9px;
      font-size: 1rem;
      font-weight: 800;
      color: #fff;
      letter-spacing: 0.06em;
    }
    .brand-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--accent);
      animation: pulse 2s infinite;
      flex-shrink: 0;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

    .sidebar-nav {
      flex: 1;
      overflow-y: auto;
      padding: 8px 10px 4px;
      scrollbar-width: thin;
      scrollbar-color: rgba(255,255,255,0.08) transparent;
    }
    .sidebar-nav::-webkit-scrollbar { width: 3px; }
    .sidebar-nav::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

    .nav-section-label {
      font-size: 0.68rem;
      font-weight: 700;
      color: #334155;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      padding: 12px 8px 5px;
    }
    .nav-btn {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 9px;
      padding: 8px 10px;
      border: none;
      border-radius: 7px;
      background: transparent;
      color: #64748b;
      font-size: 0.855rem;
      cursor: pointer;
      transition: background 0.12s, color 0.12s;
      text-align: left;
    }
    .nav-btn:hover  { background: rgba(255,255,255,0.05); color: #cbd5e1; }
    .nav-btn.active { background: var(--accent); color: #fff; }
    .nav-btn .icon  { font-size: 0.95rem; width: 18px; text-align: center; flex-shrink: 0; }

    .exchange-wrap { padding: 0 10px 10px; }
    .exchange-select {
      width: 100%;
      padding: 8px 30px 8px 11px;
      border-radius: 7px;
      border: 1px solid rgba(255,255,255,0.07);
      background: #1e293b;
      color: #64748b;
      font-size: 0.855rem;
      cursor: pointer;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath fill='%2364748b' d='M5 6L0 0h10z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 10px center;
    }
    .exchange-select:focus { outline: 2px solid var(--accent); color: #e2e8f0; }
    .exchange-select option { background: #1e293b; }

    .sidebar-stats {
      padding: 10px 16px 14px;
      border-top: 1px solid rgba(255,255,255,0.06);
      display: grid;
      gap: 7px;
    }
    .stat-row { display: flex; justify-content: space-between; align-items: center; }
    .stat-label { font-size: 0.75rem; color: #334155; }
    .stat-value { font-size: 0.82rem; font-weight: 700; color: #64748b; }

    /* ── MAIN ── */
    .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

    .topbar {
      background: #fff;
      border-bottom: 1px solid var(--border);
      padding: 12px 22px;
      display: flex;
      align-items: center;
      gap: 14px;
      flex-shrink: 0;
    }
    .topbar-info { min-width: 0; }
    .topbar-title { font-size: 1.05rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .topbar-sub   { font-size: 0.75rem; color: var(--text-muted); margin-top: 1px; }

    .search-wrap { flex: 1; max-width: 360px; position: relative; }
    .search-input {
      width: 100%;
      padding: 7px 12px 7px 32px;
      border: 1px solid var(--border);
      border-radius: 7px;
      background: var(--bg);
      font-size: 0.855rem;
      color: var(--text);
      outline: none;
      transition: border-color 0.15s;
    }
    .search-input:focus { border-color: var(--accent); background: #fff; }
    .search-icon {
      position: absolute;
      left: 10px; top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 0.85rem;
      pointer-events: none;
    }

    .topbar-right { display: flex; align-items: center; gap: 10px; margin-left: auto; flex-shrink: 0; }
    .count-badge {
      padding: 3px 9px;
      border-radius: 999px;
      background: var(--bg);
      border: 1px solid var(--border);
      font-size: 0.75rem;
      color: var(--text-muted);
      white-space: nowrap;
    }
    .refresh-pill {
      font-size: 0.72rem;
      color: var(--text-muted);
      white-space: nowrap;
    }
    .spinner {
      width: 15px; height: 15px;
      border: 2px solid var(--border);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.65s linear infinite;
      display: none;
    }
    .spinner.active { display: block; }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── CONTENT ── */
    .content {
      flex: 1;
      overflow-y: auto;
      padding: 18px 22px;
      scrollbar-width: thin;
      scrollbar-color: var(--border) transparent;
    }
    .content::-webkit-scrollbar { width: 5px; }
    .content::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

    /* ── ARTICLE CARDS ── */
    .article-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 8px;
      transition: box-shadow 0.15s, transform 0.15s;
    }
    .article-card:hover { box-shadow: 0 3px 16px rgba(0,0,0,0.07); transform: translateY(-1px); }
    .article-card.hot-card { border-left: 3px solid var(--hot); }

    .article-title { font-size: 0.935rem; font-weight: 600; line-height: 1.5; margin-bottom: 7px; }
    .article-title a { color: var(--text); text-decoration: none; }
    .article-title a:hover { color: var(--accent); }

    .article-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
    .badge {
      display: inline-flex; align-items: center;
      padding: 2px 7px; border-radius: 999px;
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.02em; white-space: nowrap;
    }
    .badge-source   { background: #f1f5f9; color: #475569; }
    .badge-hot      { background: #fff7ed; color: #c2410c; }
    .badge-breaker  { background: #eff6ff; color: #1d4ed8; }
    .badge-dup      { background: #fef2f2; color: #b91c1c; }
    .tag-chip       { padding: 2px 6px; border-radius: 999px; background: #f8fafc; color: #94a3b8; font-size: 0.68rem; border: 1px solid var(--border); }
    .time-ago       { font-size: 0.75rem; color: #94a3b8; }

    .empty-state { text-align: center; padding: 56px 20px; color: var(--text-muted); }
    .empty-icon  { font-size: 2.4rem; margin-bottom: 10px; }
    .empty-state p { font-size: 0.9rem; }

    /* ── FILTER BAR ── */
    .filterbar {
      background: #fff;
      border-bottom: 1px solid var(--border);
      padding: 8px 22px;
      display: flex;
      align-items: center;
      gap: 20px;
      flex-shrink: 0;
      flex-wrap: wrap;
    }
    .filter-group { display: flex; align-items: center; gap: 6px; }
    .filter-label { font-size: 0.72rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; white-space: nowrap; }
    .filter-divider { width: 1px; height: 20px; background: var(--border); }
    .pill-group { display: flex; gap: 3px; }
    .pill {
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: transparent;
      font-size: 0.775rem;
      color: var(--text-muted);
      cursor: pointer;
      transition: background 0.12s, color 0.12s, border-color 0.12s;
      white-space: nowrap;
    }
    .pill:hover  { background: var(--bg); color: var(--text); }
    .pill.active { background: var(--accent); color: #fff; border-color: var(--accent); }
    .sort-select {
      padding: 4px 24px 4px 9px;
      border-radius: 7px;
      border: 1px solid var(--border);
      background: transparent;
      font-size: 0.775rem;
      color: var(--text-muted);
      cursor: pointer;
      outline: none;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='9' height='5' viewBox='0 0 9 5'%3E%3Cpath fill='%2394a3b8' d='M4.5 5L0 0h9z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 8px center;
    }
    .sort-select:focus { border-color: var(--accent); color: var(--text); }
  </style>
</head>
<body>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand">
        <span class="brand-dot"></span>
        NEWS EXTRACTOR
      </div>
    </div>

    <div class="sidebar-nav">
      <div class="nav-section-label">Feeds</div>
      <div id="nav-buttons"></div>

      <div class="nav-section-label" style="margin-top:6px;">Stock Markets</div>
      <div class="exchange-wrap">
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
    </div>

    <div class="sidebar-stats">
      <div class="stat-row"><span class="stat-label">Total Articles</span><span class="stat-value" id="stat-total">—</span></div>
      <div class="stat-row"><span class="stat-label">First Breaks</span><span class="stat-value" id="stat-breakers">—</span></div>
      <div class="stat-row"><span class="stat-label">Duplicates</span><span class="stat-value" id="stat-dups">—</span></div>
    </div>
  </aside>

  <div class="main">
    <div class="topbar">
      <div class="topbar-info">
        <div class="topbar-title" id="topbar-title">All News</div>
        <div class="topbar-sub"  id="topbar-sub">Loading…</div>
      </div>
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input class="search-input" id="search-input" type="text" placeholder="Search articles…">
      </div>
      <div class="topbar-right">
        <span class="count-badge" id="count-badge"></span>
        <span class="refresh-pill" id="refresh-pill"></span>
        <div class="spinner" id="spinner"></div>
      </div>
    </div>

    <div class="filterbar">
      <div class="filter-group">
        <span class="filter-label">Sort</span>
        <select class="sort-select" id="sort-select">
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
          <option value="source_az">Source A–Z</option>
          <option value="source_za">Source Z–A</option>
        </select>
      </div>
      <div class="filter-divider"></div>
      <div class="filter-group">
        <span class="filter-label">Time</span>
        <div class="pill-group" id="time-pills">
          <button class="pill active" data-hours="">All</button>
          <button class="pill" data-hours="1">1h</button>
          <button class="pill" data-hours="6">6h</button>
          <button class="pill" data-hours="24">24h</button>
          <button class="pill" data-hours="168">7d</button>
        </div>
      </div>
      <div class="filter-divider"></div>
      <div class="filter-group">
        <span class="filter-label">Type</span>
        <div class="pill-group" id="type-pills">
          <button class="pill active" data-type="all">All</button>
          <button class="pill" data-type="hot">🔥 Hot</button>
          <button class="pill" data-type="breakers">⚡ Breakers</button>
          <button class="pill" data-type="nodups">Hide Dups</button>
        </div>
      </div>
    </div>

    <div class="content">
      <div id="article-list"></div>
    </div>
  </div>

  <script>
    const CATEGORIES = [
      { id: '',                    label: 'All News',               icon: '📰' },
      { id: '__hot__',             label: 'Hot News',               icon: '🔥' },
      { id: 'market',              label: 'Market',                 icon: '📈' },
      { id: 'national',            label: 'National',               icon: '🇮🇳' },
      { id: 'global',              label: 'Global',                 icon: '🌐' },
      { id: 'sports',              label: 'Sports',                 icon: '🏏' },
      { id: 'entertainment_india', label: 'Entertainment (India)',  icon: '🎬' },
      { id: 'entertainment_global',label: 'Entertainment (Global)', icon: '🎭' },
      { id: 'economics_india',     label: 'Economics (India)',      icon: '🏦' },
      { id: 'economics_global',    label: 'Economics (Global)',     icon: '💹' },
    ];

    let currentCategory = '';
    let currentExchange = '';
    let allArticles = [];
    let countdown = 15;
    let countdownTimer = null;

    let sortBy    = 'newest';
    let timeHours = '';
    let typeFilter = 'all';

    function timeAgo(iso) {
      const s = Math.floor((Date.now() - new Date(iso)) / 1000);
      if (s < 60)    return s + 's ago';
      if (s < 3600)  return Math.floor(s / 60)   + 'm ago';
      if (s < 86400) return Math.floor(s / 3600)  + 'h ago';
      return Math.floor(s / 86400) + 'd ago';
    }

    function buildNav() {
      const wrap = document.getElementById('nav-buttons');
      CATEGORIES.forEach(cat => {
        const btn = document.createElement('button');
        btn.className = 'nav-btn' + (cat.id === currentCategory ? ' active' : '');
        btn.dataset.id = cat.id;
        btn.innerHTML = `<span class="icon">${cat.icon}</span>${cat.label}`;
        btn.addEventListener('click', () => {
          currentCategory = cat.id;
          currentExchange  = '';
          document.getElementById('exchange-select').value = '';
          syncNav();
          fetchArticles();
        });
        wrap.appendChild(btn);
      });

      document.getElementById('exchange-select').addEventListener('change', e => {
        currentExchange = e.target.value;
        if (currentExchange) { currentCategory = ''; syncNav(); fetchArticles(); }
      });

      document.getElementById('search-input').addEventListener('input', renderArticles);

      document.getElementById('sort-select').addEventListener('change', e => {
        sortBy = e.target.value;
        renderArticles();
      });

      document.querySelectorAll('#time-pills .pill').forEach(p => {
        p.addEventListener('click', () => {
          document.querySelectorAll('#time-pills .pill').forEach(x => x.classList.remove('active'));
          p.classList.add('active');
          timeHours = p.dataset.hours;
          renderArticles();
        });
      });

      document.querySelectorAll('#type-pills .pill').forEach(p => {
        p.addEventListener('click', () => {
          document.querySelectorAll('#type-pills .pill').forEach(x => x.classList.remove('active'));
          p.classList.add('active');
          typeFilter = p.dataset.type;
          renderArticles();
        });
      });
    }

    function syncNav() {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.id === currentCategory));
      const cat   = CATEGORIES.find(c => c.id === currentCategory);
      const exSel = document.getElementById('exchange-select');
      const title = currentExchange
        ? exSel.options[exSel.selectedIndex].text
        : (cat ? cat.label : 'All News');
      document.getElementById('topbar-title').textContent = title;
    }

    function applyFiltersAndSort(articles) {
      let list = [...articles];

      // search
      const q = document.getElementById('search-input').value.toLowerCase().trim();
      if (q) list = list.filter(a => a.title.toLowerCase().includes(q));

      // time range
      if (timeHours) {
        const cutoff = Date.now() - parseInt(timeHours) * 3600 * 1000;
        list = list.filter(a => new Date(a.saved_at).getTime() >= cutoff);
      }

      // type
      if (typeFilter === 'hot')      list = list.filter(a => a.is_hot);
      if (typeFilter === 'breakers') list = list.filter(a => a.is_breaker);
      if (typeFilter === 'nodups')   list = list.filter(a => !a.is_duplicate);

      // sort
      if (sortBy === 'newest')    list.sort((a,b) => new Date(b.saved_at) - new Date(a.saved_at));
      if (sortBy === 'oldest')    list.sort((a,b) => new Date(a.saved_at) - new Date(b.saved_at));
      if (sortBy === 'source_az') list.sort((a,b) => a.source.localeCompare(b.source));
      if (sortBy === 'source_za') list.sort((a,b) => b.source.localeCompare(a.source));

      return list;
    }

    function renderArticles() {
      const list = applyFiltersAndSort(allArticles);
      const wrap = document.getElementById('article-list');
      const q    = document.getElementById('search-input').value.trim();

      document.getElementById('count-badge').textContent =
        list.length + ' article' + (list.length !== 1 ? 's' : '');

      if (!list.length) {
        wrap.innerHTML = `<div class="empty-state">
          <div class="empty-icon">📭</div>
          <p>${q || timeHours || typeFilter !== 'all'
            ? 'No articles match the current filters.'
            : 'No articles yet for this category.'}</p>
        </div>`;
        return;
      }

      wrap.innerHTML = list.map(a => {
        const tags     = (a.tags || '').split(',').map(t => t.trim()).filter(Boolean);
        const tagChips = tags.slice(0, 4).map(t => `<span class="tag-chip">${t}</span>`).join('');
        const hotCls   = a.is_hot ? ' hot-card' : '';
        return `
          <div class="article-card${hotCls}">
            <div class="article-title">
              <a href="${a.link || '#'}" target="_blank" rel="noreferrer">${a.title}</a>
            </div>
            <div class="article-meta">
              <span class="badge badge-source">${a.source}</span>
              <span class="time-ago">${timeAgo(a.saved_at)}</span>
              ${tagChips}
              ${a.is_hot       ? '<span class="badge badge-hot">🔥 Hot</span>'            : ''}
              ${a.is_breaker   ? '<span class="badge badge-breaker">⚡ First Break</span>' : ''}
              ${a.is_duplicate ? '<span class="badge badge-dup">Duplicate</span>'          : ''}
            </div>
          </div>`;
      }).join('');
    }

    async function fetchArticles() {
      document.getElementById('spinner').classList.add('active');
      document.getElementById('topbar-sub').textContent = 'Loading…';
      let q = '';
      if (currentExchange)              q = `?exchange=${encodeURIComponent(currentExchange)}`;
      else if (currentCategory === '__hot__') q = '?hot=1';
      else if (currentCategory)         q = `?category=${encodeURIComponent(currentCategory)}`;
      try {
        const res  = await fetch('/api/articles' + q);
        const data = await res.json();
        allArticles = data.articles || [];
        renderArticles();
        document.getElementById('topbar-sub').textContent =
          'Updated ' + new Date().toLocaleTimeString();
      } catch {
        document.getElementById('topbar-sub').textContent = 'Error — retrying…';
      }
      document.getElementById('spinner').classList.remove('active');
      resetCountdown();
    }

    async function fetchStats() {
      try {
        const res  = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('stat-total').textContent    = data.total.toLocaleString();
        document.getElementById('stat-breakers').textContent = data.breakers.toLocaleString();
        document.getElementById('stat-dups').textContent     = data.duplicates.toLocaleString();
      } catch {}
    }

    function resetCountdown() {
      countdown = 15;
      clearInterval(countdownTimer);
      countdownTimer = setInterval(() => {
        countdown--;
        document.getElementById('refresh-pill').textContent = 'Refresh in ' + countdown + 's';
        if (countdown <= 0) { fetchArticles(); fetchStats(); }
      }, 1000);
    }

    buildNav();
    syncNav();
    fetchArticles();
    fetchStats();
  </script>
</body>
</html>
"""


def _api_articles(query):
    category    = query.get("category",  [""])[0].strip() or None
    tag         = query.get("tag",       [""])[0].strip() or None
    exchange_id = query.get("exchange",  [""])[0].strip() or None
    hot_only    = query.get("hot",       [""])[0].strip() == "1"
    keyword_terms = None
    if exchange_id and exchange_id in config.STOCK_EXCHANGES:
        keyword_terms = config.STOCK_EXCHANGES[exchange_id]["keywords"]
    articles = storage.get_latest(limit=100, category=category, tag=tag,
                                  keyword_terms=keyword_terms, hot_only=hot_only)
    if hot_only:
        label = "Hot News"
    elif exchange_id and exchange_id in config.STOCK_EXCHANGES:
        label = config.STOCK_EXCHANGES[exchange_id]["label"]
    else:
        label = tag or category or "all"
    return {"articles": articles, "category": label}


def _api_stats(query):
    return storage.get_stats()


def main():
    storage.init_db()
    app = WebGUIApp(
        title="News Extractor",
        html=HTML,
        route_handlers={
            "/api/articles": _api_articles,
            "/api/stats":    _api_stats,
        },
    )
    app.run()


if __name__ == "__main__":
    main()
