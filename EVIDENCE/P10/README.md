# P10 evidence

Артефакты ниже генерируются workflow `Security - SAST & Secrets`:
- `semgrep.sarif` — отчёт Semgrep (профиль `p/ci` + правила `security/semgrep/rules.yml`);
- `gitleaks.json` — отчёт Gitleaks по репозиторию с базовой конфигурацией `security/.gitleaks.toml`;
- `sast_summary.md` — краткая сводка найденных проблем и секретов.

Workflow складывает файлы в этот каталог и публикует их как GitHub Actions artifacts.
