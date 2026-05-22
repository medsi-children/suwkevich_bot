# ruff: noqa: E501

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

SUPPORT_APP_HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#f9fbff" />
  <title>Профиль поддержки</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      color-scheme: light;
      --bg: #f8fbff;
      --bg-warm: #fff7f2;
      --surface: rgba(255, 255, 255, .86);
      --surface-solid: #ffffff;
      --line: rgba(87, 112, 136, .16);
      --text: #202833;
      --muted: #6d7886;
      --soft: #eef5f8;
      --mint: #8fd6c8;
      --sky: #a9c8ff;
      --peach: #ffd6a6;
      --rose: #f5b8c8;
      --lavender: #c9b7ff;
      --green: #b8e9aa;
      --shadow: 0 18px 48px rgba(96, 120, 146, .14);
      font-family: Inter, "Avenir Next", "Helvetica Neue", system-ui, -apple-system, sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      background:
        linear-gradient(rgba(96, 130, 154, .065) 1px, transparent 1px),
        linear-gradient(90deg, rgba(96, 130, 154, .055) 1px, transparent 1px),
        linear-gradient(135deg, #ffffff 0%, var(--bg) 42%, var(--bg-warm) 100%);
      background-size: 34px 34px, 34px 34px, auto;
      overflow-x: hidden;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(120deg, transparent 0 18%, rgba(143, 214, 200, .12) 18% 19%, transparent 19% 44%, rgba(169, 200, 255, .12) 44% 45%, transparent 45% 100%),
        linear-gradient(36deg, transparent 0 64%, rgba(255, 214, 166, .16) 64% 65%, transparent 65% 100%);
      opacity: .9;
    }

    button {
      font: inherit;
    }

    .app {
      width: min(1180px, 100%);
      margin: 0 auto;
      padding: max(22px, calc(env(safe-area-inset-top, 0px) + 18px)) 16px 28px;
      position: relative;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 18px;
    }

    .brand {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
      color: var(--muted);
      font-size: 13px;
      letter-spacing: .08em;
      text-transform: uppercase;
      font-weight: 750;
    }

    .brand-mark {
      width: 30px;
      height: 30px;
      border-radius: 8px;
      background:
        linear-gradient(135deg, rgba(143, 214, 200, .95), rgba(169, 200, 255, .85)),
        #fff;
      border: 1px solid rgba(255, 255, 255, .92);
      box-shadow: 0 10px 28px rgba(96, 120, 146, .16);
      position: relative;
      flex: 0 0 30px;
    }

    .brand-mark::before,
    .brand-mark::after {
      content: "";
      position: absolute;
      background: rgba(255, 255, 255, .96);
      border-radius: 999px;
      left: 8px;
      right: 8px;
      height: 2px;
      top: 10px;
      box-shadow: 0 7px 0 rgba(255, 255, 255, .96);
    }

    .icon-button {
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, .8);
      color: var(--text);
      box-shadow: 0 10px 28px rgba(96, 120, 146, .1);
      cursor: pointer;
      transition: transform .18s ease, border-color .18s ease, background .18s ease;
    }

    .icon-button:hover {
      transform: translateY(-1px);
      border-color: rgba(91, 184, 169, .42);
      background: #fff;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(280px, .8fr);
      gap: 18px;
      align-items: stretch;
      margin-bottom: 14px;
    }

    .hero.no-radar {
      grid-template-columns: 1fr;
    }

    .hero.no-radar .radar-panel {
      display: none;
    }

    .hero-copy,
    .radar-panel,
    .metric-card,
    .data-card,
    .activity-panel,
    .empty-state {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }

    .hero-copy {
      padding: clamp(20px, 4vw, 34px);
      min-height: 324px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 28px;
    }

    .kicker {
      margin: 0 0 10px;
      color: #4f9f91;
      font-size: 13px;
      letter-spacing: .1em;
      text-transform: uppercase;
      font-weight: 800;
    }

    h1 {
      margin: 0;
      max-width: 760px;
      font-size: clamp(28px, 6.2vw, 52px);
      line-height: 1.02;
      letter-spacing: 0;
      font-weight: 760;
      color: #4e978f;
      background: linear-gradient(135deg, #4f9f91 0%, #6f9fed 52%, #8f7fe1 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      text-wrap: balance;
    }

    .summary-text {
      margin: 18px 0 0;
      max-width: 760px;
      color: var(--muted);
      font-size: clamp(15px, 2.2vw, 18px);
      line-height: 1.58;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }

    .stat {
      min-height: 82px;
      padding: 12px;
      border-radius: 8px;
      background: rgba(255, 255, 255, .62);
      border: 1px solid rgba(87, 112, 136, .12);
    }

    .stat strong {
      display: block;
      font-size: 26px;
      line-height: 1;
      letter-spacing: 0;
    }

    .stat span {
      display: block;
      margin-top: 7px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.25;
    }

    .radar-panel {
      min-height: 324px;
      padding: 18px;
      display: grid;
      grid-template-rows: auto minmax(230px, 1fr) auto;
      gap: 12px;
    }

    .panel-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin: 0;
      font-size: 16px;
      line-height: 1.25;
      letter-spacing: 0;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 5px 9px;
      border-radius: 8px;
      color: #47766f;
      background: rgba(143, 214, 200, .18);
      border: 1px solid rgba(91, 184, 169, .2);
      font-size: 12px;
      font-weight: 750;
      white-space: nowrap;
    }

    .radar-wrap {
      position: relative;
      min-height: 230px;
      display: grid;
      place-items: center;
    }

    #radar {
      width: min(100%, 330px);
      max-height: 330px;
      aspect-ratio: 1 / 1;
    }

    .disclaimer {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }

    .tabs {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, .68);
      margin: 14px 0;
      backdrop-filter: blur(16px);
    }

    .tab {
      min-height: 42px;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: var(--muted);
      font-weight: 760;
      cursor: pointer;
      transition: background .18s ease, color .18s ease, box-shadow .18s ease;
    }

    .tab.active {
      color: var(--text);
      background: #fff;
      box-shadow: 0 10px 26px rgba(96, 120, 146, .12);
    }

    .panel {
      display: none;
    }

    .panel.active {
      display: grid;
      gap: 14px;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }

    .metric-card {
      min-height: 162px;
      padding: 14px;
      display: grid;
      gap: 12px;
      align-content: space-between;
    }

    .metric-card.empty {
      color: #818d9a;
      background: rgba(255, 255, 255, .68);
      border-color: rgba(128, 143, 158, .2);
      box-shadow: 0 14px 34px rgba(96, 120, 146, .08);
    }

    .metric-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }

    .metric-label {
      margin: 0;
      font-weight: 800;
      line-height: 1.2;
    }

    .metric-value {
      width: 54px;
      height: 54px;
      display: grid;
      place-items: center;
      flex: 0 0 54px;
      border-radius: 999px;
      color: var(--text);
      font-size: 16px;
      font-weight: 820;
      background:
        radial-gradient(circle at center, #fff 0 58%, transparent 59%),
        conic-gradient(var(--metric-tone) calc(var(--value) * 1%), rgba(87, 112, 136, .12) 0);
    }

    .metric-card.empty .metric-value {
      color: #8b96a3;
      background:
        radial-gradient(circle at center, #fff 0 58%, transparent 59%),
        conic-gradient(#b5bfca 0%, rgba(128, 143, 158, .16) 0);
    }

    .metric-card p {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .bar {
      height: 7px;
      border-radius: 999px;
      background: rgba(87, 112, 136, .12);
      overflow: hidden;
    }

    .bar span {
      display: block;
      width: calc(var(--value) * 1%);
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--metric-soft), var(--metric-tone));
    }

    .metric-card.empty .bar span {
      width: 0;
    }

    .two-column {
      display: grid;
      grid-template-columns: minmax(0, .96fr) minmax(0, 1.04fr);
      gap: 14px;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    .data-card {
      min-height: 184px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      justify-content: space-between;
    }

    .lifehack-card {
      position: relative;
      overflow: hidden;
      min-height: 208px;
      cursor: pointer;
      color: #fff;
      background: var(--lifehack-gradient);
      border-color: rgba(255, 255, 255, .24);
      border-radius: 16px;
      box-shadow: 0 18px 42px rgba(76, 92, 130, .18);
      justify-content: center;
      transition: transform .24s ease, box-shadow .24s ease;
    }

    .lifehack-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 22px 48px rgba(76, 92, 130, .22);
    }

    .lifehack-card:focus-visible {
      outline: 2px solid rgba(255, 255, 255, .75);
      outline-offset: 3px;
    }

    .lifehack-card::before {
      content: "";
      position: absolute;
      inset: -26px -24px auto auto;
      width: 54%;
      height: 112px;
      border-radius: 999px;
      background: rgba(255, 255, 255, .24);
      filter: blur(20px);
      opacity: .54;
      pointer-events: none;
    }

    .lifehack-card::after {
      content: "";
      position: absolute;
      inset: auto auto -70px -76px;
      width: 180px;
      height: 124px;
      border-radius: 999px;
      background: rgba(255, 255, 255, .14);
      filter: blur(18px);
      pointer-events: none;
    }

    .lifehack-card[data-style="0"] {
      --lifehack-gradient: linear-gradient(135deg, #ff4f8b 0%, #ff8a5c 48%, #ffd166 100%);
    }

    .lifehack-card[data-style="1"] {
      --lifehack-gradient: linear-gradient(135deg, #5f7cff 0%, #8759f2 55%, #c06cff 100%);
    }

    .lifehack-card[data-style="2"] {
      --lifehack-gradient: linear-gradient(135deg, #24b9d8 0%, #22d6a8 54%, #7fdc68 100%);
    }

    .lifehack-card[data-style="3"] {
      --lifehack-gradient: linear-gradient(135deg, #ffbf4f 0%, #ff6f91 48%, #9b5de5 100%);
    }

    .lifehack-card > * {
      position: relative;
      z-index: 1;
    }

    .lifehack-flash {
      position: absolute;
      inset: -12% auto -12% -45%;
      width: 42%;
      background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, .5), rgba(255, 255, 255, 0));
      transform: skewX(-20deg) translateX(0);
      opacity: 0;
      pointer-events: none;
      filter: blur(3px);
    }

    .lifehack-card.opening .lifehack-flash {
      opacity: 1;
      animation: lifehackFlash .46s ease forwards;
    }

    .lifehack-head {
      position: relative;
      min-height: 172px;
      display: block;
      text-align: center;
    }

    .lifehack-gesture {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      width: 136px;
      height: 136px;
      padding: 14px;
      display: grid;
      place-items: center;
      gap: 0;
      border: 1px solid rgba(255, 255, 255, .42);
      border-radius: 999px;
      background: linear-gradient(180deg, rgba(255, 255, 255, .24), rgba(255, 255, 255, .12));
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, .24),
        0 12px 26px rgba(40, 53, 79, .16);
      backdrop-filter: blur(12px);
      transition:
        opacity .24s ease,
        transform .24s ease,
        visibility .24s ease,
        background .18s ease;
    }

    .lifehack-card:hover .lifehack-gesture {
      background: linear-gradient(180deg, rgba(255, 255, 255, .28), rgba(255, 255, 255, .16));
    }

    .lifehack-gesture svg {
      width: 68px;
      height: 68px;
      stroke: currentColor;
      fill: none;
      stroke-width: 1.9;
    }

    .lifehack-hint {
      position: absolute;
      left: 50%;
      top: calc(50% + 30px);
      transform: translateX(-50%) translateY(6px);
      display: block;
      width: 92px;
      max-width: 92px;
      font-size: 10px;
      line-height: 1.1;
      text-transform: uppercase;
      letter-spacing: .04em;
      text-align: center;
      text-wrap: balance;
      opacity: 0;
      animation: lifehackHintLoop 5.4s ease-in-out infinite;
    }

    .lifehack-detail {
      position: absolute;
      left: 18px;
      right: 18px;
      top: 16px;
      bottom: 16px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 12px;
      opacity: 0;
      visibility: hidden;
      overflow: hidden;
      transform: translateY(10px) scale(.98);
      transition:
        opacity .34s ease .08s,
        transform .34s ease .08s,
        visibility .34s ease;
    }

    .lifehack-card.open .lifehack-detail {
      opacity: 1;
      visibility: visible;
      transform: translateY(0) scale(1);
    }

    .lifehack-card.open .lifehack-gesture {
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
      transform: translate(-50%, -50%) scale(.92);
    }

    @keyframes lifehackFlash {
      0% {
        transform: skewX(-20deg) translateX(0);
      }
      100% {
        transform: skewX(-20deg) translateX(420%);
      }
    }

    @keyframes lifehackHintLoop {
      0%, 58% {
        opacity: 0;
        transform: translateX(-50%) translateY(8px);
      }
      72%, 82% {
        opacity: .84;
        transform: translateX(-50%) translateY(0);
      }
      100% {
        opacity: 0;
        transform: translateX(-50%) translateY(-4px);
      }
    }

    .insight-card {
      position: relative;
      overflow: hidden;
      min-height: 146px;
      color: #fff;
      background:
        radial-gradient(circle at 92% 12%, rgba(255, 255, 255, .18), transparent 42%),
        linear-gradient(135deg, var(--insight-soft) 0%, var(--insight-tone) 100%);
      border-color: rgba(255, 255, 255, .22);
      border-radius: 16px;
      box-shadow: 0 18px 42px rgba(76, 92, 130, .16);
      transition: transform .24s ease, box-shadow .24s ease;
    }

    .insight-card::before {
      content: "";
      position: absolute;
      inset: -28px -30px auto auto;
      width: 132px;
      height: 96px;
      border-radius: 999px;
      background: rgba(255, 255, 255, .14);
      filter: blur(16px);
      pointer-events: none;
    }

    .insight-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 22px 48px rgba(76, 92, 130, .2);
    }

    .insight-card .insight-meta {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      width: max-content;
      max-width: 100%;
      min-height: 26px;
      padding: 5px 10px;
      border-radius: 999px;
      background: rgba(255, 255, 255, .16);
      border: 1px solid rgba(255, 255, 255, .26);
      color: rgba(255, 255, 255, .92);
      font-size: 11px;
      line-height: 1;
      text-transform: uppercase;
      letter-spacing: .08em;
      backdrop-filter: blur(10px);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, .16);
    }

    .data-card small {
      color: #4f9f91;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .08em;
    }

    .data-card h3 {
      margin: 0;
      font-size: 20px;
      line-height: 1.2;
      letter-spacing: 0;
    }

    .data-card p {
      margin: 0;
      color: var(--muted);
      line-height: 1.48;
      font-size: 14px;
    }

    .lifehack-card h3,
    .lifehack-card p,
    .insight-card h3,
    .insight-card p {
      color: #fff;
      text-shadow: 0 1px 12px rgba(38, 48, 70, .18);
    }

    .card-actions {
      display: flex;
      gap: 8px;
      align-items: center;
      justify-content: flex-start;
    }

    .action-button {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 36px;
      padding: 7px 11px;
      border-radius: 8px;
      border: 1px solid rgba(91, 184, 169, .24);
      background: rgba(143, 214, 200, .13);
      color: #316f66;
      font-weight: 780;
      cursor: pointer;
      transition: transform .18s ease, background .18s ease;
    }

    .action-button:hover {
      transform: translateY(-1px);
      background: rgba(143, 214, 200, .2);
    }

    .activity-panel {
      padding: 16px;
      min-height: 232px;
      display: grid;
      gap: 18px;
    }

    .activity-bars {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 8px;
      min-height: 150px;
      align-items: end;
    }

    .day {
      display: grid;
      gap: 7px;
      align-items: end;
      min-width: 0;
      color: var(--muted);
      font-size: 11px;
      text-align: center;
    }

    .day i {
      display: block;
      min-height: 8px;
      height: max(8px, calc(var(--height) * 1.25px));
      border-radius: 8px 8px 3px 3px;
      background: linear-gradient(180deg, var(--sky), var(--mint));
      border: 1px solid rgba(255, 255, 255, .76);
      box-shadow: 0 10px 22px rgba(96, 120, 146, .1);
    }

    .support-layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 14px;
    }

    .empty-state {
      padding: 22px;
      min-height: 160px;
      display: grid;
      align-content: center;
      gap: 8px;
      color: var(--muted);
    }

    .empty-state strong {
      color: var(--text);
      font-size: 18px;
    }

    .status {
      min-height: 24px;
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .loading .hero-copy,
    .loading .radar-panel,
    .loading .metric-card,
    .loading .data-card,
    .loading .activity-panel {
      position: relative;
      overflow: hidden;
    }

    .loading .hero-copy::after,
    .loading .radar-panel::after,
    .loading .metric-card::after,
    .loading .data-card::after,
    .loading .activity-panel::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(110deg, transparent 0 35%, rgba(255, 255, 255, .64) 45%, transparent 58% 100%);
      transform: translateX(-100%);
      animation: shimmer 1.45s ease-in-out infinite;
    }

    @keyframes shimmer {
      to { transform: translateX(100%); }
    }

    @media (max-width: 900px) {
      .hero,
      .two-column,
      .support-layout {
        grid-template-columns: 1fr;
      }
      .metrics-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 620px) {
      .app {
        padding-left: 12px;
        padding-right: 12px;
      }
      .hero-copy {
        min-height: 0;
      }
      .tabs {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
      .cards,
      .metrics-grid {
        grid-template-columns: 1fr;
      }
      .radar-panel {
        min-height: 300px;
      }
    }
  </style>
</head>
<body>
  <main class="app loading">
    <div class="topbar">
      <div class="brand"><span class="brand-mark" aria-hidden="true"></span><span>Сушкевич Бот</span></div>
      <!-- refresh button removed -->
    </div>

    <section class="hero" id="hero">
      <div class="hero-copy">
        <div>
          <p class="kicker">Личный профиль поддержки</p>
          <h1 id="hello">Собираю ваш профиль</h1>
          <p class="summary-text" id="profileSummary">Проверяю сохраненные темы, инсайты и способы поддержки.</p>
        </div>
      </div>
      <aside class="radar-panel">
        <h2 class="panel-title">Диаграмма личности</h2>
        <div class="radar-wrap">
          <canvas id="radar" width="620" height="620"></canvas>
        </div>
        <p class="disclaimer" id="disclaimer">Перед вами карта вашей личности, на основе анализа Сушкевич Бота. Она будет становится точнее и точнее с каждым разговором с вами.</p>
      </aside>
    </section>

    <nav class="tabs" aria-label="Разделы профиля">
      <button class="tab" type="button" data-tab="lifehacks">Лайфхаки</button>
      <button class="tab active" type="button" data-tab="personality">Личность</button>
      <button class="tab" type="button" data-tab="insights">Инсайты</button>
    </nav>

    <section class="panel" id="panel-lifehacks">
      <div class="cards" id="lifehackCards"></div>
    </section>

    <section class="panel active" id="panel-personality">
      <div class="metrics-grid" id="metricsGrid"></div>
      <div class="activity-panel">
        <h2 class="panel-title">Ритм последних дней <span class="badge">7 дней</span></h2>
        <div class="activity-bars" id="activityBars"></div>
      </div>
    </section>

    <section class="panel" id="panel-insights">
      <div class="cards" id="insightCards"></div>
    </section>

    <div class="status" id="status"></div>
  </main>

  <script>
    const root = document.querySelector(".app");
    const statusEl = document.getElementById("status");
    const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
    if (tg) {
      tg.ready();
      tg.expand();
      tg.setHeaderColor("#f9fbff");
      tg.setBackgroundColor("#f9fbff");
    }
    const escapeHtml = (value) => String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
    const params = new URLSearchParams(window.location.search);
    const tgUser = tg && tg.initDataUnsafe ? tg.initDataUnsafe.user || {} : {};
    const demoMode = params.get("demo") === "1";
    const localTelegramId = Number(params.get("telegram_id") || 0);
    const telegramId = Number(tgUser.id || localTelegramId || 0);
    const metricLabels = [
      "Субъектность",
      "Эмпатия",
      "Границы",
      "Чувствительность",
      "Ясность",
      "Рациональность",
    ];
    function emptyMetrics() {
      return metricLabels.map((label, order) => ({
        label,
        order,
        value: null,
        empty: true,
        hint: "Информации о вас пока мало",
        tone: ["#eef2f6", "#aeb8c4"],
      }));
    }
    function placeholderProfile(firstName) {
      return {
        user: {
          first_name: firstName || null,
          profile_summary: "Информации о вас пока мало. Профиль станет точнее после нескольких разговоров.",
        },
        metrics: emptyMetrics(),
        activity: [],
        lifehack_cards: [],
        insights: [],
        disclaimer: "Перед вами карта вашей личности, на основе анализа Сушкевич Бота. Она будет становится точнее и точнее с каждым разговором с вами.",
      };
    }
    function setText(id, value) {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    }
    function shortProfileDescription(text) {
      const clean = String(text || "").replace(/\\s+/g, " ").trim();
      if (!clean) return "Здесь появится короткое описание вас на основе ваших разговоров с ботом.";
      const firstSentence = clean.match(/.+?[.!?](\\s|$)/);
      const short = firstSentence ? firstSentence[0].trim() : clean;
      return short.length > 170 ? `${short.slice(0, 167).trimEnd()}...` : short;
    }
    function sendPrompt(text) {
      const payload = JSON.stringify({ type: "support_prompt", text });
      if (tg && tg.sendData) {
        tg.sendData(payload);
        tg.close();
        return;
      }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          statusEl.textContent = "Текст скопирован. Его можно вставить в чат с ботом.";
        });
        return;
      }
      statusEl.textContent = text;
    }
    function cardTemplate(card, actionText) {
      const title = escapeHtml(card.title || "Без названия");
      const text = escapeHtml(card.text || card.next_step || "");
      const meta = escapeHtml(card.source || card.kind || card.date || "");
      const nextStep = escapeHtml(card.next_step || "");
      const prompt = `Хочу обсудить: ${card.title || ""}. ${card.next_step || card.text || ""}`.trim();
      // Build the HTML for a card. If no actionText is provided, omit the action button.
      const actionsHtml = actionText
        ? `<div class="card-actions">
            <button class="action-button" type="button" data-prompt="${escapeHtml(prompt)}">
              <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"></path>
              </svg>
              ${escapeHtml(actionText)}
            </button>
          </div>`
        : "";
      return `
        <article class="data-card">
          <div>
            ${meta ? `<small>${meta}</small>` : ""}
            <h3>${title}</h3>
            ${text ? `<p>${text}</p>` : ""}
            ${nextStep ? `<p style="margin-top: 10px;">${nextStep}</p>` : ""}
          </div>
          ${actionsHtml}
        </article>
      `;
    }
    function renderCards(id, cards, emptyTitle, emptyText, actionText) {
      const el = document.getElementById(id);
      if (!el) return;
      if (!cards || !cards.length) {
        el.innerHTML = `<div class="empty-state"><strong>${escapeHtml(emptyTitle)}</strong><span>${escapeHtml(emptyText)}</span></div>`;
        return;
      }
      el.innerHTML = cards.map((card) => cardTemplate(card, actionText)).join("");
      el.querySelectorAll("[data-prompt]").forEach((button) => {
        button.addEventListener("click", () => sendPrompt(button.dataset.prompt));
      });
    }
    function lifehackTemplate(card, index) {
      const title = escapeHtml(card.title || "Лайфхак");
      const text = escapeHtml(card.text || "");
      const nextStep = escapeHtml(card.next_step || "");
      const styleIndex = index % 4;
      return `
        <article class="data-card lifehack-card" data-style="${styleIndex}" data-lifehack-card="${index}" tabindex="0" role="button" aria-expanded="false" aria-label="Открыть лайфхак: ${title}">
          <div class="lifehack-flash" aria-hidden="true"></div>
          <div class="lifehack-head">
            <div class="lifehack-gesture" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M2 12s3.8-6 10-6 10 6 10 6-3.8 6-10 6-10-6-10-6Z"></path>
                <circle cx="12" cy="12" r="3.2"></circle>
              </svg>
              <span class="lifehack-hint">нажмите на карточку</span>
            </div>
            <div class="lifehack-detail">
              ${text ? `<p>${text}</p>` : ""}
              ${nextStep ? `<p>${nextStep}</p>` : ""}
            </div>
          </div>
        </article>
      `;
    }
    function renderLifehacks(cards) {
      const el = document.getElementById("lifehackCards");
      if (!el) return;
      if (!cards || !cards.length) {
        el.innerHTML = `<div class="empty-state"><strong>Лайфхаки для вас ещё не готовы</strong><span>Они появятся после того, как вы немного пообщаетесь с ботом.</span></div>`;
        return;
      }
      el.innerHTML = cards.map((card, index) => lifehackTemplate(card, index)).join("");
      const openLifehack = (card) => {
        if (!card || card.classList.contains("open") || card.classList.contains("opening")) return;
        card.classList.add("opening");
        window.setTimeout(() => {
          card.classList.add("open");
          card.classList.remove("opening");
          card.setAttribute("aria-expanded", "true");
        }, 220);
      };
      el.querySelectorAll("[data-lifehack-card]").forEach((card) => {
        card.addEventListener("click", () => openLifehack(card));
        card.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            openLifehack(card);
          }
        });
      });
    }
    function renderInsights(cards) {
      const el = document.getElementById("insightCards");
      if (!el) return;
      if (!cards || !cards.length) {
        el.innerHTML = `<div class="empty-state"><strong>Наблюдений пока нет</strong><span>Здесь появятся важные осознания и динамика из разговоров.</span></div>`;
        return;
      }
      const insightThemes = {
        agency: { label: "Субъектность", soft: "#8fd6c8", tone: "#5bb8a9" },
        empathy: { label: "Эмпатия", soft: "#ffd6a6", tone: "#f3ad61" },
        boundaries: { label: "Границы", soft: "#c9b7ff", tone: "#987de8" },
        sensitivity: { label: "Чувствительность", soft: "#b7e6ff", tone: "#67badc" },
        clarity: { label: "Ясность", soft: "#a9c8ff", tone: "#6f9fed" },
        rationality: { label: "Рациональность", soft: "#f5b8c8", tone: "#df7f9a" },
      };
      const inferInsightTheme = (card) => {
        const text = `${card.title || ""} ${card.text || ""}`.toLowerCase();
        const checks = [
          ["sensitivity", ["сон", "тело", "дых", "напряж", "состояни", "тревог", "устал", "чувств"]],
          ["empathy", ["других", "другому", "ему", "ей", "людям", "обид", "поддерж", "чувства других"]],
          ["boundaries", ["границ", "просьб", "отказ", "не обяз", "сказать нет"]],
          ["agency", ["шаг", "выбор", "решил", "действ", "ответ", "сказать"]],
          ["clarity", ["ясн", "понят", "видно", "заметили", "осозн", "сформулир", "ошиб", "моя роль"]],
          ["rationality", ["факт", "доказ", "реальн", "провер", "логич", "правда", "без доказ"]],
        ];
        for (const [key, words] of checks) {
          if (words.some((word) => text.includes(word))) return key;
        }
        const fallback = {
          growth: "agency",
          attention: "sensitivity",
          resource: "empathy",
          calm: "clarity",
        };
        return fallback[card.tone || "calm"] || "clarity";
      };
      el.innerHTML = cards.map((card) => {
        const themeKey = inferInsightTheme(card);
        const theme = insightThemes[themeKey] || insightThemes.clarity;
        return `
        <article class="data-card insight-card" data-theme="${escapeHtml(themeKey)}" style="--insight-soft: ${theme.soft}; --insight-tone: ${theme.tone};">
          <div>
            <small class="insight-meta">${escapeHtml(theme.label)}</small>
            <h3>${escapeHtml(card.title || "Наблюдение")}</h3>
            <p>${escapeHtml(card.text || "")}</p>
          </div>
        </article>
      `;
      }).join("");
    }
    function renderMetrics(metrics) {
      const grid = document.getElementById("metricsGrid");
      if (!metrics || !metrics.length) {
        grid.innerHTML = `<div class="empty-state"><strong>Информации о вас пока мало</strong><span>Профиль станет точнее после нескольких сообщений в боте.</span></div>`;
        return;
      }
      grid.innerHTML = metrics.map((metric) => {
        const isEmpty = metric.empty || metric.value === null || metric.value === undefined;
        const value = isEmpty ? 0 : Math.max(0, Math.min(100, Number(metric.value || 0)));
        const soft = isEmpty ? "#eef2f6" : (metric.tone && metric.tone[0] ? metric.tone[0] : "#a9c8ff");
        const tone = isEmpty ? "#aeb8c4" : (metric.tone && metric.tone[1] ? metric.tone[1] : "#6f9fed");
        const hint = isEmpty ? (metric.hint || "Информации о вас пока мало") : metric.hint;
        return `
          <article class="metric-card${isEmpty ? " empty" : ""}" style="--value: ${value}; --metric-soft: ${soft}; --metric-tone: ${tone};">
            <div class="metric-top">
              <h3 class="metric-label">${escapeHtml(metric.label)}</h3>
              <div class="metric-value">${isEmpty ? "--" : Math.round(value)}</div>
            </div>
            <p>${escapeHtml(hint)}</p>
            <div class="bar" aria-hidden="true"><span></span></div>
          </article>
        `;
      }).join("");
    }
    function renderActivity(activity) {
      const el = document.getElementById("activityBars");
      el.innerHTML = (activity || []).map((day) => `
        <div class="day" style="--height: ${Number(day.value || 0)};">
          <i title="${Number(day.count || 0)} сообщений"></i>
          <span>${escapeHtml(day.label)}</span>
        </div>
      `).join("");
    }
    function drawRadar(metrics) {
      const canvas = document.getElementById("radar");
      const ctx = canvas.getContext("2d");
      const size = canvas.width;
      const center = size / 2;
      const radius = size * .34;
      if (!metrics || !metrics.length) {
        ctx.clearRect(0, 0, size, size);
        return;
      }
      ctx.clearRect(0, 0, size, size);
      const hasRealMetrics = metrics.some((metric) => !(metric.empty || metric.value === null || metric.value === undefined));
      const metricValue = (metric) => Math.max(0, Math.min(100, Number(metric.value || 0)));
      ctx.lineWidth = 2;
      ctx.font = "24px Inter, system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      const count = metrics.length || 1;
      const angleFor = (index) => -Math.PI / 2 + index * (Math.PI * 2 / count);
      for (let ring = 1; ring <= 4; ring += 1) {
        ctx.beginPath();
        const ringRadius = radius * ring / 4;
        for (let i = 0; i < count; i += 1) {
          const angle = angleFor(i);
          const x = center + Math.cos(angle) * ringRadius;
          const y = center + Math.sin(angle) * ringRadius;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.strokeStyle = "rgba(87, 112, 136, .16)";
        ctx.stroke();
      }
      metrics.forEach((metric, index) => {
        const angle = angleFor(index);
        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.lineTo(center + Math.cos(angle) * radius, center + Math.sin(angle) * radius);
        ctx.strokeStyle = "rgba(87, 112, 136, .12)";
        ctx.stroke();
        const labelRadius = radius + 46;
        const lx = Math.max(74, Math.min(size - 74, center + Math.cos(angle) * labelRadius));
        const ly = Math.max(42, Math.min(size - 42, center + Math.sin(angle) * labelRadius));
        ctx.fillStyle = hasRealMetrics ? "#5f6d7a" : "#8b96a3";
        const words = String(metric.label || "").split(" ");
        const lines = words.length > 2 ? [words.slice(0, -1).join(" "), words.at(-1)] : words;
        const startY = ly - (lines.length - 1) * 12;
        lines.forEach((lineText, line) => ctx.fillText(lineText, lx, startY + line * 24));
      });
      if (!hasRealMetrics) return;
      const neutralValue = 36;
      const displayValue = (metric) => (
        metric.empty || metric.value === null || metric.value === undefined
          ? neutralValue
          : metricValue(metric)
      );
      ctx.beginPath();
      metrics.forEach((metric, index) => {
        const valueRadius = radius * displayValue(metric) / 100;
        const angle = angleFor(index);
        const x = center + Math.cos(angle) * valueRadius;
        const y = center + Math.sin(angle) * valueRadius;
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      const fill = ctx.createLinearGradient(120, 80, size - 120, size - 80);
      fill.addColorStop(0, "rgba(143, 214, 200, .44)");
      fill.addColorStop(.5, "rgba(169, 200, 255, .36)");
      fill.addColorStop(1, "rgba(255, 214, 166, .34)");
      ctx.fillStyle = fill;
      ctx.fill();
      ctx.strokeStyle = "rgba(91, 184, 169, .8)";
      ctx.lineWidth = 4;
      ctx.stroke();
      metrics.forEach((metric, index) => {
        const isEmpty = metric.empty || metric.value === null || metric.value === undefined;
        const valueRadius = radius * displayValue(metric) / 100;
        const angle = angleFor(index);
        const x = center + Math.cos(angle) * valueRadius;
        const y = center + Math.sin(angle) * valueRadius;
        ctx.beginPath();
        ctx.arc(x, y, isEmpty ? 6 : 8, 0, Math.PI * 2);
        ctx.fillStyle = isEmpty ? "rgba(174, 184, 196, .72)" : (metric.tone && metric.tone[1] ? metric.tone[1] : "#5bb8a9");
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = isEmpty ? 2 : 3;
        ctx.stroke();
      });
    }
    function renderProfile(data) {
      const firstName = data.user && data.user.first_name ? data.user.first_name : "вы";
      const metrics = data.metrics || [];
      const hasRealMetrics = metrics.some((metric) => !(metric.empty || metric.value === null || metric.value === undefined));
      document.getElementById("hero").classList.toggle("no-radar", !hasRealMetrics);
      setText("hello", firstName === "вы" ? "Профиль" : firstName);
      setText("profileSummary", shortProfileDescription(data.user.profile_summary));
      setText("disclaimer", data.disclaimer);
      renderMetrics(metrics);
      renderActivity(data.activity || []);
      drawRadar(hasRealMetrics ? metrics : []);
      renderLifehacks(data.lifehack_cards);
      renderInsights(data.insights);
      root.classList.remove("loading");
      statusEl.textContent = "";
    }
    function demoProfile() {
      return {
        user: {
          first_name: params.get("first_name") || "Антон",
          profile_summary: "В последних диалогах заметны усталость, желание ясности и попытка вернуть себе управление. Сейчас важнее не давить на себя, а выбрать один понятный шаг и заметить опоры, которые уже работают.",
        },
        summary: {
          memory_count: 18,
          open_topics_count: 4,
          support_items_count: 6,
          latest_update: "21.05.2026",
        },
        disclaimer: "Перед вами карта вашей личности, на основе анализа Сушкевич Бота. Она будет становится точнее и точнее с каждым разговором с вами.",
        metrics: [
          { label: "Субъектность", value: 68, hint: "Насколько вы чувствуете, что влияете на свою жизнь, принимаете решения сами и не живете в позиции вечной уступки или подчинения чужой воле.", tone: ["#8fd6c8", "#5bb8a9"] },
          { label: "Эмпатия", value: 63, hint: "Насколько вы замечаете чувства других людей и понимаете, как ваши слова и поступки на них влияют.", tone: ["#ffd6a6", "#f3ad61"] },
          { label: "Границы", value: 52, hint: "Насколько вы чувствуете свои пределы, умеете обозначать их другим, говорить «нет» и замечать момент, когда на вас начинают заходить слишком далеко.", tone: ["#c9b7ff", "#987de8"] },
          { label: "Чувствительность", value: 70, hint: "Насколько вы замечаете сигналы своего тела и эмоций: усталость, напряжение, тревогу, перегруз, спокойствие.", tone: ["#b7e6ff", "#67badc"] },
          { label: "Ясность", value: 61, hint: "Насколько вы способны честно видеть свою роль в ситуации, признавать ошибки и отделять факты от обиды или фантазий.", tone: ["#a9c8ff", "#6f9fed"] },
          { label: "Рациональность", value: 56, hint: "Насколько для вас важны проверка, доказательства и факты, а не вера на слово, магическое объяснение или чужая уверенность.", tone: ["#f5b8c8", "#df7f9a"] },
        ],
        activity: [
          { label: "15.05", count: 1, value: 28 },
          { label: "16.05", count: 0, value: 0 },
          { label: "17.05", count: 3, value: 72 },
          { label: "18.05", count: 2, value: 50 },
          { label: "19.05", count: 4, value: 100 },
          { label: "20.05", count: 2, value: 50 },
          { label: "21.05", count: 3, value: 72 },
        ],
        lifehack_cards: [
          { title: "Пауза перед ответом", text: "Если разговор задевает, не отвечать сразу. Открыть заметку и набросать фразу, которую хочется сказать без оправданий.", next_step: "Вернуться к сообщению через 10 минут." },
          { title: "Разобрать вечер", text: "Перед сном отметить, что сегодня забрало силы и что немного помогло.", next_step: "Оставить только один пункт, к которому стоит вернуться завтра." },
          { title: "Подготовить разговор", text: "Перед сложной темой записать цель разговора и одну границу, которую не хочется отдавать.", next_step: "Начать с конкретного факта, без длинного вступления." },
        ],
        attention_cards: [
          { kind: "на что обратить внимание", title: "Перегруз после общения", text: "После напряженных разговоров стоит заранее закладывать время на восстановление." },
          { kind: "бережная заметка", title: "Сон как маркер", text: "Если несколько ночей подряд сон резко ухудшается, это важно обсудить со специалистом." },
        ],
        insights: [
          { tone: "growth", title: "После паузы точнее слова", text: "Вы заметили, что несколько минут между эмоцией и ответом помогают говорить меньше из защиты." },
          { tone: "resource", title: "Границы стали спокойнее", text: "Вы стали чаще видеть, что честная просьба не обязательно превращается в конфликт." },
          { tone: "attention", title: "Сон связан с перегрузом", text: "Стало видно, что после нескольких напряженных дней сон первым показывает нехватку сил." },
        ],
      };
    }
    async function loadProfile() {
      root.classList.add("loading");
      if (demoMode) {
        renderProfile(demoProfile());
        statusEl.textContent = "Demo-режим: реальный профиль появится при открытии из Telegram.";
        return;
      }
      if (!telegramId) {
        renderProfile(placeholderProfile(null));
        setText("hello", "Откройте профиль из Telegram");
        setText("profileSummary", "Так mini-app сможет безопасно понять, чей профиль поддержки показать.");
        statusEl.textContent = "Для локальной проверки можно открыть /app/support?telegram_id=123.";
        return;
      }
      const payload = {
        telegram_id: telegramId,
        init_data: tg ? tg.initData : params.get("init_data") || "",
        username: tgUser.username || params.get("username") || null,
        first_name: tgUser.first_name || params.get("first_name") || null,
        language_code: tgUser.language_code || params.get("language_code") || null,
      };
      renderProfile(placeholderProfile(payload.first_name));
      statusEl.textContent = "Обновляю профиль…";
      try {
        const response = await fetch("/api/v1/support/me", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!response.ok) {
          const detail = await response.json().catch(() => ({}));
          throw new Error(detail.detail || `HTTP ${response.status}`);
        }
        renderProfile(await response.json());
      } catch (error) {
        root.classList.remove("loading");
        setText("hello", "Не получилось открыть профиль");
        setText("profileSummary", "Проверьте, что mini-app открыта из Telegram и backend доступен.");
        statusEl.textContent = String(error.message || error);
      }
    }
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
        document.querySelectorAll(".panel").forEach((item) => item.classList.remove("active"));
        tab.classList.add("active");
        document.getElementById(`panel-${tab.dataset.tab}`).classList.add("active");
      });
    });
    window.addEventListener("resize", () => {
      const metrics = window.__supportMetrics || [];
      if (metrics.length) drawRadar(metrics);
    });
    const originalRenderProfile = renderProfile;
    renderProfile = (data) => {
      window.__supportMetrics = data.metrics || [];
      originalRenderProfile(data);
    };
    loadProfile();
  </script>
</body>
</html>
"""

@router.get("/app/support", response_class=HTMLResponse)
async def support_app() -> str:
    """Return the improved support mini‑app HTML."""
    return SUPPORT_APP_HTML
