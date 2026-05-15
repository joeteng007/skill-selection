# 提升机制说明

如何将学习提升到项目记忆。

## 何时提升

当学习广泛适用（不是一次性修复）时，将其提升到永久项目记忆。

### 提升条件

- 学习适用于多个文件/功能
- 任何贡献者（人类或 AI）都应该知道的知识
- 防止重复错误
- 记录项目特定的约定

## 提升目标

| 目标 | 适合什么 |
|--------|---------|
| `SOUL.md` | 行为准则、沟通风格、原则、工作流、工具使用（所有 agent 都会加载） |
| `skills/<skill-name>/SKILL.md` | 可重用技能 |

## 如何提升

### 1. 提炼

将学习提炼为简洁的规则或事实。

### 2. 添加

添加到目标文件的适当部分（如果需要则创建文件）。

### 3. 更新

更新原始条目：
- 更改 `**Status**: pending` → `**Status**: promoted`
- 添加 `**Promoted**: SOUL.md`
- 添加 `**Promoted-By**: <agent_id>`（记录哪些 agent 已经提升）

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

## 提升示例

详见 `references/examples.md`

## 自动提升规则

### 规则 A：重复 >= 3 次（自动）

**触发条件（每日检查时自动应用）：**
- 统计所有 agent 的记录
- 按 `Pattern-Key` 累计 `Recurrence-Count`
- 累计次数 >= 3 时触发提升

**示例：**
```markdown
## [ERR-20260319-001] 模式

### 元数据
- Recurrence-Count: 3  # ← 累计所有 agent 的次数
- Pattern-Key: git.push.without.pull
- First-Seen: 2026-03-01
- Last-Seen: 2026-03-19
```

**自动操作：**
1. 创建规则写入 `SOUL.md`：
   ```markdown
   ## Git 操作规范
   ### 推送前
   - **必须先拉取**：`git pull` 或 `git fetch && git rebase`
   - 避免冲突，避免推送失败

   来源：ERRORS.md [ERR-20260319-001]（重复 3 次）
   ```

2. 更新原始记录：
   ```markdown
   **Status**: promoted
   **Promoted**: SOUL.md
   **Promoted-By**: agent1  # 记录提升的 agent
   ```

**重要说明：**
- ✅ 不区分 agent，所有 agent 的记录合并统计
- ✅ 按 `Pattern-Key` 累计 `Recurrence-Count`
- ✅ Agent 字段仅用于追溯，不影响提升判断

### 规则 B：高优先级（自动）

**触发条件：**
```markdown
### 元数据
- Priority: critical
```

**自动操作：**
1. 立即提升到 SOUL.md
2. 标记为 `promoted`
3. 添加 `Promoted-By: <agent_id>`

### 规则 C：工作流/工具问题（自动）

**触发条件：**
```markdown
### 元数据
- Priority: high
- Area: infra | config | tools
```

**自动操作：**
1. 提升到 SOUL.md
2. 标记为 `promoted`
3. 添加 `Promoted-By: <agent_id>`

## 多 Agent 统计

### 统计逻辑

- 按 `Pattern-Key` 累计所有 agent 的 `Recurrence-Count`
- 累计次数 >= 3 时自动提升到 SOUL.md
- 不区分 agent，只看累计次数

### 示例

假设有以下记录：

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

## 提升决策树

```
学习是否项目特定？
├── 是 → 保留在 .learnings/
└── 否 → 提升到 SOUL.md（所有 agent 都会加载）
```
