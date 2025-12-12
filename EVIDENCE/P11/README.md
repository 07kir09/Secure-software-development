# P11 evidence

Артефакты ниже генерируются workflow `Security - DAST (ZAP baseline)`:
- `zap_baseline.html` — HTML-отчёт OWASP ZAP baseline по таргету сервиса;
- `zap_baseline.json` — JSON-отчёт со сводкой алертов;
- `zap_summary.md` — краткая выжимка для описания PR (количества по уровням + комментарий).

Workflow складывает файлы в этот каталог и публикует их как GitHub Actions artifacts.
