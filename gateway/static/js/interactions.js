/* ═══════════════════════════════════════════
   Flick — Premium Interactions
   Cinematic Micro-Animations
   ═══════════════════════════════════════════ */

/* ═══════════════════════════════════════════
   Scroll Progress Bar
   ═══════════════════════════════════════════ */
function initScrollProgress() {
    const progressBar = document.getElementById('scrollProgressBar');
    if (!progressBar) {
        // Create if doesn't exist
        const bar = document.createElement('div');
        bar.className = 'scroll-progress-bar';
        bar.id = 'scrollProgressBar';
        document.body.appendChild(bar);
    }

    window.addEventListener('scroll', () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        
        const bar = document.getElementById('scrollProgressBar');
        if (bar) bar.style.width = scrolled + '%';
    });
}

/* ═══════════════════════════════════════════
   Lazy Images with Fade-In
   ═══════════════════════════════════════════ */
function initLazyImages() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.opacity = '0';
                img.style.transition = 'opacity 0.5s ease';
                
                img.onload = () => {
                    img.style.opacity = '1';
                };
                
                // If already loaded
                if (img.complete) {
                    img.style.opacity = '1';
                }
                
                observer.unobserve(img);
            }
        });
    }, {
        rootMargin: '50px'
    });

    images.forEach(img => imageObserver.observe(img));
    
    // Also handle images added dynamically
    window.initLazyImagesForContainer = (container) => {
        container.querySelectorAll('img[loading="lazy"]').forEach(img => {
            if (!img.dataset.lazyObserved) {
                img.dataset.lazyObserved = 'true';
                imageObserver.observe(img);
            }
        });
    };
}

/* ═══════════════════════════════════════════
   Counter Animations
   ═══════════════════════════════════════════ */
function initCounterAnimations() {
    const counters = document.querySelectorAll('[data-count]');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.dataset.count, 10);
                const duration = parseInt(counter.dataset.duration, 10) || 2000;
                const suffix = counter.dataset.suffix || '';
                const prefix = counter.dataset.prefix || '';
                
                animateCounter(counter, target, duration, prefix, suffix);
                counterObserver.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => counterObserver.observe(counter));
}

function animateCounter(element, target, duration, prefix = '', suffix = '') {
    const start = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (target - start) * easeOut);
        
        element.textContent = prefix + current.toLocaleString() + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = prefix + target.toLocaleString() + suffix;
        }
    }
    
    requestAnimationFrame(update);
}

/* ═══════════════════════════════════════════
   Touch-Swipe Carousel
   ═══════════════════════════════════════════ */
function initCarousel(el) {
    if (!el) return;
    
    const container = el.closest('.carousel-container');
    if (!container) return;
    
    let isDown = false;
    let startX;
    let scrollLeft;
    let momentum = 0;
    let lastX = 0;
    let lastTime = 0;
    
    const onMousedown = (e) => {
        isDown = true;
        container.classList.add('dragging');
        startX = e.pageX - container.offsetLeft;
        scrollLeft = container.scrollLeft;
        momentum = 0;
    };
    
    const onMouseleave = () => {
        isDown = false;
        container.classList.remove('dragging');
    };
    
    const onMouseup = () => {
        isDown = false;
        container.classList.remove('dragging');
        
        // Apply momentum
        if (Math.abs(momentum) > 0.5) {
            container.scrollBy({
                left: momentum * 50,
                behavior: 'auto'
            });
        }
    };
    
    const onMousemove = (e) => {
        if (!isDown) return;
        e.preventDefault();
        
        const x = e.pageX - container.offsetLeft;
        const walk = (x - startX) * 2;
        container.scrollLeft = scrollLeft - walk;
        
        // Calculate momentum
        const now = performance.now();
        const dt = now - lastTime;
        if (dt > 0) {
            momentum = (e.pageX - lastX) / dt;
        }
        lastX = e.pageX;
        lastTime = now;
    };
    
    // Touch events
    const onTouchstart = (e) => {
        startX = e.touches[0].pageX - container.offsetLeft;
        scrollLeft = container.scrollLeft;
    };
    
    const onTouchmove = (e) => {
        const x = e.touches[0].pageX - container.offsetLeft;
        const walk = (x - startX) * 2;
        container.scrollLeft = scrollLeft - walk;
    };
    
    container.addEventListener('mousedown', onMousedown);
    container.addEventListener('mouseleave', onMouseleave);
    container.addEventListener('mouseup', onMouseup);
    container.addEventListener('mousemove', onMousemove);
    
    container.addEventListener('touchstart', onTouchstart, { passive: true });
    container.addEventListener('touchmove', onTouchmove, { passive: true });
}

