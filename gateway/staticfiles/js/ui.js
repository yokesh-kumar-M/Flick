/* ═══════════════════════════════════════════
   Flick — UI Utilities (Cinema in Space)
   Particles, 3D Tilt, Glass Effects
   ═══════════════════════════════════════════ */

// ── Toast Notifications ──
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `<span style="font-size:1.1rem;">${icon}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ── HTML Escaping ──
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ── Time Ago ──
function timeAgo(dateString) {
    const now = new Date();
    const date = new Date(dateString);
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

// ═══════════════════════════════════════════
// NAVBAR — Scroll Effects
// ═══════════════════════════════════════════
function initNavbar() {
    const navbar = document.getElementById('navbar');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 30) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Set active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
}

function toggleMobileNav() {
    const navLinks = document.getElementById('navLinks');
    if (navLinks) navLinks.classList.toggle('mobile-open');
}

// ═══════════════════════════════════════════
// AMBIENT PARTICLE SYSTEM
// ═══════════════════════════════════════════
function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    resize();
    window.addEventListener('resize', resize);

    class Particle {
        constructor() {
            this.reset();
        }
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.3;
            this.speedY = (Math.random() - 0.5) * 0.3;
            this.opacity = Math.random() * 0.4 + 0.1;
            this.hue = Math.random() * 60 + 220; // Blue-purple range
            this.pulse = Math.random() * Math.PI * 2;
            this.pulseSpeed = Math.random() * 0.01 + 0.005;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.pulse += this.pulseSpeed;

            if (this.x < -10 || this.x > canvas.width + 10 || this.y < -10 || this.y > canvas.height + 10) {
                this.reset();
            }
        }
        draw() {
            const currentOpacity = this.opacity * (0.5 + 0.5 * Math.sin(this.pulse));
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${this.hue}, 70%, 70%, ${currentOpacity})`;
            ctx.fill();
        }
    }

    // Create particles
    const count = Math.min(Math.floor((window.innerWidth * window.innerHeight) / 15000), 80);
    for (let i = 0; i < count; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        animationId = requestAnimationFrame(animate);
    }

    animate();

    // Cleanup on page leave
    window.addEventListener('beforeunload', () => {
        cancelAnimationFrame(animationId);
    });
}

// ═══════════════════════════════════════════
// 3D CARD TILT EFFECT
// ═══════════════════════════════════════════
function initCardTilt() {
    document.querySelectorAll('.movie-card').forEach(card => {
        if (card._tiltInitialized) return;
        card._tiltInitialized = true;

        let peekTimer = null;

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;

            card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.06)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            // Hide peek
            const peek = card.querySelector('.movie-card-peek');
            if (peek) peek.classList.remove('visible');
            clearTimeout(peekTimer);
        });

        card.addEventListener('mouseenter', () => {
            // Quick peek after 1.5s hover
            peekTimer = setTimeout(() => {
                const peek = card.querySelector('.movie-card-peek');
                if (peek) peek.classList.add('visible');
            }, 1500);
        });
    });
}

// ═══════════════════════════════════════════
// CAROUSEL GENERATOR
// ═══════════════════════════════════════════
function createCarousel(id, title, movies, showProgress = false, seeAllLink = '', variant = 'standard') {
    if (!movies || !movies.length) return '';

    const seeAll = seeAllLink ?
        `<a href="${seeAllLink}" class="section-link">See All <i class="fas fa-chevron-right"></i></a>` : '';

    // Use compact variant for continue watching carousels
    const cardVariant = showProgress ? 'compact' : variant;

    return `
        <section class="section">
            <div class="section-header">
                <h2 class="section-title">${title}</h2>
                ${seeAll}
            </div>
            <div class="carousel-container">
                <button class="carousel-btn left" onclick="scrollCarousel('${id}', -1)">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <div class="carousel stagger-children" id="${id}">
                    ${movies.map(m => buildMovieCard(m, cardVariant, {
                        showProgress: showProgress,
                        progressPercent: m.progress || 0,
                        showBadges: true,
                        showGenres: cardVariant !== 'compact',
                    })).join('')}
                </div>
                <button class="carousel-btn right" onclick="scrollCarousel('${id}', 1)">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        </section>
    `;
}

function scrollCarousel(id, direction) {
    const carousel = document.getElementById(id);
    if (!carousel) return;
    const scrollAmount = carousel.clientWidth * 0.7;
    carousel.scrollBy({ left: direction * scrollAmount, behavior: 'smooth' });
}

// ═══════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════
function navigateTo(url) {
    if (document.startViewTransition) {
        document.startViewTransition(() => {
            window.location.href = url;
        });
    } else {
        window.location.href = url;
    }
}

// ═══════════════════════════════════════════
// INTERSECTION OBSERVER — Reveal Animations
// ═══════════════════════════════════════════
function initRevealAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // Also init card tilt for newly loaded cards
    setTimeout(initCardTilt, 100);
}

