// ThreadHunter Client Application

const state = {
  currentTab: 'chat',
  activeModel: 'gemini-2.5-flash',
  deals: [],
  watchlist: [],
  stats: null,
  isSearchingLive: false,
  isSendingChat: false,
  filters: {
    q: '',
    category: 'All',
    brand: 'All',
    store: 'All',
    gender: 'All',
    min_discount: 0,
    max_price: null,
    sort_by: 'discount_pct'
  }
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  loadModelStatus();
  loadDeals();
  loadWatchlist();
  loadDashboardStats();
  initChatInput();
  initFilters();
});

// --- Tab Switching ---
function initTabs() {
  const navButtons = document.querySelectorAll('.nav-btn');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  state.currentTab = tabId;
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('bg-indigo-600', 'text-white');
    btn.classList.add('text-slate-400', 'hover:text-white', 'hover:bg-slate-800/60');
  });

  const activeTab = document.getElementById(`tab-${tabId}`);
  if (activeTab) activeTab.classList.remove('hidden');

  const activeBtn = document.querySelector(`.nav-btn[data-tab="${tabId}"]`);
  if (activeBtn) {
    activeBtn.classList.add('bg-indigo-600', 'text-white');
    activeBtn.classList.remove('text-slate-400');
  }

  if (tabId === 'analytics') {
    loadDashboardStats();
  } else if (tabId === 'watchlist') {
    loadWatchlist();
  } else if (tabId === 'settings') {
    loadModelStatus();
  }
}

// --- Toast System ---
function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toast-msg');
  if (!toast || !toastMsg) return;

  toastMsg.textContent = message;
  toast.className = `glass-panel px-5 py-3 rounded-xl border flex items-center gap-3 show ${
    type === 'error' ? 'border-rose-500/50 text-rose-300' : 'border-emerald-500/50 text-emerald-300'
  }`;

  setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}

// --- API Helpers ---
async function apiGet(endpoint) {
  try {
    const res = await fetch(endpoint);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Error in GET ${endpoint}:`, err);
    return null;
  }
}

async function apiPost(endpoint, body) {
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`Error in POST ${endpoint}:`, err);
    throw err;
  }
}

// --- Model Status & Rate-Limit Switching ---
async function loadModelStatus() {
  const data = await apiGet('/api/model/status');
  if (!data) return;

  state.activeModel = data.current_model;
  
  // Update header badges
  const modelPill = document.getElementById('header-active-model');
  if (modelPill) modelPill.textContent = data.current_model;

  const keyCountBadge = document.getElementById('keys-count-badge');
  if (keyCountBadge) {
    if (data.configured_keys_count > 0) {
      keyCountBadge.innerHTML = `<span class="inline-block w-2 h-2 rounded-full bg-emerald-400 mr-1.5 pulse-emerald"></span>${data.configured_keys_count} API Key(s) Active`;
      keyCountBadge.className = 'text-xs px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 flex items-center';
    } else {
      keyCountBadge.innerHTML = `<span class="inline-block w-2 h-2 rounded-full bg-amber-400 mr-1.5"></span>Free Offline Heuristic Mode`;
      keyCountBadge.className = 'text-xs px-2.5 py-1 rounded-full bg-amber-950/60 border border-amber-500/30 text-amber-300 flex items-center';
    }
  }

  // Populate model selector in settings tab
  const modelSelect = document.getElementById('settings-model-select');
  if (modelSelect && data.fallback_chain) {
    modelSelect.innerHTML = data.fallback_chain.map(m => 
      `<option value="${m}" ${m === data.current_model ? 'selected' : ''}>${m} ${m === data.fallback_chain[0] ? '(Primary)' : ''}</option>`
    ).join('');
  }

  // Render switch logs table
  renderSwitchLogs(data.recent_switches || []);
}

function renderSwitchLogs(logs) {
  const tbody = document.getElementById('switch-logs-tbody');
  if (!tbody) return;

  if (logs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-slate-500 text-xs">No model switches recorded yet. Normal operation.</td></tr>`;
    return;
  }

  tbody.innerHTML = logs.map(l => `
    <tr class="border-b border-white/5 hover:bg-white/5 transition-colors text-xs">
      <td class="py-2.5 px-3 text-slate-400 font-mono">${l.timestamp}</td>
      <td class="py-2.5 px-3">
        <span class="px-2 py-0.5 rounded bg-rose-950/50 text-rose-300 border border-rose-500/20 font-mono">${l.from_model}</span>
        <span class="mx-1 text-slate-500">→</span>
        <span class="px-2 py-0.5 rounded bg-emerald-950/50 text-emerald-300 border border-emerald-500/20 font-mono">${l.to_model}</span>
      </td>
      <td class="py-2.5 px-3 text-slate-300">${l.trigger_reason}</td>
      <td class="py-2.5 px-3">
        <span class="px-2 py-0.5 rounded text-[11px] ${l.success ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400'}">
          ${l.success ? 'Success' : 'Failed'}
        </span>
      </td>
    </tr>
  `).join('');
}

