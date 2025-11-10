# STRIDE Анализ

| Поток / элемент | STRIDE | Угроза | Контроль (ссылка на NFR) | Проверка / Обоснование |
|-----------------|--------|--------|--------------------------|------------------------|
| F1 (Product Manager → Reverse Proxy) | Spoofing / Information Disclosure | MITM или downgrade до HTTP приводит к краже токена доступа | Принудительный HTTPS + HSTS и автоматическое перенаправление (NFR-S02) | Smoke-тест `curl --proto '=https' --tlsv1.2` в CI; отчёт SSL Labs ≥ A |
| F2 (Reverse Proxy → FastAPI) | Elevation of Privilege / Tampering | Внутренний сервис может обойти проверку прав и подменить заголовки пользователя | mTLS и верификация service account на ingress, проверка JWT в приложении (NFR-S01, NFR-S07) | Интеграционные тесты авторизации в pytest; ревью nginx/Traefik конфигурации |
| F3 (FastAPI → Item Store) | Tampering | SQL-инъекции и произвольные апдейты данных | Параметризованные запросы ORM + валидация payload Pydantic (NFR-S09) | `semgrep`/`bandit` в CI + unit-тесты на отклонение опасных payload |
| FastAPI Application (элемент) | Denial of Service | Массовые запросы вызывают отказ сервиса | Rate limiting на edge + circuit breaker (NFR-S05) | Нагрузочный тест k6/Locust nightly, метрики ответа WAF |
| F5 (FastAPI → Reverse Proxy) | Information Disclosure | Отсутствие защитных заголовков → XSS/Clickjacking | Добавление CSP, HSTS, X-Content-Type-Options (NFR-S07) | Бейзлайн OWASP ZAP и smoke `curl -I` проверяют наличие заголовков |
| F7 (FastAPI → Audit Log Storage) | Repudiation | Отсутствие или подмена логов делает расследование невозможным | Структурированные аудит-логи с цифровой подписью и ротацией (NFR-S03) | Pytest проверяет запись лога, контроль retention в Terraform |
| F8 (Security Analyst → Audit Log Storage) | Information Disclosure | Неконтролируемый доступ раскрывает PII/операционные данные | RBAC + VPN сегментация, read-only роли (NFR-S03) | Ежеквартальный IAM аудит, отчёт SIEM об успешных/неуспешных запросах |
| F9 (Developer → Git Hosting) | Tampering | Коммиты с секретами или вредоносными зависимостями попадают в main | Branch protection, `trufflehog` и секрет-сканирование в CI (NFR-S06) | CI job секрет-сканера на каждый PR; репорт от Secret Manager |
| F10 (Git Hosting → CI/CD Pipeline) | Elevation of Privilege | Отключение обязательных security-джобов позволяет пролистнуть уязвимости | Блокирующие стадии `pip-audit`/`semgrep`; политика «must pass» (NFR-S04) | CI status API блокирует merge при падении; отчёт артефактов безопасности хранится 90 дней |
