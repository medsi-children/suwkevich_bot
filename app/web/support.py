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
  <title>Карта поддержки</title>
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
      justify-content: space-between;
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
      font-size: clamp(34px, 9vw, 68px);
      line-height: .96;
      letter-spacing: 0;
      font-weight: 820;
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
      grid-template-columns: repeat(4, minmax(0, 1fr));
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

      .stats,
      .tabs {
        grid-template-columns: repeat(2, minmax(0, 1fr));
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
      <button class="icon-button" id="refreshButton" type="button" title="Обновить">
        <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M20 12a8 8 0 1 1-2.34-5.66" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M20 4v6h-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <section class="hero">
      <div class="hero-copy">
        <div>
          <p class="kicker">Личная карта поддержки</p>
          <h1 id="hello">Собираю вашу карту</h1>
          <p class="summary-text" id="profileSummary">Проверяю сохраненные темы, инсайты и способы поддержки.</p>
        </div>
        <div class="stats">
          <div class="stat"><strong id="memoryCount">0</strong><span>записей памяти</span></div>
          <div class="stat"><strong id="topicCount">0</strong><span>открытых фокусов</span></div>
          <div class="stat"><strong id="supportCount">0</strong><span>опор в плане</span></div>
          <div class="stat"><strong id="updatedAt">—</strong><span>последнее обновление</span></div>
        </div>
      </div>

      <aside class="radar-panel">
        <h2 class="panel-title">Колесо состояния <span class="badge">не диагноз</span></h2>
        <div class="radar-wrap">
          <canvas id="radar" width="620" height="620"></canvas>
        </div>
        <p class="disclaimer" id="disclaimer">Это мягкий ориентир по диалогам, а не медицинская оценка.</p>
      </aside>
    </section>

    <nav class="tabs" aria-label="Разделы карты">
      <button class="tab active" type="button" data-tab="map">Карта</button>
      <button class="tab" type="button" data-tab="focus">Фокусы</button>
      <button class="tab" type="button" data-tab="support">Опора</button>
      <button class="tab" type="button" data-tab="memory">Инсайты</button>
    </nav>

    <section class="panel active" id="panel-map">
      <div class="metrics-grid" id="metricsGrid"></div>
      <div class="activity-panel">
        <h2 class="panel-title">Ритм последних дней <span class="badge">7 дней</span></h2>
        <div class="activity-bars" id="activityBars"></div>
      </div>
    </section>

    <section class="panel" id="panel-focus">
      <div class="cards" id="focusCards"></div>
    </section>

    <section class="panel" id="panel-support">
      <div class="support-layout">
        <div>
          <h2 class="panel-title" style="margin: 0 0 12px;">Что может помочь</h2>
          <div class="cards" id="supportCards"></div>
        </div>
        <div>
          <h2 class="panel-title" style="margin: 0 0 12px;">На что обратить внимание</h2>
          <div class="cards" id="attentionCards"></div>
        </div>
      </div>
    </section>

    <section class="panel" id="panel-memory">
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

    function setText(id, value) {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
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
      return `
        <article class="data-card">
          <div>
            ${meta ? `<small>${meta}</small>` : ""}
            <h3>${title}</h3>
            ${text ? `<p>${text}</p>` : ""}
            ${nextStep ? `<p style="margin-top: 10px;">${nextStep}</p>` : ""}
          </div>
          <div class="card-actions">
            <button class="action-button" type="button" data-prompt="${escapeHtml(prompt)}">
              <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              </svg>
              ${escapeHtml(actionText || "Обсудить")}
            </button>
          </div>
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

    function renderMetrics(metrics) {
      const grid = document.getElementById("metricsGrid");
      grid.innerHTML = metrics.map((metric) => {
        const soft = metric.tone && metric.tone[0] ? metric.tone[0] : "#a9c8ff";
        const tone = metric.tone && metric.tone[1] ? metric.tone[1] : "#6f9fed";
        return `
          <article class="metric-card" style="--value: ${Number(metric.value || 0)}; --metric-soft: ${soft}; --metric-tone: ${tone};">
            <div class="metric-top">
              <h3 class="metric-label">${escapeHtml(metric.label)}</h3>
              <div class="metric-value">${Number(metric.value || 0)}</div>
            </div>
            <p>${escapeHtml(metric.hint)}</p>
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
      ctx.clearRect(0, 0, size, size);
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
        ctx.fillStyle = "#5f6d7a";
        const words = String(metric.label || "").split(" ");
        const lines = words.length > 2 ? [words.slice(0, -1).join(" "), words.at(-1)] : words;
        const startY = ly - (lines.length - 1) * 12;
        lines.forEach((lineText, line) => ctx.fillText(lineText, lx, startY + line * 24));
      });

      ctx.beginPath();
      metrics.forEach((metric, index) => {
        const valueRadius = radius * Number(metric.value || 0) / 100;
        const angle = angleFor(index);
        const x = center + Math.cos(angle) * valueRadius;
        const y = center + Math.sin(angle) * valueRadius;
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      const fill = ctx.createLinearGradient(120, 80, size - 120, size - 80);
      fill.addColorStop(0, "rgba(143, 214, 200, .5)");
      fill.addColorStop(.5, "rgba(169, 200, 255, .42)");
      fill.addColorStop(1, "rgba(255, 214, 166, .42)");
      ctx.fillStyle = fill;
      ctx.fill();
      ctx.strokeStyle = "rgba(91, 184, 169, .85)";
      ctx.lineWidth = 4;
      ctx.stroke();

      metrics.forEach((metric, index) => {
        const valueRadius = radius * Number(metric.value || 0) / 100;
        const angle = angleFor(index);
        const x = center + Math.cos(angle) * valueRadius;
        const y = center + Math.sin(angle) * valueRadius;
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, Math.PI * 2);
        ctx.fillStyle = metric.tone && metric.tone[1] ? metric.tone[1] : "#5bb8a9";
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 3;
        ctx.stroke();
      });
    }

    function renderProfile(data) {
      const firstName = data.user && data.user.first_name ? data.user.first_name : "вы";
      setText("hello", firstName === "вы" ? "Ваша карта поддержки" : `${firstName}, это ваша карта`);
      setText("profileSummary", data.user.profile_summary);
      setText("memoryCount", data.summary.memory_count);
      setText("topicCount", data.summary.open_topics_count);
      setText("supportCount", data.summary.support_items_count);
      setText("updatedAt", data.summary.latest_update);
      setText("disclaimer", data.disclaimer);
      renderMetrics(data.metrics || []);
      renderActivity(data.activity || []);
      drawRadar(data.metrics || []);
      renderCards("focusCards", data.focus_cards, "Фокусов пока мало", "После пары диалогов здесь появятся повторяющиеся темы и ближайшие шаги.", "Открыть в чате");
      renderCards("supportCards", data.support_cards, "План еще собирается", "Расскажите боту, что обычно помогает, и это появится здесь.", "Обсудить");
      renderCards("attentionCards", data.attention_cards, "Осторожных заметок нет", "Если появятся триггеры или риски, карта покажет их отдельно и мягко.", "Разобрать");
      renderCards("insightCards", data.insights, "Инсайтов пока мало", "Здесь будут сохраняться важные выводы из разговоров.", "Вернуться");
      root.classList.remove("loading");
      statusEl.textContent = "";
    }

    function demoProfile() {
      return {
        user: {
          first_name: params.get("first_name") || "Антон",
          profile_summary: "В последних диалогах заметны усталость, желание ясности и осторожная попытка вернуть себе управление. Важный фокус сейчас — не давить на себя, а собрать понятный ближайший шаг и несколько опор, которые уже работают.",
        },
        summary: {
          memory_count: 18,
          open_topics_count: 4,
          support_items_count: 6,
          latest_update: "21.05.2026",
        },
        disclaimer: "Это demo-режим с примером данных. В Telegram здесь будет личная карта по сохраненным диалогам пользователя.",
        metrics: [
          { label: "Субъектность", value: 68, hint: "видны выбор, границы и следующие шаги", tone: ["#8fd6c8", "#5bb8a9"] },
          { label: "Ясность", value: 61, hint: "есть несколько сформулированных выводов", tone: ["#a9c8ff", "#6f9fed"] },
          { label: "Опора", value: 73, hint: "собраны стратегии и люди рядом", tone: ["#ffd6a6", "#f3ad61"] },
          { label: "Безопасность", value: 57, hint: "нужна бережная осторожность без драматизации", tone: ["#f5b8c8", "#df7f9a"] },
          { label: "Границы", value: 52, hint: "границы уже появляются, но требуют внимания", tone: ["#c9b7ff", "#987de8"] },
          { label: "Самосострадание", value: 64, hint: "есть мягкие способы говорить с собой", tone: ["#b8e9aa", "#79be68"] },
          { label: "Контакт с собой", value: 70, hint: "состояние и тело хорошо замечаются", tone: ["#b7e6ff", "#67badc"] },
          { label: "Ресурс", value: 49, hint: "энергия просит экономного режима", tone: ["#ffe69e", "#e7bc45"] },
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
        focus_cards: [
          { source: "открытая тема", title: "Вернуть чувство управления", text: "Много напряжения появляется там, где все кажется слишком большим и размытым.", next_step: "Разобрать ситуацию на факты, чувства и один следующий шаг." },
          { source: "открытая тема", title: "Усталость и сон", text: "Ресурс проседает, когда день не заканчивается психологически.", next_step: "Проверить вечерний ритуал и границу между делами и восстановлением." },
          { source: "память диалогов", title: "Страх быть неудобным", text: "Повторяется тема, где свои потребности становятся менее заметными.", next_step: "Сформулировать одну мягкую, но честную просьбу." },
          { source: "память диалогов", title: "Самокритика", text: "Внутренний тон иногда становится жестче, чем сама ситуация требует.", next_step: "Отделить ошибку от оценки себя целиком." },
        ],
        support_cards: [
          { kind: "быстрая практика", title: "Длинный выдох", text: "Сделать 4 спокойных выдоха длиннее вдоха и проверить опору стоп." },
          { kind: "микроплан", title: "Пять минут", text: "Выбрать действие, которое реально сделать за 5 минут, без обещаний на весь день." },
          { kind: "стратегия", title: "Письменно разложить мысль", text: "Записать: что случилось, что я чувствую, чего боюсь, что могу сделать." },
          { kind: "социальная опора", title: "Написать живому человеку", text: "Коротко обозначить состояние и попросить быть на связи без подробных объяснений." },
        ],
        attention_cards: [
          { kind: "на что обратить внимание", title: "Перегруз после общения", text: "После напряженных разговоров стоит заранее закладывать время на восстановление." },
          { kind: "бережная заметка", title: "Сон как маркер", text: "Если несколько ночей подряд сон резко ухудшается, это важно обсудить со специалистом." },
        ],
        insights: [
          { date: "21.05.2026", title: "Не все нужно решать сразу", text: "Когда задача становится меньше, тревога часто перестает диктовать темп." },
          { date: "20.05.2026", title: "Границы не равны конфликту", text: "Иногда честная просьба снижает напряжение быстрее, чем попытка выдержать молча." },
          { date: "19.05.2026", title: "Состояние можно измерять мягко", text: "Не оценивать себя, а замечать: сон, тело, напряжение, чувство опоры." },
        ],
      };
    }

    async function loadProfile() {
      root.classList.add("loading");
      if (demoMode) {
        renderProfile(demoProfile());
        statusEl.textContent = "Demo-режим: реальные данные появятся при открытии из Telegram.";
        return;
      }
      if (!telegramId) {
        root.classList.remove("loading");
        setText("hello", "Откройте карту из Telegram");
        setText("profileSummary", "Так mini-app сможет безопасно понять, чью карту поддержки показать.");
        statusEl.textContent = "Для локальной проверки можно открыть /app/support?telegram_id=123.";
        drawRadar([]);
        return;
      }

      const payload = {
        telegram_id: telegramId,
        init_data: tg ? tg.initData : params.get("init_data") || "",
        username: tgUser.username || params.get("username") || null,
        first_name: tgUser.first_name || params.get("first_name") || null,
        language_code: tgUser.language_code || params.get("language_code") || null,
      };

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
        setText("hello", "Не получилось открыть карту");
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

    document.getElementById("refreshButton").addEventListener("click", loadProfile);
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
    return SUPPORT_APP_HTML