// ═══════════════════════════════════════════
// DEBOUNCE
// ═══════════════════════════════════════════
function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

// ═══════════════════════════════════════════
// KEYBOARD NAV FOR CAROUSELS
// ═══════════════════════════════════════════
document.addEventListener('keydown', (e) => {
    const focusedCard = document.activeElement?.closest('.movie-card');
    if (!focusedCard) return;

    const carousel = focusedCard.closest('.carousel');
    if (!carousel) return;

    const cards = [...carousel.querySelectorAll('.movie-card')];
    const currentIdx = cards.indexOf(focusedCard);

    if (e.key === 'ArrowRight' && currentIdx < cards.length - 1) {
        e.preventDefault();
        cards[currentIdx + 1].focus();
    } else if (e.key === 'ArrowLeft' && currentIdx > 0) {
        e.preventDefault();
        cards[currentIdx - 1].focus();
    } else if (e.key === 'Enter') {
        focusedCard.click();
    }
});

// ═══════════════════════════════════════════
// DONUT CHART
// ═══════════════════════════════════════════
function drawDonutChart(canvas, data, colors) {
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;
    const innerRadius = radius * 0.6;

    const total = data.reduce((sum, d) => sum + d.value, 0);
    let startAngle = -Math.PI / 2;

    data.forEach((d, i) => {
        const sliceAngle = (d.value / total) * 2 * Math.PI;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
        ctx.arc(centerX, centerY, innerRadius, startAngle + sliceAngle, startAngle, true);
        ctx.closePath();
        ctx.fillStyle = colors[i % colors.length];
        ctx.fill();
        startAngle += sliceAngle;
    });

    ctx.fillStyle = '#f0f0ff';
    ctx.font = 'bold 20px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(total, centerX, centerY - 8);
    ctx.font = '12px Inter';
    ctx.fillStyle = '#8b8baf';
    ctx.fillText('Total', centerX, centerY + 12);
}

// ═══════════════════════════════════════════
// MOVIE CARD BUILDER — Revolutionary Multi-Style System
// ═══════════════════════════════════════════

/**
 * Build movie card HTML with multiple style variations
 * @param {Object} movie - Movie data object
 * @param {String} variant - Card variant: 'standard', 'hero', 'compact', 'banner', 'spotlight'
 * @param {Object} options - Additional options {showProgress, showBadges, showGenres}
 */
