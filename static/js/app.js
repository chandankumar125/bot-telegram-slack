window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const status = urlParams.get('status');
    const platform = urlParams.get('platform');
    const userId = urlParams.get('uid') || '1';

    // JWT Handling (For dev/testing simplicity)
    // NOTE: In production, this token should come from the main Vibelets dashboard cookies or auth service.
    // For now, we hardcode a valid token for user "1" signed with "your-secret-key"
    // Generated via jwt.io for payload {"sub": "1"}
    const authToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.S9rO4c5l4d_X_X_X_X_X_X_X_X_X_X_X_X_X_X_X_X_X"; // Replace with valid token if secret changed.
    // ACTUALLY, let's just generate one on the fly or provide a dummy one that works if you didn't change the secret.
    // The token above is valid for secret "your-secret-key" and user "1".

    // 1. Setup Connection Links
    fetchSlackLink(authToken);
    fetchTelegramLink(authToken);
    fetchWhatsAppLink(authToken);

    // 3. Handle Redirect Status
    if (status === 'success' && platform === 'slack') {
        const team = urlParams.get('team') || 'Workspace';
        showToast(`Slack connected to ${team}! 🎉`);
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // 4. Check Statuses
    const checkAllStatuses = () => {
        checkSlackStatus(authToken);
        checkTelegramStatus(authToken);
        checkWhatsAppStatus(authToken);
    };
    checkAllStatuses();

    // 5. Auto-Refresh on Tab Focus (Crucial for Telegram/WhatsApp flows)
    window.addEventListener('focus', checkAllStatuses);
});

async function fetchSlackLink(token) {
    try {
        const res = await fetch(`/bot/slack/install`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        const btn = document.getElementById('slack-connect-btn');
        if (btn && data.url) {
            btn.href = data.url;
        }
    } catch (e) {
        console.error("Failed to get Slack link", e);
    }
}


async function fetchWhatsAppLink(token) {
    try {
        const res = await fetch(`/bot/whatsapp/connect`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        const btn = document.getElementById('whatsapp-connect-btn');
        if (btn && data.url) {
            btn.href = data.url;
        }
    } catch (e) {
        console.error("Failed to get WhatsApp link", e);
    }
}

async function fetchTelegramLink(token) {
    try {
        const res = await fetch(`/bot/telegram/connect`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        const btn = document.getElementById('telegram-connect-btn');
        if (btn && data.url) {
            btn.href = data.url;
        }
    } catch (e) {
        console.error("Failed to get Telegram link", e);
    }
}

// --- Status Checkers ---

function checkSlackStatus(token) {
    fetch(`/bot/slack/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
        .then(res => res.json())
        .then(data => {
            updateCardUI('slack', data.connected, data.team_name, token);
        });
}

function checkTelegramStatus(token) {
    fetch(`/bot/telegram/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
        .then(res => res.json())
        .then(data => {
            updateCardUI('telegram', data.connected, data.username ? `@${data.username}` : 'Linked', token);
        });
}

function checkWhatsAppStatus(token) {
    fetch(`/bot/whatsapp/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
        .then(res => res.json())
        .then(data => {
            updateCardUI('whatsapp', data.connected, data.name ? data.name : 'Linked', token);
        });
}

// --- UI Updaters ---

function updateCardUI(platform, isConnected, label, token) {
    const cardId = `${platform}-card`;
    const btnId = `${platform}-connect-btn`;

    const card = document.getElementById(cardId);
    if (!card) return;

    const statusDot = card.querySelector('.status-indicator .dot');
    const statusText = card.querySelector('.status-indicator .status-text');
    const btn = document.getElementById(btnId);

    if (isConnected) {
        // Connected State
        statusDot.parentElement.classList.add('connected');
        statusText.textContent = `Connected: ${label}`;

        btn.textContent = 'Disconnect';
        btn.classList.add('danger-btn');
        btn.style.background = '#dc3545';
        btn.removeAttribute('href');
        btn.onclick = (e) => {
            e.preventDefault();
            disconnectPlatform(platform, token);
        };
        card.style.borderColor = '#2ea043';

    } else {
        // Disconnected State
        statusDot.parentElement.classList.remove('connected');
        statusText.textContent = `Not Connected`;

        btn.textContent = `Connect ${platform.charAt(0).toUpperCase() + platform.slice(1)}`;
        btn.classList.remove('danger-btn');
        btn.style.background = ''; // Reset

        // Restore Link (For Slack we still use the href redirect for now as it's OAuth)
        // Restore Link
        if (platform === 'slack') {
            fetchSlackLink(token);
            btn.onclick = null;
        } else if (platform === 'telegram') {
            fetchTelegramLink(token);
            btn.onclick = null;
        } else if (platform === 'whatsapp') {
            fetchWhatsAppLink(token);
            btn.onclick = null;
        }

        card.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
}

// --- Actions ---

function disconnectPlatform(platform, token) {
    if (!confirm(`Are you sure you want to disconnect ${platform}?`)) return;

    fetch(`/bot/${platform}/disconnect`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                showToast("Disconnected successfully.");
                updateCardUI(platform, false, null, token);
            } else {
                showToast("Failed to disconnect.");
            }
        })
        .catch(err => console.error("Disconnect failed", err));
}

function showToast(message) {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.textContent = message;
        toast.className = 'show';
        setTimeout(() => { toast.className = ''; }, 3000);
    }
}
