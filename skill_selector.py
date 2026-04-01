#!/usr/bin/env python3
"""
Skill Selector - 基于"易闭环、低依赖、状态可判别"标准筛选技能

筛选标准：
1. 结构化数据处理类 (Structured Data Ops)
2. 逻辑/规则验证类 (Logic & Rule Validation)  
3. 模拟 API/Mock 协作类 (Mock API & Productivity)

Usage:
    python skill_selector.py --input ./stats_report_raw.json --output ./selected_skills.json
"""

import argparse
import json
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime


# ==================== 配置 ====================

@dataclass
class SelectionConfig:
    """筛选配置"""
    # 基础门槛
    min_stars: int = 50
    min_lines: int = 50
    max_lines: int = 2000  # 排除太长的（可能是文档而非技能）
    
    # 依赖限制
    allowed_languages: List[str] = field(default_factory=lambda: ['python', 'nodejs', 'bash', 'shell'])
    max_external_deps: int = 5  # 最多允许的外部依赖数
    
    # 禁止的高依赖模式
    forbidden_patterns: List[str] = field(default_factory=lambda: [
        r'requires\s+.*\b(api\s+key|token|credential)\b',  # 需要 API 密钥
        r'requires\s+.*\b(account|login|auth)\b',          # 需要登录
        r'requires\s+.*\b(browser|selenium|playwright)\b', # 需要浏览器自动化
        r'requires\s+.*\b(docker|k8s|kubernetes)\b',       # 需要容器编排
        r'requires\s+.*\b(cloud|aws|gcp|azure)\b',         # 需要云服务
        r'npm\s+install\s+.*puppeteer',                    # Puppeteer 太重
        r'pip\s+install\s+.*selenium',                     # Selenium 太重
    ])
    
    # 三类目标技能的关键词
    structured_data_keywords: List[str] = field(default_factory=lambda: [
        'json', 'csv', 'xml', 'yaml', 'markdown', 'table',
        'parse', 'convert', 'transform', 'extract', 'validate',
        'data processing', 'data ops', 'etl',
    ])
    
    logic_validation_keywords: List[str] = field(default_factory=lambda: [
        'regex', 'regular expression', 'pattern', 'match',
        'test', 'unit test', 'pytest', 'assert', 'verify',
        'rule', 'validation', 'lint', 'check',
        'filter', 'search', 'grep',
    ])
    
    mock_api_keywords: List[str] = field(default_factory=lambda: [
        'mock', 'fake', 'simulate', 'stub',
        'sqlite', 'database', 'db', 'sql',
        'calendar', 'schedule', 'todo', 'task',
        'local', 'offline', 'memory',
    ])


# ==================== 分析器 ====================

