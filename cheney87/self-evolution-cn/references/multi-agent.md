# 多 Agent 支持说明

如何配置和使用多 agent 共享学习。

## 概述

Self-Evolution-CN 支持多个 agent 共享学习目录，所有 agent 的学习记录将存储在共享目录中，并按 `Pattern-Key` 累计 `Recurrence-Count`。

## 共享目录结构

```
/root/.openclaw/shared-learning/  # 共享目录
├── ERRORS.md                   # 所有 agent 共享
├── LEARNINGS.md                # 所有 agent 共享
├── FEATURE_REQUESTS.md         # 所有 agent 共享

/root/.openclaw/workspace-agent1/.learnings  # 软链接 → 共享目录
/root/.openclaw/workspace-agent2/.learnings  # 软链接 → 共享目录
/root/.openclaw/workspace-agent3/.learnings  # 软链接 → 共享目录
/root/.openclaw/workspace-agent4/.learnings  # 独立目录（可选）
```

## 配置

详见 `SKILL.md` 快速开始部分。

## Agent 字段

记录是哪个 agent 触发的（如 `agent1`、`agent2`、`agent3`）。

```markdown
- Agent: <agent_id>
```

## 统计逻辑

### 按 Pattern-Key 累计

所有 agent 的记录按 `Pattern-Key` 累计 `Recurrence-Count`。

### 示例

```markdown
## [ERR-20260326-001] git_push_without_pull
- Agent: agent1
- Pattern-Key: git.push.without.pull
- Recurrence-Count: 1

## [ERR-20260327-001] git_push_without_pull
- Agent: agent2
- Pattern-Key: git.push.without.pull
- Recurrence-Count: 1

## [ERR-20260328-001] git_push_without_pull
- Agent: agent3
- Pattern-Key: git.push.without.pull
- Recurrence-Count: 1
```

统计结果：
- `git.push.without.pull` 累计次数：3
- 触发自动提升到 SOUL.md

## 提升判断

### 不区分 Agent

提升到 SOUL.md 时不区分 agent，只看累计次数。

### 规则

- 累计次数 >= 3 时自动提升到 SOUL.md
- Agent 字段仅用于追溯，不影响提升判断

## 脚本支持

### daily_review.sh

支持多 agent 统计的日检查脚本。

```bash
# 每日检查
./scripts/daily_review.sh

# 每周检查
DURATION=7 ./scripts/daily_review.sh

# 每月检查
DURATION=30 ./scripts/daily_review.sh
```

### trigger-daily-review.sh

Cron 触发脚本，每日 00:00 自动执行。

```bash
# 添加到 crontab
0 0 * * * /path/to/scripts/trigger-daily-review.sh
```

## Hook 集成

### 多 Agent 模式

Hook 在 agent 启动时注入提醒，支持多 agent 共享学习目录。

### 自动识别

Hook 会自动识别以下情况并记录：

- 用户纠正（"不对"、"错了"等）
- 命令失败（非零退出码）
- 知识缺口（用户提供新信息）
- 发现更好的方法

### 启用 Hook

```bash
openclaw hooks enable self-evolution-cn
```

## 环境变量

### SHARED_LEARNING_DIR

指定共享学习目录路径。

```bash
export SHARED_LEARNING_DIR="/root/.openclaw/shared-learning"
```

### SHARED_AGENTS

指定需要共享学习目录的 agent 列表（空格分隔）。

```bash
export SHARED_AGENTS="agent1 agent2 agent3"
```

**默认值：** `agent1`（只为主 agent 创建软链接）

### AGENT_ID

指定当前 agent ID（用于日志和状态记录）。

```bash
export AGENT_ID="agent1"
```

### OPENCLAW_DIR

指定 OpenClaw 安装目录。

```bash
export OPENCLAW_DIR="/root/.openclaw"
```

## 执行状态和日志

### 状态文件

**位置**：`~/.openclaw/skills/self-evolution-cn/heartbeat-state.json`

**内容（多 agent）：**
```json
{
  "agents": {
    "agent1": {
      "last_execution_date": "2026-03-26",
      "last_execution_time": "2026-03-26T00:20:00+08:00",
      "status": "completed"
    },
    "agent2": {
      "last_execution_date": "2026-03-26",
      "last_execution_time": "2026-03-26T01:00:00+08:00",
      "status": "completed"
    }
  }
}
```

### 日志文件

**位置**：`~/.openclaw/skills/self-evolution-cn/logs/heartbeat-daily.log`

**内容（多 agent）：**
```
=== Self-Evolution-CN Daily Review (All Agents): 2026-03-26 00:20:00 ===
找到 4 个 agent: agent1 agent2 agent3 agent4

--- Processing agent: agent1 ---
执行日检查...
...

--- Processing agent: agent2 ---
执行日检查...
...
```

### 查看 Agent 状态

**查看所有 agent 状态：**
```bash
cat ~/.openclaw/skills/self-evolution-cn/heartbeat-state.json
```

**查看特定 agent 状态：**
```bash
jq '.agents.agent1' ~/.openclaw/skills/self-evolution-cn/heartbeat-state.json
```

**查看特定 agent 日志：**
```bash
grep 'Processing agent: agent1' ~/.openclaw/skills/self-evolution-cn/logs/heartbeat-daily.log
```
