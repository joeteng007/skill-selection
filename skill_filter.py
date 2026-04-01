#!/usr/bin/env python3
"""
Skill Filter - 高质量 Agent Skills 筛选工具

用于从 awesome-openclaw-skills 和 awesome-agent-skills 中筛选高质量技能，
为 MiniCPM 指令微调数据集构建提供数据源。

Usage:
    python skill_filter.py --repos ./repos --output ./filtered_skills.json
"""

import argparse
import json
import os
import re
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import yaml


# ==================== 配置 ====================

@dataclass
class FilterConfig:
    """筛选配置"""
    # 完整性检查
    min_skill_lines: int = 50
    require_skill_md: bool = True
    require_description: bool = True
    require_code_example: bool = True
    
    # 质量信号
    min_stars: int = 10
    max_update_days: int = 180  # 6 个月
    require_activity: bool = False  # issue/pr 活动
    
    # 安全性（一票否决）
    dangerous_patterns: List[str] = field(default_factory=lambda: [
        r'rm\s+(-[rf]+\s+)?/',      # rm -rf /
        r'sudo\s+',                  # sudo 命令
        r'eval\s*\(',                # eval 动态执行
        r'exec\s*\(',                # exec 动态执行
        r'__import__',               # 动态导入
        r'subprocess\..*shell\s*=\s*True',  # shell=True
    ])
    secret_patterns: List[str] = field(default_factory=lambda: [
        r'api[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9]+',
        r'password\s*[=:]\s*["\'][^"\']+',
        r'secret\s*[=:]\s*["\'][a-zA-Z0-9]+',
        r'AKIA[0-9A-Z]{16}',         # AWS Access Key
    ])
    
    # 可评测性
    require_input_output: bool = True
    require_success_criteria: bool = False  # 可选，太严格
    
    # 打分权重
    weights: Dict[str, float] = field(default_factory=lambda: {
        'completeness': 0.3,
        'quality': 0.3,
        'safety': 0.2,
        'evaluability': 0.2,
    })
    
    # 通过阈值
    min_score: float = 0.6  # 60 分以上


# ==================== 数据结构 ====================

@dataclass
class SkillInfo:
    """技能信息"""
    name: str
    repo_url: str
    skill_md_url: str
    category: str
    source: str  # awesome-openclaw-skills 或 awesome-agent-skills
    
    # 内容
    skill_md_content: Optional[str] = None
    skill_md_lines: int = 0
    
    # 元数据
    stars: int = 0
    last_update: Optional[str] = None
    description: str = ""
    
    # 筛选结果
    score: float = 0.0
    passed: bool = False
    fail_reasons: List[str] = field(default_factory=list)
    
    # 详细评分
    scores: Dict[str, float] = field(default_factory=dict)
    
    # 安全性检查
    safety_issues: List[str] = field(default_factory=list)
    
    # 分类标签
    tags: List[str] = field(default_factory=list)
    difficulty: str = "unknown"  # easy/medium/hard


# ==================== 解析器 ====================

