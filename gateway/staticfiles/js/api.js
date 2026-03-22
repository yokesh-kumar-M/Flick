/* ═══════════════════════════════════════════
   Flick — API Client (Cinema in Space)
   Full CRUD + Admin Operations
   ═══════════════════════════════════════════ */

const API = {
    baseUrl: '/proxy',

    async request(service, path, options = {}) {
        const url = `${this.baseUrl}/${service}/${path}`;
        const config = {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options,
        };

        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                if (response.status === 401 && !options._retried) {
                    const refreshed = await this.refreshToken();
                    if (refreshed) {
                        return this.request(service, path, { ...options, _retried: true });
                    }
                }
                throw { status: response.status, ...data };
            }

            return data;
        } catch (error) {
            if (error.status) throw error;
            console.error(`API Error [${service}/${path}]:`, error);
            throw { status: 0, error: 'Network error. Service may be unavailable.' };
        }
    },

    async refreshToken() {
        try {
            await fetch(`${this.baseUrl}/auth/refresh/`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
            });
            return true;
        } catch {
            return false;
        }
    },

    // ── Auth Service ──
    auth: {
        register: (data) => API.request('auth', 'register/', { method: 'POST', body: data }),
        login: (data) => API.request('auth', 'login/', { method: 'POST', body: data }),
        logout: () => API.request('auth', 'logout/', { method: 'POST' }),
        profile: () => API.request('auth', 'profile/'),
        updateProfile: (data) => API.request('auth', 'profile/update/', { method: 'PUT', body: data }),
        changePassword: (data) => API.request('auth', 'profile/password/', { method: 'POST', body: data }),

        // Avatar upload — multipart/form-data (bypasses JSON wrapper)
        uploadAvatar: async (file) => {
            const formData = new FormData();
            formData.append('avatar', file);
            const response = await fetch(`${API.baseUrl}/auth/profile/avatar/`, {
                method: 'POST',
                credentials: 'include',
                body: formData,
                // Do NOT set Content-Type — browser sets multipart boundary automatically
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw data;
            return data;
        },

        watchHistory: () => API.request('auth', 'history/'),
        updateProgress: (data) => API.request('auth', 'history/update/', { method: 'POST', body: data }),
        continueWatching: () => API.request('auth', 'continue-watching/'),
        genreStats: () => API.request('auth', 'genre-stats/'),
        stats: () => API.request('auth', 'stats/'),
        listUsers: () => API.request('auth', 'users/'),
        // Watchlist (server-side)
        watchlist: () => API.request('auth', 'watchlist/'),
        addToWatchlist: (data) => API.request('auth', 'watchlist/add/', { method: 'POST', body: data }),
        removeFromWatchlist: (movieId) => API.request('auth', `watchlist/remove/${movieId}/`, { method: 'DELETE' }),
        checkWatchlist: (movieId) => API.request('auth', `watchlist/check/${movieId}/`),
        // Admin user management
        toggleAdmin: (userId) => API.request('auth', `users/${userId}/toggle-admin/`, { method: 'POST' }),
        banUser: (userId) => API.request('auth', `users/${userId}/ban/`, { method: 'POST' }),
        toggleSuperAccess: (userId) => API.request('auth', `users/${userId}/toggle-super-access/`, { method: 'POST' }),
        adminStats: () => API.request('auth', 'admin-stats/'),
    },

    // ── Catalog Service ──
    catalog: {
        homepage: () => API.request('catalog', 'homepage/'),
        movies: (params = '') => API.request('catalog', `movies/?${params}`),
        movie: (slug) => API.request('catalog', `movies/${slug}/`),
        search: (q) => API.request('catalog', `search/?q=${encodeURIComponent(q)}`),
        categories: () => API.request('catalog', 'categories/'),
        category: (slug) => API.request('catalog', `categories/${slug}/`),
        genres: () => API.request('catalog', 'genres/'),
        genre: (slug) => API.request('catalog', `genres/${slug}/`),
        trending: () => API.request('catalog', 'trending/'),
        featured: () => API.request('catalog', 'featured/'),
        newReleases: () => API.request('catalog', 'new-releases/'),
        playlists: () => API.request('catalog', 'playlists/'),
        playlist: (slug) => API.request('catalog', `playlists/${slug}/`),
        like: (id) => API.request('catalog', `movies/${id}/like/`, { method: 'POST' }),

        // Reviews
        movieReviews: (movieId, sort = '') => API.request('catalog', `movies/${movieId}/reviews/?sort=${sort}`),
        createReview: (data) => API.request('catalog', 'reviews/create/', { method: 'POST', body: data }),
        deleteReview: (id) => API.request('catalog', `reviews/${id}/delete/`, { method: 'DELETE' }),
        likeReview: (id) => API.request('catalog', `reviews/${id}/like/`, { method: 'POST' }),
        myReviews: () => API.request('catalog', 'reviews/mine/'),

        // Admin CRUD — Movies
        createMovie: (data) => API.request('catalog', 'movies/create/', { method: 'POST', body: data }),
        updateMovie: (id, data) => API.request('catalog', `movies/${id}/update/`, { method: 'PATCH', body: data }),
        deleteMovie: (id) => API.request('catalog', `movies/${id}/delete/`, { method: 'DELETE' }),

        // Admin CRUD — Genres
        createGenre: (data) => API.request('catalog', 'genres/create/', { method: 'POST', body: data }),
        updateGenre: (id, data) => API.request('catalog', `genres/${id}/update/`, { method: 'PATCH', body: data }),
        deleteGenre: (id) => API.request('catalog', `genres/${id}/delete/`, { method: 'DELETE' }),

        // Admin CRUD — Categories
        createCategory: (data) => API.request('catalog', 'categories/create/', { method: 'POST', body: data }),
        updateCategory: (id, data) => API.request('catalog', `categories/${id}/update/`, { method: 'PATCH', body: data }),
        deleteCategory: (id) => API.request('catalog', `categories/${id}/delete/`, { method: 'DELETE' }),

        // Admin CRUD — Playlists
        createPlaylist: (data) => API.request('catalog', 'playlists/create/', { method: 'POST', body: data }),
        updatePlaylist: (id, data) => API.request('catalog', `playlists/${id}/update/`, { method: 'PATCH', body: data }),
        deletePlaylist: (id) => API.request('catalog', `playlists/${id}/delete/`, { method: 'DELETE' }),

        // Admin stats
        adminStats: () => API.request('catalog', 'admin-stats/'),
    },

    // ── Access Service ──
    access: {
        request: (data) => API.request('access', 'request/', { method: 'POST', body: data }),
        check: (movieId) => API.request('access', `check/${movieId}/`),
        verify: (data) => API.request('access', 'verify/', { method: 'POST', body: data }),
        myRequests: () => API.request('access', 'my-requests/'),
        myGrants: () => API.request('access', 'my-grants/'),
        pending: () => API.request('access', 'pending/'),
        all: (status = '') => API.request('access', `all/?status=${status}`),
        approve: (id, note = '') => API.request('access', `approve/${id}/`, { method: 'POST', body: { admin_note: note } }),
        deny: (id, note = '') => API.request('access', `deny/${id}/`, { method: 'POST', body: { admin_note: note } }),
        
        // Payment processing
        confirmPayment: (requestId) => API.request('access', `payment/confirm/${requestId}/`, { method: 'POST' }),
        resendCode: (requestId) => API.request('access', `resend/${requestId}/`, { method: 'POST' }),
    },

    // ── Streaming Service ──
    streaming: {
        start: (data) => API.request('streaming', 'start/', { method: 'POST', body: data }),
        heartbeat: (token) => API.request('streaming', 'heartbeat/', { method: 'POST', body: { session_token: token } }),
        end: (token) => API.request('streaming', 'end/', { method: 'POST', body: { session_token: token } }),
        activeStreams: () => API.request('streaming', 'active-streams/'),
    },

    // ── Recommendation Service ──
    recommendations: {
        get: (type = 'personalized') => API.request('recommendations', `?type=${type}`),
        similar: (movieId) => API.request('recommendations', `similar/${movieId}/`),
        trending: () => API.request('recommendations', 'trending/'),
        interact: (data) => API.request('recommendations', 'interaction/', { method: 'POST', body: data }),
    },

    // ── Notification Service ──
    notifications: {
        get: () => API.request('notifications', ''),
        unreadCount: () => API.request('notifications', 'unread-count/'),
        markRead: (id) => API.request('notifications', `mark-read/${id}/`, { method: 'POST' }),
        markAllRead: () => API.request('notifications', 'mark-all-read/', { method: 'POST' }),
    },
};