function buildMovieCard(movie, variant = 'standard', options = {}) {
    const {
        showProgress = false,
        showBadges = true,
        showGenres = true,
        showDescription = false,
        progressPercent = 0,
    } = options;

    // Determine which image to use (thumbnail preferred for standard/compact, poster for hero/banner)
    const imageUrl = (variant === 'standard' || variant === 'compact') && movie.thumbnail_display
        ? movie.thumbnail_display
        : movie.poster_display || '/static/img/default-poster.svg';

    // Calculate if movie is "new" (released within last 30 days)
    const releaseDate = new Date(movie.created_at || Date.now());
    const isNew = (Date.now() - releaseDate) < 30 * 24 * 60 * 60 * 1000;

    // Format duration
    const hours = Math.floor(movie.duration / 60);
    const mins = movie.duration % 60;
    const durationText = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;

    // Rating display
    const ratingText = movie.rating ? movie.rating.toFixed(1) : 'N/A';

    // Genre pills (limit to 3 for standard cards)
    const genrePills = showGenres && movie.genres
        ? movie.genres.slice(0, variant === 'hero' ? 4 : 3).map(g =>
            `<span class="movie-card-genre-pill">${escapeHtml(g.name || g)}</span>`
        ).join('')
        : '';

    // Badges
    let badges = '';
    if (showBadges) {
        if (isNew) badges += '<span class="movie-card-badge badge-new"><i class="fas fa-sparkles"></i> NEW</span>';
        if (movie.is_featured) badges += '<span class="movie-card-badge badge-featured"><i class="fas fa-crown"></i> FEATURED</span>';
        if (movie.trending_score > 50) badges += '<span class="movie-card-badge badge-trending"><i class="fas fa-fire"></i> TRENDING</span>';
    }

    // Progress bar
    const progressBar = showProgress && progressPercent > 0
        ? `<div class="movie-card-progress">
             <div class="movie-card-progress-bar" style="width: ${progressPercent}%"></div>
           </div>`
        : '';

    // Build card based on variant
    switch (variant) {
        case 'hero':
            return `
                <div class="movie-card movie-card-hero hover-lift" onclick="navigateTo('/movie/${escapeHtml(movie.slug)}/')">
                    <img class="movie-card-poster" 
                         src="${escapeHtml(imageUrl)}" 
                         alt="${escapeHtml(movie.title)}"
                         loading="lazy"
                         onerror="this.src='/static/img/default-poster.svg'">
                    ${badges ? `<div class="movie-card-badges">${badges}</div>` : ''}
                    <div class="movie-card-overlay">
                        <h3 class="movie-card-title">${escapeHtml(movie.title)}</h3>
                        <div class="movie-card-meta">
                            <span class="movie-card-year">${movie.release_year || '2024'}</span>
                            <span>•</span>
                            <span class="movie-card-duration"><i class="far fa-clock"></i> ${durationText}</span>
                            <span>•</span>
                            <span class="movie-card-rating"><i class="fas fa-star"></i> ${ratingText}</span>
                        </div>
                        ${genrePills ? `<div class="movie-card-genres">${genrePills}</div>` : ''}
                        ${showDescription && movie.description ? `<p class="movie-card-hero-desc">${escapeHtml(movie.description.slice(0, 150))}...</p>` : ''}
                    </div>
                    <div class="movie-card-play"><i class="fas fa-play"></i></div>
                    ${progressBar}
                </div>
            `;

        case 'compact':
            return `
                <div class="movie-card movie-card-compact hover-lift" onclick="navigateTo('/movie/${escapeHtml(movie.slug)}/')">
                    <img class="movie-card-poster" 
                         src="${escapeHtml(imageUrl)}" 
                         alt="${escapeHtml(movie.title)}"
                         loading="lazy"
                         onerror="this.src='/static/img/default-poster.svg'">
                    ${badges ? `<div class="movie-card-badges">${badges}</div>` : ''}
                    <div class="movie-card-overlay">
                        <h3 class="movie-card-title">${escapeHtml(movie.title)}</h3>
                        <div class="movie-card-meta">
                            <span class="movie-card-year">${movie.release_year || '2024'}</span>
                            ${movie.rating ? `<span>•</span><span class="movie-card-rating"><i class="fas fa-star"></i> ${ratingText}</span>` : ''}
                        </div>
                    </div>
                    <div class="movie-card-play"><i class="fas fa-play"></i></div>
                    ${progressBar}
                </div>
            `;

        case 'banner':
            return `
                <div class="movie-card-banner hover-lift" onclick="navigateTo('/movie/${escapeHtml(movie.slug)}/')">
                    <img class="movie-card-banner-poster" 
                         src="${escapeHtml(movie.backdrop_display || imageUrl)}" 
                         alt="${escapeHtml(movie.title)}"
                         loading="lazy"
                         onerror="this.src='${escapeHtml(imageUrl)}'">
                    <div class="movie-card-banner-content">
                        ${badges ? `<div class="movie-card-badges">${badges}</div>` : ''}
                        <h3 class="movie-card-banner-title">${escapeHtml(movie.title)}</h3>
                        ${showDescription && movie.description ? `<p class="movie-card-banner-desc">${escapeHtml(movie.description.slice(0, 200))}...</p>` : ''}
                        <div class="movie-card-banner-meta">
                            <div class="movie-card-banner-meta-item">
                                <span class="movie-card-banner-meta-label">Year</span>
                                <span class="movie-card-banner-meta-value">${movie.release_year || '2024'}</span>
                            </div>
                            <div class="movie-card-banner-meta-item">
                                <span class="movie-card-banner-meta-label">Duration</span>
                                <span class="movie-card-banner-meta-value">${durationText}</span>
                            </div>
                            <div class="movie-card-banner-meta-item">
                                <span class="movie-card-banner-meta-label">Rating</span>
                                <span class="movie-card-banner-meta-value">${ratingText} ⭐</span>
                            </div>
                        </div>
                        <div class="movie-card-banner-actions">
                            <button class="btn btn-primary" onclick="event.stopPropagation(); navigateTo('/movie/${escapeHtml(movie.slug)}/')">
                                <i class="fas fa-play"></i> Watch Now
                            </button>
                            <button class="btn btn-ghost" onclick="event.stopPropagation(); Watchlist.add({id: ${movie.id}, title: '${escapeHtml(movie.title)}', slug: '${escapeHtml(movie.slug)}', poster: '${escapeHtml(imageUrl)}'}); showToast('Added to watchlist', 'success')">
                                <i class="fas fa-bookmark"></i> Save
                            </button>
                        </div>
                    </div>
                    ${progressBar}
                </div>
            `;

        case 'spotlight':
            return `
                <div class="movie-card-spotlight hover-lift" onclick="navigateTo('/movie/${escapeHtml(movie.slug)}/')">
                    <div class="movie-card-spotlight-poster">
                        <img src="${escapeHtml(movie.poster_display || imageUrl)}" 
                             alt="${escapeHtml(movie.title)}"
                             loading="lazy"
                             onerror="this.src='/static/img/default-poster.svg'">
                    </div>
                    <div class="movie-card-spotlight-content">
                        ${badges ? `<div class="movie-card-badges">${badges}</div>` : ''}
                        <h2 class="movie-card-spotlight-title">${escapeHtml(movie.title)}</h2>
                        ${showDescription && movie.description ? `<p class="movie-card-spotlight-desc">${escapeHtml(movie.description.slice(0, 300))}...</p>` : ''}
                        <div class="movie-card-spotlight-stats">
                            <div class="movie-card-spotlight-stat">
                                <span class="movie-card-spotlight-stat-value">${movie.release_year || '2024'}</span>
                                <span class="movie-card-spotlight-stat-label">Year</span>
                            </div>
                            <div class="movie-card-spotlight-stat">
                                <span class="movie-card-spotlight-stat-value">${durationText}</span>
                                <span class="movie-card-spotlight-stat-label">Runtime</span>
                            </div>
                            <div class="movie-card-spotlight-stat">
                                <span class="movie-card-spotlight-stat-value">${ratingText}</span>
                                <span class="movie-card-spotlight-stat-label">Rating</span>
                            </div>
                            <div class="movie-card-spotlight-stat">
                                <span class="movie-card-spotlight-stat-value">${(movie.view_count || 0).toLocaleString()}</span>
                                <span class="movie-card-spotlight-stat-label">Views</span>
                            </div>
                        </div>
                        ${genrePills ? `<div class="movie-card-genres">${genrePills}</div>` : ''}
                        <div class="movie-card-banner-actions" style="margin-top: var(--space-xl);">
                            <button class="btn btn-primary btn-lg" onclick="event.stopPropagation(); navigateTo('/movie/${escapeHtml(movie.slug)}/')">
                                <i class="fas fa-play"></i> Watch Now
                            </button>
                            <button class="btn btn-ghost btn-lg" onclick="event.stopPropagation(); showToast('Added to watchlist', 'success')">
                                <i class="fas fa-bookmark"></i> Save
                            </button>
                        </div>
                    </div>
                </div>
            `;

        default: // 'standard'
            return `
                <div class="movie-card hover-lift" onclick="navigateTo('/movie/${escapeHtml(movie.slug)}/')">
                    <img class="movie-card-poster" 
                         src="${escapeHtml(imageUrl)}" 
                         alt="${escapeHtml(movie.title)}"
                         loading="lazy"
                         onerror="this.src='/static/img/default-poster.svg'">
                    ${badges ? `<div class="movie-card-badges">${badges}</div>` : ''}
                    <div class="movie-card-overlay">
                        <h3 class="movie-card-title">${escapeHtml(movie.title)}</h3>
                        <div class="movie-card-meta">
                            <span class="movie-card-year">${movie.release_year || '2024'}</span>
                            <span>•</span>
                            <span class="movie-card-duration"><i class="far fa-clock"></i> ${durationText}</span>
                            ${movie.rating ? `<span>•</span><span class="movie-card-rating"><i class="fas fa-star"></i> ${ratingText}</span>` : ''}
                        </div>
                        ${genrePills ? `<div class="movie-card-genres">${genrePills}</div>` : ''}
                    </div>
                    <div class="movie-card-play"><i class="fas fa-play"></i></div>
                    ${progressBar}
                </div>
            `;
    }
}