/* ═══════════════════════════════════════════
   Skeleton Loaders
   ═══════════════════════════════════════════ */
function initSkeletonLoaders() {
    // Add skeleton class to placeholder elements
    document.querySelectorAll('.skeleton').forEach(el => {
        if (!el.classList.contains('skeleton-loader')) {
            el.classList.add('skeleton-loader');
        }
    });
}

function showSkeleton(container, count = 6) {
    if (!container) return;
    
    container.innerHTML = Array(count).fill(0).map(() => `
        <div class="skeleton-card skeleton-loader" style="width: 200px; height: 300px; flex-shrink: 0; border-radius: var(--radius-lg);"></div>
    `).join('');
}

function hideSkeleton(container) {
    if (!container) return;
    container.querySelectorAll('.skeleton-loader').forEach(el => el.remove());
}

/* ═══════════════════════════════════════════
   Scroll Reveal
   ═══════════════════════════════════════════ */
function initScrollReveal() {
    const reveals = document.querySelectorAll('.reveal, [data-animate]');
    
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                entry.target.classList.add('animate-' + (entry.target.dataset.animate || 'fade-in'));
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    reveals.forEach(el => revealObserver.observe(el));
}

/* ═══════════════════════════════════════════
   Cursor Glow
   ═══════════════════════════════════════════ */
function initCursorGlow() {
    if (window.innerWidth <= 768) return;
    
    let glow = document.getElementById('cursorGlow');
    if (!glow) {
        glow = document.createElement('div');
        glow.id = 'cursorGlow';
        glow.className = 'cursor-glow';
        document.body.appendChild(glow);
    }
    
    let ticking = false;
    
    document.addEventListener('mousemove', (e) => {
        if (ticking) return;
        ticking = true;
        
        requestAnimationFrame(() => {
            glow.style.left = e.clientX + 'px';
            glow.style.top = e.clientY + 'px';
            ticking = false;
        });
    });
    
    document.addEventListener('mouseleave', () => {
        glow.style.opacity = '0';
    });
    
    document.addEventListener('mouseenter', () => {
        glow.style.opacity = '1';
    });
}

/* ═══════════════════════════════════════════
   Ripple Effect for Buttons
   ═══════════════════════════════════════════ */
function initRippleEffect() {
    document.querySelectorAll('.btn-ripple, .btn-cinema').forEach(btn => {
        if (btn._rippleInitialized) return;
        btn._rippleInitialized = true;
        
        btn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.className = 'ripple-effect';
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

/* ═══════════════════════════════════════════
   Page Transitions
   ═══════════════════════════════════════════ */
function initPageTransition() {
    if (!document.startViewTransition) return;
    
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;
        
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript') || href.startsWith('mailto')) return;
        if (link.hasAttribute('download')) return;
        
        e.preventDefault();
        
        document.startViewTransition(() => {
            window.location.href = href;
        });
    });
}

/* ═══════════════════════════════════════════
   Auto-Hide Navbar on Scroll
   ═══════════════════════════════════════════ */
let lastScrollY = window.scrollY;
let ticking = false;

function initAutoHideNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    const handleScroll = () => {
        if (ticking) return;
        
        ticking = true;
        
        requestAnimationFrame(() => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > 30) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            // Hide/show based on scroll direction
            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }
            
            lastScrollY = currentScrollY;
            ticking = false;
        });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
}

/* ═══════════════════════════════════════════
   Scroll to Top
   ═══════════════════════════════════════════ */
