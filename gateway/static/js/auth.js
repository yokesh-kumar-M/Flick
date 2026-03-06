/* ═══════════════════════════════════════════
   Flick — Auth & Session Management
   ═══════════════════════════════════════════ */

let currentUser = null;

async function initAuth() {
    try {
        const user = await API.auth.profile();
        if (user && user.id) {
            currentUser = user;
            showLoggedInUI(user);
            loadNotifications();
        }
    } catch {
        currentUser = null;
        showLoggedOutUI();
    }
}

function showLoggedInUI(user) {
    const authButtons = document.getElementById('authButtons');
    const userMenu = document.getElementById('userMenu');
    const notifBell = document.getElementById('notificationBell');
    const avatarInitials = document.getElementById('avatarInitials');
    const dropdownUsername = document.getElementById('dropdownUsername');
    const adminLink = document.getElementById('adminLink');

    if (authButtons) authButtons.style.display = 'none';
    if (userMenu) userMenu.style.display = 'block';
    if (notifBell) notifBell.style.display = 'block';

    const initials = (user.display_name || user.username || 'U').charAt(0).toUpperCase();
    if (avatarInitials) {
        if (user.avatar_display) {
            avatarInitials.innerHTML = `<img src="${user.avatar_display}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
        } else {
            avatarInitials.textContent = initials;
        }
    }
    if (dropdownUsername) dropdownUsername.textContent = user.display_name || user.username;

    if (adminLink && user.is_admin) {
        adminLink.style.display = 'flex';
    }

    // Set avatar ring color based on favorite genre
    updateAvatarRing(user.favorite_genre);
}

function showLoggedOutUI() {
    const authButtons = document.getElementById('authButtons');
    const userMenu = document.getElementById('userMenu');
    const notifBell = document.getElementById('notificationBell');

    if (authButtons) authButtons.style.display = 'flex';
    if (userMenu) userMenu.style.display = 'none';
    if (notifBell) notifBell.style.display = 'none';
}

function updateAvatarRing(genre) {
    const ring = document.getElementById('avatarRing');
    if (!ring) return;

    const genreColors = {
        'Action': 'linear-gradient(135deg, #ef4444, #f97316)',
        'Comedy': 'linear-gradient(135deg, #f59e0b, #eab308)',
        'Drama': 'linear-gradient(135deg, #6366f1, #8b5cf6)',
        'Horror': 'linear-gradient(135deg, #dc2626, #7f1d1d)',
        'Sci-Fi': 'linear-gradient(135deg, #06b6d4, #3b82f6)',
        'Romance': 'linear-gradient(135deg, #ec4899, #f43f5e)',
        'Thriller': 'linear-gradient(135deg, #1e293b, #475569)',
        'Animation': 'linear-gradient(135deg, #10b981, #34d399)',
        'Documentary': 'linear-gradient(135deg, #78716c, #a8a29e)',
    };

    ring.style.background = genreColors[genre] || 'var(--gradient-primary)';
}

async function logout() {
    // Use direct logout endpoint that clears cookies server-side
    window.location.href = '/logout/';
}

async function loadNotifications() {
    try {
        const data = await API.notifications.unreadCount();
        const badge = document.getElementById('notifBadge');
        if (badge) {
            if (data.unread_count > 0) {
                badge.style.display = 'flex';
                badge.textContent = data.unread_count > 9 ? '9+' : data.unread_count;
            } else {
                badge.style.display = 'none';
            }
        }
    } catch {}
}

function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }
}

function toggleNotifications() {
    const dropdown = document.getElementById('notifDropdown');
    if (dropdown) {
        const isVisible = dropdown.style.display !== 'none';
        dropdown.style.display = isVisible ? 'none' : 'block';
        if (!isVisible) loadNotificationList();
    }
}

async function loadNotificationList() {
    const list = document.getElementById('notifList');
    if (!list) return;

    try {
        const notifications = await API.notifications.get();
        if (!notifications.length) {
            list.innerHTML = '<div class="notif-item"><p class="notif-message">No notifications yet</p></div>';
            return;
        }
        list.innerHTML = notifications.slice(0, 10).map(n => `
            <div class="notif-item ${n.is_read ? '' : 'unread'}" onclick="markNotifRead(${n.id}${n.link ? ", '" + n.link + "'" : ''})">
                <div class="notif-title">${escapeHtml(n.title)}</div>
                <div class="notif-message">${escapeHtml(n.message)}</div>
                <div class="notif-time">${timeAgo(n.created_at)}</div>
            </div>
        `).join('');
    } catch {
        list.innerHTML = '<div class="notif-item"><p class="notif-message">Failed to load</p></div>';
    }
}

async function markNotifRead(id, link) {
    try {
        await API.notifications.markRead(id);
        loadNotifications();
        loadNotificationList();
        if (link) navigateTo(link);
    } catch {}
}

async function markAllRead() {
    try {
        await API.notifications.markAllRead();
        loadNotifications();
        loadNotificationList();
    } catch {}
}

// Close dropdowns on outside click
document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-user')) {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) dropdown.style.display = 'none';
    }
    if (!e.target.closest('.nav-notification')) {
        const dropdown = document.getElementById('notifDropdown');
        if (dropdown) dropdown.style.display = 'none';
    }
});
