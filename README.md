# Audio Visualizer

A real-time audio visualizer that reacts to music in your browser. Drop any audio file and watch the frequency spectrum come alive with colors extracted directly from the album artwork.

![Audio Visualizer Demo](https://github.com/user-attachments/assets/placeholder)

> **No install. No build step. Just open `visualizer.html` in your browser.**

---

## Features

- **Drag & drop** — drop any audio file onto the page, or click to browse
- **Pill spectrum visualizer** — 60 frequency bands rendered as rounded pills that rise from a shared baseline
- **Artwork-driven colors** — dominant color palette is extracted from the album art and mapped across the full spectrum
- **Bass-reactive background glow** — a soft radial glow pulses with the low-end energy, tinted to the primary album color
- **Logarithmic response** — power-law height scaling makes loud peaks dramatic while quiet bands sit near the baseline
- **Album metadata** — title, artist, and artwork pulled from embedded ID3 tags (MP3/AAC/FLAC)
- **Recently played sidebar** — quick access to previously played tracks, click any to replay
- **Full playback controls** — play/pause, click-to-seek progress bar, volume slider
- **Zero dependencies to install** — libraries load from CDN at runtime

---

## Usage

1. Open `visualizer.html` in any modern browser (Chrome, Firefox, Safari, Edge)
2. Drop an audio file onto the drop zone, or click to pick one from your file system
3. The visualizer starts immediately — use the controls at the bottom to pause, seek, or adjust volume
4. Click **Back** in the sidebar to return to the drop zone and load a new file
5. Previously played tracks appear in the sidebar and can be replayed with one click

**Supported formats:** MP3, AAC, FLAC, WAV (anything your browser's Web Audio API can decode)

---

## How It Works

| Concern | Approach |
|---|---|
| Audio decoding | Web Audio API — `AudioContext.decodeAudioData` |
| Real-time analysis | `AnalyserNode` with FFT size 2048, smoothing 0.8 |
| Frequency mapping | 60 pills mapped to 0–12 kHz using averaged frequency bins |
| Height scaling | Power-law curve `(amplitude/255)²` for dynamic contrast |
| Pill colors | `ColorThief.getPalette()` → linearly interpolated across all 60 pills |
| Background glow | `ColorThief.getColor()` primary color, opacity driven by 0–250 Hz bass energy |
| Metadata | `jsmediatags` reads ID3v2/v3 tags for title, artist, and embedded artwork |
| Playback | `BufferSourceNode` — recreated on each play/seek; source ID guards stale `onended` callbacks |

---

## Libraries (CDN)

| Library | Version | Purpose |
|---|---|---|
| [jsmediatags](https://github.com/nicktindall/jsmediatags) | 3.9.5 | ID3 tag parsing |
| [color-thief](https://github.com/lokesh/color-thief) | 2.6.0 | Album art color extraction |

---

## Browser Support

Requires a browser with Web Audio API support. All modern browsers qualify.

| Browser | Support |
|---|---|
| Chrome 99+ | Full |
| Firefox 112+ | Full |
| Safari 15.4+ | Full |
| Edge 99+ | Full |

> `CanvasRenderingContext2D.roundRect` (Chrome 99+, Firefox 112+, Safari 15.4+) is used for pill rendering, with an `arcTo`-based fallback for older browsers.

---

## Project Structure

```
audio-visualizer/
└── visualizer.html    # Single self-contained file — HTML, CSS, and JS
```

---

## License

MIT
