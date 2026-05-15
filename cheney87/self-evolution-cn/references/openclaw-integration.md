# OpenClaw 集成

将 self-evolution-cn 技能与 OpenClaw 集成的完整设置和使用指南。

## 概述

OpenClaw 使用基于工作区的提示注入结合事件驱动的 hook。上下文在会话开始时从工作区文件注入，hook 可以在生命周期事件上触发。

## 工作区结构

```
~/.openclaw/
├── workspace-agent1/               # 主工作区
│   ├── AGENTS.md               # 多代理协调模式
│   ├── SOUL.md                 # 行为准则和个性
│   ├── TOOLS.md                # 工具能力和注意事项
│   ├── MEMORY.md               # 长期记忆（仅主会话）
│   ├── .learnings/             # 学习记录目录（软链接）
│   │   ├── ERRORS.md
│   │   ├── LEARNINGS.md
│   │   └── FEATURE_REQUESTS.md
│   └── memory/                 # 每日记忆文件
│       └── YYYY-MM-DD.md
├── workspace-agent2/               # 其他工作区
│   ├── .learnings/             # 学习记录目录（软链接或独立）
│   └── ...
├── shared-learning/           # 共享学习目录
│   ├── ERRORS.md
│   ├── LEARNINGS.md
│   └── FEATURE_REQUESTS.md
├── skills/                     # 已安装的技能
│   └── self-evolution-cn/
│       ├── SKILL.md
│       ├── .learnings/
│       ├── scripts/
│       ├── hooks/
│       ├── logs/              # 执行日志
│       ├── heartbeat-state.json  # 执行状态
│       └── references/
└── hooks/                      # 自定义 hook
    └── self-evolution-cn/
        ├── HOOK.md
        └── handler.js
```

## 快速设置

详见 `SKILL.md` 快速开始部分。

## 学习工作流

### 捕获学习

1. **会话内**：按常规记录到 `.learnings/`
2. **跨会话**：提升到工作区文件

### 提升决策树

```
学习是否项目特定？
├── 是 → 保留在 .learnings/
└── 否 → 提升到 SOUL.md（所有 agent 都会加载）
```

详见 `references/promotion.md`

## 跨 Agent 通信

OpenClaw 提供跨会话通信的工具：

### sessions_list

查看活动和最近的会话：
```
sessions_list(activeMinutes=30, messageLimit=3)
```

### sessions_history

从另一个会话读取记录：
```
sessions_history(sessionKey="session-id", limit=50)
```

### sessions_send

向另一个会话发送消息：
```
sessions_send(sessionKey="session-id", message="学习：API 需要 X-Custom-Header")
```

### sessions_spawn

生成后台子代理：
```
sessions_spawn(task="研究 X 并报告", label="research")
```

## 可用的 Hook 事件

| 事件 | 何时触发 |
|------|---------|
| `agent:bootstrap` | 在工作区文件注入之前 |
| `message:received` | 收到用户消息时 |
| `tool:after` | 工具执行之后 |

## 检测触发器

### 标准触发器
- 用户纠正（"No, that's wrong..."）
- 命令失败（非零退出码）
- API 错误
- 知识缺口

### OpenClaw 特定触发器

| 触发器 | 操作 |
|---------|------|
| 工具调用错误 | 使用工具名称记录到 TOOLS.md |
| 会话交接混乱 | 使用委托模式记录到 AGENTS.md |
| 模型行为意外 | 使用预期 vs 实际记录到 SOUL.md |
| 技能问题 | 记录到 .learnings/ 或向上游报告 |

## 多 Agent 支持

### 共享学习目录

所有 agent 共享学习目录，学习记录存储在共享目录中。

### 统计逻辑

按 `Pattern-Key` 累计所有 agent 的 `Recurrence-Count`，累计次数 >= 3 时自动提升到 SOUL.md。

详见 `references/multi-agent.md`

## 验证

检查 hook 是否已注册：

```bash
openclaw hooks list
```

检查技能是否已加载：

```bash
openclaw status
```

## 故障排除

### Hook 未触发

1. 确保在配置中启用了 hook
2. 配置更改后重启 gateway
3. 检查 gateway 日志是否有错误

### 学习未持久化

1. 验证 `.learnings/` 目录存在
2. 检查文件权限
3. 确保工作区路径配置正确

### 技能未加载

1. 检查技能在 skills 目录中
2. 验证 SKILL.md 有正确的前置内容
3. 运行 `openclaw status` 查看已加载的技能

### Cron 任务未运行

1. 检查 crontab：`crontab -l`
2. 检查日志文件：`cat ~/.openclaw/skills/self-evolution-cn/logs/heartbeat-daily.log`
3. 手动运行脚本：`bash scripts/trigger-daily-review.sh`

### 软链接问题

1. 检查软链接：`ls -la ~/.openclaw/workspace-agent1/.learnings`
2. 检查共享目录：`ls -la $SHARED_LEARNING_DIR`
3. 重新运行配置脚本：`./scripts/setup.sh`

## 环境变量

详见 `references/multi-agent.md`

## 执行状态和日志

详见 `references/multi-agent.md`

## Cron 任务

### 查看当前 Cron 任务

```bash
crontab -l | grep trigger-daily-review
```

### 手动触发检查

```bash
bash ~/.openclaw/skills/self-evolution-cn/scripts/daily_review.sh
```

### 查看执行日志

```bash
tail -f ~/.openclaw/skills/self-evolution-cn/logs/heartbeat-daily.log
```

## 技能提取

### 从学习创建技能

```bash
./scripts/extract-skill.sh skill-name
```

### 干运行

```bash
./scripts/extract-skill.sh skill-name --dry-run
```

### 模板

参考 `assets/SKILL-TEMPLATE.md` 获取技能模板。

## 高级用法

### 自定义 Hook 事件

编辑 `hooks/openclaw/handler.js` 以支持其他事件。

### 自定义触发器

编辑 `hooks/openclaw/handler.js` 以添加自定义触发器。

### 自定义记录格式

编辑 `references/format.md` 以自定义记录格式。

## 最佳实践

1. **定期检查**：每天运行日检查以识别重复模式
2. **及时提升**：当学习被证明时立即提升
3. **保持简洁**：保持学习记录简洁，只包含必要信息
4. **使用模板**：使用提供的模板确保一致性
5. **测试技能**：在发布前测试提取的技能

## 相关文档

- `SKILL.md` - 主要文档
- `references/format.md` - 记录格式说明
- `references/promotion.md` - 提升机制说明
- `references/multi-agent.md` - 多 agent 支持说明
- `references/hooks-setup.md` - Hook 配置指南
- `assets/SKILL-TEMPLATE.md` - 技能模板
- `assets/LEARNINGS.md` - 学习记录模板
