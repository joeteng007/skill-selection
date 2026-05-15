#!/bin/bash
# 日/周/月检查脚本
# 用法：
#   ./daily_review.sh        # 最近 24 小时（每日）
#   DURATION=7 ./daily_review.sh  # 最近 7 天（每周）
#   DURATION=30 ./daily_review.sh # 最近 30 天（每月）

set -e

# 获取共享学习目录
SHARED_LEARNING_DIR="${SHARED_LEARNING_DIR:-/root/.openclaw/shared-learning}"

# 获取当前 agent ID
AGENT_ID="${AGENT_ID:-agent1}"

# 获取 agent 对应的 workspace
WORKSPACE_BASE="/root/.openclaw"
WORKSPACE="$WORKSPACE_BASE/workspace-$AGENT_ID"

# 如果 workspace 不存在，尝试从 OpenClaw 配置获取
if [ ! -d "$WORKSPACE" ]; then
    if command -v openclaw &> /dev/null; then
        WORKSPACE=$(openclaw config get agents.list 2>&1 | jq -r --arg agent "$AGENT_ID" '.[] | select(.id == $agent) | .workspace' 2>/dev/null)
    fi
fi

# 如果还是找不到，使用默认值
if [ -z "$WORKSPACE" ] || [ ! -d "$WORKSPACE" ]; then
    WORKSPACE="$WORKSPACE_BASE/workspace-agent1"
fi

# 读取对应 workspace 中的 .learnings 目录
LEARNINGS_DIR="$WORKSPACE/.learnings"

# 如果 .learnings 不存在，使用共享目录
if [ ! -d "$LEARNINGS_DIR" ]; then
    LEARNINGS_DIR="$SHARED_LEARNING_DIR"
fi

ERRORS_FILE="$LEARNINGS_DIR/ERRORS.md"
LEARNINGS_FILE="$LEARNINGS_DIR/LEARNINGS.md"
FEATURES_FILE="$LEARNINGS_DIR/FEATURE_REQUESTS.md"

# 持续时间（天）（默认：1 表示每日）
DURATION=${DURATION:-1}

echo "=== 自我进化检查 [$AGENT_ID]（${DURATION} 天） ==="
echo "扫描 .learnings/ 目录..."
echo ""

# 1. 统计待处理项（排除模板）
echo "📊 1. 待处理项概览"
# 排除模板部分（包含 "模板"、"template"、"<agent_id>" 等标记）
PENDING_COUNT=$(grep -h "Status: pending" "$ERRORS_FILE" "$LEARNINGS_FILE" "$FEATURES_FILE" 2>/dev/null | \
  grep -v "模板\|template\|<agent_id>\|<YYYYMMDD>" | wc -l)
echo "   待处理项总数：$PENDING_COUNT"
echo ""

# 2. 高优先级项
echo "🚨 2. 高优先级和关键优先级项"
echo ""
grep -B10 -h "Priority: high\|Priority: critical" "$ERRORS_FILE" "$LEARNINGS_FILE" "$FEATURES_FILE" 2>/dev/null | \
  grep -v "模板\|template\|<agent_id>\|<YYYYMMDD>" | grep "^## 2026" || echo "   无高优先级项。"
echo ""

# 3. 重复模式
echo "🔄 3. 重复模式（>= 2 次）"
echo ""
echo "   错误："
grep -B5 -h "Recurrence-Count: [23-9]" "$ERRORS_FILE" 2>/dev/null | \
  grep -v "模板\|template\|<agent_id>\|<YYYYMMDD>" | grep -E "^## 2026|Recurrence-Count:" || echo "   无重复错误。"
echo ""
echo "   学习："
grep -B5 -h "Recurrence-Count: [23-9]" "$LEARNINGS_FILE" 2>/dev/null | \
  grep -v "模板\|template\|<agent_id>\|<YYYYMMDD>" | grep -E "^## 2026|Recurrence-Count:" || echo "   无重复学习。"
echo ""

