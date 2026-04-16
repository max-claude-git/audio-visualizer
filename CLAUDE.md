# Audio Visualizer — Project Context for Claude

## What This Is

A single-file browser-based audio visualizer. The entire app lives in **`visualizer.html`** (~2600 lines of HTML + CSS + JS). There is no build step, no package.json, no framework. Open the file in a browser and it works.

**`server.py`** is a trivial local HTTP server (Python) for serving the file at `http://127.0.0.1:8080/visualizer.html`, which is required for Spotify OAuth to work (the redirect URI is hardcoded to that address).

---

## Architecture

Everything is in `visualizer.html`. Edits always happen to this single file.

```
visualizer.html
  <style>      — all CSS (~400 lines)
  <body>       — all HTML (~200 lines of elements)
  <script>     — all JS (~2000 lines)
```

**Libraries loaded from CDN at runtime** (no npm):
- `jsmediatags` 3.9.5 — ID3 tag parsing
- `color-thief` 2.6.0 — album art color extraction
- Google Fonts — DM Sans (body), Space Grotesk (headings/numbers)

**Native browser APIs used:**
- Web Audio API — `AudioContext`, `AnalyserNode`, `BiquadFilterNode`, `BufferSourceNode`, `MediaStreamSource`
- Canvas 2D API — all visualization rendering
- `getUserMedia` — microphone input
- Web Crypto API — Spotify PKCE code challenge

---

## Two Modes

### File Mode (default)
User drags/drops local audio files. Queue of files plays sequentially or shuffled. Audio goes through the full signal chain: `source → gainNode → bassFilter → midFilter → trebleFilter → analyser → destination`.

### Spotify Mode
User connects Spotify via PKCE OAuth. The browser **cannot** access Spotify's audio stream. Visualization is synthetic — built from beats/segments from the (now deprecated) audio-analysis API, or from the user's microphone. The "Mic Input" button becomes visible in Spotify mode; pressing it captures real audio via `getUserMedia`.

---

## Current Feature Set

### Visualizer Styles (all canvas-based, switched via `vizStyle`)
- **Bars** — frequency bars from bottom; in cinema mode bars also grow down from top (mirror-crush)
- **Mirror** — bars symmetric around center line
- **Wave** — smooth bezier waveform with gradient fill (frequency amplitude → wave height)
- **Scope** — oscilloscope time-domain waveform; real audio in file mode, synthesized in Spotify mode

### Audio Processing
- 3-band EQ: Bass (lowshelf 200Hz), Mid (peaking 1kHz), Treble (highshelf 8kHz), ±12dB
- Sensitivity multiplier (0.5–3×)
- Smoothing constant (0–0.95)

### Cinema Mode
Full-screen overlay triggered by `F` key or ⛶ button. Effects:
- Canvas height 82% of screen, bar max-height 68% of canvas
- Waveform glow via `ctx.shadowBlur` (wave/scope only — too expensive for bars)
- Beat-flash: `#cinema-bg` brightens on each detected beat, fades back over 450ms
- Expanding elliptical rings from screen center on each beat (drawn **behind** the waveform)
- Particles spawn near the top edge, fall down with gravity, colored by frequency band
- Track title + artist rendered on canvas, glow + subtle scale pulse driven by `smoothBass`

### Theming
Dynamic CSS variables `--accent`, `--accent-dim`, `--accent-subtle`, `--accent-label`, `--accent-text`, `--bg-tint`. Updated by:
- **Auto** — Color-Thief extracts palette from album artwork
- **Presets** — Purple, Blue, Green, Gold, Red, Mono (hardcoded RGB in `THEME_PRESETS`)

Theme persists across reloads via `localStorage.getItem('theme')`.

### Info Panel (right side)
Dual-tab: **Info** and **Queue**.

Info tab sections:
- BPM + Key (large numbers; from ID3 tags → autocorrelation fallback for BPM; Camelot wheel notation)
- **Lyrics** (lrclib.net; synced auto-scroll or plain text)
- **Stats section** — switches content based on mode:
  - File mode: Last.fm album info (listeners, tags, wiki summary, similar artists, tracklist)
  - Spotify mode: Popularity score (0–100), **no feature bars** (audio-features API deprecated)
- Wikipedia sections: Song, Album, Artist (collapsible, from Wikipedia REST API)
- Recently played list

