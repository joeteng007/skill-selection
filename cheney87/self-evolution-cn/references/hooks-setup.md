# Hook 配置指南

为 AI 编码代理配置自动自我改进触发器。

## 概述

Hook 通过在关键时刻注入提醒来启用主动学习捕获：
- **UserPromptSubmit**：每次提示后提醒评估学习
- **PostToolUse (Bash)**：命令失败时错误检测

## OpenClaw 设置

### 1. 安装 Hook

复制 hook 到 OpenClaw 的 hooks 目录：

```bash
cp -r hooks/openclaw ~/.openclaw/hooks/self-evolution-cn
```

启用 hook：

```bash
openclaw hooks enable self-evolution-cn
```

### 2. 验证 Hook

检查 hook 是否已注册：

```bash
openclaw hooks list
```

### 3. 测试 Hook

1. 启用 hook 配置
2. 启动新的 OpenClaw 会话
3. 发送任何提示
4. 验证你在上下文中看到 `<self-improvement-reminder>`

## Claude Code 设置

### 项目级配置

在项目根目录创建 `.claude/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "./skills/self-evolution-cn/scripts/activator.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./skills/self-evolution-cn/scripts/error-detector.sh"
          }
        ]
      }
    ]
  }
}
```

### 用户级配置

添加到 `~/.claude/settings.json` 以进行全局激活：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/self-evolution-cn/scripts/activator.sh"
          }
        ]
      }
    ]
  }
}
```

### 最小设置（仅激活器）

为了降低开销，仅使用 UserPromptSubmit hook：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "./skills/self-evolution-cn/scripts/activator.sh"
          }
        ]
      }
    ]
  }
}
```

## Codex CLI 设置

Codex 使用与 Claude Code 相同的 hook 系统。创建 `.codex/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "./skills/self-evolution-cn/scripts/activator.sh"
          }
        ]
      }
    ]
  }
}
```

## GitHub Copilot 设置

Copilot 不直接支持 hook。相反，将指导添加到 `.github/copilot-instructions.md`：

```markdown
## 自我改进

在完成涉及以下内容的任务后：
- 调试非显而易见的问题
- 发现变通方法
- 学习项目特定模式
- 解决意外错误

考虑使用 self-evolution-cn 技能的格式将学习记录到 `.learnings/`。

对于将使其他会话受益的高价值学习，考虑技能提取。
```

## 验证

### 测试激活器 Hook

1. 启用 hook 配置
2. 启动新的 Claude Code 会话
3. 发送任何提示
4. 验证你在上下文中看到 `<self-improvement-reminder>`

### 测试错误检测器 Hook

1. 为 Bash 启用 PostToolUse hook
2. 运行失败的命令：`ls /nonexistent/path`
3. 验证你看到 `<error-detected>` 提醒

### 干运行提取脚本

```bash
./skills/self-evolution-cn/scripts/extract-skill.sh test-skill --dry-run
```

预期输出显示将创建的技能脚手架。

## 故障排除

### Hook 未触发

1. **检查脚本权限**：`chmod +x scripts/*.sh`
2. **验证路径**：使用绝对路径或相对于项目根目录的路径
3. **检查设置位置**：项目级 vs 用户级设置
4. **重启会话**：Hook 在会话启动时加载

### 权限被拒绝

```bash
chmod +x ./skills/self-evolution-cn/scripts/activator.sh
chmod +x ./skills/self-evolution-cn/scripts/error-detector.sh
chmod +x ./skills/self-evolution-cn/scripts/extract-skill.sh
```

### 脚本未找到

如果使用相对路径，确保你在正确的目录中或使用绝对路径：

```json
{
  "command": "/absolute/path/to/skills/self-evolution-cn/scripts/activator.sh"
}
```

### 开销太大

如果激活器感觉侵入性太强：

1. **使用最小设置**：仅 UserPromptSubmit，跳过 PostToolUse
2. **添加匹配器过滤器**：仅对某些提示触发：

```json
{
  "matcher": "fix|debug|error|issue",
  "hooks": [...]
}
```

## Hook 输出预算

激活器设计为轻量级：
- **目标**：每次激活约 50-100 个 token
- **内容**：结构化提醒，不是冗长的指令
- **格式**：XML 标签以便于解析

如果需要进一步减少开销，可以编辑 `activator.sh` 以输出更少的文本。

## 安全考虑

- Hook 脚本以与 Claude Code 相同的权限运行
- 脚本仅输出文本；它们不修改文件或运行命令
- 错误检测器读取 `CLAUDE_TOOL_OUTPUT` 环境变量
- 所有脚本都是可选的（你必须显式配置它们）

## 禁用 Hook

要在不删除配置的情况下临时禁用：

1. **在设置中注释掉**：
```json
{
  "hooks": {
    // "UserPromptSubmit": [...]
  }
}
```

2. **或删除设置文件**：没有配置 Hook 不会运行

## OpenClaw Hook 事件

| 事件 | 何时触发 |
|------|---------|
| `agent:bootstrap` | 在工作区文件注入之前 |
| `message:received` | 收到用户消息时 |
| `tool:after` | 工具执行之后 |

## 自动识别触发器

### 用户纠正

检测到关键词："不对"、"错了"、"错误"、"不是这样"、"应该是"

### 命令失败

检测到工具执行失败（非零退出码）

### 知识缺口

检测到用户提供新信息

### 发现更好的方法

检测到"更好的方法"、"更简单"、"优化"等表达
