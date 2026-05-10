/**
 * Flick — GSAP Scroll Animations
 * Premium Cinematic Micro-Interactions
 */

gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);

const ScrollAnims = {
    /**
     * Magnetic Button Effect
     */
    initMagneticButtons() {
        const buttons = document.querySelectorAll('.spotlight-btn, .btn-primary, .nav-logo');
        
        buttons.forEach(btn => {
            btn.addEventListener('mousemove', (e) => {
                const rect = btn.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                
                gsap.to(btn, {
                    x: x * 0.3,
                    y: y * 0.3,
                    duration: 0.3,
                    ease: "power2.out"
                });
            });
            
            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, {
                    x: 0,
                    y: 0,
                    duration: 0.5,
                    ease: "elastic.out(1, 0.3)"
                });
            });
        });
    },

    /**
     * Advanced Cursor Follower
     */
    initCursorFollower() {
        const cursor = document.querySelector('#cursorGlow');
        if (!cursor || window.innerWidth <= 768) return;

        window.addEventListener('mousemove', (e) => {
            gsap.to(cursor, {
                x: e.clientX,
                y: e.clientY,
                duration: 0.6,
                ease: "power2.out",
                overwrite: "auto"
            });
        });

        // Interactive states
        const interactables = document.querySelectorAll('a, button, .movie-card, .orbital-node');
        interactables.forEach(el => {
            el.addEventListener('mouseenter', () => {
                gsap.to(cursor, {
                    scale: 1.5,
                    backgroundColor: "rgba(124, 58, 237, 0.15)",
                    duration: 0.3
                });
            });
            el.addEventListener('mouseleave', () => {
                gsap.to(cursor, {
                    scale: 1,
                    backgroundColor: "rgba(124, 58, 237, 0.08)",
                    duration: 0.3
                });
            });
        });
    },

    init() {
        this.initHeroParallax();
        this.initRevealAnimations();
        this.initCounterAnimations();
        this.initSmoothNav();
        this.initMovieCardStaggers();
        this.initMagneticButtons();
        this.initCursorFollower();
        
        console.log('🎬 Flick Scroll Animations Initialized');
    },

    /**
     * Hero Section Parallax & Reveal
     */
    initHeroParallax() {
        const heroInfo = document.querySelector('#heroInfo');
        const heroArea = document.querySelector('#heroArea');
        const heroBackdrop = document.querySelector('#heroBackdrop');
        
        if (!heroInfo) return;

        // Stunning entry animation
        const tl = gsap.timeline({ delay: 0.6 });
        
        tl.to(heroInfo, {
            y: 0,
            opacity: 1,
            duration: 1.4,
            ease: "expo.out"
        })
        .from(".hero-display-title span", {
            y: 40,
            opacity: 0,
            duration: 1,
            stagger: 0.2,
            ease: "power3.out"
        }, "-=0.8")
        .from(".hero-actions-row .btn", {
            x: -20,
            opacity: 0,
            duration: 0.8,
            stagger: 0.15,
            ease: "power2.out"
        }, "-=0.5");

        // Parallax scroll effect
        if (heroArea) {
            gsap.to(heroArea, {
                scrollTrigger: {
                    trigger: "#heroSection",
                    start: "top top",
                    end: "bottom top",
                    scrub: true
                },
                y: 100,
                scale: 1.1,
                ease: "none"
            });
        }

        if (heroBackdrop) {
            gsap.to(heroBackdrop, {
                scrollTrigger: {
                    trigger: "#heroSection",
                    start: "top top",
                    end: "bottom top",
                    scrub: true
                },
                scale: 1.2,
                ease: "none"
            });
        }
    },

    /**
     * Staggered Reveal for Sections
     */
    initRevealAnimations() {
        // Generic reveal-up
        gsap.utils.toArray('.reveal-up').forEach(el => {
            gsap.from(el, {
                scrollTrigger: {
                    trigger: el,
                    start: "top 90%",
                    toggleActions: "play none none reverse"
                },
                y: 60,
                opacity: 0,
                duration: 1,
                ease: "power3.out"
            });
        });

        // reveal-left
        gsap.utils.toArray('.reveal-left').forEach(el => {
            gsap.from(el, {
                scrollTrigger: {
                    trigger: el,
                    start: "top 90%",
                },
                x: -100,
                opacity: 0,
                duration: 1.2,
                ease: "expo.out"
            });
        });

        // reveal-right
        gsap.utils.toArray('.reveal-right').forEach(el => {
            gsap.from(el, {
                scrollTrigger: {
                    trigger: el,
                    start: "top 90%",
                },
                x: 100,
                opacity: 0,
                duration: 1.2,
                ease: "expo.out"
            });
        });

        // reveal-scale
        gsap.utils.toArray('.reveal-scale').forEach(el => {
            gsap.from(el, {
                scrollTrigger: {
                    trigger: el,
                    start: "top 85%",
                },
                scale: 0.8,
                opacity: 0,
                duration: 1,
                ease: "back.out(1.7)"
            });
        });

        // Special handling for carousels
        gsap.utils.toArray('.stagger-reveal').forEach(container => {
            const items = container.children;
            gsap.from(items, {
                scrollTrigger: {
                    trigger: container,
                    start: "top 85%",
                },
                y: 50,
                opacity: 0,
                duration: 0.8,
                stagger: 0.1,
                ease: "power2.out"
            });
        });
    },

    /**
     * Animated Counter Stats
     */
    initCounterAnimations() {
        const counters = document.querySelectorAll('.stat-number');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-count'));
            const duration = parseInt(counter.getAttribute('data-duration')) / 1000 || 2;
            const prefix = counter.getAttribute('data-prefix') || '';

            gsap.to(counter, {
                scrollTrigger: {
                    trigger: counter,
                    start: "top 90%",
                },
                innerText: target,
                duration: duration,
                snap: { innerText: 1 },
                ease: "power1.inOut",
                onUpdate: function() {
                    counter.innerText = prefix + Math.ceil(this.targets()[0].innerText);
                }
            });
        });
    },

    /**
     * Smooth Navigation Response
     */
    initSmoothNav() {
        const navbar = document.querySelector('#navbar');
        if (!navbar) return;

        ScrollTrigger.create({
            start: "top -50",
            onUpdate: (self) => {
                if (self.direction === 1) { // Scrolling down
                    gsap.to(navbar, { y: -100, duration: 0.4, ease: "power2.inOut" });
                } else { // Scrolling up
                    gsap.to(navbar, { y: 0, duration: 0.4, ease: "power2.out" });
                }
            }
        });
    },

    /**
     * Movie Card Hover & Entry Staggers
     */
    initMovieCardStaggers() {
        // This will be called whenever new content is injected (e.g., after API calls)
        const cards = document.querySelectorAll('.movie-card:not(.gsap-init)');
        
        if (cards.length) {
            gsap.from(cards, {
                scrollTrigger: {
                    trigger: cards[0],
                    start: "top 95%",
                },
                scale: 0.9,
                opacity: 0,
                duration: 0.6,
                stagger: {
                    amount: 0.5,
                    grid: "auto",
                    from: "start"
                },
                ease: "back.out(1.4)",
                onComplete: () => {
                    cards.forEach(c => c.classList.add('gsap-init'));
                }
            });
        }
    },

    /**
     * Refresh ScrollTrigger for Dynamic Content
     */
    refresh() {
        ScrollTrigger.refresh();
        this.initMovieCardStaggers(); // Re-run for new elements
    }
};

// Auto-init when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    ScrollAnims.init();
});

// Export for use in other files
window.ScrollAnims = ScrollAnims;
