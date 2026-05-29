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
      --surface-radius: 18px;
      --section-radius: 20px;
      --accent-radius: 22px;
      --mint: #8fd6c8;
      --sky: #a9c8ff;
      --peach: #ffd6a6;
      --rose: #f5b8c8;
      --lavender: #c9b7ff;
      --green: #b8e9aa;
      --shadow: 0 18px 48px rgba(96, 120, 146, .14);
      --shadow-soft: 0 14px 34px rgba(96, 120, 146, .1);
      --shadow-color: 0 18px 42px rgba(76, 92, 130, .18);
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
      min-height: 100vh;
    }

    .app-shell {
      transition: opacity .28s ease, transform .28s ease;
    }

    .app.loading .app-shell {
      opacity: 0;
      transform: translateY(10px);
      pointer-events: none;
      user-select: none;
    }

    .loading-overlay {
      position: absolute;
      inset: max(22px, calc(env(safe-area-inset-top, 0px) + 18px)) 16px 28px;
      display: grid;
      align-content: start;
      gap: 22px;
      opacity: 0;
      pointer-events: none;
      transition: opacity .24s ease;
    }

    .app.loading .loading-overlay {
      opacity: 1;
    }

    .loading-card {
      border: 1px solid rgba(143, 214, 200, .42);
      border-radius: 28px;
      background: rgba(255, 255, 255, .8);
      box-shadow: 0 22px 52px rgba(143, 214, 200, .1);
      backdrop-filter: blur(18px);
      padding: 28px;
      overflow: hidden;
      position: relative;
    }

    .loading-card::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(110deg, transparent 0 34%, rgba(255, 255, 255, .72) 48%, transparent 62% 100%);
      transform: translateX(-100%);
      animation: shimmer 1.4s ease-in-out infinite;
    }

    .loading-card.featured {
      min-height: 224px;
    }

    .loading-card.medium {
      min-height: 194px;
    }

    .loading-card.tall {
      min-height: 214px;
    }

    .loading-lines {
      display: grid;
      gap: 14px;
    }

    .loading-line {
      height: 24px;
      border-radius: 999px;
      background: linear-gradient(135deg, rgba(210, 243, 247, .96), rgba(233, 249, 252, .94));
    }

    .loading-line.short {
      width: min(280px, 46%);
    }

    .loading-line.medium {
      width: min(620px, 88%);
    }

    .loading-line.long {
      width: min(760px, 100%);
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
      flex-wrap: wrap;
    }

    .brand-note {
      color: #4f9f91;
      font-weight: 780;
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
    .section-shell,
    .metric-card,
    .data-card,
    .empty-state {
      border: 1px solid var(--line);
      border-radius: var(--surface-radius);
      background: var(--surface);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }

    .hero-copy {
      padding: clamp(20px, 4vw, 34px);
      min-height: 250px;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      gap: 18px;
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
      min-height: 250px;
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
      border-radius: 16px;
      background: rgba(255, 255, 255, .68);
      margin: 14px 0;
      backdrop-filter: blur(16px);
      box-shadow: var(--shadow-soft);
    }

    .tab {
      min-height: 42px;
      border: 0;
      border-radius: 12px;
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
      gap: 16px;
    }

    #panel-lifehacks.active {
      gap: 8px;
    }

    .section-shell {
      padding: 18px 18px 16px;
      display: grid;
      gap: 12px;
    }

    .section-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
    }

    .section-head > div {
      flex: 1 1 auto;
      min-width: 0;
    }

    .section-title {
      margin: 0;
      font-size: clamp(20px, 2vw, 24px);
      line-height: 1.1;
      letter-spacing: 0;
      font-weight: 800;
      color: #243140;
    }

    .section-copy {
      margin: 8px 0 0;
      max-width: 720px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .metric-card {
      min-height: 214px;
      padding: 16px;
      display: grid;
      gap: 12px;
      align-content: start;
    }

    .skeleton-card {
      pointer-events: none;
    }

    .skeleton-line {
      display: block;
      border-radius: 999px;
      background: linear-gradient(135deg, rgba(232, 239, 246, .92), rgba(244, 248, 252, .96));
    }

    .skeleton-line.title {
      width: 58%;
      height: 18px;
    }

    .skeleton-line.short {
      width: 42%;
      height: 12px;
    }

    .skeleton-line.medium {
      width: 74%;
      height: 12px;
    }

    .skeleton-line.long {
      width: 92%;
      height: 12px;
    }

    .skeleton-stack {
      display: grid;
      gap: 10px;
    }

    .metric-card.empty {
      color: #818d9a;
      background: rgba(255, 255, 255, .68);
      border-color: rgba(128, 143, 158, .2);
      box-shadow: 0 14px 34px rgba(96, 120, 146, .08);
    }

    .metric-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .metric-label {
      margin: 0;
      font-size: 17px;
      font-weight: 800;
      line-height: 1.2;
    }

    .metric-value {
      min-width: 44px;
      min-height: 34px;
      padding: 0 11px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex: 0 0 auto;
      border-radius: 999px;
      color: #4f5f70;
      font-size: 13px;
      font-weight: 820;
      background: linear-gradient(135deg, rgba(255, 255, 255, .92), rgba(247, 250, 255, .88));
      border: 1px solid rgba(87, 112, 136, .12);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, .9);
    }

    .metric-card.empty .metric-value {
      color: #8b96a3;
    }

    .metric-card p {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.42;
    }

    .metric-detail {
      color: #566577;
      font-size: 14px;
      line-height: 1.56;
      font-weight: 430;
    }

    .metric-dots {
      min-height: 58px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-top: auto;
      padding: 8px 6px 0;
    }

    .metric-dot {
      display: block;
      width: 14px;
      height: 14px;
      border-radius: 999px;
      background: rgba(87, 112, 136, .2);
      border: 1px solid rgba(87, 112, 136, .16);
      box-shadow:
        inset 0 1px 2px rgba(87, 112, 136, .1),
        0 3px 8px rgba(96, 120, 146, .08);
      transition: transform .18s ease, background .18s ease, box-shadow .18s ease;
    }

    .metric-dot:nth-child(2) {
      width: 16px;
      height: 16px;
    }

    .metric-dot:nth-child(3) {
      width: 18px;
      height: 18px;
    }

    .metric-dot:nth-child(4) {
      width: 20px;
      height: 20px;
    }

    .metric-dot:nth-child(5) {
      width: 24px;
      height: 24px;
    }

    .metric-dot:nth-child(6) {
      width: 28px;
      height: 28px;
    }

    .metric-dot:nth-child(7) {
      width: 32px;
      height: 32px;
    }

    .metric-dot:nth-child(8) {
      width: 36px;
      height: 36px;
    }

    .metric-dot:nth-child(9) {
      width: 40px;
      height: 40px;
    }

    .metric-dot:nth-child(10) {
      width: 44px;
      height: 44px;
    }

    .metric-dot.filled {
      background: linear-gradient(135deg, var(--metric-soft), var(--metric-tone));
      border-color: rgba(255, 255, 255, .7);
      box-shadow:
        inset 0 2px 3px rgba(255, 255, 255, .42),
        0 10px 20px rgba(96, 120, 146, .2);
    }

    .metric-card.empty .metric-dot {
      background: rgba(128, 143, 158, .18);
      border-color: rgba(128, 143, 158, .12);
      box-shadow: inset 0 1px 2px rgba(87, 112, 136, .08);
    }

    .two-column {
      display: grid;
      grid-template-columns: minmax(0, .96fr) minmax(0, 1.04fr);
      gap: 14px;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 12px;
    }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .mini-action {
      width: 38px;
      height: 38px;
      border: 1px solid rgba(87, 112, 136, .16);
      border-radius: 999px;
      background: rgba(255, 255, 255, .82);
      color: #556575;
      font-size: 24px;
      line-height: 1;
      display: grid;
      place-items: center;
      cursor: pointer;
      box-shadow: 0 10px 28px rgba(96, 120, 146, .1);
      transition: transform .18s ease, border-color .18s ease, background .18s ease;
    }

    .mini-action:hover {
      transform: translateY(-1px);
      border-color: rgba(111, 159, 237, .36);
      background: #fff;
    }

    .composer {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      padding: 0;
      border-radius: 0;
      border: 0;
      background: transparent;
      box-shadow: none;
    }

    .composer-input {
      width: 100%;
      min-height: 48px;
      border: 1px solid rgba(87, 112, 136, .14);
      border-radius: 999px;
      background: rgba(248, 251, 255, .98);
      color: var(--text);
      padding: 0 16px;
      font: inherit;
      outline: none;
    }

    .composer-input:focus {
      border-color: rgba(111, 159, 237, .4);
      box-shadow: 0 0 0 4px rgba(111, 159, 237, .1);
    }

    .composer-button {
      min-width: 106px;
      min-height: 48px;
      padding: 0 16px;
      border-radius: 999px;
      border: 1px solid rgba(111, 159, 237, .26);
      background: linear-gradient(135deg, #78d6c9 0%, #7abff5 36%, #9e90f1 68%, #78d6c9 100%);
      background-size: 220% 220%;
      color: #fff;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 10px 28px rgba(111, 159, 237, .18);
      animation: composerGlow 7.5s ease-in-out infinite;
    }

    .consultation-cta {
      min-height: 48px;
      padding: 0 18px;
      border-radius: 999px;
      border: 1px solid rgba(91, 184, 169, .24);
      background: linear-gradient(135deg, rgba(143, 214, 200, .96), rgba(169, 200, 255, .96));
      color: #fff;
      font: inherit;
      font-weight: 820;
      white-space: nowrap;
      cursor: pointer;
      box-shadow: 0 12px 30px rgba(91, 184, 169, .18);
      transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
      align-self: flex-start;
    }

    .consultation-cta:hover {
      transform: translateY(-1px);
      box-shadow: 0 16px 34px rgba(91, 184, 169, .22);
      filter: saturate(1.04);
    }

    .consultation-layout {
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(260px, .9fr);
      gap: 14px;
      align-items: start;
    }

    .consultation-form {
      display: grid;
      gap: 12px;
    }

    .consultation-stage {
      display: grid;
      gap: 12px;
      transition: opacity .32s ease, transform .32s ease, visibility .32s ease, max-height .32s ease;
      transform-origin: top center;
    }

    .consultation-stage.hidden {
      opacity: 0;
      visibility: hidden;
      transform: translateY(-10px) scale(.98);
      max-height: 0;
      overflow: hidden;
      pointer-events: none;
    }

    .consultation-success {
      display: grid;
      gap: 14px;
      padding: 22px 20px;
      border-radius: 18px;
      border: 1px solid rgba(91, 184, 169, .22);
      background:
        radial-gradient(circle at top right, rgba(143, 214, 200, .26), transparent 42%),
        linear-gradient(135deg, rgba(255, 255, 255, .96), rgba(242, 249, 255, .95));
      box-shadow: 0 16px 40px rgba(96, 120, 146, .12);
    }

    .consultation-success-badge {
      width: 56px;
      height: 56px;
      display: grid;
      place-items: center;
      border-radius: 999px;
      background: linear-gradient(135deg, #78d6c9 0%, #7abff5 100%);
      color: #fff;
      box-shadow: 0 14px 28px rgba(111, 159, 237, .2);
    }

    .consultation-success-badge svg {
      width: 28px;
      height: 28px;
      fill: none;
      stroke: currentColor;
      stroke-width: 2.4;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .consultation-success h3 {
      margin: 0;
      color: #203040;
      font-size: 22px;
      line-height: 1.2;
    }

    .consultation-success p {
      margin: 0;
      color: #607081;
      font-size: 15px;
      line-height: 1.6;
    }

    .consultation-side {
      min-height: 100%;
      padding: 20px;
      display: grid;
      gap: 14px;
      align-content: start;
      border: 1px solid var(--line);
      border-radius: var(--surface-radius);
      background:
        radial-gradient(circle at top right, rgba(143, 214, 200, .24), transparent 38%),
        linear-gradient(180deg, rgba(255, 255, 255, .9), rgba(247, 250, 255, .94));
      box-shadow: var(--shadow-soft);
    }

    .consultation-side strong {
      font-size: 18px;
      line-height: 1.25;
      color: #223142;
    }

    .consultation-side p,
    .consultation-side li {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.55;
    }

    .consultation-points {
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 8px;
    }

    .form-grid {
      display: grid;
      gap: 12px;
    }

    .form-field {
      display: grid;
      gap: 8px;
    }

    .form-label {
      font-size: 13px;
      font-weight: 760;
      color: #536272;
    }

    .form-note {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .form-input,
    .form-textarea {
      width: 100%;
      border-radius: 16px;
      border: 1px solid rgba(87, 112, 136, .16);
      background: rgba(248, 251, 255, .96);
      color: var(--text);
      padding: 14px 15px;
      font: inherit;
      outline: none;
      transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
    }

    .form-input:focus,
    .form-textarea:focus {
      border-color: rgba(111, 159, 237, .42);
      box-shadow: 0 0 0 4px rgba(111, 159, 237, .11);
      background: #fff;
    }

    .form-textarea {
      min-height: 154px;
      resize: vertical;
      line-height: 1.55;
    }

    .form-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }

    .secondary-button {
      min-height: 48px;
      padding: 0 16px;
      border-radius: 999px;
      border: 1px solid rgba(87, 112, 136, .16);
      background: rgba(255, 255, 255, .86);
      color: var(--text);
      font: inherit;
      font-weight: 720;
      cursor: pointer;
    }

    .composer-status {
      min-height: 0;
      padding: 0;
      color: #667483;
      font-size: 13px;
      line-height: 1.45;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      transition: min-height .24s ease, padding .24s ease;
    }

    .composer-status.active {
      min-height: 44px;
      padding: 4px 18px 0;
    }

    .status-blob {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 38px;
      padding: 0 18px;
      border-radius: 999px;
      background: linear-gradient(135deg, rgba(120, 214, 201, .92), rgba(122, 191, 245, .92), rgba(158, 144, 241, .92));
      color: #fff;
      font-weight: 700;
      box-shadow: 0 12px 30px rgba(111, 159, 237, .2);
      animation: statusBlobIn .28s ease both, statusBlobFloat 2.8s ease-in-out infinite;
    }

    .status-blob.fading {
      animation: statusBlobOut .34s ease forwards;
    }

    .data-card {
      min-height: 184px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      justify-content: space-between;
    }

    .data-card.skeleton-card {
      min-height: 164px;
    }

    .insight-actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      margin-top: 14px;
    }

    .insight-action {
      width: 34px;
      height: 34px;
      border-radius: 999px;
      border: 1px solid rgba(255, 255, 255, .28);
      background: rgba(255, 255, 255, .14);
      color: rgba(255, 255, 255, .96);
      display: grid;
      place-items: center;
      cursor: pointer;
      transition: transform .18s ease, background .18s ease, border-color .18s ease;
    }

    .insight-action:hover {
      transform: translateY(-1px);
      background: rgba(255, 255, 255, .22);
      border-color: rgba(255, 255, 255, .42);
    }

    .insight-action svg {
      width: 16px;
      height: 16px;
      fill: none;
      stroke: currentColor;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .dialog-backdrop {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 18px;
      background: rgba(26, 33, 42, .22);
      backdrop-filter: blur(10px);
      z-index: 30;
    }

    .dialog-backdrop.open {
      display: flex;
    }

    .dialog {
      width: min(560px, 100%);
      border-radius: 18px;
      border: 1px solid rgba(87, 112, 136, .16);
      background: rgba(255, 255, 255, .96);
      box-shadow: 0 20px 60px rgba(96, 120, 146, .22);
      padding: 18px;
      display: grid;
      gap: 14px;
    }

    .dialog-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .dialog-title {
      margin: 0;
      font-size: 18px;
      line-height: 1.2;
    }

    .dialog-close {
      width: 34px;
      height: 34px;
      border-radius: 999px;
      border: 1px solid rgba(87, 112, 136, .16);
      background: rgba(255, 255, 255, .84);
      color: #647382;
      font-size: 18px;
      cursor: pointer;
    }

    .dialog-field {
      display: grid;
      gap: 8px;
    }

    .dialog-label {
      font-size: 13px;
      font-weight: 700;
      color: #536272;
    }

    .dialog-input,
    .dialog-textarea,
    .dialog-select {
      width: 100%;
      border-radius: 14px;
      border: 1px solid rgba(87, 112, 136, .16);
      background: rgba(248, 251, 255, .92);
      color: var(--text);
      padding: 12px 14px;
      font: inherit;
      outline: none;
    }

    .dialog-input:focus,
    .dialog-textarea:focus,
    .dialog-select:focus {
      border-color: rgba(111, 159, 237, .45);
      box-shadow: 0 0 0 4px rgba(111, 159, 237, .12);
    }

    .dialog-textarea {
      min-height: 124px;
      resize: vertical;
      line-height: 1.5;
    }

    .dialog-select {
      min-height: 48px;
      appearance: none;
      background:
        linear-gradient(45deg, transparent 50%, #71808f 50%) calc(100% - 22px) 50% / 7px 7px no-repeat,
        linear-gradient(135deg, rgba(248, 251, 255, .96), rgba(239, 245, 253, .96));
      cursor: pointer;
    }

    .swatches {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .swatch {
      width: 26px;
      height: 26px;
      border-radius: 999px;
      border: 0;
      padding: 0;
      appearance: none;
      overflow: hidden;
      cursor: pointer;
      box-shadow: 0 8px 22px rgba(96, 120, 146, .16);
      transition: transform .18s ease, box-shadow .18s ease;
      background-clip: padding-box;
    }

    .swatch.active {
      transform: scale(1.06);
      box-shadow:
        0 0 0 2px rgba(255, 255, 255, .92),
        0 0 0 4px rgba(32, 40, 51, .22),
        0 8px 22px rgba(96, 120, 146, .16);
    }

    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }

    .dialog-button {
      min-height: 42px;
      padding: 0 16px;
      border-radius: 999px;
      border: 1px solid rgba(87, 112, 136, .16);
      background: rgba(255, 255, 255, .88);
      color: var(--text);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    .dialog-button.primary {
      border-color: rgba(111, 159, 237, .26);
      background: linear-gradient(135deg, rgba(143, 214, 200, .94), rgba(169, 200, 255, .94));
      color: #fff;
      text-shadow: 0 1px 10px rgba(54, 75, 108, .18);
    }

    .lifehack-card {
      position: relative;
      overflow: hidden;
      min-height: 192px;
      cursor: pointer;
      color: #fff;
      background: var(--lifehack-gradient);
      border: 0;
      border-radius: var(--accent-radius);
      box-shadow:
        inset 0 0 0 1px rgba(255, 255, 255, .3),
        var(--shadow-color);
      background-clip: padding-box;
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
      --lifehack-gradient: linear-gradient(135deg, #8fd6c8 0%, #86d2e8 50%, #a9c8ff 100%);
    }

    .lifehack-card[data-style="1"] {
      --lifehack-gradient: linear-gradient(135deg, #ffd6a6 0%, #f5b8c8 52%, #c9b7ff 100%);
    }

    .lifehack-card[data-style="2"] {
      --lifehack-gradient: linear-gradient(135deg, #b7e6ff 0%, #8fd6c8 52%, #a8e986 100%);
    }

    .lifehack-card[data-style="3"] {
      --lifehack-gradient: linear-gradient(135deg, #c9b7ff 0%, #a9c8ff 52%, #b7e6ff 100%);
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
      min-height: 156px;
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
      top: 18px;
      bottom: 18px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 14px;
      opacity: 0;
      visibility: hidden;
      overflow: hidden;
      transform: translateY(10px) scale(.98);
      transition:
        opacity .34s ease .08s,
        transform .34s ease .08s,
        visibility .34s ease;
    }

    .lifehack-detail p {
      overflow-wrap: anywhere;
    }

    .lifehack-detail p + p {
      font-weight: 800;
      line-height: 1.38;
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

    @keyframes statusBlobIn {
      from {
        opacity: 0;
        transform: translateY(8px) scale(.96);
      }
      to {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    @keyframes statusBlobFloat {
      0%, 100% {
        transform: translateY(0);
      }
      50% {
        transform: translateY(-2px);
      }
    }

    @keyframes statusBlobOut {
      from {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
      to {
        opacity: 0;
        transform: translateY(-6px) scale(.98);
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
      border-radius: var(--accent-radius);
      box-shadow: var(--shadow-color);
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

    .insight-badges {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }

    .insight-source {
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 5px 10px;
      border-radius: 999px;
      background: rgba(26, 35, 49, .14);
      border: 1px solid rgba(255, 255, 255, .18);
      color: rgba(255, 255, 255, .92);
      font-size: 11px;
      line-height: 1;
      letter-spacing: .03em;
      backdrop-filter: blur(10px);
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
      border-radius: var(--surface-radius);
    }

    .inline-empty {
      padding: 2px 18px 0;
      color: #738092;
      font-size: 13px;
      line-height: 1.45;
    }

    .inline-empty strong {
      font-weight: 500;
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
    .loading .data-card {
      position: relative;
      overflow: hidden;
    }

    .loading #hello,
    .loading #profileSummary,
    .loading .panel-title,
    .loading #disclaimer {
      color: transparent;
      user-select: none;
    }

    .loading .consultation-cta {
      color: transparent;
      border-color: rgba(209, 219, 231, .7);
      background: linear-gradient(135deg, rgba(244, 248, 252, .98), rgba(232, 239, 246, .94));
      box-shadow: none;
      pointer-events: none;
      user-select: none;
    }

    .loading .hero-copy::after,
    .loading .radar-panel::after,
    .loading .metric-card::after,
    .loading .data-card::after {
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

    @keyframes composerGlow {
      0% {
        background-position: 0% 50%;
      }
      50% {
        background-position: 100% 50%;
      }
      100% {
        background-position: 0% 50%;
      }
    }

    @media (max-width: 900px) {
      .hero,
      .two-column,
      .support-layout,
      .consultation-layout {
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
      .section-shell {
        padding: 16px;
      }
      .section-head {
        gap: 12px;
      }
    }
  </style>
</head>
<body>
  <main class="app loading">
    <div class="loading-overlay" aria-hidden="true">
      <section class="loading-card featured">
        <div class="loading-lines">
          <span class="loading-line short"></span>
          <span class="loading-line long"></span>
          <span class="loading-line medium"></span>
        </div>
      </section>
      <section class="loading-card medium">
        <div class="loading-lines">
          <span class="loading-line short"></span>
          <span class="loading-line long"></span>
          <span class="loading-line medium"></span>
        </div>
      </section>
      <section class="loading-card tall">
        <div class="loading-lines">
          <span class="loading-line short"></span>
          <span class="loading-line long"></span>
          <span class="loading-line medium"></span>
        </div>
      </section>
      <section class="loading-card medium">
        <div class="loading-lines">
          <span class="loading-line short"></span>
          <span class="loading-line long"></span>
          <span class="loading-line medium"></span>
        </div>
      </section>
    </div>

    <div class="app-shell">
      <div class="topbar">
        <div class="brand"><span class="brand-mark" aria-hidden="true"></span><span class="brand-note">Личный профиль поддержки</span></div>
        <!-- refresh button removed -->
      </div>

      <section class="hero" id="hero">
        <div class="hero-copy">
          <div>
            <h1 id="hello">Собираю ваш профиль</h1>
            <p class="summary-text" id="profileSummary">Проверяю сохраненные темы, инсайты и способы поддержки.</p>
          </div>
          <button class="consultation-cta" id="heroConsultationButton" type="button">Записаться на прием</button>
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
        <button class="tab" type="button" data-tab="diary">Дневник</button>
      </nav>

      <section class="panel" id="panel-consultation">
        <div class="consultation-layout">
          <div class="section-shell consultation-form">
            <div class="section-head">
              <div>
                <h2 class="section-title">Запись на прием</h2>
                <p class="section-copy">Оставьте заявку, и мы передадим ее врачу.</p>
              </div>
            </div>
            <div class="consultation-stage" id="consultationFormStage">
              <div class="form-grid">
                <label class="form-field" for="consultationFullName">
                  <span class="form-label">Фамилия, имя и отчество</span>
                  <input class="form-input" id="consultationFullName" maxlength="120" autocomplete="name" />
                </label>
                <label class="form-field" for="consultationPhone">
                  <span class="form-label">Телефон для связи</span>
                  <input class="form-input" id="consultationPhone" maxlength="32" autocomplete="tel" inputmode="tel" />
                </label>
                <label class="form-field" for="consultationMessage">
                  <span class="form-label">Что случилось</span>
                  <textarea class="form-textarea" id="consultationMessage" maxlength="2000"></textarea>
                </label>
              </div>
              <p class="form-note" id="consultationNote"></p>
              <div class="form-actions">
                <button class="composer-button" id="submitConsultationButton" type="button">Отправить</button>
              </div>
            </div>
            <div class="consultation-stage hidden" id="consultationSuccessStage" aria-live="polite">
              <div class="consultation-success">
                <div class="consultation-success-badge" aria-hidden="true">
                  <svg viewBox="0 0 24 24"><path d="m5 12 4.2 4.2L19 6.5"/></svg>
                </div>
                <div>
                  <h3>Заявка отправлена успешно</h3>
                  <p>Ожидайте, пока врач свяжется с вами.</p>
                </div>
              </div>
            </div>
          </div>
          <aside class="consultation-side">
            <strong>Что будет дальше</strong>
            <ul class="consultation-points">
              <li>Мы отправим врачу ваше имя, телефон, Telegram и описание ситуации.</li>
              <li>Чем конкретнее вы опишете состояние, тем легче будет сориентироваться перед звонком.</li>
              <li>Если есть немедленная опасность для жизни, не ждите ответа в чате и звоните 112 или 103.</li>
            </ul>
          </aside>
        </div>
      </section>

      <section class="panel" id="panel-lifehacks">
        <div class="section-shell">
          <div class="section-head">
            <div>
              <h2 class="section-title">Лайфхаки</h2>
              <p class="section-copy">Короткий лайфхак под ваш запрос.</p>
            </div>
          </div>
          <div class="composer">
            <input class="composer-input" id="lifehackPrompt" maxlength="180" />
            <button class="composer-button" id="generateLifehackButton" type="button">Спросить</button>
          </div>
        </div>
        <div class="composer-status" id="lifehackStatus"></div>
        <div class="cards" id="lifehackCards"></div>
      </section>

      <section class="panel active" id="panel-personality">
        <div class="metrics-grid" id="metricsGrid"></div>
      </section>

      <section class="panel" id="panel-diary">
        <div class="section-shell">
          <div class="section-head">
            <div>
              <h2 class="section-title">Дневник</h2>
              <p class="section-copy">Ваши осознания и важные заметки о себе.</p>
            </div>
            <button class="mini-action" id="addDiaryButton" type="button" aria-label="Добавить осознание">+</button>
          </div>
        </div>
        <div class="cards" id="insightCards"></div>
      </section>

      <div class="status" id="status"></div>
    </div>
  </main>

  <div class="dialog-backdrop" id="diaryDialog">
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="diaryDialogTitle">
      <div class="dialog-top">
        <h3 class="dialog-title" id="diaryDialogTitle">Осознание</h3>
        <button class="dialog-close" id="closeDiaryDialog" type="button" aria-label="Закрыть">×</button>
      </div>
      <div class="dialog-field">
        <label class="dialog-label" for="diaryTitle">Заголовок</label>
        <input class="dialog-input" id="diaryTitle" maxlength="78" />
      </div>
      <div class="dialog-field">
        <label class="dialog-label" for="diaryText">Текст</label>
        <textarea class="dialog-textarea" id="diaryText" maxlength="240"></textarea>
      </div>
      <div class="dialog-field">
        <span class="dialog-label">Цвет</span>
        <div class="swatches" id="diarySwatches"></div>
      </div>
      <div class="dialog-field">
        <label class="dialog-label" for="diaryTheme">Категория</label>
        <select class="dialog-select" id="diaryTheme"></select>
      </div>
      <div class="dialog-actions">
        <button class="dialog-button" id="cancelDiaryButton" type="button">Отмена</button>
        <button class="dialog-button primary" id="saveDiaryButton" type="button">Сохранить</button>
      </div>
    </div>
  </div>

  <script>
(() => {
  var __defProp = Object.defineProperty;
  var __defProps = Object.defineProperties;
  var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
  var __getOwnPropSymbols = Object.getOwnPropertySymbols;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __propIsEnum = Object.prototype.propertyIsEnumerable;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __spreadValues = (a, b) => {
    for (var prop in b || (b = {}))
      if (__hasOwnProp.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    if (__getOwnPropSymbols)
      for (var prop of __getOwnPropSymbols(b)) {
        if (__propIsEnum.call(b, prop))
          __defNormalProp(a, prop, b[prop]);
      }
    return a;
  };
  var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
  const root = document.querySelector(".app");
  const statusEl = document.getElementById("status");
  const diaryDialog = document.getElementById("diaryDialog");
  const diaryTitleInput = document.getElementById("diaryTitle");
  const diaryTextInput = document.getElementById("diaryText");
  const diarySwatches = document.getElementById("diarySwatches");
  const diaryThemeSelect = document.getElementById("diaryTheme");
  const lifehackStatus = document.getElementById("lifehackStatus");
  const lifehackPromptInput = document.getElementById("lifehackPrompt");
  const consultationFullNameInput = document.getElementById("consultationFullName");
  const consultationPhoneInput = document.getElementById("consultationPhone");
  const consultationMessageInput = document.getElementById("consultationMessage");
  const consultationNote = document.getElementById("consultationNote");
  const consultationFormStage = document.getElementById("consultationFormStage");
  const consultationSuccessStage = document.getElementById("consultationSuccessStage");
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  if (tg) {
    tg.ready();
    tg.expand();
    tg.setHeaderColor("#f9fbff");
    tg.setBackgroundColor("#f9fbff");
  }
  const escapeHtml = (value) => String(value || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  function compactSentence(value, limit) {
    const clean = String(value || "").replace(/\s+/g, " ").trim();
    if (clean.length <= limit) return clean;
    const clipped = clean.slice(0, limit);
    const sentenceEnds = [clipped.lastIndexOf("."), clipped.lastIndexOf("!"), clipped.lastIndexOf("?")];
    const sentenceEnd = Math.max.apply(null, sentenceEnds);
    if (sentenceEnd >= Math.max(36, Math.floor(limit / 3))) return clean.slice(0, sentenceEnd + 1).trim();
    const trimmed = clipped.replace(/\s+\S*$/, "").replace(/[,\s;:-]+$/, "");
    return trimmed ? `${trimmed}.` : "";
  }
  const params = new URLSearchParams(window.location.search);
  const tgUser = tg && tg.initDataUnsafe ? tg.initDataUnsafe.user || {} : {};
  const demoMode = params.get("demo") === "1";
  const localTelegramId = Number(params.get("telegram_id") || 0);
  const telegramId = Number(tgUser.id || localTelegramId || 0);
  const diaryThemeAliases = {
    empathy: "emotional_intelligence",
    sensitivity: "self_contact",
    clarity: "criticality"
  };
  const normalizeDiaryTheme = (value) => diaryThemeAliases[value] || value;
  const diaryThemes = {
    agency: { label: "\u0421\u0443\u0431\u044A\u0435\u043A\u0442\u043D\u043E\u0441\u0442\u044C", soft: "#8fd6c8", tone: "#5bb8a9" },
    emotional_intelligence: { label: "\u042D\u043C\u043E\u0446\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u044B\u0439 \u0438\u043D\u0442\u0435\u043B\u043B\u0435\u043A\u0442", soft: "#ffd6a6", tone: "#f3ad61" },
    boundaries: { label: "\u0413\u0440\u0430\u043D\u0438\u0446\u044B", soft: "#c9b7ff", tone: "#987de8" },
    self_contact: { label: "\u041A\u043E\u043D\u0442\u0430\u043A\u0442 \u0441 \u0441\u043E\u0431\u043E\u0439", soft: "#b7e6ff", tone: "#67badc" },
    criticality: { label: "\u041A\u0440\u0438\u0442\u0438\u0447\u043D\u043E\u0441\u0442\u044C", soft: "#a9c8ff", tone: "#6f9fed" },
    self_regulation: { label: "\u0421\u0430\u043C\u043E\u0440\u0435\u0433\u0443\u043B\u044F\u0446\u0438\u044F", soft: "#ff9c8b", tone: "#ff6f91" },
    rationality: { label: "\u0420\u0430\u0446\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u043E\u0441\u0442\u044C", soft: "#f5b8c8", tone: "#df7f9a" }
  };
  const diaryColors = {
    mint: { label: "\u041C\u044F\u0442\u043D\u044B\u0439", soft: "#8fd6c8", tone: "#5bb8a9" },
    peach: { label: "\u041F\u0435\u0440\u0441\u0438\u043A\u043E\u0432\u044B\u0439", soft: "#ffd6a6", tone: "#f3ad61" },
    violet: { label: "\u0424\u0438\u043E\u043B\u0435\u0442\u043E\u0432\u044B\u0439", soft: "#c9b7ff", tone: "#987de8" },
    sky: { label: "\u0413\u043E\u043B\u0443\u0431\u043E\u0439", soft: "#b7e6ff", tone: "#67badc" },
    blue: { label: "\u0421\u0438\u043D\u0438\u0439", soft: "#a9c8ff", tone: "#6f9fed" },
    rose: { label: "\u0420\u043E\u0437\u043E\u0432\u044B\u0439", soft: "#f5b8c8", tone: "#df7f9a" },
    coral: { label: "\u041A\u043E\u0440\u0430\u043B\u043B\u043E\u0432\u044B\u0439", soft: "#ff9c8b", tone: "#ff6f91" },
    lemon: { label: "\u041B\u0438\u043C\u043E\u043D\u043D\u044B\u0439", soft: "#ffe58f", tone: "#f2bd55" },
    green: { label: "\u0417\u0435\u043B\u0435\u043D\u044B\u0439", soft: "#a8e986", tone: "#66c66c" }
  };
  const diaryThemeColors = {
    agency: "mint",
    emotional_intelligence: "peach",
    boundaries: "violet",
    self_contact: "sky",
    criticality: "blue",
    self_regulation: "coral",
    rationality: "rose"
  };
  let currentProfileData = null;
  let currentDiaryDraft = { item_id: null, theme: "criticality", color_theme: "blue" };
  let consultationSending = false;
  const metricLabels = [
    "\u0421\u0443\u0431\u044A\u0435\u043A\u0442\u043D\u043E\u0441\u0442\u044C",
    "\u042D\u043C\u043E\u0446\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u044B\u0439 \u0438\u043D\u0442\u0435\u043B\u043B\u0435\u043A\u0442",
    "\u0413\u0440\u0430\u043D\u0438\u0446\u044B",
    "\u041A\u043E\u043D\u0442\u0430\u043A\u0442 \u0441 \u0441\u043E\u0431\u043E\u0439",
    "\u041A\u0440\u0438\u0442\u0438\u0447\u043D\u043E\u0441\u0442\u044C",
    "\u0421\u0430\u043C\u043E\u0440\u0435\u0433\u0443\u043B\u044F\u0446\u0438\u044F",
    "\u0420\u0430\u0446\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u043E\u0441\u0442\u044C"
  ];
  function emptyMetrics() {
    return metricLabels.map((label, order) => ({
      label,
      order,
      value: null,
      empty: true,
      hint: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E",
      tone: ["#eef2f6", "#aeb8c4"]
    }));
  }
  function placeholderProfile(firstName) {
    return {
      user: {
        first_name: firstName || null,
        profile_summary: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E. \u041F\u0440\u043E\u0444\u0438\u043B\u044C \u0441\u0442\u0430\u043D\u0435\u0442 \u0442\u043E\u0447\u043D\u0435\u0435 \u043F\u043E\u0441\u043B\u0435 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u0438\u0445 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u043E\u0432."
      },
      metrics: emptyMetrics(),
      activity: [],
      lifehack_cards: [],
      insights: [],
      disclaimer: "\u041F\u0435\u0440\u0435\u0434 \u0432\u0430\u043C\u0438 \u043A\u0430\u0440\u0442\u0430 \u0432\u0430\u0448\u0435\u0439 \u043B\u0438\u0447\u043D\u043E\u0441\u0442\u0438, \u043D\u0430 \u043E\u0441\u043D\u043E\u0432\u0435 \u0430\u043D\u0430\u043B\u0438\u0437\u0430 \u0421\u0443\u0448\u043A\u0435\u0432\u0438\u0447 \u0411\u043E\u0442\u0430. \u041E\u043D\u0430 \u0431\u0443\u0434\u0435\u0442 \u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u0441\u044F \u0442\u043E\u0447\u043D\u0435\u0435 \u0438 \u0442\u043E\u0447\u043D\u0435\u0435 \u0441 \u043A\u0430\u0436\u0434\u044B\u043C \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u043E\u043C \u0441 \u0432\u0430\u043C\u0438."
    };
  }
  function metricSkeletonTemplate() {
    return `
      <article class="metric-card skeleton-card">
        <div class="metric-top">
          <span class="skeleton-line title"></span>
          <div class="metric-value">--</div>
        </div>
        <div class="skeleton-stack">
          <span class="skeleton-line long"></span>
          <span class="skeleton-line medium"></span>
          <span class="skeleton-line short"></span>
        </div>
      </article>
    `;
  }
  function dataCardSkeletonTemplate() {
    return `
      <article class="data-card skeleton-card">
        <div class="skeleton-stack">
          <span class="skeleton-line short"></span>
          <span class="skeleton-line title"></span>
          <span class="skeleton-line long"></span>
          <span class="skeleton-line medium"></span>
        </div>
      </article>
    `;
  }
  function renderLoadingState() {
    document.getElementById("hero").classList.remove("no-radar");
    setText("hello", "");
    setText("profileSummary", "");
    setText("disclaimer", "");
    document.getElementById("metricsGrid").innerHTML = Array.from({ length: 6 }, () => metricSkeletonTemplate()).join("");
    document.getElementById("lifehackCards").innerHTML = Array.from({ length: 3 }, () => dataCardSkeletonTemplate()).join("");
    document.getElementById("insightCards").innerHTML = Array.from({ length: 3 }, () => dataCardSkeletonTemplate()).join("");
    const canvas = document.getElementById("radar");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
  function buildSupportPayload() {
    return {
      telegram_id: telegramId,
      init_data: tg ? tg.initData : params.get("init_data") || "",
      username: tgUser.username || params.get("username") || null,
      first_name: tgUser.first_name || params.get("first_name") || null,
      language_code: tgUser.language_code || params.get("language_code") || null
    };
  }
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }
  function openTab(tabName) {
    document.querySelectorAll(".tab").forEach((item) => item.classList.toggle("active", item.dataset.tab === tabName));
    document.querySelectorAll(".panel").forEach((item) => item.classList.toggle("active", item.id === `panel-${tabName}`));
  }
  function normalizeFullName(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }
  function normalizePhone(value) {
    const digits = String(value || "").replace(/\D+/g, "");
    if (digits.length === 11 && digits.startsWith("8")) {
      return `+7 ${digits.slice(1, 4)} ${digits.slice(4, 7)}-${digits.slice(7, 9)}-${digits.slice(9, 11)}`;
    }
    if (digits.length === 11 && digits.startsWith("7")) {
      return `+7 ${digits.slice(1, 4)} ${digits.slice(4, 7)}-${digits.slice(7, 9)}-${digits.slice(9, 11)}`;
    }
    if (digits.length >= 10 && digits.length <= 15) {
      return `+${digits}`;
    }
    return "";
  }
  function setConsultationNote(text) {
    if (consultationNote) consultationNote.textContent = text;
  }
  function showConsultationSuccess() {
    if (consultationFormStage) consultationFormStage.classList.add("hidden");
    if (consultationSuccessStage) consultationSuccessStage.classList.remove("hidden");
  }
  function prefillConsultationForm(data) {
    const firstName = data && data.user && data.user.first_name ? String(data.user.first_name).trim() : "";
    if (consultationFullNameInput && !consultationFullNameInput.value.trim() && firstName) {
      consultationFullNameInput.value = firstName;
    }
  }
  function shortProfileDescription(text, firstName) {
    const clean = String(text || "").replace(/\\s+/g, " ").trim();
    const fallback = "\u041F\u043E\u043A\u0430 \u0438\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043C\u0430\u043B\u043E. \u041F\u043E\u0441\u043B\u0435 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u0438\u0445 \u0434\u0438\u0430\u043B\u043E\u0433\u043E\u0432 \u0437\u0434\u0435\u0441\u044C \u043F\u043E\u044F\u0432\u0438\u0442\u0441\u044F \u043A\u043E\u0440\u043E\u0442\u043A\u043E\u0435 \u043E\u043F\u0438\u0441\u0430\u043D\u0438\u0435.";
    const normalizedName = String(firstName || "").replace(/\\s+/g, " ").trim().replace(/[.,:;!?"'«»()[\\]{}]+/g, "").toLowerCase();
    const normalizedSummary = clean.replace(/[.,:;!?"'«»()[\\]{}]+/g, "").toLowerCase();
    if (!clean) return fallback;
    if (normalizedName && normalizedSummary === normalizedName) return fallback;
    if (normalizedName && ["это " + normalizedName, "я " + normalizedName].includes(normalizedSummary)) return fallback;
    if (normalizedName && normalizedSummary.length < 16 && normalizedSummary.includes(normalizedName)) return fallback;
    const firstSentence = clean.match(/.+?[.!?](\\s|$)/);
    const short = firstSentence ? firstSentence[0].trim() : clean;
    return short.length > 170 ? `${short.slice(0, 167).replace(/\\s+$/, "")}...` : short;
  }
  function lifehackTemplate(card, index) {
    const title = escapeHtml(card.title || "\u041B\u0430\u0439\u0444\u0445\u0430\u043A");
    const text = escapeHtml(compactSentence(card.text || "", 145));
    const nextStep = escapeHtml(compactSentence(card.next_step || "", 88));
    const styleIndex = index % 4;
    return `
        <article class="data-card lifehack-card" data-style="${styleIndex}" data-lifehack-card="${index}" tabindex="0" role="button" aria-expanded="false" aria-label="\u041E\u0442\u043A\u0440\u044B\u0442\u044C \u043B\u0430\u0439\u0444\u0445\u0430\u043A: ${title}">
          <div class="lifehack-flash" aria-hidden="true"></div>
          <div class="lifehack-head">
            <div class="lifehack-gesture" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M2 12s3.8-6 10-6 10 6 10 6-3.8 6-10 6-10-6-10-6Z"></path>
                <circle cx="12" cy="12" r="3.2"></circle>
              </svg>
              <span class="lifehack-hint">\u043D\u0430\u0436\u043C\u0438\u0442\u0435 \u043D\u0430 \u043A\u0430\u0440\u0442\u043E\u0447\u043A\u0443</span>
            </div>
            <div class="lifehack-detail">
              ${text ? `<p>${text}</p>` : ""}
              ${nextStep ? `<p>${nextStep}</p>` : ""}
            </div>
          </div>
        </article>
      `;
  }
  let lifehackStatusTimer = null;
  function showLifehackStatus(text) {
    if (!lifehackStatus) return;
    window.clearTimeout(lifehackStatusTimer);
    lifehackStatus.classList.add("active");
    lifehackStatus.innerHTML = `<span class="status-blob">${escapeHtml(text)}</span>`;
  }
  function hideLifehackStatus() {
    if (!lifehackStatus) return;
    window.clearTimeout(lifehackStatusTimer);
    const blob = lifehackStatus.querySelector(".status-blob");
    if (!blob) {
      lifehackStatus.textContent = "";
      lifehackStatus.classList.remove("active");
      return;
    }
    blob.classList.add("fading");
    lifehackStatusTimer = window.setTimeout(() => {
      lifehackStatus.textContent = "";
      lifehackStatus.classList.remove("active");
    }, 360);
  }
  function flashLifehackStatus(text) {
    showLifehackStatus(text);
    lifehackStatusTimer = window.setTimeout(hideLifehackStatus, 2300);
  }
  function renderLifehacks(cards) {
    const el = document.getElementById("lifehackCards");
    if (!el) return;
    if (!cards || !cards.length) {
      el.innerHTML = `<div class="inline-empty">\u041B\u0430\u0439\u0444\u0445\u0430\u043A\u0438 \u043F\u043E\u044F\u0432\u044F\u0442\u0441\u044F \u043F\u043E\u0441\u043B\u0435 \u0442\u043E\u0433\u043E, \u043A\u0430\u043A \u0432\u044B \u043D\u0435\u043C\u043D\u043E\u0433\u043E \u043F\u043E\u043E\u0431\u0449\u0430\u0435\u0442\u0435\u0441\u044C \u0441 \u0431\u043E\u0442\u043E\u043C.</div>`;
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
  async function generateLifehack() {
    if (demoMode || !telegramId) return;
    const prompt = lifehackPromptInput.value.trim();
    if (!prompt) {
      flashLifehackStatus("\u041D\u0430\u043F\u0438\u0448\u0438\u0442\u0435 \u0437\u0430\u043F\u0440\u043E\u0441");
      return;
    }
    showLifehackStatus("\u0413\u0435\u043D\u0435\u0440\u0438\u0440\u0443\u0435\u043C \u043B\u0430\u0439\u0444\u0445\u0430\u043A...");
    const response = await fetch("/api/v1/support/lifehacks/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(__spreadProps(__spreadValues({}, buildSupportPayload()), {
        prompt
      }))
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(detail.detail || `HTTP ${response.status}`);
    }
    lifehackPromptInput.value = "";
    hideLifehackStatus();
    renderProfile(await response.json());
  }
  function renderInsights(cards) {
    const el = document.getElementById("insightCards");
    if (!el) return;
    if (!cards || !cards.length) {
      el.innerHTML = `<div class="inline-empty">\u041E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u044F \u043F\u043E\u044F\u0432\u044F\u0442\u0441\u044F \u0437\u0434\u0435\u0441\u044C, \u043A\u043E\u0433\u0434\u0430 \u0432\u044B \u0437\u0430\u0445\u043E\u0442\u0438\u0442\u0435 \u0447\u0442\u043E-\u0442\u043E \u0437\u0430\u0444\u0438\u043A\u0441\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0441\u0430\u043C\u0438 \u0438\u043B\u0438 \u0431\u043E\u0442 \u0437\u0430\u043C\u0435\u0442\u0438\u0442 \u0432\u0430\u0436\u043D\u0443\u044E \u043C\u044B\u0441\u043B\u044C \u0432 \u0434\u0438\u0430\u043B\u043E\u0433\u0435.</div>`;
      return;
    }
    const inferInsightTheme = (card) => {
      const normalizedTheme = normalizeDiaryTheme(card.theme || "");
      if (normalizedTheme && diaryThemes[normalizedTheme]) return normalizedTheme;
      const text = `${card.title || ""} ${card.text || ""}`.toLowerCase();
      const checks = [
        ["self_contact", ["\u0441\u043E\u043D", "\u0442\u0435\u043B\u043E", "\u0434\u044B\u0445", "\u043D\u0430\u043F\u0440\u044F\u0436", "\u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438", "\u0442\u0440\u0435\u0432\u043E\u0433", "\u0443\u0441\u0442\u0430\u043B", "\u0447\u0443\u0432\u0441\u0442\u0432"]],
        ["emotional_intelligence", ["\u044D\u043C\u043E\u0446", "\u0434\u0440\u0443\u0433\u0438\u0445", "\u0434\u0440\u0443\u0433\u043E\u043C\u0443", "\u0435\u043C\u0443", "\u0435\u0439", "\u043B\u044E\u0434\u044F\u043C", "\u043E\u0431\u0438\u0434", "\u043F\u043E\u0434\u0434\u0435\u0440\u0436", "\u0441\u0442\u044B\u0434"]],
        ["boundaries", ["\u0433\u0440\u0430\u043D\u0438\u0446", "\u043F\u0440\u043E\u0441\u044C\u0431", "\u043E\u0442\u043A\u0430\u0437", "\u043D\u0435 \u043E\u0431\u044F\u0437", "\u0441\u043A\u0430\u0437\u0430\u0442\u044C \u043D\u0435\u0442"]],
        ["agency", ["\u0448\u0430\u0433", "\u0432\u044B\u0431\u043E\u0440", "\u0440\u0435\u0448\u0438\u043B", "\u0434\u0435\u0439\u0441\u0442\u0432", "\u043E\u0442\u0432\u0435\u0442", "\u0441\u043A\u0430\u0437\u0430\u0442\u044C"]],
        ["criticality", ["\u043A\u0440\u0438\u0442\u0438\u0447", "\u0441\u043E\u043C\u043D\u0435\u0432", "\u0438\u043D\u0442\u0435\u0440\u043F\u0440\u0435\u0442", "\u044F\u0441\u043D", "\u043F\u043E\u043D\u044F\u0442", "\u0432\u0438\u0434\u043D\u043E", "\u0437\u0430\u043C\u0435\u0442\u0438\u043B\u0438", "\u043E\u0441\u043E\u0437\u043D", "\u043E\u0448\u0438\u0431", "\u043C\u043E\u044F \u0440\u043E\u043B\u044C"]],
        ["rationality", ["\u0444\u0430\u043A\u0442", "\u0434\u043E\u043A\u0430\u0437", "\u0440\u0435\u0430\u043B\u044C\u043D", "\u043F\u0440\u043E\u0432\u0435\u0440", "\u043B\u043E\u0433\u0438\u0447", "\u043F\u0440\u0430\u0432\u0434\u0430", "\u0431\u0435\u0437 \u0434\u043E\u043A\u0430\u0437"]],
        ["self_regulation", ["\u043F\u0430\u0443\u0437", "\u0432\u044B\u0434\u0435\u0440\u0436", "\u0441\u043F\u0440\u0430\u0432", "\u043E\u043F\u043E\u0440", "\u0443\u0441\u043F\u043E\u043A", "\u043D\u0435 \u0441\u043E\u0440\u0432", "\u0431\u0435\u0437\u043E\u043F\u0430\u0441"]]
      ];
      for (const entry of checks) {
        const key = entry[0];
        const words = entry[1];
        if (words.some((word) => text.includes(word))) return key;
      }
      const fallback = {
        growth: "agency",
        attention: "self_contact",
        resource: "self_regulation",
        calm: "criticality"
      };
      return fallback[card.tone || "calm"] || "criticality";
    };
    el.innerHTML = cards.map((card, index) => {
      const themeKey = inferInsightTheme(card);
      const theme = diaryThemes[themeKey] || diaryThemes.criticality;
      const colorKey = card.color_theme && diaryColors[card.color_theme] ? card.color_theme : themeKey;
      const color = diaryColors[colorKey] || theme;
      const displayThemeKey = normalizeDiaryTheme(card.theme || "");
      const displayTheme = displayThemeKey && diaryThemes[displayThemeKey] ? diaryThemes[displayThemeKey] : null;
      return `
        <article class="data-card insight-card" data-theme="${escapeHtml(themeKey)}" data-diary-index="${index}" style="--insight-soft: ${color.soft}; --insight-tone: ${color.tone};">
          <div>
            <div class="insight-badges">
              ${displayTheme ? `<small class="insight-meta">${escapeHtml(displayTheme.label)}</small>` : ""}
            </div>
            <h3>${escapeHtml(card.title || "\u041E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u0435")}</h3>
            <p>${escapeHtml(card.text || "")}</p>
            <div class="insight-actions">
              <button class="insight-action" type="button" data-edit-diary="${escapeHtml(card.id || "")}" aria-label="\u0420\u0435\u0434\u0430\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u043E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u0435">
                <svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
              </button>
              ${card.manual ? `
              <button class="insight-action" type="button" data-delete-diary="${escapeHtml(card.id || "")}" aria-label="\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u043E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u0435">
                <svg viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>
              </button>` : ""}
            </div>
          </div>
        </article>
      `;
    }).join("");
    el.querySelectorAll("[data-edit-diary]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        const cardEl = button.closest(".insight-card");
        const index = Number((cardEl && cardEl.dataset ? cardEl.dataset.diaryIndex : -1) || -1);
        openDiaryEditor(cards[index] || null);
      });
    });
    el.querySelectorAll("[data-delete-diary]").forEach((button) => {
      button.addEventListener("click", async (event) => {
        event.stopPropagation();
        const id = button.dataset.deleteDiary || "";
        if (!id) return;
        await deleteDiaryEntry(id);
      });
    });
  }
  function renderMetrics(metrics) {
    const grid = document.getElementById("metricsGrid");
    if (!metrics || !metrics.length) {
      grid.innerHTML = `<div class="empty-state"><strong>\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E</strong><span>\u041F\u0440\u043E\u0444\u0438\u043B\u044C \u0441\u0442\u0430\u043D\u0435\u0442 \u0442\u043E\u0447\u043D\u0435\u0435 \u043F\u043E\u0441\u043B\u0435 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u0438\u0445 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439 \u0432 \u0431\u043E\u0442\u0435.</span></div>`;
      return;
    }
    grid.innerHTML = metrics.map((metric) => {
      const isEmpty = metric.empty || metric.value === null || metric.value === void 0;
      const value = isEmpty ? 0 : Math.max(0, Math.min(100, Number(metric.value || 0)));
      const level = isEmpty ? 0 : Math.max(1, Math.min(10, Math.ceil(value / 10)));
      const soft = isEmpty ? "#eef2f6" : metric.tone && metric.tone[0] ? metric.tone[0] : "#a9c8ff";
      const tone = isEmpty ? "#aeb8c4" : metric.tone && metric.tone[1] ? metric.tone[1] : "#6f9fed";
      const detail = isEmpty ? String(metric.hint || "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E") : String(metric.detail || "");
      const dots = Array.from({ length: 10 }, (_, index) => `<span class="metric-dot${index < level ? " filled" : ""}"></span>`).join("");
      return `
          <article class="metric-card${isEmpty ? " empty" : ""}" style="--metric-soft: ${soft}; --metric-tone: ${tone};">
            <div class="metric-top">
              <h3 class="metric-label">${escapeHtml(metric.label)}</h3>
              <div class="metric-value">${isEmpty ? "--" : `${level}/10`}</div>
            </div>
            ${detail ? `<p class="metric-detail">${escapeHtml(detail)}</p>` : ""}
            <div class="metric-dots" aria-label="${isEmpty ? "\u041D\u0435\u0442 \u043E\u0446\u0435\u043D\u043A\u0438" : `\u0423\u0440\u043E\u0432\u0435\u043D\u044C ${level} \u0438\u0437 10`}">${dots}</div>
          </article>
        `;
    }).join("");
  }
  function drawRadar(metrics) {
    const canvas = document.getElementById("radar");
    const ctx = canvas.getContext("2d");
    const size = canvas.width;
    const center = size / 2;
    const radius = size * 0.34;
    if (!metrics || !metrics.length) {
      ctx.clearRect(0, 0, size, size);
      return;
    }
    ctx.clearRect(0, 0, size, size);
    const hasRealMetrics = metrics.some((metric) => !(metric.empty || metric.value === null || metric.value === void 0));
    const metricValue = (metric) => Math.max(0, Math.min(100, Number(metric.value || 0)));
    ctx.lineWidth = 2;
    ctx.font = "20px Inter, system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const count = metrics.length || 1;
    const angleFor = (index) => -Math.PI / 2 + index * (Math.PI * 2 / count);
    const labelLines = (label) => {
      const words = String(label || "").split(" ");
      return words.length > 2 ? [words.slice(0, -1).join(" "), words[words.length - 1]] : words;
    };
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
      const labelRadius = radius + 42;
      const lines = labelLines(metric.label);
      const maxLineWidth = Math.max(...lines.map((lineText) => ctx.measureText(lineText).width), 0);
      const horizontalPadding = Math.max(76, maxLineWidth / 2 + 16);
      const lx = Math.max(horizontalPadding, Math.min(size - horizontalPadding, center + Math.cos(angle) * labelRadius));
      const ly = Math.max(42, Math.min(size - 42, center + Math.sin(angle) * labelRadius));
      ctx.fillStyle = hasRealMetrics ? "#5f6d7a" : "#8b96a3";
      const startY = ly - (lines.length - 1) * 11;
      lines.forEach((lineText, line) => ctx.fillText(lineText, lx, startY + line * 22));
    });
    if (!hasRealMetrics) return;
    const neutralValue = 36;
    const displayValue = (metric) => metric.empty || metric.value === null || metric.value === void 0 ? neutralValue : metricValue(metric);
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
    fill.addColorStop(0.5, "rgba(169, 200, 255, .36)");
    fill.addColorStop(1, "rgba(255, 214, 166, .34)");
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = "rgba(91, 184, 169, .8)";
    ctx.lineWidth = 4;
    ctx.stroke();
    metrics.forEach((metric, index) => {
      const isEmpty = metric.empty || metric.value === null || metric.value === void 0;
      const valueRadius = radius * displayValue(metric) / 100;
      const angle = angleFor(index);
      const x = center + Math.cos(angle) * valueRadius;
      const y = center + Math.sin(angle) * valueRadius;
      ctx.beginPath();
      ctx.arc(x, y, isEmpty ? 7 : 10, 0, Math.PI * 2);
      ctx.fillStyle = isEmpty ? "rgba(174, 184, 196, .72)" : metric.tone && metric.tone[1] ? metric.tone[1] : "#5bb8a9";
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = isEmpty ? 2 : 3;
      ctx.stroke();
    });
  }
  function renderProfile(data) {
    currentProfileData = data;
    const firstName = data.user && data.user.first_name ? data.user.first_name : "\u0432\u044B";
    const metrics = data.metrics || [];
    const hasRealMetrics = metrics.some((metric) => !(metric.empty || metric.value === null || metric.value === void 0));
    document.getElementById("hero").classList.toggle("no-radar", !hasRealMetrics);
    setText("hello", firstName === "\u0432\u044B" ? "\u041F\u0440\u043E\u0444\u0438\u043B\u044C" : firstName);
    setText("profileSummary", shortProfileDescription(data.user.profile_summary, firstName));
    setText("disclaimer", data.disclaimer);
    renderMetrics(metrics);
    drawRadar(hasRealMetrics ? metrics : []);
    renderLifehacks(data.lifehack_cards);
    renderInsights(data.insights);
    prefillConsultationForm(data);
    requestAnimationFrame(() => {
      root.classList.remove("loading");
      statusEl.textContent = "";
    });
  }
  function renderDiarySwatches(selectedColor) {
    diarySwatches.innerHTML = Object.keys(diaryColors).map((key) => {
      const color = diaryColors[key];
      return `
        <button
          class="swatch${selectedColor === key ? " active" : ""}"
          type="button"
          data-swatch-color="${escapeHtml(key)}"
          title="${escapeHtml(color.label)}"
          style="background: linear-gradient(135deg, ${color.soft}, ${color.tone});"
        ></button>
      `;
    }).join("");
    diarySwatches.querySelectorAll("[data-swatch-color]").forEach((button) => {
      button.addEventListener("click", () => {
        currentDiaryDraft.color_theme = button.dataset.swatchColor || "blue";
        renderDiarySwatches(currentDiaryDraft.color_theme);
      });
    });
  }
  function renderDiaryCategories(selectedTheme) {
    if (!diaryThemeSelect) return;
    diaryThemeSelect.innerHTML = [`<option value="">\u041D\u0435 \u0432\u044B\u0431\u0440\u0430\u043D\u043E</option>`].concat(Object.keys(diaryThemes).map((key) => {
      const theme = diaryThemes[key];
      return `<option value="${escapeHtml(key)}">${escapeHtml(theme.label)}</option>`;
    })).join("");
    diaryThemeSelect.value = selectedTheme && diaryThemes[selectedTheme] ? selectedTheme : "";
  }
  function openDiaryEditor(card) {
    const normalizedCardTheme = normalizeDiaryTheme(card && card.theme ? card.theme : "");
    const theme = normalizedCardTheme && diaryThemes[normalizedCardTheme] ? normalizedCardTheme : "";
    const colorTheme = card && card.color_theme && diaryColors[card.color_theme] ? card.color_theme : theme && diaryThemeColors[theme] ? diaryThemeColors[theme] : "blue";
    currentDiaryDraft = {
      item_id: card && card.manual ? card.id || null : null,
      theme,
      color_theme: diaryColors[colorTheme] ? colorTheme : "blue"
    };
    diaryTitleInput.value = card && card.title ? card.title : "";
    diaryTextInput.value = card && card.text ? card.text : "";
    document.getElementById("diaryDialogTitle").textContent = card && card.manual ? "\u0420\u0435\u0434\u0430\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u043E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u0435" : "\u041D\u043E\u0432\u043E\u0435 \u043E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u0435";
    renderDiarySwatches(currentDiaryDraft.color_theme);
    renderDiaryCategories(currentDiaryDraft.theme);
    diaryDialog.classList.add("open");
  }
  function closeDiaryEditor() {
    diaryDialog.classList.remove("open");
  }
  async function saveDiaryEntry() {
    if (demoMode || !telegramId) return;
    const title = diaryTitleInput.value.trim();
    const text = diaryTextInput.value.trim();
    if (!title || !text) {
      statusEl.textContent = "\u0417\u0430\u043F\u043E\u043B\u043D\u0438\u0442\u0435 \u0437\u0430\u0433\u043E\u043B\u043E\u0432\u043E\u043A \u0438 \u0442\u0435\u043A\u0441\u0442 \u043E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u044F.";
      return;
    }
    statusEl.textContent = "\u0421\u043E\u0445\u0440\u0430\u043D\u044F\u044E \u043E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u0435\u2026";
    const payload = __spreadProps(__spreadValues({}, buildSupportPayload()), {
      item_id: currentDiaryDraft.item_id,
      title,
      text,
      theme: currentDiaryDraft.theme || null,
      color_theme: currentDiaryDraft.color_theme
    });
    const response = await fetch("/api/v1/support/diary/upsert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(detail.detail || `HTTP ${response.status}`);
    }
    closeDiaryEditor();
    renderProfile(await response.json());
  }
  async function deleteDiaryEntry(itemId) {
    if (demoMode || !telegramId || !itemId) return;
    statusEl.textContent = "\u0423\u0434\u0430\u043B\u044F\u044E \u043E\u0441\u043E\u0437\u043D\u0430\u043D\u0438\u0435\u2026";
    const response = await fetch("/api/v1/support/diary/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(__spreadProps(__spreadValues({}, buildSupportPayload()), {
        item_id: itemId
      }))
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(detail.detail || `HTTP ${response.status}`);
    }
    renderProfile(await response.json());
  }
  async function submitConsultationRequest() {
    if (consultationSending) return;
    if (demoMode || !telegramId) {
      setConsultationNote("Форма отправляется только из Telegram или в локальном режиме с telegram_id.");
      return;
    }
    const fullName = normalizeFullName(consultationFullNameInput.value);
    const phone = normalizePhone(consultationPhoneInput.value);
    const message = consultationMessageInput.value.trim();
    if (fullName.length < 5) {
      setConsultationNote("Напишите, пожалуйста, полное имя.");
      consultationFullNameInput.focus();
      return;
    }
    if (!phone) {
      setConsultationNote("Проверьте номер телефона. Нужен формат вроде +7 999 123-45-67.");
      consultationPhoneInput.focus();
      return;
    }
    if (message.length < 10) {
      setConsultationNote("Коротко опишите, пожалуйста, что случилось и с чем нужна консультация.");
      consultationMessageInput.focus();
      return;
    }
    consultationSending = true;
    setConsultationNote("Отправляем заявку врачу…");
    try {
      const response = await fetch("/api/v1/support/consultation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(__spreadProps(__spreadValues({}, buildSupportPayload()), {
          full_name: fullName,
          phone,
          message
        }))
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || `HTTP ${response.status}`);
      }
      const result = await response.json();
      consultationFullNameInput.value = fullName;
      consultationPhoneInput.value = phone;
      consultationMessageInput.value = "";
      setConsultationNote("");
      statusEl.textContent = result.message || "";
      showConsultationSuccess();
    } catch (error) {
      setConsultationNote(String(error.message || error));
    } finally {
      consultationSending = false;
    }
  }
  function demoProfile() {
    return {
      user: {
        first_name: params.get("first_name") || "\u0410\u043D\u0442\u043E\u043D",
        profile_summary: "\u0412 \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0445 \u0434\u0438\u0430\u043B\u043E\u0433\u0430\u0445 \u0437\u0430\u043C\u0435\u0442\u043D\u044B \u0443\u0441\u0442\u0430\u043B\u043E\u0441\u0442\u044C, \u0436\u0435\u043B\u0430\u043D\u0438\u0435 \u044F\u0441\u043D\u043E\u0441\u0442\u0438 \u0438 \u043F\u043E\u043F\u044B\u0442\u043A\u0430 \u0432\u0435\u0440\u043D\u0443\u0442\u044C \u0441\u0435\u0431\u0435 \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u0435. \u0421\u0435\u0439\u0447\u0430\u0441 \u0432\u0430\u0436\u043D\u0435\u0435 \u043D\u0435 \u0434\u0430\u0432\u0438\u0442\u044C \u043D\u0430 \u0441\u0435\u0431\u044F, \u0430 \u0432\u044B\u0431\u0440\u0430\u0442\u044C \u043E\u0434\u0438\u043D \u043F\u043E\u043D\u044F\u0442\u043D\u044B\u0439 \u0448\u0430\u0433 \u0438 \u0437\u0430\u043C\u0435\u0442\u0438\u0442\u044C \u043E\u043F\u043E\u0440\u044B, \u043A\u043E\u0442\u043E\u0440\u044B\u0435 \u0443\u0436\u0435 \u0440\u0430\u0431\u043E\u0442\u0430\u044E\u0442."
      },
      summary: {
        memory_count: 18,
        open_topics_count: 4,
        support_items_count: 6,
        latest_update: "21.05.2026"
      },
      disclaimer: "\u041F\u0435\u0440\u0435\u0434 \u0432\u0430\u043C\u0438 \u043A\u0430\u0440\u0442\u0430 \u0432\u0430\u0448\u0435\u0439 \u043B\u0438\u0447\u043D\u043E\u0441\u0442\u0438, \u043D\u0430 \u043E\u0441\u043D\u043E\u0432\u0435 \u0430\u043D\u0430\u043B\u0438\u0437\u0430 \u0421\u0443\u0448\u043A\u0435\u0432\u0438\u0447 \u0411\u043E\u0442\u0430. \u041E\u043D\u0430 \u0431\u0443\u0434\u0435\u0442 \u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u0441\u044F \u0442\u043E\u0447\u043D\u0435\u0435 \u0438 \u0442\u043E\u0447\u043D\u0435\u0435 \u0441 \u043A\u0430\u0436\u0434\u044B\u043C \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u043E\u043C \u0441 \u0432\u0430\u043C\u0438.",
      metrics: [
        { label: "\u0421\u0443\u0431\u044A\u0435\u043A\u0442\u043D\u043E\u0441\u0442\u044C", value: 68, hint: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E", detail: "\u0421\u0435\u0439\u0447\u0430\u0441 \u0432\u044B \u0447\u0430\u0449\u0435 \u0441\u0430\u043C\u0438 \u0437\u0430\u0434\u0430\u0435\u0442\u0435 \u043A\u0443\u0440\u0441 \u0441\u0432\u043E\u0435\u0439 \u0436\u0438\u0437\u043D\u0438 \u0438 \u043F\u0440\u0438\u043D\u0438\u043C\u0430\u0435\u0442\u0435 \u0440\u0435\u0448\u0435\u043D\u0438\u044F \u0441\u0430\u043C\u0438, \u043D\u0435 \u0436\u0438\u0432\u0435\u0442\u0435 \u0432 \u043F\u043E\u0437\u0438\u0446\u0438\u0438 \u0432\u0435\u0447\u043D\u043E\u0439 \u0443\u0441\u0442\u0443\u043F\u043A\u0438 \u0438\u043B\u0438 \u043F\u043E\u0434\u0447\u0438\u043D\u0435\u043D\u0438\u044F \u0447\u0443\u0436\u043E\u0439 \u0432\u043E\u043B\u0435.", tone: ["#8fd6c8", "#5bb8a9"] },
        { label: "\u042D\u043C\u043E\u0446\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u044B\u0439 \u0438\u043D\u0442\u0435\u043B\u043B\u0435\u043A\u0442", value: 63, hint: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E", detail: "\u0412\u044B \u043E\u0431\u044B\u0447\u043D\u043E \u0437\u0430\u043C\u0435\u0447\u0430\u0435\u0442\u0435 \u044D\u043C\u043E\u0446\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u044B\u0439 \u043A\u043E\u043D\u0442\u0435\u043A\u0441\u0442 \u0438 \u043C\u043E\u0436\u0435\u0442\u0435 \u043D\u0430\u0437\u0432\u0430\u0442\u044C, \u0447\u0442\u043E \u043F\u0440\u043E\u0438\u0441\u0445\u043E\u0434\u0438\u0442, \u0445\u043E\u0442\u044F \u0432 \u043F\u0435\u0440\u0435\u0433\u0440\u0443\u0437\u0435 \u0447\u0430\u0441\u0442\u044C \u043D\u044E\u0430\u043D\u0441\u043E\u0432 \u0435\u0449\u0435 \u0442\u0435\u0440\u044F\u0435\u0442\u0441\u044F.", tone: ["#ffd6a6", "#f3ad61"] },
        { label: "\u0413\u0440\u0430\u043D\u0438\u0446\u044B", value: 52, hint: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E", detail: '\u0412 \u043F\u043E\u043D\u044F\u0442\u043D\u044B\u0445 \u0441\u0438\u0442\u0443\u0430\u0446\u0438\u044F\u0445 \u0432\u044B \u0443\u043C\u0435\u0435\u0442\u0435 \u0433\u043E\u0432\u043E\u0440\u0438\u0442\u044C "\u043D\u0435\u0442" \u0438 \u043E\u0431\u043E\u0437\u043D\u0430\u0447\u0430\u0442\u044C \u0441\u0432\u043E\u0438 \u043F\u0440\u0435\u0434\u0435\u043B\u044B, \u043D\u043E \u0432 \u0447\u0443\u0432\u0441\u0442\u0432\u0438\u0442\u0435\u043B\u044C\u043D\u044B\u0445 \u0442\u0435\u043C\u0430\u0445 \u0433\u0440\u0430\u043D\u0438\u0446\u044B \u0435\u0449\u0435 \u043C\u043E\u0433\u0443\u0442 \u0448\u0430\u0442\u0430\u0442\u044C\u0441\u044F.', tone: ["#c9b7ff", "#987de8"] },
        { label: "\u041A\u043E\u043D\u0442\u0430\u043A\u0442 \u0441 \u0441\u043E\u0431\u043E\u0439", value: 70, hint: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E", detail: "\u0412\u044B \u0445\u043E\u0440\u043E\u0448\u043E \u0437\u0430\u043C\u0435\u0447\u0430\u0435\u0442\u0435 \u0441\u0438\u0433\u043D\u0430\u043B\u044B \u0442\u0435\u043B\u0430 \u0438 \u044D\u043C\u043E\u0446\u0438\u0439, \u043F\u043E\u044D\u0442\u043E\u043C\u0443 \u043E\u0431\u044B\u0447\u043D\u043E \u0440\u0430\u043D\u044C\u0448\u0435 \u0432\u0438\u0434\u0438\u0442\u0435 \u043F\u0435\u0440\u0435\u0433\u0440\u0443\u0437, \u043D\u0430\u043F\u0440\u044F\u0436\u0435\u043D\u0438\u0435 \u0438 \u0441\u043C\u0435\u043D\u0443 \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u044F.", tone: ["#b7e6ff", "#67badc"] },
        { label: "\u041A\u0440\u0438\u0442\u0438\u0447\u043D\u043E\u0441\u0442\u044C", value: 61, hint: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E", detail: "\u0412\u044B \u0443\u0436\u0435 \u0443\u043C\u0435\u0435\u0442\u0435 \u043E\u0442\u0434\u0435\u043B\u044F\u0442\u044C \u0444\u0430\u043A\u0442\u044B \u043E\u0442 \u044D\u043C\u043E\u0446\u0438\u0439 \u0438 \u043F\u0440\u043E\u0432\u0435\u0440\u044F\u0442\u044C \u0441\u0432\u043E\u0438 \u0432\u044B\u0432\u043E\u0434\u044B, \u0445\u043E\u0442\u044F \u0432 \u0437\u0430\u0440\u044F\u0436\u0435\u043D\u043D\u044B\u0445 \u0442\u0435\u043C\u0430\u0445 \u0432\u0430\u0441 \u0435\u0449\u0435 \u043C\u043E\u0436\u0435\u0442 \u0443\u043D\u043E\u0441\u0438\u0442\u044C \u0432 \u043F\u0435\u0440\u0432\u0443\u044E \u0438\u043D\u0442\u0435\u0440\u043F\u0440\u0435\u0442\u0430\u0446\u0438\u044E.", tone: ["#a9c8ff", "#6f9fed"] },
        { label: "\u0421\u0430\u043C\u043E\u0440\u0435\u0433\u0443\u043B\u044F\u0446\u0438\u044F", value: 64, hint: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E", detail: "\u0423 \u0432\u0430\u0441 \u0443\u0436\u0435 \u0435\u0441\u0442\u044C \u0441\u043F\u043E\u0441\u043E\u0431\u044B \u0432\u044B\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0442\u044C \u043F\u0435\u0440\u0435\u0433\u0440\u0443\u0437 \u0438 \u0432\u043E\u0437\u0432\u0440\u0430\u0449\u0430\u0442\u044C\u0441\u044F \u043A \u043E\u043F\u043E\u0440\u0430\u043C, \u0445\u043E\u0442\u044F \u0432 \u0442\u044F\u0436\u0435\u043B\u044B\u0435 \u043C\u043E\u043C\u0435\u043D\u0442\u044B \u044D\u0442\u043E \u0432\u0441\u0435 \u0435\u0449\u0435 \u0442\u0440\u0435\u0431\u0443\u0435\u0442 \u0443\u0441\u0438\u043B\u0438\u044F.", tone: ["#ff9c8b", "#ff6f91"] },
        { label: "\u0420\u0430\u0446\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u043E\u0441\u0442\u044C", value: 56, hint: "\u0418\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438 \u043E \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043C\u0430\u043B\u043E", detail: "\u0412\u044B \u0432 \u0446\u0435\u043B\u043E\u043C \u0440\u0430\u0441\u0441\u0443\u0436\u0434\u0430\u0435\u0442\u0435 \u0441\u0432\u044F\u0437\u043D\u043E, \u0438\u0449\u0435\u0442\u0435 \u043F\u0440\u0438\u0447\u0438\u043D\u044B \u0438 \u043E\u043F\u0438\u0440\u0430\u0435\u0442\u0435\u0441\u044C \u043D\u0430 \u0437\u0434\u0440\u0430\u0432\u044B\u0439 \u0441\u043C\u044B\u0441\u043B, \u0445\u043E\u0442\u044F \u0432 \u044D\u043C\u043E\u0446\u0438\u043E\u043D\u0430\u043B\u044C\u043D\u044B\u0445 \u0442\u0435\u043C\u0430\u0445 \u043B\u043E\u0433\u0438\u043A\u0430 \u043D\u0435 \u0432\u0441\u0435\u0433\u0434\u0430 \u0443\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u0442 \u043F\u043E\u0437\u0438\u0446\u0438\u044E.", tone: ["#f5b8c8", "#df7f9a"] }
      ],
      activity: [
        { label: "15.05", count: 1, value: 28 },
        { label: "16.05", count: 0, value: 0 },
        { label: "17.05", count: 3, value: 72 },
        { label: "18.05", count: 2, value: 50 },
        { label: "19.05", count: 4, value: 100 },
        { label: "20.05", count: 2, value: 50 },
        { label: "21.05", count: 3, value: 72 }
      ],
      lifehack_cards: [
        { title: "\u041F\u0430\u0443\u0437\u0430 \u043F\u0435\u0440\u0435\u0434 \u043E\u0442\u0432\u0435\u0442\u043E\u043C", text: "\u0415\u0441\u043B\u0438 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440 \u0437\u0430\u0434\u0435\u0432\u0430\u0435\u0442, \u043D\u0435 \u043E\u0442\u0432\u0435\u0447\u0430\u0442\u044C \u0441\u0440\u0430\u0437\u0443. \u041E\u0442\u043A\u0440\u044B\u0442\u044C \u0437\u0430\u043C\u0435\u0442\u043A\u0443 \u0438 \u043D\u0430\u0431\u0440\u043E\u0441\u0430\u0442\u044C \u0444\u0440\u0430\u0437\u0443, \u043A\u043E\u0442\u043E\u0440\u0443\u044E \u0445\u043E\u0447\u0435\u0442\u0441\u044F \u0441\u043A\u0430\u0437\u0430\u0442\u044C \u0431\u0435\u0437 \u043E\u043F\u0440\u0430\u0432\u0434\u0430\u043D\u0438\u0439.", next_step: "\u0412\u0435\u0440\u043D\u0443\u0442\u044C\u0441\u044F \u043A \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044E \u0447\u0435\u0440\u0435\u0437 10 \u043C\u0438\u043D\u0443\u0442." },
        { title: "\u0420\u0430\u0437\u043E\u0431\u0440\u0430\u0442\u044C \u0432\u0435\u0447\u0435\u0440", text: "\u041F\u0435\u0440\u0435\u0434 \u0441\u043D\u043E\u043C \u043E\u0442\u043C\u0435\u0442\u0438\u0442\u044C, \u0447\u0442\u043E \u0441\u0435\u0433\u043E\u0434\u043D\u044F \u0437\u0430\u0431\u0440\u0430\u043B\u043E \u0441\u0438\u043B\u044B \u0438 \u0447\u0442\u043E \u043D\u0435\u043C\u043D\u043E\u0433\u043E \u043F\u043E\u043C\u043E\u0433\u043B\u043E.", next_step: "\u041E\u0441\u0442\u0430\u0432\u0438\u0442\u044C \u0442\u043E\u043B\u044C\u043A\u043E \u043E\u0434\u0438\u043D \u043F\u0443\u043D\u043A\u0442, \u043A \u043A\u043E\u0442\u043E\u0440\u043E\u043C\u0443 \u0441\u0442\u043E\u0438\u0442 \u0432\u0435\u0440\u043D\u0443\u0442\u044C\u0441\u044F \u0437\u0430\u0432\u0442\u0440\u0430." },
        { title: "\u041F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u0438\u0442\u044C \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440", text: "\u041F\u0435\u0440\u0435\u0434 \u0441\u043B\u043E\u0436\u043D\u043E\u0439 \u0442\u0435\u043C\u043E\u0439 \u0437\u0430\u043F\u0438\u0441\u0430\u0442\u044C \u0446\u0435\u043B\u044C \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u0430 \u0438 \u043E\u0434\u043D\u0443 \u0433\u0440\u0430\u043D\u0438\u0446\u0443, \u043A\u043E\u0442\u043E\u0440\u0443\u044E \u043D\u0435 \u0445\u043E\u0447\u0435\u0442\u0441\u044F \u043E\u0442\u0434\u0430\u0432\u0430\u0442\u044C.", next_step: "\u041D\u0430\u0447\u0430\u0442\u044C \u0441 \u043A\u043E\u043D\u043A\u0440\u0435\u0442\u043D\u043E\u0433\u043E \u0444\u0430\u043A\u0442\u0430, \u0431\u0435\u0437 \u0434\u043B\u0438\u043D\u043D\u043E\u0433\u043E \u0432\u0441\u0442\u0443\u043F\u043B\u0435\u043D\u0438\u044F." }
      ],
      attention_cards: [
        { kind: "\u043D\u0430 \u0447\u0442\u043E \u043E\u0431\u0440\u0430\u0442\u0438\u0442\u044C \u0432\u043D\u0438\u043C\u0430\u043D\u0438\u0435", title: "\u041F\u0435\u0440\u0435\u0433\u0440\u0443\u0437 \u043F\u043E\u0441\u043B\u0435 \u043E\u0431\u0449\u0435\u043D\u0438\u044F", text: "\u041F\u043E\u0441\u043B\u0435 \u043D\u0430\u043F\u0440\u044F\u0436\u0435\u043D\u043D\u044B\u0445 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u043E\u0432 \u0441\u0442\u043E\u0438\u0442 \u0437\u0430\u0440\u0430\u043D\u0435\u0435 \u0437\u0430\u043A\u043B\u0430\u0434\u044B\u0432\u0430\u0442\u044C \u0432\u0440\u0435\u043C\u044F \u043D\u0430 \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u0435." },
        { kind: "\u0431\u0435\u0440\u0435\u0436\u043D\u0430\u044F \u0437\u0430\u043C\u0435\u0442\u043A\u0430", title: "\u0421\u043E\u043D \u043A\u0430\u043A \u043C\u0430\u0440\u043A\u0435\u0440", text: "\u0415\u0441\u043B\u0438 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u043E \u043D\u043E\u0447\u0435\u0439 \u043F\u043E\u0434\u0440\u044F\u0434 \u0441\u043E\u043D \u0440\u0435\u0437\u043A\u043E \u0443\u0445\u0443\u0434\u0448\u0430\u0435\u0442\u0441\u044F, \u044D\u0442\u043E \u0432\u0430\u0436\u043D\u043E \u043E\u0431\u0441\u0443\u0434\u0438\u0442\u044C \u0441\u043E \u0441\u043F\u0435\u0446\u0438\u0430\u043B\u0438\u0441\u0442\u043E\u043C." }
      ],
      insights: [
        { id: "demo-1", tone: "growth", theme: "agency", title: "\u041F\u043E\u0441\u043B\u0435 \u043F\u0430\u0443\u0437\u044B \u0442\u043E\u0447\u043D\u0435\u0435 \u0441\u043B\u043E\u0432\u0430", text: "\u0412\u044B \u0437\u0430\u043C\u0435\u0442\u0438\u043B\u0438, \u0447\u0442\u043E \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u043E \u043C\u0438\u043D\u0443\u0442 \u043C\u0435\u0436\u0434\u0443 \u044D\u043C\u043E\u0446\u0438\u0435\u0439 \u0438 \u043E\u0442\u0432\u0435\u0442\u043E\u043C \u043F\u043E\u043C\u043E\u0433\u0430\u044E\u0442 \u0433\u043E\u0432\u043E\u0440\u0438\u0442\u044C \u043C\u0435\u043D\u044C\u0448\u0435 \u0438\u0437 \u0437\u0430\u0449\u0438\u0442\u044B.", manual: false },
        { id: "demo-2", tone: "resource", theme: "boundaries", title: "\u0413\u0440\u0430\u043D\u0438\u0446\u044B \u0441\u0442\u0430\u043B\u0438 \u0441\u043F\u043E\u043A\u043E\u0439\u043D\u0435\u0435", text: "\u0412\u044B \u0441\u0442\u0430\u043B\u0438 \u0447\u0430\u0449\u0435 \u0432\u0438\u0434\u0435\u0442\u044C, \u0447\u0442\u043E \u0447\u0435\u0441\u0442\u043D\u0430\u044F \u043F\u0440\u043E\u0441\u044C\u0431\u0430 \u043D\u0435 \u043E\u0431\u044F\u0437\u0430\u0442\u0435\u043B\u044C\u043D\u043E \u043F\u0440\u0435\u0432\u0440\u0430\u0449\u0430\u0435\u0442\u0441\u044F \u0432 \u043A\u043E\u043D\u0444\u043B\u0438\u043A\u0442.", manual: true },
        { id: "demo-3", tone: "attention", theme: "self_contact", title: "\u0421\u043E\u043D \u0441\u0432\u044F\u0437\u0430\u043D \u0441 \u043F\u0435\u0440\u0435\u0433\u0440\u0443\u0437\u043E\u043C", text: "\u0421\u0442\u0430\u043B\u043E \u0432\u0438\u0434\u043D\u043E, \u0447\u0442\u043E \u043F\u043E\u0441\u043B\u0435 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u0438\u0445 \u043D\u0430\u043F\u0440\u044F\u0436\u0435\u043D\u043D\u044B\u0445 \u0434\u043D\u0435\u0439 \u0441\u043E\u043D \u043F\u0435\u0440\u0432\u044B\u043C \u043F\u043E\u043A\u0430\u0437\u044B\u0432\u0430\u0435\u0442 \u043D\u0435\u0445\u0432\u0430\u0442\u043A\u0443 \u0441\u0438\u043B.", manual: false }
      ]
    };
  }
  async function loadProfile() {
    root.classList.add("loading");
    if (demoMode) {
      renderProfile(demoProfile());
      statusEl.textContent = "Demo-\u0440\u0435\u0436\u0438\u043C: \u0440\u0435\u0430\u043B\u044C\u043D\u044B\u0439 \u043F\u0440\u043E\u0444\u0438\u043B\u044C \u043F\u043E\u044F\u0432\u0438\u0442\u0441\u044F \u043F\u0440\u0438 \u043E\u0442\u043A\u0440\u044B\u0442\u0438\u0438 \u0438\u0437 Telegram.";
      return;
    }
    if (!telegramId) {
      renderProfile(placeholderProfile(null));
      setText("hello", "\u041E\u0442\u043A\u0440\u043E\u0439\u0442\u0435 \u043F\u0440\u043E\u0444\u0438\u043B\u044C \u0438\u0437 Telegram");
      setText("profileSummary", "\u0422\u0430\u043A mini-app \u0441\u043C\u043E\u0436\u0435\u0442 \u0431\u0435\u0437\u043E\u043F\u0430\u0441\u043D\u043E \u043F\u043E\u043D\u044F\u0442\u044C, \u0447\u0435\u0439 \u043F\u0440\u043E\u0444\u0438\u043B\u044C \u043F\u043E\u0434\u0434\u0435\u0440\u0436\u043A\u0438 \u043F\u043E\u043A\u0430\u0437\u0430\u0442\u044C.");
      statusEl.textContent = "\u0414\u043B\u044F \u043B\u043E\u043A\u0430\u043B\u044C\u043D\u043E\u0439 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438 \u043C\u043E\u0436\u043D\u043E \u043E\u0442\u043A\u0440\u044B\u0442\u044C /app/support?telegram_id=123.";
      return;
    }
    const payload = buildSupportPayload();
    renderLoadingState();
    statusEl.textContent = "";
    try {
      const response = await fetch("/api/v1/support/me", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || `HTTP ${response.status}`);
      }
      renderProfile(await response.json());
    } catch (error) {
      root.classList.remove("loading");
      setText("hello", "\u041D\u0435 \u043F\u043E\u043B\u0443\u0447\u0438\u043B\u043E\u0441\u044C \u043E\u0442\u043A\u0440\u044B\u0442\u044C \u043F\u0440\u043E\u0444\u0438\u043B\u044C");
      setText("profileSummary", "\u041F\u0440\u043E\u0432\u0435\u0440\u044C\u0442\u0435, \u0447\u0442\u043E mini-app \u043E\u0442\u043A\u0440\u044B\u0442\u0430 \u0438\u0437 Telegram \u0438 backend \u0434\u043E\u0441\u0442\u0443\u043F\u0435\u043D.");
      statusEl.textContent = String(error.message || error);
    }
  }
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => openTab(tab.dataset.tab));
  });
  document.getElementById("heroConsultationButton").addEventListener("click", () => {
    openTab("consultation");
    if (consultationFullNameInput) consultationFullNameInput.focus();
  });
  document.getElementById("submitConsultationButton").addEventListener("click", async () => {
    await submitConsultationRequest();
  });
  document.getElementById("addDiaryButton").addEventListener("click", () => openDiaryEditor(null));
  document.getElementById("closeDiaryDialog").addEventListener("click", closeDiaryEditor);
  document.getElementById("cancelDiaryButton").addEventListener("click", closeDiaryEditor);
  diaryThemeSelect.addEventListener("change", () => {
    currentDiaryDraft.theme = diaryThemeSelect.value && diaryThemes[diaryThemeSelect.value] ? diaryThemeSelect.value : "";
  });
  document.getElementById("generateLifehackButton").addEventListener("click", async () => {
    try {
      await generateLifehack();
    } catch (error) {
      flashLifehackStatus(String(error.message || error));
    }
  });
  lifehackPromptInput.addEventListener("keydown", async (event) => {
    if (event.key !== "Enter") return;
    event.preventDefault();
    try {
      await generateLifehack();
    } catch (error) {
      flashLifehackStatus(String(error.message || error));
    }
  });
  consultationMessageInput.addEventListener("keydown", async (event) => {
    if (!(event.metaKey || event.ctrlKey) || event.key !== "Enter") return;
    event.preventDefault();
    await submitConsultationRequest();
  });
  document.getElementById("saveDiaryButton").addEventListener("click", async () => {
    try {
      await saveDiaryEntry();
    } catch (error) {
      statusEl.textContent = String(error.message || error);
    }
  });
  diaryDialog.addEventListener("click", (event) => {
    if (event.target === diaryDialog) closeDiaryEditor();
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
})();
  </script>
</body>
</html>
"""

@router.get("/app/support", response_class=HTMLResponse)
async def support_app() -> str:
    """Return the improved support mini‑app HTML."""
    return SUPPORT_APP_HTML