### Playback Controls
- Prev / Play-Pause / Next buttons always visible
- Like button (♥) — Spotify mode only
- Waveform scrubber — click to seek (file mode)
- Volume slider
- **Spotify/File button** — label reads "Spotify" in file mode, "File" in Spotify mode; sits in `#player-actions` at the far right with `margin-left:auto`

### Queue
Files accumulate into an ordered queue. Auto-advances on track end (400ms delay). Shuffle uses Fisher-Yates. Queue tab shows track list; click to jump.

### Spotify Features
- PKCE OAuth (no backend, tokens in `sessionStorage`)
- Polls `/me/player/currently-playing` every 5s
- Playback: play/pause, seek, next/prev via API
- Like/unlike tracks
- Playlist creation and adding tracks (current track or session history)
- Mic input for real spectrum visualization

---

## Key Constants

```js
const PILL_COUNT     = 60;    // frequency bins
const PILL_GAP       = 3;     // px between bars
const MAX_HEIGHT     = 280;   // px, max bar height (file mode)
const FREQ_CAP_HZ    = 12000; // only analyze up to 12kHz
const MAX_GLOW_ALPHA = 0.36;
const MAX_RECENT     = 8;
```

---

## Important State Variables

| Variable | Type | Purpose |
|---|---|---|
| `vizStyle` | string | 'bars' / 'mirror' / 'wave' / 'scope' |
| `activeTheme` | string | 'auto' / 'purple' / 'blue' / 'green' / 'gold' / 'red' / 'mono' |
| `spotifyMode` | boolean | true when Spotify auth active |
| `glowColor` | [r,g,b] | current accent color (used by glow + cinema rings) |
| `pillColors` | string[60] | per-bar color strings |
| `smoothBass` | number | EMA of low-frequency energy (drives beat detection at 0.52 threshold) |
| `cinemaRings` | array | active pulse rings `{r, speed, alpha, decay, maxR}` |
| `cinemaParticles` | array | active falling particles |
| `cinemaMaxH` | number | set in `enterCinema()` to `floor(canvasH * 0.68)` |
| `queue` | File[] | ordered playback queue |
| `fetchGen` | number | incremented on each new track; cancels stale API callbacks |
| `micActive` | boolean | whether getUserMedia mic is live |

---

## Key Functions to Know

| Function | What It Does |
|---|---|
| `drawViz(data, onCinema)` | Dispatches to bars/mirror/wave/scope; in cinema adds glow, rings, particles, text |
| `updateGlow(data)` | Computes bass level, updates radial glow, triggers beat at threshold 0.52 |
| `triggerBeat()` | Artwork pulse, title pulse, cinema ring emit, cinema bg flash |
| `applyTheme([r,g,b])` | Updates all `--accent-*` CSS variables |
| `extractColors(imgEl)` | Color-Thief → pillColors + glowColor (skipped if activeTheme !== 'auto') |
| `selectTheme(name)` | Applies preset, saves to localStorage, updates buttons |
| `handleFile(file)` | Full reset + load: metadata, audio decode, BPM, start playback |
| `onSpotifyTrackChange(track)` | Shows Spotify section, populates popularity, fetches audio features |
| `transitionToPlayer()` | Shows player UI, calls `updateQueueButtons()`, sets btn-back label |
| `triggerFetches()` | Kicks off Last.fm (file mode only), Wikipedia, and lrclib fetches |
| `resetInfoPanel()` | Clears all info; restores Last.fm mode in stats section |
| `enterSpotifyMode()` | Sets btn-back to "File", shows mic/like buttons |
| `exitSpotifyMode()` | Sets btn-back to "Spotify", hides Spotify-only buttons |

---

## API Integrations

### Spotify
- Client ID: `44815ed0fe794738baa4b4290f0114d9`
- Redirect URI: `http://127.0.0.1:8080/visualizer.html`
- Scopes: `user-read-currently-playing user-read-playback-state user-modify-playback-state user-library-read user-library-modify playlist-read-private playlist-modify-public playlist-modify-private`
- `/audio-features` — **deprecated by Spotify for new apps (Nov 2024)**. BPM/Key show "—" in Spotify mode for new app registrations. Code still tries the endpoint but handles null gracefully.
- `/audio-analysis` — also effectively deprecated. Beats/segments may not be returned.

### Last.fm
- API key: `e515670feb2da14f25406442f18f17a0` (hardcoded public key)
- Only called in **file mode** (`triggerFetches` guards with `if (!spotifyMode)`)

