# Codex handoff

Этот файл нужен для будущих итераций Codex, чтобы быстро понять архитектуру
«Сушкевич Бота» и не откатить важные клинические решения.

## Проект

- Локальная папка: `/Users/ori.space.cat/Психиатрия/Сушкевич Бот`
- GitHub: `https://github.com/medsi-children/suwkevich_bot`
- Git remote:
  - fetch: `https://github.com/medsi-children/suwkevich_bot.git`
  - push: `https://github.com/medsi-children/suwkevich_bot.git`
- Основная ветка: `main`
- Пользователь обычно просит пушить прямо в `main`.
- Перед работой делать `git status --short --branch`.
- Если пользователь просит подтянуть актуальное состояние, использовать `git pull --ff-only`
  только после проверки локальных изменений.

## Суть бота

Бот не является “виртуальным психиатром” и не ставит диагнозы. Его роль:

- психиатрическое ориентирование;
- раннее выявление рисков;
- распознавание красных флагов;
- сбор материала для очного врача;
- психообразование безопасным языком;
- поддержка в кризисе без инструкций для самоповреждения;
- longitudinal-aware подход: учитывать динамику во времени и память пользователя.

Важная формула: не диагноз, а гипотеза, уровень риска, красный флаг, очная оценка
или экстренная ситуация.

## Архитектура диалога

- `app/services/dialogue.py` — главный диалоговый слой.
- `build_system_prompt` содержит расширенный базовый промпт: клинические гипотезы,
  риск, синдромы, динамика, reality testing, РПП, ПАВ, соматика, подростковая осторожность.
- `detect_risk_level` определяет кризисные маркеры.
- `ensure_risk_contact` добавляет safety-строку или конкретный контакт врача.
- `handle_user_text` собирает память, клинические домены, relevant knowledge и вызывает LLM.

Контакт врача нельзя снова делать навязчивым. Текущее правило:

- при кризисе без прямой просьбы — только короткая рекомендация связаться с врачом
  или экстренной помощью 112/103;
- конкретный контакт Сушкевича Антона Геннадьевича добавляется только если пользователь
  сам просит контакт или если пользователь прямо просит помощь и есть кризисные маркеры.

## Клиническая база

- Основной файл: `app/knowledge/clinical_orientation.md`.
- Нормативный слой клинреков: `app/knowledge/clinical_guidelines_minzdrav.md`.
- Резервный placeholder: `app/knowledge/psychiatry_literature_digest.md`.
- Доменные карточки: `app/knowledge/disorders/*.md`.
- Retrieval: `app/services/clinical_knowledge.py`.
- Домены и маркеры: `app/services/diagnostic_domains.py`.

`clinical_orientation.md` не надо ужимать. Это большой расширенный ориентир, который
код режет по Markdown-разделам, кэширует по mtime и подставляет в LLM только релевантные
фрагменты.

`clinical_guidelines_minzdrav.md` — это не файл “для ответа пользователю названиями
рекомендаций”, а нормативный слой безопасности и маршрутизации. Его задача — усиливать
красные флаги, уровни срочности и клинические развилки, а не превращать бота в диагнозатор.

`diagnostic_domains.py` не должен быть диагнозатором. Маркеры нужны только для выбора
релевантных знаний и фокуса уточняющих вопросов. Не делать логику вида “слово X значит
диагноз Y”.

Если добавляешь новый домен:

1. Создай Markdown-карточку в `app/knowledge/disorders/`.
2. Добавь `DiagnosticDomain` в `app/services/diagnostic_domains.py`.
3. Добавь тест в `tests/test_clinical_knowledge.py`.
4. Проверь, что формулировки остаются осторожными: гипотезы, риски, очная оценка.

## Память и mini-app

- `app/services/memory.py` извлекает долговременную память, обновляет профиль,
  лайфхаки и инсайты.
- `app/services/support_profile.py` строит профиль mini-app, метрики, лайфхаки,
  дневник и ограничения текста.
- `app/web/support.py` содержит HTML/CSS/JS mini-app.

Лайфхаки ограничены по длине и обрезаются до законченной фразы. В поле создания
нового лайфхака placeholder убран намеренно.

## Railway и переменные

Production-переменные задаются в Railway. Секреты в репозиторий не писать.

Актуальные важные переменные:

- `DATABASE_URL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET_TOKEN`
- `PUBLIC_BASE_URL`
- `PUBLIC_WEBAPP_URL`
- `CLINICAL_KNOWLEDGE_PATH=app/knowledge/clinical_orientation.md`
- `CLINICAL_KNOWLEDGE_MAX_CHARS=5200`
- `MEMORY_EXTRACTION_ENABLED=true`

Старые переменные больше не используются:

- `PREFERRED_AUTHORS`
- `AVOIDED_APPROACHES`
- `CUSTOM_CLINICAL_GUIDANCE`

## Проверки

Перед commit/push запускать:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check app tests
```

Если меняешь только документы, тесты можно не гонять, но лучше хотя бы проверить
`git diff` и `git status`.

## Git-практика

- Не перетирать локальные изменения пользователя.
- Не использовать destructive-команды вроде `git reset --hard`.
- При просьбе “пушим” обычно commit в `main` и `git push origin main`.
- После push проверить `git status --short --branch` и последний commit.
