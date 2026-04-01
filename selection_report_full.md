# Skill 筛选报告（易闭环、低依赖、状态可判别）

**生成时间:** 2026-04-01 14:09:02

## 📊 总览

| 指标 | 数值 |
|------|------|
| 总技能数 | 5885 |
| 通过数量 | 1105 |
| 通过率 | 18.8% |

## 📈 分类统计

| 类别 | 数量 | 占比 |
|------|------|------|
| 结构化数据处理 | 154 | 2.6% |
| 逻辑/规则验证 | 560 | 9.5% |
| 模拟 API/Mock | 391 | 6.6% |

## ❌ 失败原因分析

| 原因 | 数量 |
|------|------|

## 🏆 Top 20 高置信度技能

| 排名 | 名称 | 类别 | 置信度 | Stars | 语言 | 依赖数 |
|------|------|------|--------|-------|------|--------|
| 1 | test-gas-skill | logic_validation | 0.62 | 0 | None | 0 |
| 2 | clean-pytest | logic_validation | 0.62 | 0 | None | 0 |
| 3 | hollow-validation-checker | logic_validation | 0.62 | 0 | None | 0 |
| 4 | local-task-runner | mock_api | 0.62 | 0 | None | 0 |
| 5 | obra/testing-anti-patterns | logic_validation | 0.62 | 0 | None | 0 |
| 6 | expanso-csv-to-json | structured_data | 0.50 | 0 | None | 0 |
| 7 | expanso-json-to-csv | structured_data | 0.50 | 0 | None | 0 |
| 8 | expanso-json-to-yaml | structured_data | 0.50 | 0 | None | 0 |
| 9 | expanso-xml-to-json | structured_data | 0.50 | 0 | None | 0 |
| 10 | expanso-yaml-to-json | structured_data | 0.50 | 0 | None | 0 |
| 11 | markdown-converter | structured_data | 0.50 | 0 | None | 0 |
| 12 | basal-ganglia-memory | mock_api | 0.50 | 0 | None | 0 |
| 13 | family-todo-management | mock_api | 0.50 | 0 | None | 0 |
| 14 | neural-memory | mock_api | 0.50 | 0 | None | 0 |
| 15 | ng-lawyer-db-build | mock_api | 0.50 | 0 | None | 0 |
| 16 | publora-mastodon | mock_api | 0.50 | 0 | None | 0 |
| 17 | teamo-lite-offline | mock_api | 0.50 | 0 | None | 0 |
| 18 | telegram-todolist | mock_api | 0.50 | 0 | None | 0 |
| 19 | todo-boss | mock_api | 0.50 | 0 | None | 0 |
| 20 | todokan | mock_api | 0.50 | 0 | None | 0 |

## 🔧 筛选配置

```json
{
  "min_stars": 50,
  "min_lines": 50,
  "max_lines": 2000,
  "allowed_languages": [
    "python",
    "nodejs",
    "bash",
    "shell"
  ],
  "max_external_deps": 5,
  "forbidden_patterns": [
    "requires\\s+.*\\b(api\\s+key|token|credential)\\b",
    "requires\\s+.*\\b(account|login|auth)\\b",
    "requires\\s+.*\\b(browser|selenium|playwright)\\b",
    "requires\\s+.*\\b(docker|k8s|kubernetes)\\b",
    "requires\\s+.*\\b(cloud|aws|gcp|azure)\\b",
    "npm\\s+install\\s+.*puppeteer",
    "pip\\s+install\\s+.*selenium"
  ],
  "structured_data_keywords": [
    "json",
    "csv",
    "xml",
    "yaml",
    "markdown",
    "table",
    "parse",
    "convert",
    "transform",
    "extract",
    "validate",
    "data processing",
    "data ops",
    "etl"
  ],
  "logic_validation_keywords": [
    "regex",
    "regular expression",
    "pattern",
    "match",
    "test",
    "unit test",
    "pytest",
    "assert",
    "verify",
    "rule",
    "validation",
    "lint",
    "check",
    "filter",
    "search",
    "grep"
  ],
  "mock_api_keywords": [
    "mock",
    "fake",
    "simulate",
    "stub",
    "sqlite",
    "database",
    "db",
    "sql",
    "calendar",
    "schedule",
    "todo",
    "task",
    "local",
    "offline",
    "memory"
  ]
}
```

## 📋 筛选标准说明

### 1. 结构化数据处理类 (Structured Data Ops)
**关键词:** json, csv, xml, yaml, markdown, table, parse, convert, transform, extract

**特点:**
- 输入输出都是纯文本或标准文件 (JSON/CSV/XML/Markdown)
- Docker 只需要 Python 或 Node 基础环境
- 评测：直接比对输出文件的行数、字段值或格式

### 2. 逻辑/规则验证类 (Logic & Rule Validation)
**关键词:** regex, regular expression, pattern, match, test, unit test, pytest, assert, verify, rule

**特点:**
- 测试模型推理能力，而非环境配置能力
- 评测：运行 pytest 或 grep，看返回码是否为 0

### 3. 模拟 API/Mock 协作类 (Mock API & Productivity)
**关键词:** mock, fake, simulate, stub, sqlite, database, db, sql, calendar, schedule

**特点:**
- 环境通过本地 Mock Server 实现
- 不依赖真实网络和账号
- 评测：检查数据库 (.db 文件) 或 Mock 服务状态变更

### 禁止的高依赖模式
- 需要 API 密钥/Token
- 需要登录/认证
- 需要浏览器自动化 (Selenium/Playwright)
- 需要容器编排 (Docker/K8s)
- 需要云服务 (AWS/GCP/Azure)
