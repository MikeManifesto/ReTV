:root {
    --bg: #0b0d10;
    --text: #f4f6f8;
    --muted: #8a949e;
    --accent: #5ed16a;
    --accent-dark: #2fa043;
    --border: rgba(255, 255, 255, .08);
}

* { box-sizing: border-box; }

html, body {
    height: 100%;
    margin: 0;
    overflow: hidden;
}

body {
    display: flex;
    flex-direction: column;
    background: var(--bg);
    background-image:
    radial-gradient(900px 600px at 25% 30%, rgba(94, 209, 106, .10), transparent 60%),
    radial-gradient(800px 600px at 85% 85%, rgba(70, 120, 255, .08), transparent 60%);
    color: var(--text);
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ---------- top bar ---------- */
.topbar {
    flex: none;
    padding: clamp(14px, 2.4vh, 28px) clamp(20px, 3.5vw, 56px) 0;
}

.brand {
    font-size: clamp(20px, 1.8vw, 26px);
    font-weight: 800;
    letter-spacing: -.5px;
    color: var(--text);
}

.brand::after {
    content: "";
    display: inline-block;
    width: 7px;
    height: 7px;
    margin-left: 4px;
    border-radius: 50%;
    background: var(--accent);
}

/* ---------- layout: image left, download right ---------- */
.stage {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
    gap: clamp(24px, 4vw, 72px);
    padding: clamp(12px, 2.5vh, 32px) clamp(20px, 3.5vw, 56px) clamp(20px, 3.5vh, 44px);
}

/* ---------- gallery ---------- */
.gallery {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    min-width: 0;
    min-height: 0;
}

.frame {
    position: relative;
    flex: 1;
    width: 100%;
    min-height: 0;
}

.shot {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    opacity: 0;
    transform: scale(.985);
    transition: opacity .7s ease, transform .7s ease;
    border-radius: 10px;
    filter: drop-shadow(0 20px 48px rgba(0, 0, 0, .6));
}

.shot.is-active {
    opacity: 1;
    transform: scale(1);
}

.dots {
    display: flex;
    gap: 10px;
    flex: none;
}

.dot {
    width: 28px;
    height: 4px;
    padding: 0;
    border: 0;
    border-radius: 4px;
    background: rgba(255, 255, 255, .18);
    cursor: pointer;
    transition: background .3s ease, width .3s ease;
}

.dot:hover { background: rgba(255, 255, 255, .35); }

.dot.is-active {
    width: 44px;
    background: var(--accent);
}

/* ---------- right panel ---------- */
.panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: clamp(28px, 6vh, 64px);
    text-align: center;
    min-width: 0;
}

.headline {
    margin: 0;
    font-size: clamp(30px, 3.6vw, 62px);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -.03em;
    text-wrap: balance;
    background: linear-gradient(180deg, #ffffff 0%, #b9c2cb 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.headline .accent {
    background: linear-gradient(180deg, #8cf09a 0%, var(--accent-dark) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.download {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: clamp(12px, 2vh, 20px);
    width: 100%;
    max-width: 420px;
    padding: clamp(20px, 3.4vh, 36px) clamp(20px, 2.4vw, 36px);
    background: rgba(255, 255, 255, .03);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, .35), inset 0 1px 0 rgba(255, 255, 255, .05);
    backdrop-filter: blur(8px);
}

.title {
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: clamp(16px, 1.35vw, 21px);
    font-weight: 600;
    color: var(--text);
}

.badge {
    padding: 3px 9px;
    font-size: .68em;
    font-weight: 700;
    letter-spacing: .5px;
    color: var(--accent);
    background: rgba(94, 209, 106, .12);
    border: 1px solid rgba(94, 209, 106, .35);
    border-radius: 999px;
}

/* ---------- button ---------- */
.btn {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    width: 100%;
    padding: clamp(15px, 2.2vh, 22px) 32px;
    font-size: clamp(17px, 1.5vw, 22px);
    font-weight: 700;
    letter-spacing: .2px;
    color: #06240d;
    text-decoration: none;
    white-space: nowrap;
    border-radius: 12px;
    background: linear-gradient(180deg, #7be389 0%, #4cc25b 100%);
    box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, .5),
    0 8px 24px rgba(94, 209, 106, .32),
    0 2px 4px rgba(0, 0, 0, .35);
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}

.btn:hover {
    transform: translateY(-2px);
    filter: brightness(1.06);
    box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, .55),
    0 12px 32px rgba(94, 209, 106, .42),
    0 2px 4px rgba(0, 0, 0, .35);
}

.btn:active {
    transform: translateY(0);
    box-shadow:
    inset 0 2px 6px rgba(0, 0, 0, .25),
    0 4px 12px rgba(94, 209, 106, .25);
}

.btn:focus-visible {
    outline: 3px solid rgba(255, 255, 255, .8);
    outline-offset: 3px;
}

.btn-icon { font-size: 1.15em; line-height: 1; }

.meta {
    margin: 0;
    font-size: clamp(12px, .9vw, 14px);
    color: var(--muted);
}

/* ---------- narrow screens: stack ---------- */
@media (max-width: 860px) {
    .stage {
        grid-template-columns: 1fr;
        grid-template-rows: minmax(0, 1fr) auto;
        gap: 20px;
    }

    .panel {
        order: -1;
        gap: 16px;
    }

    .stage { grid-template-rows: auto minmax(0, 1fr); }

    .headline { font-size: clamp(24px, 6.5vw, 36px); }

    .download { max-width: 360px; }
}

@media (max-width: 860px) and (max-height: 700px) {
    .gallery { display: none; }
    .stage { grid-template-rows: 1fr; }
}

@media (prefers-reduced-motion: reduce) {
    .shot, .btn, .dot { transition: none; }
}
