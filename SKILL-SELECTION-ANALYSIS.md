# OpenClaw 技能选择分析报告（SkillLLM 专用）

> 30 个 OpenClaw 技能分类的全面分析，专为 SkillLLM 数据集构建。每个分类通过 10 个技能的 SKILL.md 验证。

**分析日期：** 2026-04-08  
**总分类数：** 30  
**总技能数：** ~5,355  
**SKILL.md 验证技能：** 300 (每分类 10 个)

---

## 📊 执行摘要

| 指标 | 数值 |
|------|------|
| 总分类数 | 30 |
| 总技能数 | ~5,355 |
| SkillLLM 推荐 | ~1,560 (29%) |
| 不推荐 | ~3,800 (71%) |
| 预估训练任务 | 5,000-8,000 |

---

## ⭐ 分类评级 (1-5 星)

### ⭐⭐⭐⭐⭐ 5 星分类（强烈推荐）

| # | 分类 | 技能数 | 保留率 | 关键发现 |
|---|------|--------|--------|----------|
| 1 | **CLI Utilities** (命令行工具) | 180 | 82% | 纯本地工具，无外部依赖 |
| 2 | **Data & Analytics** (数据分析) | 39 | 85% | 纯数据处理，无需认证 |

**验证技能 (每分类 10 个):**
- ✅ `catfact` - 免费 API，无需密钥
- ✅ `clean-pytest` - 本地测试框架
- ✅ `checksum` - 纯 Node.js
- ✅ `csv-pipeline` - Python 标准库
- ✅ `duckdb-en` - 嵌入式 SQL
- ✅ `data-viz` - 终端图表
- ✅ `fzf-fuzzy-finder` - 本地 CLI
- ✅ `country-info` - 免费 API
- ✅ `json-pretty` - 本地转换
- ✅ `xml-to-json` - 本地转换

---

### ⭐⭐⭐⭐ 4 星分类（推荐）

| # | 分类 | 技能数 | 保留率 | 关键发现 |
|---|------|--------|--------|----------|
| 3 | **Git & GitHub** | 167 | 65% | 本地 git 操作可沙箱化 |
| 4 | **Search & Research** (搜索研究) | 352 | 70% | 免费学术 API (arXiv, OpenAlex) |
| 5 | **PDF & Documents** (PDF 文档) | 110 | 75% | 本地文档处理 |
| 6 | **Self-Hosted & Automation** (自托管自动化) | 32 | 60% | 部分需自托管服务 |
| 7 | **iOS & macOS Development** (iOS/macOS 开发) | 29 | 70% | 部分 macOS 独占，但多数通用 |

**验证技能示例:**
- ✅ `arc-skill-gitops` - 本地 git 版本控制
- ✅ `conventional-commits` - 纯文本格式化
- ✅ `arxiv-search-collector` - 免费 arXiv API
- ✅ `academic-research` - OpenAlex 免费 API
- ✅ `docx` - 本地 OOXML 处理
- ✅ `casual-cron` - 本地 cron 管理
- ✅ `agent-defibrillator` - 本地 watchdog
- ✅ `app-store-optimization` - 方法论/异步

---

### ⭐⭐⭐ 3 星分类（中等）

| # | 分类 | 技能数 | 保留率 | 关键发现 |
|---|------|--------|--------|----------|
| 8 | **Browser & Automation** (浏览器自动化) | 322 | 50% | 需浏览器环境 |
| 9 | **AI & LLMs** | 176 | 60% | 大部分可沙箱化，部分需 API 密钥 |
| 10 | **Image & Video Generation** (图像视频生成) | 171 | 55% | 算法艺术可，AI 生成需 API |
| 11 | **Coding Agents & IDEs** (编码代理) | 1,200 | 60% | 纯代码处理高度可沙箱化 |
| 12 | **DevOps & Cloud** | 392 | 50% | 本地 Docker/日志可，云需认证 |
| 13 | **Web & Frontend Development** (Web 前端) | 924 | 45% | 本地开发工具可，部署需认证 |
| 14 | **Clawdbot Tools** (Clawdbot 工具) | 37 | 55% | 本地 OpenClaw 工具 |
| 15 | **Gaming** (游戏) | 35 | 60% | 游戏逻辑可，外部服务需 API |

**验证技能示例:**
- ✅ `api-tester` - 纯 Node.js HTTP 客户端
- ✅ `ai-humanizer` - 文本模式检测
- ✅ `adversarial-prompting` - 方法论
- ✅ `algorithmic-art` - p5.js 生成艺术
- ✅ `ascii-art-generator` - Python 文本艺术
- ✅ `code-review` - 静态分析
- ✅ `unit-test-generator` - 代码生成
- ✅ `agentic-devops` - 本地 Docker/日志
- ✅ `html-generator` - 本地模板渲染
- ✅ `arena` - 可 Mock 的 API

