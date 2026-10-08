# Структура проекта

```text
two/
|-- .github/
|   |-- ISSUE_TEMPLATE/bug_report.md
|   |-- PULL_REQUEST_TEMPLATE.md
|   `-- workflows/ci.yml
|-- docs/
|   |-- architecture.md
|   |-- project_structure.md
|   |-- review.md
|   |-- russian_git_analogs.md
|   |-- specification.md
|   `-- testing.md
|-- src/
|   |-- __init__.py
|   `-- main.py
|-- tests/
|   |-- __init__.py
|   `-- test_main.py
|-- .gitignore
|-- pytest.ini
`-- README.md
```

Каталог `src` содержит программу, `tests` - автоматические тесты, `docs` -
описание проекта, а `.github` - настройки GitHub Actions и шаблоны.