// ═══════════════════════════════════════════
// WATCHLIST (Server-side with localStorage fallback)
// ═══════════════════════════════════════════
const Watchlist = {
    key: 'flick_watchlist',

    // Local fallback
    get() {
        try { return JSON.parse(localStorage.getItem(this.key) || '[]'); }
        catch { return []; }
    },

    add(movie) {
        // Try server-side first
        if (typeof currentUser !== 'undefined' && currentUser) {
            API.auth.addToWatchlist({
                movie_id: movie.id,
                movie_title: movie.title,
                movie_slug: movie.slug,
                movie_poster: movie.poster_display || movie.poster || '',
            }).catch(() => {});
        }
        // Also update local
        const list = this.get();
        if (!list.find(m => m.id === movie.id)) {
            list.push({
                id: movie.id, title: movie.title, slug: movie.slug,
                poster: movie.poster_display, addedAt: Date.now()
            });
            localStorage.setItem(this.key, JSON.stringify(list));
        }
    },

    remove(movieId) {
        // Try server-side first
        if (typeof currentUser !== 'undefined' && currentUser) {
            API.auth.removeFromWatchlist(movieId).catch(() => {});
        }
        const list = this.get().filter(m => m.id !== movieId);
        localStorage.setItem(this.key, JSON.stringify(list));
    },

    has(movieId) {
        return this.get().some(m => m.id === movieId);
    },
};

// ═══════════════════════════════════════════
// INIT ON DOM READY
// ═══════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    initRevealAnimations();
    initCardTilt();
});
