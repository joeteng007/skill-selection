# Skill Filter - 高质量 Agent Skills 筛选工具

用于从 awesome-openclaw-skills 和 awesome-agent-skills 中筛选高质量技能，为 MiniCPM 指令微调数据集构建提供数据源。

## 🚀 快速开始

### 1. 安装依赖

```bash
cd skill-filter
pip install -r requirements.txt
```

### 2. 克隆 awesome-list 仓库

```bash
mkdir -p repos
cd repos
git clone --depth 1 https://github.com/VoltAgent/awesome-openclaw-skills
git clone --depth 1 https://github.com/VoltAgent/awesome-agent-skills
cd ..
```

### 3. 运行筛选

```bash
# 默认配置
python skill_filter.py --repos ./repos --output ./filtered_skills.json

# 自定义配置
python skill_filter.py \
    --repos ./repos \
    --output ./filtered_skills.json \
    --report ./filter_report.md \
    --min-stars 20 \
    --min-score 0.7
```

## 📁 输出文件

### filtered_skills.json

```json
{
  "metadata": {
    "timestamp": "2026-04-01T11:30:00",
    "config": {...},
    "total": 5000,
    "passed": 1500
  },
  "passed_skills": [
    {
      "name": "skill-name",
      "repo_url": "https://github.com/...",
      "category": "Coding Agents & IDEs",
      "source": "awesome-openclaw-skills",
      "score": 0.85,
      "stars": 150,
      "skill_md_lines": 234,
      ...
    }
  ],
  "category_stats": {...}
}
```

### filter_report.md

Markdown 格式的筛选报告，包含：
- 总览统计
- 分类通过率
- 失败原因分析
- Top 通过技能列表

## ⚙️ 筛选配置

### 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--repos` | `./repos` | awesome-list 仓库目录 |
| `--output` | `./filtered_skills.json` | 输出 JSON 文件路径 |
| `--report` | `./filter_report.md` | 筛选报告路径 |
| `--min-stars` | `10` | 最小 stars 数 |
| `--min-score` | `0.6` | 最小分数 (0-1) |

### 代码配置

编辑 `skill_filter.py` 中的 `FilterConfig` 类：

```python
@dataclass
class FilterConfig:
    # 完整性检查
    min_skill_lines: int = 50       # 最小行数
    require_skill_md: bool = True   # 必须有 SKILL.md
    require_description: bool = True
    require_code_example: bool = True
    
    # 质量信号
    min_stars: int = 10
    max_update_days: int = 180
    
    # 安全性（一票否决）
    dangerous_patterns: List[str] = [...]
    secret_patterns: List[str] = [...]
    
    # 打分权重
    weights: Dict[str, float] = {
        'completeness': 0.3,
        'quality': 0.3,
        'safety': 0.2,
        'evaluability': 0.2,
    }
    
    # 通过阈值
    min_score: float = 0.6
```

## 📊 筛选维度

### 1. 完整性检查
- SKILL.md 存在
- 内容行数 ≥ 50
- 有标题/描述
- 有代码示例

### 2. 安全性检查（一票否决）
- 无 `rm -rf /` 等危险命令
- 无 `sudo` 命令
- 无 `eval/exec` 动态执行
- 无硬编码 API Key/密码

### 3. 质量打分
- GitHub stars 数
- 最后更新时间
- 内容长度

### 4. 可评测性
- 输入输出定义清晰
- 有成功标准
- 任务描述明确

## 🎯 使用建议

### Phase 1: 验证筛选标准
```bash
# 用小样本验证
python skill_filter.py --min-stars 50 --min-score 0.7
```

### Phase 2: 批量筛选
```bash
# 放宽标准获取更大样本
python skill_filter.py --min-stars 10 --min-score 0.6
```

### Phase 3: 导出特定类别
```python
# 读取结果后按类别过滤
import json
with open('filtered_skills.json') as f:
    data = json.load(f)

coding_skills = [s for s in data['passed_skills'] 
                 if 'Coding' in s['category']]
```

## 📈 预期结果

基于当前 awesome-list 数据：

| 配置 | 通过率 | 预估数量 |
|------|--------|---------|
| 严格 (stars≥50, score≥0.7) | ~15% | ~800 |
| 中等 (stars≥20, score≥0.6) | ~25% | ~1,300 |
| 宽松 (stars≥10, score≥0.5) | ~35% | ~1,800 |

## 🔧 扩展

### 添加新的筛选规则

在 `SkillFilter` 类中添加新方法：

```python
def _check_custom(self, skill: SkillInfo):
    """自定义检查"""
    if not skill.skill_md_content:
        return
    
    # 你的检查逻辑
    if some_condition:
        skill.fail_reasons.append("自定义失败原因")
```

### 集成到数据合成 Pipeline

```python
from skill_filter import SkillFilter, FilterConfig

# 筛选
config = FilterConfig(min_score=0.6)
filter_engine = SkillFilter(config)
passed_skills = filter_engine.filter_batch(skills)

# 传递给任务合成器
for skill in passed_skills:
    generate_tasks(skill)
```

## 📝 License

MIT
