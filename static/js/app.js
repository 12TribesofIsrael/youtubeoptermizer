/* ── YouTube Optimizer — Client-side helpers ─────────────────────────────── */

// Toast notifications
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Tab switching
function switchTab(tabGroup, tabName) {
    document.querySelectorAll(`[data-tab-group="${tabGroup}"] .tab`).forEach(t => t.classList.remove('active'));
    document.querySelectorAll(`[data-tab-group="${tabGroup}"] .tab-content`).forEach(c => c.classList.remove('active'));
    document.querySelector(`[data-tab-group="${tabGroup}"] .tab[data-tab="${tabName}"]`)?.classList.add('active');
    document.getElementById(`tab-${tabName}`)?.classList.add('active');
}

// Modal
function openModal(id) {
    document.getElementById(id)?.classList.add('active');
}

function closeModal(id) {
    document.getElementById(id)?.classList.remove('active');
}

// Toggle (dry-run / live)
function toggleSwitch(el) {
    el.classList.toggle('active');
    const isLive = el.classList.contains('active');
    const label = el.parentElement.querySelector('.toggle-label');
    if (label) {
        label.textContent = isLive ? 'LIVE' : 'DRY RUN';
        label.className = `toggle-label ${isLive ? 'live' : 'dry'}`;
    }
    return isLive;
}

// Confirm destructive action
function confirmAction(message) {
    return confirm(message);
}

// Fetch helper with error handling
async function apiFetch(url, options = {}) {
    try {
        const resp = await fetch(url, options);
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: resp.statusText }));
            throw new Error(err.detail || 'Request failed');
        }
        return await resp.json();
    } catch (e) {
        showToast(e.message, 'error');
        throw e;
    }
}

// Format numbers with commas
function formatNumber(n) {
    return Number(n).toLocaleString();
}

// Debounce for search inputs
function debounce(fn, ms = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
    };
}

// Load content via HTMX-style fetch and swap
async function loadInto(selector, url) {
    const el = document.querySelector(selector);
    if (!el) return;
    el.innerHTML = '<div class="skeleton" style="height:40px;margin:8px 0"></div>'.repeat(3);
    try {
        const resp = await fetch(url);
        if (resp.ok) {
            el.innerHTML = await resp.text();
        } else {
            el.innerHTML = `<p class="text-dim">Failed to load data</p>`;
        }
    } catch {
        el.innerHTML = `<p class="text-dim">Connection error</p>`;
    }
}
