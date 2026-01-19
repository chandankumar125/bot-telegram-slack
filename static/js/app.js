window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const status = urlParams.get('status');
    const platform = urlParams.get('platform');

    // Simulate User ID
    const userId = urlParams.get('uid') || 'VL_TEST_USER_001';

    // Update Connect Link with User ID
    const connectBtn = document.getElementById('slack-connect-btn');
    if (connectBtn) {
        // Point to the backend install endpoint
        connectBtn.href = `/bot/slack/install?user_id=${userId}`;
    }

    if (status === 'success' && platform === 'slack') {
        const team = urlParams.get('team') || 'Workspace';
        showToast(`Slack connected to ${team}! 🎉`);
        // Remove params from URL to clean up
        window.history.replaceState({}, document.title, window.location.pathname);
        checkStatus(userId);
    } else {
        checkStatus(userId);
    }
});

function checkStatus(userId) {
    fetch(`/bot/slack/status?user_id=${userId}`)
        .then(res => res.json())
        .then(data => {
            if (data.connected) {
                updateUIConnected(data.team_name, userId);
            } else {
                updateUIDisconnected(userId);
            }
        })
        .catch(err => console.error("Failed to check status", err));
}

function disconnectUser(userId) {
    if (!confirm("Are you sure you want to disconnect Slack?")) return;

    fetch(`/bot/slack/disconnect?user_id=${userId}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                showToast("Disconnected successfully.");
                updateUIDisconnected(userId);
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
        toast.className = 'show'; // Add class to animate in
        setTimeout(() => {
            toast.className = '';
        }, 3000);
    }
}

function updateUIConnected(teamName = "Active Connection", userId) {
    const statusDot = document.querySelector('.status-indicator .dot');
    const statusText = document.querySelector('.status-indicator .status-text');
    const connectBtn = document.getElementById('slack-connect-btn');
    const card = document.querySelector('.card');

    if (statusDot) {
        statusDot.parentElement.classList.add('connected');
    }

    if (statusText) statusText.textContent = `Connected: ${teamName}`;

    if (connectBtn) {
        connectBtn.textContent = 'Disconnect';
        connectBtn.style.background = '#dc3545'; // Red for disconnect
        connectBtn.classList.add('danger-btn');
        connectBtn.href = '#';
        connectBtn.onclick = (e) => {
            e.preventDefault();
            disconnectUser(userId);
        };
    }

    if (card) {
        card.style.borderColor = '#2ea043';
    }
}

function updateUIDisconnected(userId) {
    const statusDot = document.querySelector('.status-indicator .dot');
    const statusText = document.querySelector('.status-indicator .status-text');
    const connectBtn = document.getElementById('slack-connect-btn');
    const card = document.querySelector('.card');

    if (statusDot) {
        statusDot.parentElement.classList.remove('connected');
    }

    if (statusText) statusText.textContent = `Not Connected`;

    if (connectBtn) {
        connectBtn.textContent = 'Connect Slack';
        connectBtn.style.background = ''; // Reset to CSS default (purple)
        connectBtn.classList.remove('danger-btn');
        // Point back to install endpoint
        connectBtn.href = `/bot/slack/install?user_id=${userId}`;
        connectBtn.onclick = null; // Remove disconnect handler
    }

    if (card) {
        card.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
}