function initScrollToTop() {
    let btn = document.getElementById('scrollToTop');
    
    if (!btn) {
        btn = document.createElement('button');
        btn.id = 'scrollToTop';
        btn.className = 'scroll-to-top';
        btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        btn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
        document.body.appendChild(btn);
    }

    const handleScroll = () => {
        if (window.scrollY > 400) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
}

/* ═══════════════════════════════════════════
   Password Strength Indicator
   ═══════════════════════════════════════════ */
function checkPasswordStrength(password) {
    const fill = document.getElementById('strengthFill');
    const text = document.getElementById('strengthText');
    
    if (!fill || !text) return { score: 0, label: '' };
    
    let score = 0;
    
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    const labels = ['Weak', 'Fair', 'Good', 'Strong', 'Excellent'];
    const colors = ['#ef4444', '#f59e0b', '#f59e0b', '#10b981', '#10b981'];
    
    fill.style.width = (score * 25) + '%';
    fill.style.background = colors[Math.min(score, 4)];
    text.textContent = score > 0 ? labels[Math.min(score, 4) - 1] : '';
    text.style.color = colors[Math.min(score, 4)];
    
    return { score, label: labels[Math.min(score, 4) - 1] || '' };
}

/* ═══════════════════════════════════════════
   Genre Pills Hover Effects
   ═══════════════════════════════════════════ */
function initGenrePills() {
    document.querySelectorAll('.genre-tag, .mood-pill').forEach(pill => {
        pill.addEventListener('mouseenter', () => {
            pill.style.transform = 'scale(1.05)';
        });
        pill.addEventListener('mouseleave', () => {
            pill.style.transform = 'scale(1)';
        });
    });
}

/* ═══════════════════════════════════════════
   Tab Indicator Animation
   ═══════════════════════════════════════════ */
function initTabIndicator(tabContainer) {
    if (!tabContainer) return;
    
    const tabs = tabContainer.querySelectorAll('.ptab, .tab-btn');
    if (tabs.length === 0) return;
    
    const indicator = document.createElement('div');
    indicator.className = 'tab-indicator';
    indicator.style.cssText = `
        position: absolute;
        bottom: 0;
        height: 2px;
        background: var(--color-cinema-violet);
        transition: all 0.3s ease;
        box-shadow: 0 0 10px var(--color-cinema-violet);
    `;
    tabContainer.style.position = 'relative';
    tabContainer.appendChild(indicator);
    
    function updateIndicator(activeTab) {
        if (!activeTab) return;
        const rect = activeTab.getBoundingClientRect();
        const containerRect = tabContainer.getBoundingClientRect();
        
        indicator.style.left = (rect.left - containerRect.left) + 'px';
        indicator.style.width = rect.width + 'px';
    }
    
    // Set initial position
    const activeTab = tabContainer.querySelector('.active') || tabs[0];
    if (activeTab) updateIndicator(activeTab);
    
    // Update on click
    tabs.forEach(tab => {
        tab.addEventListener('click', () => updateIndicator(tab));
    });
}

/* ═══════════════════════════════════════════
   Mobile Nav Toggle Animation
   ═══════════════════════════════════════════ */
function initMobileNavAnimation() {
    const toggle = document.querySelector('.nav-mobile-toggle');
    const navLinks = document.getElementById('navLinks');
    
    if (!toggle || !navLinks) return;
    
    toggle.addEventListener('click', () => {
        navLinks.classList.toggle('mobile-open');
        
        // Animate icon
        const icon = toggle.querySelector('i');
        if (navLinks.classList.contains('mobile-open')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        } else {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        }
    });
}

/* ═══════════════════════════════════════════
   Initialize All Premium Interactions
   ═══════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
    initScrollProgress();
    initScrollToTop();
    initCursorGlow();
    initAutoHideNavbar();
    initScrollReveal();
    initCounterAnimations();
    initLazyImages();
    initRippleEffect();
    initGenrePills();
    initMobileNavAnimation();
    initSkeletonLoaders();
    
    // Initialize carousels
    document.querySelectorAll('.carousel-container').forEach(container => {
        const carousel = container.querySelector('.carousel');
        if (carousel) initCarousel(carousel);
    });
    
    // Initialize tab indicators
    document.querySelectorAll('.profile-tabs-nav').forEach(initTabIndicator);
});

// Export for global use
window.initScrollProgress = initScrollProgress;
window.initLazyImages = initLazyImages;
window.initCounterAnimations = initCounterAnimations;
window.initCarousel = initCarousel;
window.initSkeletonLoaders = initSkeletonLoaders;
window.showSkeleton = showSkeleton;
window.hideSkeleton = hideSkeleton;
window.initCursorGlow = initCursorGlow;
window.initRippleEffect = initRippleEffect;
window.initPageTransition = initPageTransition;
window.initAutoHideNavbar = initAutoHideNavbar;
window.checkPasswordStrength = checkPasswordStrength;