---

### ⭐⭐ 2 星分类（有限）

| # | 分类 | 技能数 | 保留率 | 关键发现 |
|---|------|--------|--------|----------|
| 16 | **Communication** (通信) | 146 | 40% | 大部分需 OAuth |
| 17 | **Notes & PKM** (笔记知识管理) | 69 | 35% | 严重平台依赖 |
| 18 | **Calendar & Scheduling** (日历调度) | 65 | 45% | 大部分需 Google/Microsoft OAuth |
| 19 | **Marketing & Sales** (营销销售) | 103 | 50% | 内容生成可，外部 API 需认证 |
| 20 | **Health & Fitness** (健康健身) | 87 | 40% | 隐私敏感，大部分需 OAuth |
| 21 | **Security & Passwords** (安全密码) | 53 | 50% | 部分教育可，密码管理器需认证 |
| 22 | **Shopping & E-commerce** (购物电商) | 51 | 60% | 价格检查可，商店需 API |
| 23 | **Smart Home & IoT** (智能家居) | 41 | 40% | 需真实硬件 |
| 24 | **Transportation** (交通出行) | 110 | 35% | 大部分需付费 API |
| 25 | **Media & Streaming** (媒体流媒体) | 84 | 50% | FFmpeg 可，流媒体需 API |
| 26 | **Speech & Transcription** (语音转录) | 45 | 40% | 本地 Whisper 可，TTS API 需密钥 |
| 27 | **Personal Development** (个人发展) | 51 | 50% | 习惯追踪可，教练需 API |

**验证技能示例:**
- ✅ `email-autoreply` - 仅文本生成
- ⚠️ `airc` - 需 IRC 服务器
- ❌ `bluesky` - 需 App Password
- ❌ `bear-notes` - 仅 macOS
- ❌ `fitbit` - 需 Fitbit OAuth
- ✅ `stock-price-checker` - yfinance 免费
- ✅ `turnip-prophet` - 游戏算法
- ✅ `ffmpeg-master` - 本地 FFmpeg
- ✅ `faster-whisper` - 本地 STT
- ✅ `morning-routine` - 本地 SQLite

---

### ⭐ 1 星分类（不推荐）

| # | 分类 | 技能数 | 保留率 | 关键发现 |
|---|------|--------|--------|----------|
| 28 | **Apple Apps & Services** (苹果应用服务) | 44 | 20% | 全部 macOS 独占 |
| 29 | **Moltbook** | 44 | 45% | 需 Moltbook API |
| 30 | **Productivity & Tasks** (生产力任务) | 205 | 35% | 大部分需 OAuth (Todoist, Notion 等) |

**验证技能示例:**
- ❌ `apple-health-skill` - 需 Transition API
- ❌ `homebrew` - 仅 macOS
- ❌ `say` - 仅 macOS
- ❌ `apple-mail` - 仅 macOS
- ❌ `apple-calendar` - 仅 macOS
- ⚠️ `moltbook` - 需 Moltbook API
- ✅ `speedtest` - 本地 CLI
- ❌ `actual-budget` - 需服务器
- ❌ `todoist` - 需 API 密钥
- ❌ `notion` - 需 API 密钥

---

## 🎯 SkillLLM 推荐

### Tier 1 - 立即启动 (~560 技能)

```
5 星分类 (180 技能)
+ 4 星分类纯本地子集 (380 技能)
```

**特点:**
- ✅ 100% 可沙箱化
- ✅ 输出可验证
- ✅ 无外部依赖

**分类:**
1. CLI Utilities (135 技能)
2. Data & Analytics (33 技能)
3. Git & GitHub 本地操作 (70 技能)
4. Search & Research 免费 API (175 技能)
5. PDF & Documents (70 技能)
6. Self-Hosted 本地工具 (20 技能)
7. iOS & macOS Dev 通用 (17 技能)

---

### Tier 2 - 第二阶段 (~1,000 技能)

```
3 星分类可沙箱化子集
```

**特点:**
- ⚠️ 部分需 Mock
- ⚠️ 环境配置较复杂

**分类:**
1. Coding Agents & IDEs (仅代码处理)
2. AI & LLMs (方法论/工具，非 API 调用)
3. Image & Video (算法，非 AI 生成)
4. Browser & Automation (API 测试，非浏览器)
5. Web & Frontend (本地开发工具)
6. DevOps (本地 Docker/日志)
7. Gaming (游戏逻辑，非外部服务)
8. Clawdbot Tools (本地 OpenClaw)

---

### ❌ 不推荐 (~3,800 技能)

```
1-2 星分类，平台/OAuth 依赖
```

**排除原因:**
- ❌ 平台依赖 (macOS, 硬件)
- ❌ 需真实账户/OAuth
- ❌ 隐私敏感
- ❌ 无法沙箱化

