# P12 evidence

Артефакты ниже генерируются workflow `Security - IaC & Container Security (P12)`:
- `hadolint_report.json` — результаты Hadolint по Dockerfile;
- `checkov_report.json` — результаты Checkov по IaC/Dockerfile/Compose;
- `trivy_report.json` — результаты Trivy по собранному образу;
- `hardening_summary.md` — краткая сводка по итогам сканов (счётчики по severity и заметки по харднингу).

Workflow складывает файлы в этот каталог и публикует их как GitHub Actions artifacts.