class AwesomeListParser:
    """解析 awesome-list README.md 提取技能链接"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.readme_path = self.repo_path / "README.md"
        
    def parse(self) -> List[Dict[str, str]]:
        """解析 README.md 返回技能列表"""
        if not self.readme_path.exists():
            raise FileNotFoundError(f"README.md not found: {self.readme_path}")
        
        content = self.readme_path.read_text(encoding='utf-8')
        skills = []
        
        # 提取 GitHub 链接 (格式：[name](https://github.com/xxx/yyy))
        # 也支持 clawskills.sh 链接
        github_pattern = r'\[([^\]]+)\]\((https://github\.com/[^)]+)\)'
        clawhub_pattern = r'\[([^\]]+)\]\((https://clawskills\.sh/skills/[^)]+)\)'
        
        current_category = "Uncategorized"
        
        for line in content.split('\n'):
            # 检测分类标题
            category_match = re.search(r'^#+\s*(?:<details[^>]*>)?\s*(?:<summary[^>]*>)?\s*([A-Za-z\s&]+?)(?:</summary>)?', line)
            if category_match:
                current_category = category_match.group(1).strip()
                continue
            
            # 提取 GitHub 链接
            for match in re.finditer(github_pattern, line):
                name = match.group(1).strip()
                url = match.group(2).strip()
                if self._is_valid_skill_url(url):
                    skills.append({
                        'name': name,
                        'github_url': url,
                        'category': current_category,
                        'source': 'github'
                    })
            
            # 提取 ClawHub 链接
            for match in re.finditer(clawhub_pattern, line):
                name = match.group(1).strip()
                url = match.group(2).strip()
                skills.append({
                    'name': name,
                    'clawhub_url': url,
                    'category': current_category,
                    'source': 'clawhub'
                })
        
        return skills
    
    def _is_valid_skill_url(self, url: str) -> bool:
        """检查是否是有效的技能仓库链接"""
        # 排除组织主页、awesome-list 自身等
        invalid_patterns = [
            r'github\.com/[^/]+/awesome',
            r'github\.com/[^/]+/skills/tree/main$',  # 组织主页
            r'github\.com/[^/]+$',  # 用户主页
        ]
        for pattern in invalid_patterns:
            if re.search(pattern, url):
                return False
        return True


class SkillContentFetcher:
    """获取技能内容"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; SkillFilter/1.0)'
        })
    
    def fetch_skill_md(self, github_url: str) -> Optional[str]:
        """从 GitHub 获取 SKILL.md 内容"""
        # 解析 URL
        match = re.search(r'github\.com/([^/]+)/([^/]+)(?:/tree/[^/]+)?(?:/tree/main)?(?:/skills/[^/]+/([^/]+))?', github_url)
        if not match:
            return None
        
        owner, repo = match.group(1), match.group(2)
        
        # 尝试不同路径
        paths_to_try = [
            f"skills/{match.group(3)}/SKILL.md" if match.group(3) else "SKILL.md",
            f"SKILL.md",
            f"README.md",
        ]
        
        for path in paths_to_try:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
            content = self._fetch_url(raw_url)
            if content:
                return content
            
            # 尝试 master 分支
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{path}"
            content = self._fetch_url(raw_url)
            if content:
                return content
        
        return None
    
    def _fetch_url(self, url: str) -> Optional[str]:
        """获取 URL 内容（带缓存）"""
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.txt"
        
        # 检查缓存（24 小时内）
        if cache_file.exists():
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(hours=24):
                return cache_file.read_text(encoding='utf-8')
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                cache_file.write_text(content, encoding='utf-8')
                return content
        except Exception as e:
            print(f"  ⚠️  Fetch failed: {url} - {e}")
        
        return None
    
    def get_repo_stars(self, github_url: str) -> int:
        """获取仓库 stars 数（需要 GitHub API）"""
        match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
        if not match:
            return 0
        
        owner, repo = match.group(1), match.group(2)
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        try:
            response = self.session.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('stargazers_count', 0)
        except:
            pass
        
        return 0


# ==================== 筛选器 ====================

