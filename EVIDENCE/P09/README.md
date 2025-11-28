# P09 evidence

Артефакты ниже генерируются workflow `Security - SBOM & SCA`:
- `sbom.json` — SBOM в формате CycloneDX (Syft 1.16.0);
- `sca_report.json` — отчёт Grype 0.77.0 по SBOM;
- `sca_summary.md` — агрегированная сводка по severity.

Workflow складывает файлы в этот каталог и загружает их в Actions artifacts.
