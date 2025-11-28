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

Security workflow **Security - SBOM & SCA** генерирует SBOM (Syft 1.16.0, CycloneDX) и запускает SCA (Grype 0.77.0) на push/pull_request/workflow_dispatch. Артефакты складываются в `EVIDENCE/P09/` (`sbom.json`, `sca_report.json`, `sca_summary.md`) и публикуются как artifacts; вейверы ведутся в `policy/waivers.yml`.

## Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Логика проекта
Приложение моделирует простой бэклог учебного проекта: можно добавлять задачи, менять их
статус (`draft` → `in_progress` → `done`) и удалять ненужные элементы. Память — временная
(`in-memory`), что достаточно для учебного стенда и автоматических тестов.

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
