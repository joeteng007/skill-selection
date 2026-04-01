# Skill 筛选报告（易闭环、低依赖、状态可判别）

**生成时间:** 2026-04-01 13:03:58

## 📊 总览

| 指标 | 数值 |
|------|------|
| 总技能数 | 755 |
| 通过数量 | 49 |
| 通过率 | 6.5% |

## 📈 分类统计

| 类别 | 数量 | 占比 |
|------|------|------|
| 结构化数据处理 | 9 | 1.2% |
| 逻辑/规则验证 | 20 | 2.6% |
| 模拟 API/Mock | 20 | 2.6% |

## ❌ 失败原因分析

| 原因 | 数量 |
|------|------|
| Stars 不足 | 156 |
| 内容太短 | 72 |

## 🏆 Top 20 高置信度技能

| 排名 | 名称 | 类别 | 置信度 | Stars | 语言 | 依赖数 |
|------|------|------|--------|-------|------|--------|
| 1 | trailofbits/semgrep-rule-creator | logic_validation | 0.50 | 4173 | None | 0 |
| 2 | trailofbits/semgrep-rule-variant-creator | logic_validation | 0.50 | 4173 | None | 0 |
| 3 | anthropics/webapp-testing | logic_validation | 0.38 | 107721 | None | 0 |
| 4 | trailofbits/property-based-testing | logic_validation | 0.38 | 4173 | None | 0 |
| 5 | trailofbits/testing-handbook-skills | logic_validation | 0.38 | 4173 | None | 0 |
| 6 | microsoft/azure-data-tables-java | structured_data | 0.38 | 1911 | None | 0 |
| 7 | microsoft/azure-data-tables-py | structured_data | 0.38 | 1911 | None | 0 |
| 8 | microsoft/azure-microsoft-playwright-testing-ts | logic_validation | 0.38 | 1911 | None | 0 |
| 9 | coreyhaines31/ab-test-setup | logic_validation | 0.38 | 17980 | None | 0 |
| 10 | phuryn/ab-test-analysis | logic_validation | 0.38 | 9057 | None | 0 |
| 11 | phuryn/test-scenarios | logic_validation | 0.38 | 9057 | None | 0 |
| 12 | firecrawl/firecrawl-search | logic_validation | 0.25 | 237 | None | 0 |
| 13 | neondatabase/neon-postgres | mock_api | 0.25 | 43 | None | 0 |
| 14 | neondatabase/claimable-postgres | mock_api | 0.25 | 43 | None | 0 |
| 15 | neondatabase/neon-postgres-egress-optimizer | mock_api | 0.25 | 43 | None | 0 |
| 16 | vercel-labs/composition-patterns | logic_validation | 0.25 | 24194 | None | 0 |
| 17 | googleworkspace/gws-calendar | mock_api | 0.25 | 23388 | None | 0 |
| 18 | googleworkspace/gws-tasks | mock_api | 0.25 | 23388 | None | 0 |
| 19 | huggingface/transformers.js | structured_data | 0.25 | 9993 | None | 0 |
| 20 | trailofbits/burpsuite-project-parser | structured_data | 0.25 | 4173 | None | 0 |

## 🔧 筛选配置

```json
{
  "min_stars": 20,
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