// Trigger Simulated Rate Limit
async function simulateRateLimit() {
  try {
    const res = await apiPost('/api/model/simulate-ratelimit', {});
    showToast(`⚡ Switched to ${res.to_model} due to simulated 429 quota limit!`, 'success');
    await loadModelStatus();
  } catch (err) {
    showToast('Failed to trigger simulation', 'error');
  }
}

// Update Active Model manually
async function updateActiveModel() {
  const select = document.getElementById('settings-model-select');
  if (!select) return;
  try {
    const res = await apiPost('/api/model/set-active', { target_model: select.value });
    showToast(`Active model changed to ${res.current_model}`, 'success');
    await loadModelStatus();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Save API Keys
async function saveApiKeys() {
  const input = document.getElementById('gemini-api-keys-input');
  if (!input) return;
  const raw = input.value.trim();
  const keys = raw.split(',').map(k => k.trim()).filter(Boolean);

  try {
    const res = await apiPost('/api/settings/keys', { keys });
    showToast(res.message, 'success');
    input.value = '';
    await loadModelStatus();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// --- Deal Explorer & Filtering ---
async function loadDeals() {
  const { q, category, brand, store, gender, min_discount, max_price, sort_by } = state.filters;
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (category && category !== 'All') params.set('category', category);
  if (brand && brand !== 'All') params.set('brand', brand);
  if (store && store !== 'All') params.set('store', store);
  if (gender && gender !== 'All') params.set('gender', gender);
  if (min_discount > 0) params.set('min_discount', min_discount);
  if (max_price) params.set('max_price', max_price);
  if (sort_by) params.set('sort_by', sort_by);
  params.set('limit', '40');

  const deals = await apiGet(`/api/deals?${params.toString()}`);
  state.deals = deals || [];
  renderDealsGrid(state.deals);
}

function initFilters() {
  // Search input debounced
  const searchInput = document.getElementById('deal-search-input');
  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        state.filters.q = e.target.value.trim();
        loadDeals();
      }, 300);
    });
  }

  // Category pills
  const catButtons = document.querySelectorAll('.cat-pill');
  catButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      catButtons.forEach(b => {
        b.classList.remove('bg-indigo-600', 'text-white', 'border-indigo-500');
        b.classList.add('bg-slate-800/60', 'text-slate-300', 'border-white/10');
      });
      btn.classList.add('bg-indigo-600', 'text-white', 'border-indigo-500');
      btn.classList.remove('bg-slate-800/60', 'text-slate-300');
      state.filters.category = btn.dataset.category;
      loadDeals();
    });
  });

  // Select filters
  const storeSelect = document.getElementById('filter-store');
  if (storeSelect) {
    storeSelect.addEventListener('change', (e) => {
      state.filters.store = e.target.value;
      loadDeals();
    });
  }

  const genderSelect = document.getElementById('filter-gender');
  if (genderSelect) {
    genderSelect.addEventListener('change', (e) => {
      state.filters.gender = e.target.value;
      loadDeals();
    });
  }

  const sortSelect = document.getElementById('filter-sort');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.filters.sort_by = e.target.value;
      loadDeals();
    });
  }

  // Discount slider
  const discSlider = document.getElementById('filter-discount-slider');
  const discLabel = document.getElementById('filter-discount-val');
  if (discSlider) {
    discSlider.addEventListener('input', (e) => {
      discLabel.textContent = `${e.target.value}%+`;
      state.filters.min_discount = parseInt(e.target.value, 10);
      loadDeals();
    });
  }
}

