# SecDev Course Template

Стартовый шаблон для студенческого репозитория (HSE SecDev 2025).

## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
```

## Ритуал перед PR
```bash
ruff --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## Тесты
```bash
pytest -q
```

## CI
В репозитории настроен workflow **CI** (GitHub Actions) — required check для `main`.
Badge добавится автоматически после загрузки шаблона в GitHub.

## Контейнеры
```bash
# production-like image
docker build --target runtime -t secdev-course-app .
docker run --rm -p 8000:8000 \
  -e APP_API_TOKEN=local-token \
  secdev-course-app

# полный стек: приложение + PostgreSQL
docker compose up --build
```

`docker compose` разворачивает приложение и Postgres 15 с `DATABASE_URL` и dev-токеном.
Контейнер приложения запускается как non-root, с отрубленными capabilities,
read-only rootfs и HEALTHCHECK на `/health`.

## Логика проекта
Приложение моделирует простой бэклог учебного проекта: можно добавлять задачи, менять их
статус (`draft` → `in_progress` → `done`) и удалять ненужные элементы. По умолчанию данные
хранятся в SQLite (`app.db`), но при запуске через `docker compose` используется PostgreSQL
(`DATABASE_URL=postgresql+psycopg://...`).

## Эндпойнты
- `GET /health` → `{"status": "ok"}`
- `GET /items` — вернуть список задач, `?status=` фильтрует по состоянию
- `POST /items` — создать задачу (`name`, опционально `description`, `status`)
- `GET /items/{id}` — получить задачу по идентификатору
- `PUT /items/{id}` — частично обновить задачу (статус/описание/название)
- `DELETE /items/{id}` — удалить задачу

## Формат ошибок
Все ошибки — JSON-обёртка:
```json
{
  "error": {"code": "not_found", "message": "item not found"}
}
```

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.
