# 示例条目

格式良好的条目示例，包含所有字段。

## 学习：纠正

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

## 学习：知识缺口（已解决）

```markdown
## [LRN-20260326-002] knowledge_gap

- Agent: agent1
- Logged: 2026-03-26T14:22:00+08:00
- Priority: medium
- Status: resolved
- Area: config

### 摘要
项目使用 pnpm 而不是 npm 进行包管理

### 详情
尝试运行 `npm install` 但项目使用 pnpm workspaces。锁文件是 `pnpm-lock.yaml`，而不是 `package-lock.json`。

### 建议行动
在假设 npm 之前检查 `pnpm-lock.yaml` 或 `pnpm-workspace.yaml`。为此项目使用 `pnpm install`。

### 元数据
- Source: error
- Related Files: pnpm-lock.yaml, pnpm-workspace.yaml
- Tags: package-manager, pnpm, setup

### 解决方案
- **Resolved**: 2026-03-26T14:30:00Z
- **Commit/PR**: N/A - 知识更新
- **Notes**: 已添加到 CLAUDE.md 以供将来参考

---
```

## 学习：提升到 SOUL.md

```markdown
## [LRN-20260326-003] best_practice

- Agent: agent1
- Logged: 2026-03-26T16:00:00+08:00
- Priority: high
- Status: promoted
- Promoted: SOUL.md
- Promoted-By: agent1
- Area: backend

### 摘要
API 响应必须包含请求头中的关联 ID

### 详情
所有 API 响应应该回传请求中的 X-Correlation-ID 头。这是分布式跟踪所必需的。没有此头的响应会破坏可观察性管道。

### 建议行动
始终在 API 处理程序中包含关联 ID 传递。

### 元数据
- Source: user_feedback
- Related Files: src/middleware/correlation.ts
- Tags: api, observability, tracing

---
```

## 学习：提升到 SOUL.md

```markdown
## [LRN-20260327-001] best_practice

- Agent: agent2
- Logged: 2026-03-27T09:00:00+08:00
- Priority: high
- Status: promoted
- Promoted: SOUL.md
- Promoted-By: agent2
- Area: backend

### 摘要
OpenAPI 规范更改后必须重新生成 API 客户端

### 详情
修改 API 端点时，必须重新生成 TypeScript 客户端。忘记这一点会导致仅在运行时出现的类型不匹配。生成脚本还运行验证。

### 建议行动
添加到 agent 工作流：任何 API 更改后，运行 `pnpm run generate:api`。

### 元数据
- Source: error
- Related Files: openapi.yaml, src/client/api.ts
- Tags: api, codegen, typescript

---
```

## 错误条目

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

## 错误条目：重复问题

```markdown
## [ERR-20260320-B2C] api_timeout

- Agent: agent2
- Logged: 2026-03-20T11:30:00+08:00
- Priority: critical
- Status: pending
- Area: backend

### 摘要
结账期间第三方支付 API 超时

### 错误
```
TimeoutError: Request to payments.example.com timed out after 30000ms
```

### 上下文
- 命令：POST /api/checkout
- 超时设置为 30s
- 在高峰时段（午餐、晚上）发生

### 建议修复
实现指数退避重试。考虑断路器模式。

### 元数据
- Reproducible: yes（高峰时段）
- Related Files: src/services/payment.ts
- See Also: ERR-20260315-X1Y, ERR-20260318-Z3W

---
```

## 功能需求

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

## 功能需求：已解决

```markdown
## [FEAT-20260310-002] dark_mode

- Agent: agent3
- Logged: 2026-03-10T14:00:00+08:00
- Priority: low
- Status: resolved
- Area: frontend

### 请求的能力
仪表板支持暗色模式

### 用户上下文
用户深夜工作，发现明亮的界面令人不适。其他几位用户也非正式地提到了这一点。

### 复杂度估算
medium

### 建议实现
使用 CSS 变量表示颜色。在用户设置中添加切换。考虑系统偏好检测。

### 元数据
- Frequency: recurring
- Related Features: user settings, theme system

### 解决方案
- **Resolved**: 2026-03-18T16:00:00Z
- **Commit/PR**: #142
- **Notes**: 实现了系统偏好检测和手动切换

---
```

## 学习：提升到技能

```markdown
## [LRN-20260318-001] best_practice

- Agent: agent1
- Logged: 2026-03-18T11:00:00+08:00
- Priority: high
- Status: promoted_to_skill
- Skill-Path: skills/docker-m1-fixes
- Area: infra

### 摘要
Docker 构建在 Apple Silicon 上因平台不匹配而失败

### 详情
在 M1/M2 Mac 上构建 Docker 镜像时，构建失败，因为基础镜像没有 ARM64 变体。这是影响许多开发人员的常见问题。

### 建议行动
将 `--platform linux/amd64` 添加到 docker build 命令，或在 Dockerfile 中使用 `FROM --platform=linux/amd64`。

### 元数据
- Source: error
- Related Files: Dockerfile
- Tags: docker, arm64, m1, apple-silicon
- See Also: ERR-20260315-A3F, ERR-20260317-B2D

---
```

## 提取的技能示例

当上述学习被提取为技能时，它变为：

**文件**：`skills/docker-m1-fixes/SKILL.md`

```markdown
---
name: docker-m1-fixes
description: "修复 Apple Silicon (M1/M2) 上的 Docker 构建失败。当 docker build 因平台不匹配错误失败时使用。"
---

# Docker M1 修复

Apple Silicon Mac 上的 Docker 构建问题解决方案。

## 快速参考

| 错误 | 修复 |
|------|------|
| `no match for platform linux/arm64` | 将 `--platform linux/amd64` 添加到构建 |
| 镜像运行但崩溃 | 使用仿真或查找 ARM 兼容的基础 |

## 问题

许多 Docker 基础镜像没有 ARM64 变体。在 Apple Silicon (M1/M2/M3) 上构建时，Docker 默认尝试拉取 ARM64 镜像，导致平台不匹配错误。

## 解决方案

### 选项 1：构建标志（推荐）

将平台标志添加到构建命令：

\`\`\`bash
docker build --platform linux/amd64 -t myapp .
\`\`\`

### 选项 2：Dockerfile 修改

在 FROM 指令中指定平台：

\`\`\`dockerfile
FROM --platform=linux/amd64 python:3.11-slim
\`\`\`

### 选项 3：Docker Compose

为服务添加平台：

\`\`\`yaml
services:
  app:
    platform: linux/amd64
    build: .
\`\`\`

## 权衡

| 方法 | 优点 | 缺点 |
|------|------|------|
| 构建标志 | 无文件更改 | 必须记住标志 |
| Dockerfile | 明确，版本化 | 影响所有构建 |
| Compose | 开发方便 | 需要 compose |

## 性能说明

在 ARM64 上运行 AMD64 镜像使用 Rosetta 2 仿真。这对开发有效，但可能较慢。对于生产，如果可能，请查找 ARM 原生替代方案。

## 来源

- 学习 ID：LRN-20260318-001
- 类别：best_practice
- 提取日期：2026-03-18
```