class SkillFilter:
    """技能筛选器"""
    
    def __init__(self, config: FilterConfig):
        self.config = config
    
    def filter(self, skill: SkillInfo) -> SkillInfo:
        """对单个技能进行筛选"""
        # 1. 完整性检查
        self._check_completeness(skill)
        
        # 2. 安全性检查（一票否决）
        self._check_safety(skill)
        if skill.safety_issues:
            skill.passed = False
            skill.fail_reasons.append(f"安全問題：{', '.join(skill.safety_issues)}")
            return skill
        
        # 3. 质量打分
        self._score_quality(skill)
        
        # 4. 可评测性打分
        self._score_evaluability(skill)
        
        # 5. 计算总分
        self._calculate_total_score(skill)
        
        # 6. 判定是否通过
        skill.passed = (skill.score >= self.config.min_score and not skill.fail_reasons)
        
        return skill
    
    def _check_completeness(self, skill: SkillInfo):
        """完整性检查"""
        if not skill.skill_md_content:
            skill.fail_reasons.append("无法获取 SKILL.md 内容")
            return
        
        lines = skill.skill_md_content.split('\n')
        skill.skill_md_lines = len(lines)
        
        if len(lines) < self.config.min_skill_lines:
            skill.fail_reasons.append(f"内容太短 ({len(lines)} < {self.config.min_skill_lines})")
        
        # 检查描述
        if self.config.require_description:
            if not re.search(r'^#+\s*.*\n', skill.skill_md_content, re.MULTILINE):
                skill.fail_reasons.append("缺少标题/描述")
        
        # 检查代码示例
        if self.config.require_code_example:
            if not re.search(r'```[\s\S]*?```', skill.skill_md_content):
                skill.fail_reasons.append("缺少代码示例")
    
    def _check_safety(self, skill: SkillInfo):
        """安全性检查"""
        if not skill.skill_md_content:
            return
        
        content_lower = skill.skill_md_content.lower()
        
        # 检查危险模式
        for pattern in self.config.dangerous_patterns:
            if re.search(pattern, skill.skill_md_content, re.IGNORECASE):
                skill.safety_issues.append(f"危险模式：{pattern}")
        
        # 检查密钥
        for pattern in self.config.secret_patterns:
            if re.search(pattern, skill.skill_md_content, re.IGNORECASE):
                skill.safety_issues.append(f"可能包含密钥：{pattern}")
    
    def _score_quality(self, skill: SkillInfo):
        """质量打分"""
        score = 0.0
        max_score = 1.0
        
        # Stars 分数 (0-0.4)
        if skill.stars >= 100:
            score += 0.4
        elif skill.stars >= 50:
            score += 0.3
        elif skill.stars >= 10:
            score += 0.2
        
        # 更新频率 (0-0.3)
        if skill.last_update:
            try:
                update_date = datetime.strptime(skill.last_update, "%Y-%m-%d")
                days_old = (datetime.now() - update_date).days
                if days_old < 30:
                    score += 0.3
                elif days_old < 90:
                    score += 0.2
                elif days_old < 180:
                    score += 0.1
            except:
                pass
        
        # 内容长度 (0-0.3)
        if skill.skill_md_lines >= 200:
            score += 0.3
        elif skill.skill_md_lines >= 100:
            score += 0.2
        elif skill.skill_md_lines >= 50:
            score += 0.1
        
        skill.scores['quality'] = score / max_score
    
    def _score_evaluability(self, skill: SkillInfo):
        """可评测性打分"""
        if not skill.skill_md_content:
            skill.scores['evaluability'] = 0.0
            return
        
        score = 0.0
        content = skill.skill_md_content
        
        # 检查输入输出定义 (0-0.5)
        io_patterns = [
            r'input', r'输出', r'output', r'参数', r'参数',
            r'返回', r'return', r'用法', r'usage',
        ]
        io_matches = sum(1 for p in io_patterns if re.search(p, content, re.IGNORECASE))
        score += 0.5 * min(io_matches / 3, 1.0)
        
        # 检查成功标准 (0-0.3)
        success_patterns = [
            r'完成', r'成功', r'success', r'complete',
            r'验证', r'verify', r'测试', r'test',
        ]
        success_matches = sum(1 for p in success_patterns if re.search(p, content, re.IGNORECASE))
        score += 0.3 * min(success_matches / 2, 1.0)
        
        # 检查是否有明确任务 (0-0.2)
        task_patterns = [
            r'当用户', r'when user', r'用于', r'used to',
            r'功能', r'function', r'任务', r'task',
        ]
        task_matches = sum(1 for p in task_patterns if re.search(p, content, re.IGNORECASE))
        score += 0.2 * min(task_matches / 2, 1.0)
        
        skill.scores['evaluability'] = score
    
    def _calculate_total_score(self, skill: SkillInfo):
        """计算总分"""
        total = 0.0
        for key, weight in self.config.weights.items():
            if key in skill.scores:
                total += skill.scores[key] * weight
        skill.score = total


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(description='高质量 Agent Skills 筛选工具')
    parser.add_argument('--repos', type=str, default='./repos',
                       help='awesome-list 仓库目录')
    parser.add_argument('--output', type=str, default='./filtered_skills.json',
                       help='输出文件路径')
    parser.add_argument('--report', type=str, default='./filter_report.md',
                       help='筛选报告路径')
    parser.add_argument('--min-stars', type=int, default=10,
                       help='最小 stars 数')
    parser.add_argument('--min-score', type=float, default=0.6,
                       help='最小分数 (0-1)')
    
    args = parser.parse_args()
    
    # 初始化
    config = FilterConfig()
    config.min_stars = args.min_stars
    config.min_score = args.min_score
    
    fetcher = SkillContentFetcher()
    filter_engine = SkillFilter(config)
    
    # 解析 awesome-lists
    all_skills = []
    
    repos_to_scan = [
        ('awesome-openclaw-skills', 'awesome-openclaw-skills'),
        ('awesome-agent-skills', 'awesome-agent-skills'),
    ]
    
    for repo_name, source_name in repos_to_scan:
        repo_path = Path(args.repos) / repo_name
        if not repo_path.exists():
            print(f"⚠️  仓库不存在：{repo_path}")
            print(f"   请先克隆：git clone https://github.com/VoltAgent/{repo_name} {repo_path}")
            continue
        
        print(f"📂 解析 {repo_name}...")
        parser = AwesomeListParser(str(repo_path))
        skills_data = parser.parse()
        print(f"   找到 {len(skills_data)} 个技能链接")
        
        for skill_data in skills_data:
            skill = SkillInfo(
                name=skill_data.get('name', 'Unknown'),
                repo_url=skill_data.get('github_url', skill_data.get('clawhub_url', '')),
                skill_md_url='',
                category=skill_data.get('category', 'Uncategorized'),
                source=source_name,
            )
            all_skills.append(skill)
    
    print(f"\n📊 总计 {len(all_skills)} 个技能，开始筛选...\n")
    
    # 筛选
    results = []
    category_stats = {}
    
    for i, skill in enumerate(all_skills):
        if i % 100 == 0:
            print(f"  处理进度：{i}/{len(all_skills)} ({i/len(all_skills)*100:.1f}%)")
        
        # 获取 SKILL.md 内容
        if 'github.com' in skill.repo_url:
            skill.skill_md_content = fetcher.fetch_skill_md(skill.repo_url)
            skill.stars = fetcher.get_repo_stars(skill.repo_url)
        
        # 筛选
        result = filter_engine.filter(skill)
        results.append(result)
        
        # 统计
        cat = result.category
        if cat not in category_stats:
            category_stats[cat] = {'total': 0, 'passed': 0}
        category_stats[cat]['total'] += 1
        if result.passed:
            category_stats[cat]['passed'] += 1
    
    # 输出结果
    passed_skills = [r for r in results if r.passed]
    
    print(f"\n✅ 筛选完成!")
    print(f"   通过：{len(passed_skills)}/{len(results)} ({len(passed_skills)/len(results)*100:.1f}%)")
    
    # 保存 JSON
    output_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'config': asdict(config),
            'total': len(results),
            'passed': len(passed_skills),
        },
        'passed_skills': [asdict(s) for s in passed_skills],
        'category_stats': category_stats,
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"   结果已保存：{args.output}")
    
    # 生成报告
    generate_report(results, passed_skills, category_stats, args.report, config)
    print(f"   报告已保存：{args.report}")
    
    # 打印分类统计
    print(f"\n📈 分类统计:")
    for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]['passed'], reverse=True):
        rate = stats['passed']/stats['total']*100 if stats['total'] > 0 else 0
        print(f"   {cat}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")


