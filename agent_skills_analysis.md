# Awesome Agent Skills 分析报告

## 执行摘要

| 类别 | 数量 |
|------|------|
| README 徽章显示 | 1060+ |
| 实际可提取链接 | 664 |
| **已验证有 SKILL.md** | **557** |
| 链接失效/路径错误 | 68 |
| 其他（仓库根目录等） | 39 |

## 问题分析

### 68 个链接失效的原因

1. **路径命名不匹配** (主要问题)
   - README 使用：`hugging-face-cli`
   - 实际路径：`hf-cli`
   - 示例：`huggingface/skills` 仓库有多个此类问题

2. **仓库已删除或重构**
   - 部分技能仓库已被作者删除
   - 部分技能已移动到新位置

3. **非标准技能格式**
   - `cloudflare/skills/commands` - 使用 `.md` 文件而非 `SKILL.md`
   - `hashicorp/agent-skills` - 使用 `.claude-plugin` 目录
   - `googleworkspace/cli` - 使用不同的技能结构

4. **链接指向仓库根目录**
   - 部分链接只指向仓库，没有具体技能路径

### 数据质量

- **有效率**: 557/664 = **83.9%**
- **失效率**: 68/664 = **10.2%**
- **其他**: 39/664 = **5.9%**

## 文件说明

- `github_agent_skills_ultimate.txt` - 557 个已验证的 GitHub 技能链接
- 所有链接已确认包含 `SKILL.md` 文件
- 格式：`https://github.com/owner/repo/tree/branch/path/to/skill`

## 建议

1. README 徽章数字 (1060+) 可能包含：
   - 子技能计数（一个技能包内多个技能）
   - 已删除/失效的链接
   - 营销夸大

2. 实际可用的独立技能链接：**557 个**

---
生成时间：2026-04-04 21:47:58