### Wikipedia
- No API key needed; uses `origin=*` for CORS

### lrclib.net
- No API key needed; free lyrics API
- Returns `syncedLyrics` (LRC format with timestamps) and `plainLyrics`

---

## Known Limitations

- **Spotify audio is inaccessible**: No raw PCM from Spotify. All spectrum viz in Spotify mode is synthetic (or mic-based).
- **Spotify audio-features deprecated**: BPM and Key display as "—" in Spotify mode for apps created after May 2024.
- **Spotify stats section**: Shows popularity score (0–100) only. Stream counts are **not available** via the public Spotify API — do not attempt to implement this.
- **BPM from ID3**: Reads `tag.tags.TBPM` first (the correct jsmediatags frame ID), then `BPM`/`bpm` as fallbacks. Many files lack TBPM tags; autocorrelation fallback covers 55–180 BPM range.
- **Cinema glow on bars is disabled**: `shadowBlur` during 120 fillRect calls (~60 bars × top+bottom) causes lag. Glow only applied for wave/scope in cinema.
- **Particles fall from top**: Spawn at y≈0, fall downward with gravity (`vy *= 1.015`). Removed when `y > h`.

---

## Coding Conventions

- **No frameworks, no build tools.** Vanilla JS only.
- **No TypeScript, no JSDoc.** Plain JS.
- **Single file.** Do not split into multiple files.
- **CDN libraries only.** Do not add npm dependencies or inline large libraries.
- **CSS custom properties** (`--accent-*`) drive all color theming — update these, not hardcoded colors.
- **`fetchGen`** must be checked after every `await` in any API function that fetches metadata (`if (gen !== fetchGen) return`).
- **Canvas sizing**: `sizeCanvas()` computes `pillW` and `cinemaPillW`. Do not hardcode pixel widths for bars.
- **Beat detection**: Threshold is `smoothBass > 0.52`, compared against `prevBass` for rising-edge detection. Don't lower this — false positives ruin the effect.

---

## UI Layout Reference

```
body (min-height: 100vh, dark bg)
├── #splash        — initial landing (file drop + Spotify button)
├── #drop-zone     — full-screen drop overlay
├── #player-layout — flex row (file: cols 2:1, flex: left:right)
│   ├── #player-left
│   │   ├── #viz-wrap → canvas#viz
│   │   ├── #viz-panel (collapsible) — Bars/Mirror/Wave/Scope buttons
│   │   ├── #eq-panel (collapsible) — EQ sliders
│   │   ├── #theme-panel (collapsible) — color preset buttons
│   │   └── #player-bottom
│   │       ├── #artwork-col → img#artwork + #btn-youtube
│   │       └── #player-bottom-right
│   │           ├── #track-info (title / artist / album / #spotify-badge)
│   │           ├── #controls (prev | play | next | like | waveform | time | vol)
│   │           └── #player-actions (+ Song | Shuffle | Viz | EQ | Theme | Mic | Cinema | Save | [Spotify/File →])
│   └── #info-panel (right, scrollable, max-width 360px)
│       ├── #panel-tabs (Info / Queue)
│       ├── #tab-info
│       │   ├── #song-meta-panel (BPM + Key)
│       │   ├── #lyrics-section (collapsible)
│       │   ├── #lastfm-section (file: Last.fm | spotify: popularity score)
│       │   ├── #wiki-song / #wiki-album / #wiki-artist (collapsible)
│       │   └── #recent-songs
│       └── #tab-queue (queue list + clear)
├── #cinema        — fixed full-screen overlay (z-index 50)
├── #playlist-modal — fixed full-screen overlay (z-index 60)
├── #art-blur-bg   — fixed ambient blur (z-index -1)
├── #glow-overlay  — fixed radial glow (z-index 0)
└── #toast         — fixed notification
```

**Panel mutual exclusivity**: Viz, EQ, and Theme panels all close each other on open. Wired in `initControls()`.

**Stats section switching**: `#lastfm-content` (default) and `#spotify-info-content` (hidden) live inside `#lastfm-section`. Shown/hidden in `onSpotifyTrackChange` and `resetInfoPanel`.

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| Space | Play / Pause |
| ← / → | Seek ±10s |
| ↑ / ↓ | Volume ±10% |
| F | Toggle cinema mode |
| Esc | Exit cinema mode |