# 4. 候选提升项（>= 3 次）
echo "⬆️  4. 提升候选（>= 3 次）"
echo ""
PROMOTE_ITEMS=$(grep -l "Recurrence-Count: [3-9]" "$ERRORS_FILE" "$LEARNINGS_FILE" 2>/dev/null || true)
if [ -n "$PROMOTE_ITEMS" ]; then
    echo "   发现准备提升的项："
    for file in $PROMOTE_ITEMS; do
        echo "   - $(basename "$file"):"
        grep -B5 "Recurrence-Count: [3-9]" "$file" | grep -v "模板\|template\|<agent_id>\|<YYYYMMDD>" | grep "^## 2026"
        # 检查是否已提升
        PROMOTED_STATUS=$(grep -A5 "Recurrence-Count: [3-9]" "$file" | grep "Status:" | head -1 | sed 's/.*Status: //' | tr -d ' ')
        PROMOTED_BY=$(grep -A5 "Recurrence-Count: [3-9]" "$file" | grep "Promoted-By:" | head -1 | sed 's/.*Promoted-By: //' | tr -d ' ' || echo "")
        if [ -n "$PROMOTED_BY" ]; then
            if echo "$PROMOTED_BY" | grep -q "$AGENT_ID"; then
                echo "     ✓ 已提升（Promoted-By: $PROMOTED_BY）"
            else
                echo "     ⚠ 需要提升（其他 agent 已提升: $PROMOTED_BY）"
            fi
        else
            echo "     ⚠ 需要提升（尚未提升）"
        fi
    done
else
    echo "   无准备提升的项。"
fi
echo ""

# 5. 最近项（最近 N 天）
echo "📅 5. 最近项（最近 ${DURATION} 天）"
echo ""
# 使用 ls 查找最近修改的文件
RECENT_CUTOFF_SECONDS=$((${DURATION} * 86400))
CURRENT_TIME=$(date +%s)
RECENT_FILES=""
RECENT_COUNT=0

for file in "$LEARNINGS_DIR"/*.md; do
    if [ -f "$file" ]; then
        FILE_TIME=$(stat -c %Y "$file" 2>/dev/null)
        TIME_DIFF=$((CURRENT_TIME - FILE_TIME))
        if [ $TIME_DIFF -lt $RECENT_CUTOFF_SECONDS ]; then
            RECENT_FILES="$RECENT_FILES $file"
        fi
    fi
done

if [ -n "$RECENT_FILES" ]; then
    RECENT_DATE=$(date -d "${DURATION} days ago" +%Y-%m-%d)
    echo "   自 $RECENT_DATE 起："
    # 统计最近修改的文件中的记录条数（以 ## 开头的章节）
    RECENT_COUNT=$(echo $RECENT_FILES | xargs grep "^## 2026" 2>/dev/null | wc -l)
    FILE_COUNT=$(echo $RECENT_FILES | wc -w)
    echo "   $RECENT_COUNT 条记录在 $FILE_COUNT 个文件中"
    echo ""
    echo "   修改的文件："
    for file in $RECENT_FILES; do
        echo "   - $(basename "$file") ($(stat -c %y "$file" | cut -d'.' -f1))"
    done
else
    echo "   最近 ${DURATION} 天内无修改的项。"
fi
echo ""

# 6. 生成操作摘要
echo "📋 6. 推荐操作"
echo ""

HIGH_COUNT=$(grep -h "Priority: high\|Priority: critical" "$ERRORS_FILE" "$LEARNINGS_FILE" "$FEATURES_FILE" 2>/dev/null | \
  grep -v "模板\|template\|<agent_id>\|<YYYYMMDD>" | wc -l)
RECURRING_COUNT=$(grep "Recurrence-Count: [23-9]" "$ERRORS_FILE" "$LEARNINGS_FILE" 2>/dev/null | \
  grep -v "模板\|template\|<agent_id>\|<YYYYMMDD>" | wc -l)
PROMOTE_COUNT=$(grep "Recurrence-Count: [3-9]" "$ERRORS_FILE" "$LEARNINGS_FILE" 2>/dev/null | \
  grep -v "模板\|template\|<agent_id>\|<YYYYMMDD>" | wc -l)

echo "   ✅ 审查 $HIGH_COUNT 个高优先级项"
echo "   ✅ 分析 $RECURRING_COUNT 个重复模式"
echo "   ✅ 提升到核心文件（SOUL.md）$PROMOTE_COUNT 个项"
echo ""

# 7. 请求确认
echo "要继续提升，使用 AI agent："
echo "1. 审查上述候选项"
echo "2. 从中提取核心规则"
echo "3. 提升到 SOUL.md"
echo "4. 更新状态为 'promoted' 并添加 'Promoted: SOUL.md'"
echo "5. 添加 'Promoted-By: <agent_id>'（记录哪些 agent 已经提升）"
echo "6. 如果所有 agent 都已提升，Status 改为 'promoted:all'"
echo ""

echo "=== 检查完成 [$AGENT_ID] ==="