class SkillAnalyzer:
    """技能分析器"""
    
    def __init__(self, config: SelectionConfig):
        self.config = config
    
    def analyze(self, skill_data: Dict) -> Dict:
        """分析单个技能"""
        result = {
            **skill_data,
            'selected': False,
            'category': None,
            'confidence': 0.0,
            'reasons': [],
            'issues': [],
            'deps': [],
            'language': None,
        }
        
        # 1. 基础门槛检查
        self._check_thresholds(result, skill_data)
        if result['issues']:
            return result
        
        # 2. 使用名称 + 分类进行关键词匹配（无需内容）
        name = skill_data.get('name', '').lower()
        category = skill_data.get('category', '').lower()
        source = skill_data.get('source', '').lower()
        
        # 组合文本用于匹配
        text_to_match = f"{name} {category} {source}"
        
        # 3. 三类技能匹配
        matched_category, confidence, reasons = self._match_category_simple(text_to_match)
        result['category'] = matched_category
        result['confidence'] = confidence
        result['reasons'] = reasons
        
        if matched_category:
            result['selected'] = True
        
        return result
    
    def _check_thresholds(self, result: Dict, skill_data: Dict):
        """检查基础门槛"""
        stars = skill_data.get('stars', 0)
        lines = skill_data.get('skill_md_lines', 0)
        
        if stars < self.config.min_stars:
            result['issues'].append(f'Stars 不足 ({stars} < {self.config.min_stars})')
        if lines < self.config.min_lines:
            result['issues'].append(f'内容太短 ({lines} < {self.config.min_lines})')
        if lines > self.config.max_lines:
            result['issues'].append(f'内容过长 ({lines} > {self.config.max_lines})')
    
    def _detect_language(self, content: str) -> Optional[str]:
        """检测主要编程语言"""
        content_lower = content.lower()
        
        # 检查代码块
        python_patterns = [r'```python', r'```py ', r'import\s+\w+', r'from\s+\w+\s+import']
        node_patterns = [r'```javascript', r'```js ', r'```typescript', r'```ts ', r'require\(', r'import\s+.*from']
        bash_patterns = [r'```bash', r'```sh ', r'```shell', r'\$\s+\w+', r'echo\s+', r'export\s+']
        
        if any(re.search(p, content, re.IGNORECASE) for p in python_patterns):
            return 'python'
        if any(re.search(p, content, re.IGNORECASE) for p in node_patterns):
            return 'nodejs'
        if any(re.search(p, content, re.IGNORECASE) for p in bash_patterns):
            return 'bash'
        
        return 'unknown'
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """提取依赖包"""
        deps = []
        
        # pip install
        pip_matches = re.findall(r'pip\s+install\s+([a-zA-Z0-9_-]+)', content, re.IGNORECASE)
        deps.extend([f'pip:{m}' for m in pip_matches])
        
        # npm install
        npm_matches = re.findall(r'npm\s+install\s+([a-zA-Z0-9_@/-]+)', content, re.IGNORECASE)
        deps.extend([f'npm:{m}' for m in npm_matches])
        
        # requirements.txt
        req_matches = re.findall(r'^([a-zA-Z0-9_-]+)==', content, re.MULTILINE)
        deps.extend([f'pip:{m}' for m in req_matches])
        
        # package.json
        pkg_matches = re.findall(r'"([a-zA-Z0-9_@/-]+)"\s*:\s*"[^"]+"', content)
        deps.extend([f'npm:{m}' for m in pkg_matches if not m.startswith('@types')])
        
        return list(set(deps))
    
    def _check_forbidden(self, content: str) -> List[str]:
        """检查禁止的高依赖模式"""
        forbidden = []
        content_lower = content.lower()
        
        for pattern in self.config.forbidden_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                forbidden.append(pattern)
        
        return forbidden
    
    def _match_category_simple(self, text: str) -> tuple:
        """匹配三类技能（简化版，仅使用名称/分类）"""
        scores = {
            'structured_data': 0,
            'logic_validation': 0,
            'mock_api': 0,
        }
        reasons = {
            'structured_data': [],
            'logic_validation': [],
            'mock_api': [],
        }
        
        # 结构化数据处理
        for kw in self.config.structured_data_keywords:
            if kw in text:
                scores['structured_data'] += 2  # 名称匹配权重更高
                reasons['structured_data'].append(kw)
        
        # 逻辑/规则验证
        for kw in self.config.logic_validation_keywords:
            if kw in text:
                scores['logic_validation'] += 2
                reasons['logic_validation'].append(kw)
        
        # 模拟 API/Mock
        for kw in self.config.mock_api_keywords:
            if kw in text:
                scores['mock_api'] += 2
                reasons['mock_api'].append(kw)
        
        # 分类名称加分
        if 'data' in text:
            scores['structured_data'] += 1
        if 'test' in text or 'valid' in text:
            scores['logic_validation'] += 1
        if 'mock' in text or 'local' in text:
            scores['mock_api'] += 1
        
        # 选择最高分的类别
        max_score = max(scores.values())
        if max_score == 0:
            return None, 0.0, []
        
        best_category = max(scores, key=scores.get)
        confidence = min(max_score / 8.0, 1.0)  # 归一化到 0-1
        
        return best_category, confidence, reasons[best_category]


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(description='基于"易闭环、低依赖、状态可判别"标准筛选技能')
    parser.add_argument('--input', type=str, default='./stats_report_raw.json',
                       help='输入文件（skill_stats.py 的输出）')
    parser.add_argument('--output', type=str, default='./selected_skills.json',
                       help='输出文件路径')
    parser.add_argument('--report', type=str, default='./selection_report.md',
                       help='筛选报告路径')
    parser.add_argument('--min-stars', type=int, default=50,
                       help='最小 stars 数')
    parser.add_argument('--max-deps', type=int, default=5,
                       help='最大依赖数')
    
    args = parser.parse_args()
    
    # 加载数据
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 输入文件不存在：{input_path}")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    skills = data.get('skills', [])
    print(f"📂 加载了 {len(skills)} 个技能")
    
    # 初始化
    config = SelectionConfig()
    config.min_stars = args.min_stars
    config.max_external_deps = args.max_deps
    
    analyzer = SkillAnalyzer(config)
    
    # 分析
    print(f"🔍 开始分析...\n")
    
    results = []
    category_counts = {
        'structured_data': 0,
        'logic_validation': 0,
        'mock_api': 0,
    }
    
    for i, skill in enumerate(skills):
        if i % 100 == 0:
            print(f"  进度：{i}/{len(skills)} ({i/len(skills)*100:.1f}%)")
        
        result = analyzer.analyze(skill)
        results.append(result)
        
        if result['selected']:
            category_counts[result['category']] += 1
    
    # 统计
    selected = [r for r in results if r['selected']]
    
    print(f"\n✅ 筛选完成!")
    print(f"   通过：{len(selected)}/{len(results)} ({len(selected)/len(results)*100:.1f}%)")
    print(f"\n📊 分类统计:")
    for cat, count in category_counts.items():
        cat_name = {
            'structured_data': '结构化数据处理',
            'logic_validation': '逻辑/规则验证',
            'mock_api': '模拟 API/Mock',
        }.get(cat, cat)
        print(f"   {cat_name}: {count}")
    
    # 保存结果
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'config': asdict(config),
        'total': len(results),
        'selected': len(selected),
        'category_counts': category_counts,
        'selected_skills': [r for r in results if r['selected']],
        'rejected_skills': [r for r in results if not r['selected']],
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"\n📦 结果已保存：{args.output}")
    
    # 生成报告
    generate_report(results, selected, category_counts, args.report, config)
    print(f"📄 报告已保存：{args.report}")
    
    # 打印 Top 技能
    print(f"\n🏆 Top 10 高置信度技能:")
    top_skills = sorted(selected, key=lambda x: x['confidence'], reverse=True)[:10]
    for i, s in enumerate(top_skills, 1):
        print(f"   {i}. {s['name']} ({s['category']}) - 置信度：{s['confidence']:.2f}, Stars: {s['stars']}")


