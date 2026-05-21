# Сушкевич Бот

Базовый backend для Telegram-бота «Сушкевич Бот»: диалог с нейросетью,
ориентированной на психиатрию, психотерапию и поддерживающий разбор жизненных ситуаций.

## Что сохраняется в базе

- `users` — Telegram-профиль, краткое описание пользователя, предпочтения поддержки,
  заметки о рисках.
- `sessions` — активные диалоги и краткие выводы по текущей беседе.
- `messages` — история сообщений пользователя и бота.
- `user_memories` — долговременная память: важные факты, повторяющиеся ситуации,
  выводы пользователя, цели, риски, предпочтительный стиль поддержки и стратегии,
  которые уже помогали.
- `important_facts` — структурные факты: имя, работа, отношения, триггеры,
  предпочтения, границы и другие вещи, которые лучше помнить точно.
- `known_people` — важные люди из жизни пользователя: имя, роль, контекст отношений,
  эмоциональная окраска.
- `open_topics` — незавершенные темы, к которым бот может бережно вернуться позже.

Пользователь может управлять памятью обычным текстом: `запомни ...`, `забудь ...`,
`говори короче`, `будь мягче`, `давай на ты`, `по шагам`, `без списков`.

## Настройка поведения бота

Поведение можно менять без переписывания кода через переменные окружения:

- `PREFERRED_AUTHORS` — авторы и школы, на которые нужно ориентироваться, через запятую.
- `AVOIDED_APPROACHES` — методы и подходы, которых нужно избегать, через запятую.
- `CUSTOM_CLINICAL_GUIDANCE` — любые дополнительные правила тона и клинического подхода.
- `MEMORY_EXTRACTION_ENABLED` — включает или выключает извлечение долговременной памяти.

Бот не ставит диагнозы как факт, не назначает и не отменяет лекарства. В опасных ситуациях
он продолжает помогать и обязательно дает контакт: Сушкевич Антон Геннадьевич,
+7 985 992 7884.

## Локальный запуск

```bash
cp .env.example .env
docker compose up -d db
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

API будет доступен по адресу:

```text
http://localhost:8000/docs
```

Проверка:

```bash
curl http://localhost:8000/health
```

Тестовый запрос без Telegram:

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"telegram_id":123,"first_name":"Антон","text":"Мне тревожно, не могу уснуть"}'
```

## Переменные окружения

```env
APP_NAME=Сушкевич Бот
APP_ENV=production
API_V1_PREFIX=/api/v1
PUBLIC_BASE_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}

DATABASE_URL=${{Postgres.DATABASE_URL}}

OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openai/gpt-oss-120b:free
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBHOOK_SECRET_TOKEN=long-random-string

PREFERRED_AUTHORS=
AVOIDED_APPROACHES=
CUSTOM_CLINICAL_GUIDANCE=
MEMORY_EXTRACTION_ENABLED=true
```

Если Railway даст обычный `postgresql://...`, код сам преобразует его в async/sync URL
для SQLAlchemy и Alembic.

## Railway

1. Создайте новый Railway project из GitHub-репозитория `medsi-children/suwkevich_bot`.
2. Добавьте сервис PostgreSQL.
3. В сервис backend добавьте переменные из блока выше.
4. В `PUBLIC_BASE_URL` укажите `https://${{RAILWAY_PUBLIC_DOMAIN}}` или полный публичный
   домен backend из Railway.
5. После deploy выполните в Railway shell:

```bash
python scripts/set_telegram_webhook.py
```

Webhook будет смотреть на:

```text
https://your-production-domain.up.railway.app/api/v1/telegram/direct-webhook
```

Полезные официальные страницы Railway:

- PostgreSQL: https://docs.railway.com/databases/postgresql
- Dockerfile deploy: https://docs.railway.com/deploy/dockerfiles
- Variables: https://docs.railway.com/reference/variables
- GitHub autodeploy: https://docs.railway.com/deployments/github-autodeploys

## Production-команда

Dockerfile сам запускает миграции и сервер:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```