def generate_report(results: List[SkillInfo], passed: List[SkillInfo], 
                   category_stats: Dict, report_path: str, config: FilterConfig):
    """生成筛选报告"""
    
    fail_reasons = {}
    for r in results:
        if not r.passed:
            for reason in r.fail_reasons + r.safety_issues:
                key = reason.split(':')[0] if ':' in reason else reason
                fail_reasons[key] = fail_reasons.get(key, 0) + 1
    
    report = f"""# Skill 筛选报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总览

| 指标 | 数值 |
|------|------|
| 总技能数 | {len(results)} |
| 通过数量 | {len(passed)} |
| 通过率 | {len(passed)/len(results)*100:.1f}% |
| 最小分数 | {config.min_score} |
| 最小 Stars | {config.min_stars} |

## 📈 分类统计

| 分类 | 通过 | 总数 | 通过率 |
|------|------|------|--------|
"""
    
    for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]['passed'], reverse=True):
        rate = stats['passed']/stats['total']*100 if stats['total'] > 0 else 0
        report += f"| {cat} | {stats['passed']} | {stats['total']} | {rate:.1f}% |\n"
    
    report += f"""
## ❌ 失败原因分析

| 原因 | 数量 |
|------|------|
"""
    
    for reason, count in sorted(fail_reasons.items(), key=lambda x: x[1], reverse=True)[:10]:
        report += f"| {reason} | {count} |\n"
    
    report += f"""
## 🏆 Top 通过技能

| 名称 | 分类 | 分数 | Stars | 来源 |
|------|------|------|-------|------|
"""
    
    top_skills = sorted(passed, key=lambda x: x.score, reverse=True)[:20]
    for s in top_skills:
        report += f"| {s.name} | {s.category} | {s.score:.2f} | {s.stars} | {s.source} |\n"
    
    report += f"""
## 🔧 筛选配置

```json
{json.dumps(asdict(config), indent=2, ensure_ascii=False)}
```
"""
    
    Path(report_path).write_text(report, encoding='utf-8')


if __name__ == '__main__':
    main()