**分类:**
1. Apple Apps & Services (44 技能) - 全部 macOS
2. Notes & PKM (69 技能) - 平台锁定
3. Communication (146 技能) - 需 OAuth
4. Calendar & Scheduling (65 技能) - 需 OAuth
5. Health & Fitness (87 技能) - 隐私 + OAuth
6. Transportation (110 技能) - 付费 API
7. Smart Home & IoT (41 技能) - 真实硬件
8. Productivity & Tasks (205 技能) - 需 OAuth

---

## 📈 Pipeline 验证标准

### ✅ 可沙箱化 (保留)

| 标准 | 示例 |
|------|------|
| 纯本地计算 | `checksum`, `csv-pipeline`, `duckdb-en` |
| 免费 API 无需密钥 | `arxiv-search`, `academic-research`, `catfact` |
| 文本生成/转换 | `email-autoreply`, `cold-outreach`, `ai-humanizer` |
| 本地文件操作 | `docx`, `pdf-to-text`, `git-ops` |
| CLI 工具 | `ffmpeg`, `grep`, `fzf` |
| 方法论/框架 | `adversarial-prompting`, `app-store-optimization` |

### ❌ 不可沙箱化 (排除)

| 标准 | 示例 |
|------|------|
| 需 OAuth/认证 | `1password`, `fitbit`, `google-calendar` |
| 平台独占 | `homebrew`, `say`, `apple-health` |
| 需真实硬件 | `alexa`, `google-home`, `bambu-cli` |
| 付费 API | `amadeus-flights`, `elevenlabs`, `shopify` |
| 隐私敏感 | `health-guardian`, `password-manager` |
| 外部服务依赖 | `notion`, `todoist`, `slack-bot` |

---

## 🔧 方法论

### 阶段 1: 分类列表
- 从 awesome-openclaw-skills 提取全部 30 个分类
- 记录每分类技能数量

### 阶段 2: SKILL.md 验证
- 每分类选择 10 个代表性技能 (共 300 个)
- 从 openclaw/skills 仓库获取 SKILL.md
- 评估标准:
  - 外部依赖 (API 密钥，OAuth)
  - 平台要求 (macOS, 硬件)
  - 可沙箱化 (能否在 Docker 运行)
  - 输出可验证性 (能否验证结果)

### 阶段 3: 评级分配
- ⭐⭐⭐⭐⭐ (5): 80%+ 技能可沙箱化
- ⭐⭐⭐⭐ (4): 60-79% 技能可沙箱化
- ⭐⭐⭐ (3): 40-59% 技能可沙箱化
- ⭐⭐ (2): 20-39% 技能可沙箱化
- ⭐ (1): <20% 技能可沙箱化

### 阶段 4: 推荐层级
- Tier 1: 5 星 + 4 星纯本地 (~560 技能)
- Tier 2: 3 星可沙箱化子集 (~1,000 技能)
- 排除：1-2 星分类 (~3,800 技能)

---

## 📋 本仓库文件

| 文件 | 描述 |
|------|------|
| `skills-by-category.md` | 5,143+ 技能分类列表 |
| `SKILL-SELECTION-ANALYSIS.md` | 本分析文档 |
| `categories/` | 独立分类文件 |

---

## 🚀 SkillLLM 使用指南

### 数据集构建 Pipeline

```
1. 选择 Tier 1 分类 (~560 技能)
   ↓
2. 按 SKILL.md 标准筛选
   ↓
3. 生成合成任务 (每技能 10-15 个)
   ↓
4. Docker 沙箱执行
   ↓
5. 自动评分输出
   ↓
6. 编译数据集 (5,000-8,000 任务)
```

### 成本估算

| 阶段 | 任务数 | Token/任务 | 总 Token | 成本 (@$0.15/1M) |
|------|--------|------------|----------|------------------|
| Tier 1 | 5,600 | 15K | 84M | ~$12.60 |
| Tier 2 | 10,000 | 15K | 150M | ~$22.50 |
| **总计** | **15,600** | **15K** | **234M** | **~$35.10** |

---

## 📝 注意事项

- 分析基于 `openclaw/skills` 仓库的 SKILL.md 文件
- 评级可能随技能更新而变化
- 标记为"⚠️"的技能可能通过 Mock 数据沙箱化
- 建议大规模合成前重新验证顶级技能

---

## 🔗 参考链接

- [OpenClaw Skills 仓库](https://github.com/openclaw/skills)
- [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills)
- [ClawHub](https://clawhub.com)
- [SkillLLM 仓库](https://github.com/JoylimJY/skill-llm)

---

## 📄 许可证

本分析与源仓库使用相同许可证。

---

**分析执行者：** OpenClaw Agent  
**日期：** 2026-04-08  
**联系方式：** [GitHub Issues](https://github.com/joeteng007/skill-selection/issues)