def generate_report(results: List[Dict], selected: List[Dict], 
                   category_counts: Dict, report_path: str, config: SelectionConfig):
    """生成筛选报告"""
    
    # 失败原因统计
    issue_counts = {}
    for r in results:
        if not r['selected']:
            for issue in r.get('issues', []):
                key = issue.split('(')[0].strip()
                issue_counts[key] = issue_counts.get(key, 0) + 1
    
    report = f"""# Skill 筛选报告（易闭环、低依赖、状态可判别）

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总览

| 指标 | 数值 |
|------|------|
| 总技能数 | {len(results)} |
| 通过数量 | {len(selected)} |
| 通过率 | {len(selected)/len(results)*100:.1f}% |

## 📈 分类统计

| 类别 | 数量 | 占比 |
|------|------|------|
| 结构化数据处理 | {category_counts['structured_data']} | {category_counts['structured_data']/len(results)*100:.1f}% |
| 逻辑/规则验证 | {category_counts['logic_validation']} | {category_counts['logic_validation']/len(results)*100:.1f}% |
| 模拟 API/Mock | {category_counts['mock_api']} | {category_counts['mock_api']/len(results)*100:.1f}% |

## ❌ 失败原因分析

| 原因 | 数量 |
|------|------|
"""
    
    for reason, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        report += f"| {reason} | {count} |\n"
    
    report += f"""
## 🏆 Top 20 高置信度技能

| 排名 | 名称 | 类别 | 置信度 | Stars | 语言 | 依赖数 |
|------|------|------|--------|-------|------|--------|
"""
    
    top_skills = sorted(selected, key=lambda x: x['confidence'], reverse=True)[:20]
    for i, s in enumerate(top_skills, 1):
        report += f"| {i} | {s['name']} | {s['category']} | {s['confidence']:.2f} | {s['stars']} | {s.get('language', 'N/A')} | {len(s.get('deps', []))} |\n"
    
    report += f"""
## 🔧 筛选配置

```json
{json.dumps(asdict(config), indent=2, ensure_ascii=False)}
```

## 📋 筛选标准说明

### 1. 结构化数据处理类 (Structured Data Ops)
**关键词:** {', '.join(config.structured_data_keywords[:10])}

**特点:**
- 输入输出都是纯文本或标准文件 (JSON/CSV/XML/Markdown)
- Docker 只需要 Python 或 Node 基础环境
- 评测：直接比对输出文件的行数、字段值或格式

### 2. 逻辑/规则验证类 (Logic & Rule Validation)
**关键词:** {', '.join(config.logic_validation_keywords[:10])}

**特点:**
- 测试模型推理能力，而非环境配置能力
- 评测：运行 pytest 或 grep，看返回码是否为 0

### 3. 模拟 API/Mock 协作类 (Mock API & Productivity)
**关键词:** {', '.join(config.mock_api_keywords[:10])}

**特点:**
- 环境通过本地 Mock Server 实现
- 不依赖真实网络和账号
- 评测：检查数据库 (.db 文件) 或 Mock 服务状态变更

### 禁止的高依赖模式
- 需要 API 密钥/Token
- 需要登录/认证
- 需要浏览器自动化 (Selenium/Playwright)
- 需要容器编排 (Docker/K8s)
- 需要云服务 (AWS/GCP/Azure)
"""
    
    Path(report_path).write_text(report, encoding='utf-8')


if __name__ == '__main__':
    main()
