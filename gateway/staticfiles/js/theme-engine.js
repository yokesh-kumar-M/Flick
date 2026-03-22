/* ═══════════════════════════════════════════
   Flick — Dynamic Adaptive Theming Engine
   Powered by ColorThief.js
   ═══════════════════════════════════════════ */

const ThemeEngine = {
    colorThief: null,
    currentPalette: null,
    defaultPalette: {
        primary: [99, 102, 241],
        accent: [245, 158, 11],
        bg: [10, 10, 15],
        surface: [20, 20, 32],
        text: [248, 250, 252],
    },

    init() {
        if (typeof ColorThief !== 'undefined') {
            this.colorThief = new ColorThief();
        }
    },

    /**
     * Attach hover events to movie cards to dynamically change theme.
     */
    attachCardListeners() {
        // Disabled to allow the global infinite morphing loop to take precedence
        // without being overridden by individual card hovers.
    },

    /**
     * Extract colors from an image and morph the UI theme.
     * @param {string} imageUrl - URL of the poster/image
     * @param {HTMLElement} [scope] - Optional scope element (defaults to :root)
     */
    async extractAndApply(imageUrl, scope = null) {
        // Disabled to allow the global infinite morphing loop to take precedence
        // without being overridden by individual card images or page loads.
        return null;
    },

    /**
     * Extract dominant color palette from image.
     */
    extractColors(imageUrl) {
        return new Promise((resolve, reject) => {
            if (!this.colorThief) {
                this.init();
                if (!this.colorThief) return reject('ColorThief not loaded');
            }

            const img = new Image();
            img.crossOrigin = 'Anonymous';
            img.src = imageUrl;

            img.onload = () => {
                try {
                    const palette = this.colorThief.getPalette(img, 5);
                    if (!palette || palette.length < 5) return resolve(null);

                    // Sort by luminance for intelligent assignment
                    const sorted = [...palette].sort((a, b) =>
                        this.getLuminance(a) - this.getLuminance(b)
                    );

                    const result = {
                        primary: palette[0],     // Dominant color
                        accent: palette[1],      // Secondary dominant
                        bg: this.darken(sorted[0], 0.7),  // Darkest, made darker
                        surface: this.darken(sorted[1], 0.5),  // Second darkest
                        text: this.ensureReadable(sorted[4], sorted[0]),  // Lightest
                        raw: palette,
                    };

                    resolve(result);
                } catch (e) {
                    reject(e);
                }
            };

            img.onerror = () => reject('Image load failed');

            // Timeout
            setTimeout(() => reject('Timeout'), 5000);
        });
    },

    /**
     * Apply extracted palette to CSS custom properties.
     */
    applyPalette(palette, scope = null) {
        const target = scope || document.documentElement;

        // Add a class for smooth transition
        if (!target.classList.contains('theme-transitioning')) {
            target.classList.add('theme-transitioning');
            setTimeout(() => target.classList.remove('theme-transitioning'), 500);
        }

        const primary = palette.primary;
        const accent = palette.accent;
        const bg = palette.bg;
        const surface = palette.surface;
        const text = palette.text;

        target.style.setProperty('--theme-primary', this.rgb(primary));
        target.style.setProperty('--theme-primary-rgb', primary.join(', '));
        target.style.setProperty('--theme-accent', this.rgb(accent));
        target.style.setProperty('--theme-accent-rgb', accent.join(', '));
        target.style.setProperty('--theme-bg', this.rgb(bg));
        target.style.setProperty('--theme-bg-rgb', bg.join(', '));
        target.style.setProperty('--theme-surface', this.rgb(surface));
        target.style.setProperty('--theme-surface-rgb', surface.join(', '));
        target.style.setProperty('--theme-surface-2', this.rgb(this.lighten(surface, 0.15)));
        target.style.setProperty('--theme-text', this.rgb(text));
        target.style.setProperty('--theme-text-secondary', this.rgb(this.blend(text, bg, 0.4)));
        target.style.setProperty('--theme-text-muted', this.rgb(this.blend(text, bg, 0.6)));
        target.style.setProperty('--theme-border', this.rgb(this.lighten(bg, 0.1)));

        // Aurora colors shift to match primary
        target.style.setProperty('--aurora-1', this.rgb(primary));
        target.style.setProperty('--aurora-2', this.rgb(this.blend(primary, accent, 0.5)));
        target.style.setProperty('--aurora-3', this.rgb(accent));

        // Glassmorphism
        target.style.setProperty('--glass-bg', `rgba(${surface[0]}, ${surface[1]}, ${surface[2]}, 0.8)`);

        // Gradients
        target.style.setProperty('--gradient-primary',
            `linear-gradient(135deg, ${this.rgb(primary)}, ${this.rgb(accent)})`);

        // Shadow glow
        target.style.setProperty('--shadow-glow',
            `0 0 30px rgba(${primary[0]}, ${primary[1]}, ${primary[2]}, 0.15)`);
        target.style.setProperty('--shadow-glow-lg',
            `0 0 60px rgba(${primary[0]}, ${primary[1]}, ${primary[2]}, 0.25)`);
        target.style.setProperty('--neon-primary',
            `rgba(${primary[0]}, ${primary[1]}, ${primary[2]}, 0.6)`);
        target.style.setProperty('--neon-accent',
            `rgba(${accent[0]}, ${accent[1]}, ${accent[2]}, 0.5)`);

        this.currentPalette = palette;
    },

    /**
     * Reset to default dark theme.
     */
    resetTheme() {
        this.applyPalette(this.defaultPalette);
        this.currentPalette = null;
    },

    // ── Color Utilities ──

    rgb(color) {
        return `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
    },

    getLuminance([r, g, b]) {
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    },

    getContrastRatio(fg, bg) {
        const l1 = this.getLuminance(fg) + 0.05;
        const l2 = this.getLuminance(bg) + 0.05;
        return Math.max(l1, l2) / Math.min(l1, l2);
    },

    ensureReadable(textColor, bgColor) {
        // WCAG AA requires 4.5:1 contrast ratio
        let color = [...textColor];
        let iterations = 0;

        while (this.getContrastRatio(color, bgColor) < 4.5 && iterations < 20) {
            color = this.lighten(color, 0.1);
            iterations++;
        }

        return color;
    },

    darken(color, amount) {
        return color.map(c => Math.max(0, Math.round(c * (1 - amount))));
    },

    lighten(color, amount) {
        return color.map(c => Math.min(255, Math.round(c + (255 - c) * amount)));
    },

    blend(color1, color2, ratio) {
        return color1.map((c, i) => Math.round(c * (1 - ratio) + color2[i] * ratio));
    },
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    ThemeEngine.init();
    ThemeEngine.attachCardListeners();
});