function renderDealsGrid(deals) {
  const grid = document.getElementById('deals-grid');
  const countLabel = document.getElementById('deals-count-label');
  if (!grid) return;

  if (countLabel) countLabel.textContent = `${deals.length} deals available`;

  if (deals.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full py-16 text-center glass-panel rounded-2xl border border-white/5">
        <div class="w-16 h-16 rounded-full bg-slate-800/80 mx-auto flex items-center justify-center text-2xl mb-4">🔍</div>
        <h4 class="text-lg font-bold text-slate-200">No deals match this exact filter</h4>
        <p class="text-sm text-slate-400 mt-1 max-w-md mx-auto">Try lowering the discount threshold or click below to trigger a live web search for this apparel item!</p>
        <button onclick="triggerLiveSearchPrompt()" class="mt-4 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-500/20">
          🌐 Run Live Web Deal Search
        </button>
      </div>
    `;
    return;
  }

  grid.innerHTML = deals.map(deal => createDealCardHTML(deal)).join('');
}

function createDealCardHTML(deal) {
  return `
    <div class="deal-card glass-panel rounded-2xl overflow-hidden border border-white/10 glass-panel-hover flex flex-col justify-between">
      <div>
        <div class="deal-img-container bg-slate-900 relative">
          <img src="${deal.image_url || 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600'}" alt="${deal.title}" class="deal-img" loading="lazy">
          <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
            <span class="badge-discount px-2.5 py-1 rounded-lg text-xs shadow-md">-${deal.discount_pct}%</span>
            ${deal.badge && deal.badge.includes('Live Web') 
              ? `<span class="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-600/90 text-white border border-emerald-400/40 shadow-lg shadow-emerald-500/20 backdrop-blur-md">${deal.badge}</span>`
              : (deal.badge ? `<span class="badge-steal px-2.5 py-1 rounded-lg text-xs font-semibold backdrop-blur-md">${deal.badge}</span>` : '<span class="px-2 py-0.5 rounded-lg text-[10px] bg-slate-900/80 text-slate-400 border border-white/10 backdrop-blur-md">🏷️ Benchmark</span>')
            }
          </div>
          <span class="absolute top-3 right-3 px-2 py-0.5 rounded-md bg-black/60 backdrop-blur-md text-slate-300 text-[11px] font-medium border border-white/10">
            ${deal.store}
          </span>
        </div>
        <div class="p-4">
          <div class="flex items-center justify-between text-xs text-indigo-400 font-semibold mb-1">
            <span>${deal.brand}</span>
            <span class="text-amber-400 flex items-center gap-1">★ ${deal.rating || 4.5}</span>
          </div>
          <h3 class="font-bold text-slate-100 text-sm leading-snug line-clamp-2 h-10 mb-2" title="${deal.title}">
            ${deal.title}
          </h3>
          
          <div class="flex items-baseline gap-2 mb-3">
            <span class="text-xl font-extrabold text-emerald-400">$${deal.discount_price.toFixed(2)}</span>
            <span class="text-xs text-slate-500 line-through">$${deal.original_price.toFixed(2)}</span>
            <span class="text-[11px] text-slate-400 ml-auto">Sizes: ${deal.sizes.split(',')[0]}...</span>
          </div>

          ${deal.coupon_code ? `
            <div class="mb-3 p-2 rounded-lg bg-indigo-950/40 border border-dashed border-indigo-500/30 flex items-center justify-between">
              <span class="text-xs text-indigo-300 font-mono">Code: <strong class="text-indigo-200">${deal.coupon_code}</strong></span>
              <button onclick="copyToClipboard('${deal.coupon_code}')" class="text-[11px] px-2 py-0.5 rounded bg-indigo-600/40 hover:bg-indigo-600 text-indigo-200 hover:text-white transition-colors">
                Copy
              </button>
            </div>
          ` : '<div class="h-4"></div>'}
        </div>
      </div>

      <div class="p-4 pt-0 border-t border-white/5 mt-auto flex items-center gap-2">
        <a href="${deal.url}" target="_blank" rel="noopener noreferrer" class="flex-1 text-center py-2 px-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 hover:text-white text-xs font-semibold transition-colors border border-white/10">
          View Store ↗
        </a>
        <button onclick="addToWatchlist('${deal.id}')" title="Track Deal / Add to Watchlist" class="p-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600 text-indigo-400 hover:text-white transition-all border border-indigo-500/30">
          ⭐
        </button>
      </div>
    </div>
  `;
}

// Copy Code Helper
function copyToClipboard(text) {
  navigator.clipboard.writeText(text);
  showToast(`Copied code "${text}" to clipboard!`, 'success');
}

// Fetch Live Deals from Online Feeds
async function fetchLiveDealsFromFeeds() {
  showToast('📡 Connecting to live fashion clearance feeds...', 'success');
  try {
    const res = await apiPost('/api/deals/fetch-live-web', {});
    if (res.count > 0) {
      showToast(`🎉 Harvested ${res.count} live clothing deals directly from the web!`, 'success');
      await loadDeals();
      await loadDashboardStats();
    } else {
      showToast('Checked live feeds! Existing catalog is up to date.', 'success');
    }
  } catch (err) {
    showToast('Notice: External feeds query failed or offline.', 'error');
  }
}

// Live Search Trigger
async function triggerLiveSearchPrompt() {
  const query = state.filters.q || prompt('Enter clothing item or style to crawl the web for (e.g., "vintage denim jacket", "waterproof trail runners"):');
  if (!query) return;

  showToast(`🔍 Searching web & retailer feeds for "${query}"...`, 'success');
  try {
    const res = await apiPost(`/api/deals/search-live?query=${encodeURIComponent(query)}`, {});
    showToast(`Found new deals! Updated catalog with ${res.newly_discovered.title}`, 'success');
    await loadDeals();
    await loadDashboardStats();
  } catch (err) {
    showToast('Live search error', 'error');
  }
}

// --- Watchlist Management ---
async function loadWatchlist() {
  const list = await apiGet('/api/watchlist');
  state.watchlist = list || [];
  renderWatchlist(state.watchlist);

  const countBadge = document.getElementById('watchlist-badge-count');
  if (countBadge) countBadge.textContent = state.watchlist.length;
}

function renderWatchlist(items) {
  const container = document.getElementById('watchlist-container');
  const totalSavedEl = document.getElementById('watchlist-total-saved');
  if (!container) return;

  const totalSaved = items.reduce((acc, item) => acc + (item.original_price - item.discount_price), 0);
  if (totalSavedEl) totalSavedEl.textContent = `$${totalSaved.toFixed(2)}`;

  if (items.length === 0) {
    container.innerHTML = `
      <div class="py-16 text-center text-slate-500">
        <div class="text-3xl mb-2">⭐</div>
        <p class="font-medium">Your price watch list is empty.</p>
        <p class="text-xs text-slate-400 mt-1">Click the ⭐ button on any deal or in the chatbot to track price drops!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="glass-panel p-4 rounded-xl border border-white/10 flex items-center justify-between gap-4 glass-panel-hover">
      <div class="flex items-center gap-3">
        <img src="${item.image_url || 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600'}" class="w-14 h-14 rounded-lg object-cover bg-slate-900 border border-white/10" alt="${item.title}">
        <div>
          <span class="text-xs text-indigo-400 font-semibold">${item.brand} • ${item.store}</span>
          <h4 class="font-bold text-sm text-slate-100 line-clamp-1">${item.title}</h4>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-emerald-400 font-bold text-sm">$${item.discount_price.toFixed(2)}</span>
            <span class="text-slate-500 line-through text-xs">$${item.original_price.toFixed(2)}</span>
            <span class="text-xs px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-500/20">
              Save $${(item.original_price - item.discount_price).toFixed(2)}
            </span>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold transition-colors">
          Go to Store ↗
        </a>
        <button onclick="removeFromWatchlist('${item.deal_id}')" class="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition-colors" title="Remove">
          ✕
        </button>
      </div>
    </div>
  `).join('');
}

async function addToWatchlist(dealId) {
  try {
    const res = await apiPost('/api/watchlist', { deal_id: dealId });
    showToast(res.message, 'success');
    await loadWatchlist();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function removeFromWatchlist(dealId) {
  try {
    await fetch(`/api/watchlist/${dealId}`, { method: 'DELETE' });
    showToast('Removed from watchlist', 'success');
    await loadWatchlist();
  } catch (err) {
    showToast('Failed to remove deal', 'error');
  }
}

// --- Dashboard & Analytics Stats ---
async function loadDashboardStats() {
  const stats = await apiGet('/api/stats');
  if (!stats) return;

  state.stats = stats;

  const totalDealsEl = document.getElementById('stat-total-deals');
  if (totalDealsEl) totalDealsEl.textContent = stats.total_deals;

  const avgDiscEl = document.getElementById('stat-avg-discount');
  if (avgDiscEl) avgDiscEl.textContent = `${stats.avg_discount}%`;

  const avgPriceEl = document.getElementById('stat-avg-price');
  if (avgPriceEl) avgPriceEl.textContent = `$${stats.avg_price}`;

  const switchesEl = document.getElementById('stat-total-switches');
  if (switchesEl) switchesEl.textContent = stats.total_switches;

  // Initialize or update Chart.js
  if (window.initDashboardCharts) {
    window.initDashboardCharts(stats);
  }

  // Render Top 5 Steals Leaderboard
  const stealsTable = document.getElementById('top-steals-tbody');
  if (stealsTable && stats.top_steals) {
    stealsTable.innerHTML = stats.top_steals.map(d => `
      <tr class="border-b border-white/5 hover:bg-white/5 transition-colors text-xs">
        <td class="py-2.5 px-3 font-semibold text-slate-200">${d.brand}</td>
        <td class="py-2.5 px-3 text-slate-300">${d.title}</td>
        <td class="py-2.5 px-3 text-slate-400">${d.store}</td>
        <td class="py-2.5 px-3 font-mono font-bold text-emerald-400">$${d.discount_price.toFixed(2)}</td>
        <td class="py-2.5 px-3">
          <span class="badge-discount px-2 py-0.5 rounded text-[11px]">-${d.discount_pct}%</span>
        </td>
        <td class="py-2.5 px-3">
          <a href="${d.url}" target="_blank" class="text-indigo-400 hover:text-indigo-300 font-medium">Link ↗</a>
        </td>
      </tr>
    `).join('');
  }
}

// --- Chatbot Functionality ---
function initChatInput() {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  if (form && input) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = input.value.trim();
      if (!message || state.isSendingChat) return;
      input.value = '';
      sendChatMessage(message);
    });
  }
}

function sendPresetPrompt(promptText) {
  const input = document.getElementById('chat-input');
  if (input) {
    input.value = promptText;
    sendChatMessage(promptText);
  }
}

async function sendChatMessage(message) {
  state.isSendingChat = true;
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return;

  // Append user bubble
  appendChatBubble('user', message);

  // Append thinking bubble
  const thinkingId = 'thinking-' + Date.now();
  appendThinkingBubble(thinkingId);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  try {
    const res = await apiPost('/api/chat', {
      message: message,
      preferred_model: state.activeModel
    });

    removeThinkingBubble(thinkingId);

    // Update active model in header if switched
    if (res.model_used) {
      state.activeModel = res.model_used.split(' ')[0];
      const modelPill = document.getElementById('header-active-model');
      if (modelPill) modelPill.textContent = state.activeModel;
    }

    // Append AI response
    appendChatBubble('assistant', res.reply, res.deals, {
      model_used: res.model_used,
      fallback_triggered: res.fallback_triggered,
      fallback_details: res.fallback_details,
      latency_ms: res.latency_ms
    });

    if (res.fallback_triggered) {
      showToast(`🔄 Failover Triggered: ${res.fallback_details || 'Switched model'}`, 'success');
      loadModelStatus();
    }
  } catch (err) {
    removeThinkingBubble(thinkingId);
    appendChatBubble('assistant', `⚠️ Sorry, encountered an issue: ${err.message}. Check your API keys or settings!`);
  } finally {
    state.isSendingChat = false;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}

function appendChatBubble(role, text, deals = [], telemetry = null) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const bubbleDiv = document.createElement('div');
  bubbleDiv.className = `flex gap-3 animate-msg ${role === 'user' ? 'justify-end' : 'justify-start'}`;

  if (role === 'user') {
    bubbleDiv.innerHTML = `
      <div class="max-w-[75%] px-4 py-3 rounded-2xl rounded-tr-sm bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md text-sm leading-relaxed">
        ${escapeHTML(text)}
      </div>
      <div class="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-xs font-bold text-white shrink-0 shadow">
        YOU
      </div>
    `;
  } else {
    // Format markdown-like text
    const formattedHtml = formatChatMarkdown(text);
    
    // Telemetry pill
    let telemetryHtml = '';
    if (telemetry) {
      telemetryHtml = `
        <div class="mt-2.5 pt-2 border-t border-white/5 flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
          <span class="px-2 py-0.5 rounded bg-slate-800 font-mono text-indigo-300 border border-white/5">
            🤖 ${telemetry.model_used}
          </span>
          <span class="text-slate-500">•</span>
          <span>⚡ ${telemetry.latency_ms}ms</span>
          ${telemetry.fallback_triggered ? `
            <span class="px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-500/30 flex items-center gap-1 font-semibold">
              🔄 Rate-Limit Failover Activated
            </span>
          ` : ''}
        </div>
      `;
    }

    // Embedded Deals Carousel/Cards
    let dealsHtml = '';
    if (deals && deals.length > 0) {
      dealsHtml = `
        <div class="mt-3 pt-3 border-t border-white/10">
          <div class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1">
            <span>🔥 Recommended Steals (${deals.length})</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            ${deals.map(d => `
              <div class="p-2.5 rounded-xl bg-slate-900/80 border border-white/10 flex items-center gap-3">
                <img src="${d.image_url || 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600'}" class="w-12 h-12 rounded-lg object-cover shrink-0 bg-slate-800" alt="${d.title}">
                <div class="min-w-0 flex-1">
                  <div class="text-[11px] text-indigo-400 font-semibold truncate">${d.brand} • ${d.store}</div>
                  <div class="text-xs font-bold text-slate-100 truncate">${d.title}</div>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span class="text-emerald-400 font-bold text-xs">$${d.discount_price}</span>
                    <span class="text-slate-500 line-through text-[10px]">$${d.original_price}</span>
                    <span class="badge-discount text-[10px] px-1.5 py-0.2 rounded">-${d.discount_pct}%</span>
                  </div>
                </div>
                <button onclick="addToWatchlist('${d.id}')" title="Track Deal" class="p-1.5 rounded-lg text-indigo-400 hover:text-white hover:bg-indigo-600 transition-colors text-xs shrink-0">
                  ⭐
                </button>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    bubbleDiv.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-sm font-bold text-white shrink-0 shadow">
        🛍️
      </div>
      <div class="max-w-[85%] px-5 py-4 rounded-2xl rounded-tl-sm glass-panel text-slate-200 text-sm leading-relaxed border border-white/10">
        <div class="prose prose-invert max-w-none text-sm">${formattedHtml}</div>
        ${dealsHtml}
        ${telemetryHtml}
      </div>
    `;
  }

  container.appendChild(bubbleDiv);
}

function appendThinkingBubble(id) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const div = document.createElement('div');
  div.id = id;
  div.className = 'flex gap-3 justify-start animate-msg';
  div.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-indigo-900/60 flex items-center justify-center text-sm text-indigo-300 shrink-0">
      ⏳
    </div>
    <div class="px-4 py-3 rounded-2xl rounded-tl-sm glass-panel text-slate-400 text-xs flex items-center gap-2 border border-white/5">
      <span>ThreadHunter is searching deals & analyzing fashion prices...</span>
      <div class="flex gap-1">
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce"></span>
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" style="animation-delay: 0.2s"></span>
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" style="animation-delay: 0.4s"></span>
      </div>
    </div>
  `;
  container.appendChild(div);
}

function removeThinkingBubble(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function formatChatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/^### (.*$)/gim, '<h3 class="text-base font-bold text-indigo-300 mt-2 mb-1">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-lg font-bold text-slate-100 mt-2 mb-1">$1</h2>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong class="text-slate-100 font-semibold">$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/~~(.*?)~~/gim, '<del class="text-slate-500">$1</del>')
    .replace(/`([^`]+)`/gim, '<code class="px-1.5 py-0.5 rounded bg-indigo-950/80 text-indigo-300 font-mono text-xs border border-indigo-500/20">$1</code>')
    .replace(/^\- (.*$)/gim, '<li class="ml-4 list-disc text-slate-300 my-0.5">$1</li>')
    .replace(/\n/gim, '<br>');
}

function escapeHTML(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

// Make functions accessible globally for HTML event attributes
window.switchTab = switchTab;
window.simulateRateLimit = simulateRateLimit;
window.updateActiveModel = updateActiveModel;
window.saveApiKeys = saveApiKeys;
window.triggerLiveSearchPrompt = triggerLiveSearchPrompt;
window.addToWatchlist = addToWatchlist;
window.removeFromWatchlist = removeFromWatchlist;
window.copyToClipboard = copyToClipboard;
window.sendPresetPrompt = sendPresetPrompt;
window.fetchLiveDealsFromFeeds = fetchLiveDealsFromFeeds;
