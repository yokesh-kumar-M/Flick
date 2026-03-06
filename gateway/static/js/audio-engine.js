/* ═══════════════════════════════════════════
   Flick — Advanced Audio Pipeline
   Web Audio API: Equalizer, Normalization,
   Spatial Audio, Visualizer
   ═══════════════════════════════════════════ */

class FlickAudioEngine {
    constructor() {
        this.ctx = null;
        this.source = null;
        this.gainNode = null;
        this.compressor = null;
        this.panner = null;
        this.analyser = null;
        this.eqBands = [];
        this.isInitialized = false;
        this.currentPreset = 'flat';

        // EQ frequency bands
        this.bandFrequencies = [
            { freq: 60, label: 'Bass', type: 'lowshelf' },
            { freq: 250, label: 'Low-Mid', type: 'peaking' },
            { freq: 1000, label: 'Mid', type: 'peaking' },
            { freq: 4000, label: 'Hi-Mid', type: 'peaking' },
            { freq: 12000, label: 'Treble', type: 'highshelf' },
        ];

        // Audio presets
        this.presets = {
            flat: [0, 0, 0, 0, 0],
            cinema: [3, 1, 0, 2, 4],
            music: [4, 2, -1, 3, 5],
            voice: [-2, 0, 4, 3, 1],
            night: [-4, -2, 0, -1, -3],
            bass_boost: [8, 4, 0, 0, 0],
            treble_boost: [0, 0, 0, 4, 8],
        };
    }

    /**
     * Initialize the audio pipeline from a video element.
     * Video → GainNode → EQ Chain → Compressor → Panner → Destination
     */
    init(videoElement) {
        if (this.isInitialized) return;

        try {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            this.source = this.ctx.createMediaElementSource(videoElement);

            // Gain (volume)
            this.gainNode = this.ctx.createGain();
            this.gainNode.gain.value = 1.0;

            // EQ Bands (5-band equalizer)
            this.eqBands = this.bandFrequencies.map(({ freq, type }) => {
                const filter = this.ctx.createBiquadFilter();
                filter.type = type;
                filter.frequency.value = freq;
                filter.gain.value = 0;
                filter.Q.value = 1.0;
                return filter;
            });

            // Dynamics Compressor (volume normalization)
            this.compressor = this.ctx.createDynamicsCompressor();
            this.compressor.threshold.value = -24;
            this.compressor.knee.value = 30;
            this.compressor.ratio.value = 12;
            this.compressor.attack.value = 0.003;
            this.compressor.release.value = 0.25;

            // Spatial Audio (Panner)
            this.panner = this.ctx.createStereoPanner();
            this.panner.pan.value = 0;

            // Analyser (for visualizer)
            this.analyser = this.ctx.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;

            // Connect the chain:
            // Source → Gain → EQ[0] → EQ[1] → ... → Compressor → Panner → Analyser → Destination
            this.source.connect(this.gainNode);

            let lastNode = this.gainNode;
            this.eqBands.forEach(band => {
                lastNode.connect(band);
                lastNode = band;
            });

            lastNode.connect(this.compressor);
            this.compressor.connect(this.panner);
            this.panner.connect(this.analyser);
            this.analyser.connect(this.ctx.destination);

            this.isInitialized = true;
        } catch (e) {
        }
    }

    resume() {
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    // ── Volume ──
    setVolume(value) {
        if (this.gainNode) {
            this.gainNode.gain.setValueAtTime(
                Math.max(0, Math.min(2, value)),
                this.ctx.currentTime
            );
        }
    }

    // ── Equalizer ──
    setEQBand(index, gainDb) {
        if (this.eqBands[index]) {
            this.eqBands[index].gain.setValueAtTime(
                Math.max(-12, Math.min(12, gainDb)),
                this.ctx.currentTime
            );
        }
    }

    applyPreset(presetName) {
        const values = this.presets[presetName];
        if (!values) return;

        values.forEach((gain, i) => this.setEQBand(i, gain));
        this.currentPreset = presetName;
    }

    // ── Spatial Audio ──
    setPan(value) {
        if (this.panner) {
            this.panner.pan.setValueAtTime(
                Math.max(-1, Math.min(1, value)),
                this.ctx.currentTime
            );
        }
    }

    // ── Compressor (Normalization) ──
    setNormalization(enabled) {
        if (!this.compressor) return;
        if (enabled) {
            this.compressor.threshold.value = -24;
            this.compressor.ratio.value = 12;
        } else {
            this.compressor.threshold.value = 0;
            this.compressor.ratio.value = 1;
        }
    }

    // ── Visualizer ──
    getFrequencyData() {
        if (!this.analyser) return new Uint8Array(0);
        const data = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(data);
        return data;
    }

    getWaveformData() {
        if (!this.analyser) return new Uint8Array(0);
        const data = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteTimeDomainData(data);
        return data;
    }

    /**
     * Start rendering frequency bars on a canvas.
     */
    startVisualizer(canvas) {
        if (!canvas || !this.analyser) return;

        const ctx = canvas.getContext('2d');
        const WIDTH = canvas.width;
        const HEIGHT = canvas.height;

        const draw = () => {
            requestAnimationFrame(draw);

            const freqData = this.getFrequencyData();
            ctx.clearRect(0, 0, WIDTH, HEIGHT);

            const barCount = 64;
            const barWidth = WIDTH / barCount - 1;
            const step = Math.floor(freqData.length / barCount);

            for (let i = 0; i < barCount; i++) {
                const value = freqData[i * step];
                const barHeight = (value / 255) * HEIGHT;
                const x = i * (barWidth + 1);
                const y = HEIGHT - barHeight;

                // Gradient color based on theme
                const hue = (i / barCount) * 60 + 240; // Purple to blue range
                ctx.fillStyle = `hsla(${hue}, 80%, 60%, 0.8)`;
                ctx.fillRect(x, y, barWidth, barHeight);
            }
        };

        draw();
    }

    destroy() {
        if (this.ctx) {
            this.ctx.close();
        }
        this.isInitialized = false;
    }
}

// Create global instance
const flickAudio = new FlickAudioEngine();
