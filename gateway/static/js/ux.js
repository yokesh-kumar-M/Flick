/* ═══════════════════════════════════════════
   Flick — UX JavaScript Enhancements
   Search Autocomplete, Infinite Scroll,
   Lazy Loading, PWA Registration
   ═══════════════════════════════════════════ */

(function() {
    'use strict';

    // ═══════════════════════════════════════════
    // SEARCH AUTOCOMPLETE
    // ═══════════════════════════════════════════
    window.SearchAutocomplete = {
        container: null,
        input: null,
        results: null,
        debounceTimer: null,
        minChars: 2,
        
        init(selector = '.search-input') {
            this.input = document.querySelector(selector);
            if (!this.input) return;
            
            this.createResultsContainer();
            this.bindEvents();
        },
        
        createResultsContainer() {
            this.results = document.createElement('div');
            this.results.className = 'search-results';
            this.input.parentElement.appendChild(this.results);
        },
        
        bindEvents() {
            this.input.addEventListener('input', (e) => this.handleInput(e));
            this.input.addEventListener('focus', () => {
                if (this.results.children.length > 0) {
                    this.results.classList.add('active');
                }
            });
            document.addEventListener('click', (e) => {
                if (!this.input.parentElement.contains(e.target)) {
                    this.results.classList.remove('active');
                }
            });
            // Clear button
            const clearBtn = this.input.parentElement.querySelector('.search-clear');
            if (clearBtn) {
                clearBtn.addEventListener('click', () => {
                    this.input.value = '';
                    this.results.classList.remove('active');
                    this.input.focus();
                });
            }
        },
        
        handleInput(e) {
            const query = e.target.value.trim();
            
            if (query.length < this.minChars) {
                this.results.classList.remove('active');
                return;
            }
            
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => this.search(query), 300);
        },
        
        async search(query) {
            this.showLoading();
            
            try {
                const response = await fetch(`/proxy/catalog/search/?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    this.showResults(data.results);
                } else {
                    this.showNoResults();
                }
            } catch (error) {
                this.showNoResults();
            }
        },
        
        showLoading() {
            this.results.innerHTML = '<div class="search-loading">Searching...</div>';
            this.results.classList.add('active');
        },
        
        showNoResults() {
            this.results.innerHTML = '<div class="search-no-results">No results found</div>';
            this.results.classList.add('active');
        },
        
        showResults(movies) {
            this.results.innerHTML = movies.slice(0, 8).map(movie => `
                <a href="/movie/${movie.slug}/" class="search-result-item">
                    <img src="${movie.poster_url || '/static/img/default-poster.svg'}" alt="${escapeHtml(movie.title)}" class="search-result-poster" loading="lazy">
                    <div class="search-result-info">
                        <div class="search-result-title">${escapeHtml(movie.title)}</div>
                        <div class="search-result-meta">${movie.release_date?.split('-')[0] || ''} • ${movie.duration || ''} min</div>
                    </div>
                </a>
            `).join('');
            
            this.results.classList.add('active');
        }
    };

    // ═══════════════════════════════════════════
    // INFINITE SCROLL
    // ═══════════════════════════════════════════
    window.InfiniteScroll = {
        container: null,
        trigger: null,
        isLoading: false,
        hasMore: true,
        page: 1,
        apiEndpoint: null,
        
        init(config = {}) {
            this.container = config.container || document.querySelector('.movie-grid');
            this.apiEndpoint = config.apiEndpoint || '/proxy/catalog/movies/';
            
            if (!this.container) return;
            
            this.createTrigger();
            this.bindScroll();
            this.loadMore();
        },
        
        createTrigger() {
            this.trigger = document.createElement('div');
            this.trigger.className = 'infinite-scroll-trigger';
            this.trigger.innerHTML = '<div class="infinite-scroll-spinner"></div>';
            this.container.parentElement.appendChild(this.trigger);
        },
        
        bindScroll() {
            const observer = new IntersectionObserver(
                (entries) => {
                    if (entries[0].isIntersecting && !this.isLoading && this.hasMore) {
                        this.loadMore();
                    }
                },
                { threshold: 0.1 }
            );
            observer.observe(this.trigger);
        },
        
        async loadMore() {
            if (this.isLoading || !this.hasMore) return;
            
            this.isLoading = true;
            this.trigger.classList.add('visible');
            
            try {
                const url = `${this.apiEndpoint}?page=${this.page}`;
                const response = await fetch(url);
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    this.appendMovies(data.results);
                    this.page++;
                    
                    if (data.next === null) {
                        this.hasMore = false;
                    }
                } else {
                    this.hasMore = false;
                }
            } catch (error) {
                console.error('Infinite scroll error:', error);
            } finally {
                this.isLoading = false;
                this.trigger.classList.remove('visible');
            }
        },
        
        appendMovies(movies) {
            const template = document.createElement('template');
            template.innerHTML = movies.map(movie => this.createMovieCard(movie)).join('');
            this.container.appendChild(template.content);
        },
        
        createMovieCard(movie) {
            return `
                <a href="/movie/${movie.slug}/" class="movie-card">
                    <img src="${movie.poster_url || '/static/img/default-poster.svg'}" 
                         alt="${escapeHtml(movie.title)}" 
                         class="movie-card-poster"
                         loading="lazy">
                </a>
            `;
        }
    };

    // ═══════════════════════════════════════════
    // LAZY LOADING WITH BLUR-UP
    // ═══════════════════════════════════════════
    window.LazyImage = {
        init() {
            if ('IntersectionObserver' in window) {
                this.observer = new IntersectionObserver(
                    (entries) => entries.forEach(entry => this.handleIntersection(entry)),
                    { rootMargin: '50px' }
                );
                
                document.querySelectorAll('img[lazy]').forEach(img => {
                    this.observer.observe(img);
                });
            }
        },
        
        handleIntersection(entry) {
            const img = entry.target;
            
            if (entry.isIntersecting) {
                img.src = img.dataset.src;
                img.classList.add('loaded');
                img.removeAttribute('lazy');
                this.observer.unobserve(img);
            }
        }
    };

    // ═══════════════════════════════════════════
    // PWA SERVICE WORKER REGISTRATION
    // ═══════════════════════════════════════════
    window.PWARegistration = {
        init() {
            if ('serviceWorker' in navigator) {
                this.registerSW();
            }
        },
        
        async registerSW() {
            try {
                const registration = await navigator.serviceWorker.register('/static/js/sw.js');
                console.log('Service Worker registered:', registration.scope);
                
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateToast();
                        }
                    });
                });
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        },
        
        showUpdateToast() {
            if (typeof showToast === 'function') {
                showToast('New version available! Refresh to update.', 'info', 0);
            }
        }
    };

    // ═══════════════════════════════════════════
    // SKELETON INITIALIZATION
    // ═══════════════════════════════════════════
    window.SkeletonLoader = {
        show(container, type = 'grid') {
            const skeleton = document.createElement('div');
            skeleton.className = type === 'grid' ? 'skeleton-grid' : 'skeleton-row';
            
            for (let i = 0; i < 6; i++) {
                skeleton.innerHTML += '<div class="skeleton skeleton-card"></div>';
            }
            
            container.innerHTML = '';
            container.appendChild(skeleton);
        },
        
        hide(container) {
            const skeleton = container.querySelector('.skeleton-grid, .skeleton-row');
            if (skeleton) skeleton.remove();
        }
    };

    // ═══════════════════════════════════════════
    // ENHANCED TOAST NOTIFICATIONS
    // ═══════════════════════════════════════════
    window.EnhancedToast = {
        init() {
            this.createContainer();
        },
        
        createContainer() {
            if (!document.getElementById('toastContainer')) {
                const container = document.createElement('div');
                container.id = 'toastContainer';
                container.className = 'toast-container';
                document.body.appendChild(container);
            }
        },
        
        show(title, message, type = 'info', duration = 4000) {
            const container = document.getElementById('toastContainer') || this.createContainer();
            
            const icons = {
                success: '✓',
                error: '✕',
                warning: '⚠',
                info: 'ℹ'
            };
            
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.innerHTML = `
                <div class="toast-icon">${icons[type]}</div>
                <div class="toast-content">
                    <div class="toast-title">${escapeHtml(title)}</div>
                    ${message ? `<div class="toast-message">${escapeHtml(message)}</div>` : ''}
                </div>
                <button class="toast-close" onclick="this.parentElement.remove()">×</button>
            `;
            
            container.appendChild(toast);
            
            if (duration > 0) {
                setTimeout(() => {
                    toast.classList.add('toast-exit');
                    setTimeout(() => toast.remove(), 300);
                }, duration);
            }
        }
    };

    // ═══════════════════════════════════════════
    // INIT ALL ON DOM READY
    // ═══════════════════════════════════════════
    document.addEventListener('DOMContentLoaded', () => {
        // Initialize all enhancements
        window.EnhancedToast.init();
        window.LazyImage.init();
        window.PWARegistration.init();
        
        // Initialize search autocomplete if input exists
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            window.SearchAutocomplete.init('.search-input');
        }
    });

})();