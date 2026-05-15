# 记录格式说明

详细的记录格式说明和示例。

## 学习记录

### 格式

```markdown
## [LRN-YYYYMMDD-XXX] 类别

- Agent: <agent_id>
- Logged: 2026-03-26T10:00:00+08:00
- Priority: low|medium|high|critical
- Status: pending|in_progress|resolved|promoted|promoted:all|promoted_to_skill
- Promoted: SOUL.md  # 提升后添加
- Promoted-By: agent1, agent2  # 提升后添加，记录哪些 agent 已经提升
- Area: frontend|backend|infra|tests|docs|config

### 摘要
一句话描述

### 详情
完整上下文：发生了什么、什么是错的、什么是正确的

### 建议行动
具体的修复或改进

### 元数据
- Source: conversation|error|user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001（如果与现有条目相关）
- Pattern-Key: simplify.dead_code | harden.input_validation（可选，用于重复模式跟踪）
- Recurrence-Count: 1（可选）
- First-Seen: 2026-03-26（可选）
- Last-Seen: 2026-03-26（可选）

---
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| Agent | 触发记录的 agent 标识 | agent1, agent2, agent3 |
| Logged | ISO-8601 时间戳 | 2026-03-26T10:00:00+08:00 |
| Priority | 优先级 | low, medium, high, critical |
| Status | 状态 | pending, in_progress, resolved, promoted, promoted:all, promoted_to_skill |
| Promoted | 提升到的文件 | SOUL.md |
| Promoted-By | 已提升的 agent 列表 | agent1, agent2, agent3 |
| Area | 代码库区域 | frontend, backend, infra, tests, docs, config |
| Source | 来源 | conversation, error, user_feedback |
| Pattern-Key | 模式标识 | simplify.dead_code |
| Recurrence-Count | 重复次数 | 1, 2, 3... |
| First-Seen | 首次出现日期 | 2026-03-26 |
| Last-Seen | 最近出现日期 | 2026-03-26 |

### 示例

```markdown
## [LRN-20260326-001] correction

- Agent: agent1
- Logged: 2026-03-26T10:30:00+08:00
- Priority: high
- Status: pending
- Area: tests

### 摘要
错误地假设 pytest fixtures 默认为函数作用域

### 详情
编写测试 fixtures 时，我假设所有 fixtures 都是函数作用域的。用户纠正说虽然函数作用域是默认的，但代码库约定对数据库连接使用模块作用域的 fixtures 以提高测试性能。

### 建议行动
创建涉及昂贵设置（DB、网络）的 fixtures 时，在默认为函数作用域之前检查现有 fixtures 的作用域模式。

### 元数据
- Source: user_feedback
- Related Files: tests/conftest.py
- Tags: pytest, testing, fixtures

---
```

## 错误记录

### 格式

```markdown
## [ERR-YYYYMMDD-XXX] 技能或命令名称

- Agent: <agent_id>
- Logged: 2026-03-26T10:00:00+08:00
- Priority: high
- Status: pending
- Area: frontend|backend|infra|tests|docs|config

### 摘要
简要描述失败内容

### 错误
```
实际错误消息或输出
```

### 上下文
- 尝试的命令/操作
- 使用的输入或参数
- 相关的环境细节

### 建议修复
如果可识别，可能解决此问题

### 元数据
- Reproducible: yes|no|unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001（如果重复）

---
```

### 示例

```markdown
## [ERR-20260326-A3F] docker_build

- Agent: agent1
- Logged: 2026-03-26T09:15:00+08:00
- Priority: high
- Status: pending
- Area: infra

### 摘要
Docker 构建在 M1 Mac 上因平台不匹配而失败

### 错误
```
error: failed to solve: python:3.11-slim: no match for platform linux/arm64
```

### 上下文
- 命令：`docker build -t myapp .`
- Dockerfile 使用 `FROM python:3.11-slim`
- 在 Apple Silicon (M1/M2) 上运行

### 建议修复
添加平台标志：`docker build --platform linux/amd64 -t myapp .`
或更新 Dockerfile：`FROM --platform=linux/amd64 python:3.11-slim`

### 元数据
- Reproducible: yes
- Related Files: Dockerfile

---
```

## 功能需求

### 格式

```markdown
## [FEAT-YYYYMMDD-XXX] 功能名称

- Agent: <agent_id>
- Logged: 2026-03-26T10:00:00+08:00
- Priority: medium
- Status: pending
- Area: frontend|backend|infra|tests|docs|config

### 请求的能力
用户想要做什么

### 用户上下文
为什么需要，解决什么问题

### 复杂度估算
simple|medium|complex

### 建议实现
如何构建，可能扩展什么

### 元数据
- Frequency: first_time|recurring
- Related Features: existing_feature_name

---
```

### 示例

```markdown
## [FEAT-20260326-001] export_to_csv

- Agent: agent1
- Logged: 2026-03-26T16:45:00+08:00
- Priority: medium
- Status: pending
- Area: backend

### 请求的能力
导出分析结果为 CSV 格式

### 用户上下文
用户运行每周报告，需要与非技术利益相关者在 Excel 中共享结果。目前手动复制输出。

### 复杂度估算
simple

### 建议实现
为 analyze 命令添加 `--output csv` 标志。使用标准 csv 模块。可以扩展现有的 `--output json` 模式。

### 元数据
- Frequency: recurring
- Related Features: analyze command, json output

---
```

## ID 生成

格式：`TYPE-YYYYMMDD-XXX`
- TYPE: `LRN`（学习）、`ERR`（错误）、`FEAT`（功能）
- YYYYMMDD: 当前日期
- XXX: 序号或随机 3 个字符（例如：`001`、`A7B`）

示例：`LRN-20260326-001`、`ERR-20260326-A3F`、`FEAT-20260326-002`

## 解决条目

当问题被修复时，更新条目：

1. 更改 `**Status**: pending` → `**Status**: resolved`
2. 在元数据后添加解决块：

```markdown
### 解决方案
- **Resolved**: 2026-03-27T09:00:00Z
- **Commit/PR**: abc123 或 #42
- **Notes**: 简要描述做了什么
```

## 提升条目

当条目被提升到 SOUL.md 时，更新条目：

1. 更改 `**Status**: pending` → `**Status**: promoted`
2. 添加 `**Promoted**: SOUL.md`
3. 添加 `**Promoted-By**: <agent_id>`（记录哪些 agent 已经提升）

**多 agent 场景：**

当多个 agent 都提升同一个条目时：
- 每个 agent 提升后，将自己的 ID 添加到 `Promoted-By`
- 当所有 agent 都提升后，Status 改为 `promoted:all`

**示例：**

```markdown
## [LRN-20260326-001] best_practice

- Agent: agent1
- Logged: 2026-03-26T10:00:00+08:00
- Priority: high
- Status: promoted
- Promoted: SOUL.md
- Promoted-By: agent1, agent2  # agent1 和 agent2 都已提升
- Area: backend

### 摘要
...
```

其他状态值：
- `in_progress` - 正在积极处理
- `wont_fix` - 决定不处理（在解决说明中添加原因）
- `promoted` - 已提升到 SOUL.md（部分 agent）
- `promoted:all` - 已提升到 SOUL.md（所有 agent）
- `promoted_to_skill` - 提取为可重用技能
