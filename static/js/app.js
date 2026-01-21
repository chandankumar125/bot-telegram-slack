window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const status = urlParams.get('status');
    const platform = urlParams.get('platform');
    const userId = urlParams.get('uid') || 'VL_TEST_USER_001';

    // 1. Setup Slack Link
    const slackBtn = document.getElementById('slack-connect-btn');
    if (slackBtn) {
        slackBtn.href = `/bot/slack/install?user_id=${userId}`;
    }

    // 2. Setup Telegram Link (Need to fetch the dynamic link)
    fetchTelegramLink(userId);

    // 3. Handle Redirect Status
    if (status === 'success' && platform === 'slack') {
        const team = urlParams.get('team') || 'Workspace';
        showToast(`Slack connected to ${team}! 🎉`);
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // 4. Check Statuses
    checkSlackStatus(userId);
    checkTelegramStatus(userId);
});

async function fetchTelegramLink(userId) {
    try {
        const res = await fetch(`/bot/telegram/connect?user_id=${userId}`);
        const data = await res.json();
        const btn = document.getElementById('telegram-connect-btn');
        if (btn && data.link) {
            btn.href = data.link;
        }
    } catch (e) {
        console.error("Failed to get Telegram link", e);
    }
}

// --- Status Checkers ---

function checkSlackStatus(userId) {
    fetch(`/bot/slack/status?user_id=${userId}`)
        .then(res => res.json())
        .then(data => {
            updateCardUI('slack', data.connected, data.team_name, userId);
        });
}

function checkTelegramStatus(userId) {
    fetch(`/bot/telegram/status?user_id=${userId}`)
        .then(res => res.json())
        .then(data => {
            updateCardUI('telegram', data.connected, data.username ? `@${data.username}` : 'Linked', userId);
        });
}

// --- UI Updaters ---

function updateCardUI(platform, isConnected, label, userId) {
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
            disconnectPlatform(platform, userId);
        };
        card.style.borderColor = '#2ea043';

    } else {
        // Disconnected State
        statusDot.parentElement.classList.remove('connected');
        statusText.textContent = `Not Connected`;

        btn.textContent = `Connect ${platform.charAt(0).toUpperCase() + platform.slice(1)}`;
        btn.classList.remove('danger-btn');
        btn.style.background = ''; // Reset

        // Restore Link
        if (platform === 'slack') {
            btn.href = `/bot/slack/install?user_id=${userId}`;
            btn.onclick = null;
        } else if (platform === 'telegram') {
            fetchTelegramLink(userId); // Re-fetch logic
            btn.onclick = null;
        }

        card.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
}

// --- Actions ---

function disconnectPlatform(platform, userId) {
    if (!confirm(`Are you sure you want to disconnect ${platform}?`)) return;

    fetch(`/bot/${platform}/disconnect?user_id=${userId}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                showToast("Disconnected successfully.");
                updateCardUI(platform, false, null, userId);
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
