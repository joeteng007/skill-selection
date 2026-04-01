#!/usr/bin/env python3
"""
Skill Stats - 技能元数据统计工具

统计 awesome-openclaw-skills 和 awesome-agent-skills 中技能的：
- Stars 分布
- 更新频率
- 内容长度
- 分类统计

Usage:
    python skill_stats.py --repos ./repos --output ./stats_report.md
"""

import argparse
import json
import re
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from collections import defaultdict


# ==================== 数据结构 ====================

@dataclass
class SkillStats:
    """单个技能统计"""
    name: str
    repo_url: str
    category: str
    source: str
    
    # 元数据
    stars: int = 0
    forks: int = 0
    last_update: Optional[str] = None
    created_at: Optional[str] = None
    
    # 内容
    skill_md_lines: int = 0
    skill_md_size: int = 0  # bytes
    
    # 派生指标
    days_since_update: Optional[int] = None
    is_active: bool = False  # 180 天内更新


# ==================== 数据获取器 ====================

class GitHubStatsFetcher:
    """从 GitHub 获取仓库统计信息"""
    
    def __init__(self, cache_dir: str = "./cache_stats", token: Optional[str] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; SkillStats/1.0)',
            'Accept': 'application/vnd.github.v3+json',
        })
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})
        
        # 速率限制跟踪
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = 0
    
    def fetch_repo_stats(self, github_url: str) -> Optional[Dict]:
        """获取仓库统计信息"""
        match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
        if not match:
            return None
        
        owner, repo = match.group(1), match.group(2)
        cache_key = hashlib.md5(f"{owner}/{repo}".encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # 检查缓存（7 天内）
        if cache_file.exists():
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(days=7):
                return json.loads(cache_file.read_text(encoding='utf-8'))
        
        # 检查速率限制
        if self.rate_limit_remaining < 10:
            print(f"  ⚠️  GitHub API 速率限制剩余：{self.rate_limit_remaining}")
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        try:
            response = self.session.get(api_url, timeout=10)
            
            # 更新速率限制信息
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 5000))
            self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
            
            if response.status_code == 200:
                data = response.json()
                stats = {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'last_update': data.get('updated_at', ''),
                    'created_at': data.get('created_at', ''),
                    'size': data.get('size', 0),  # KB
                    'language': data.get('language', ''),
                    'description': data.get('description', ''),
                }
                cache_file.write_text(json.dumps(stats), encoding='utf-8')
                return stats
            elif response.status_code == 404:
                print(f"  ⚠️  仓库不存在：{owner}/{repo}")
            elif response.status_code == 403:
                print(f"  ⚠️  API 被限制，稍后重试")
        except Exception as e:
            print(f"  ⚠️  获取失败：{owner}/{repo} - {e}")
        
        return None
    
    def fetch_skill_md(self, github_url: str) -> Optional[str]:
        """获取 SKILL.md 内容"""
        match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
        if not match:
            return None
        
        owner, repo = match.group(1), match.group(2)
        
        paths_to_try = [
            f"SKILL.md",
            f"README.md",
        ]
        
        for path in paths_to_try:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
            content = self._fetch_raw(raw_url)
            if content:
                return content
            
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{path}"
            content = self._fetch_raw(raw_url)
            if content:
                return content
        
        return None
    
    def _fetch_raw(self, url: str) -> Optional[str]:
        """获取原始文件内容"""
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.md"
        
        if cache_file.exists():
            return cache_file.read_text(encoding='utf-8')
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                cache_file.write_text(content, encoding='utf-8')
                return content
        except:
            pass
        
        return None


# ==================== 解析器 ====================

class AwesomeListParser:
    """解析 awesome-list README.md"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.readme_path = self.repo_path / "README.md"
    
    def parse(self) -> List[Dict[str, str]]:
        """解析 README.md 返回技能列表"""
        if not self.readme_path.exists():
            raise FileNotFoundError(f"README.md not found: {self.readme_path}")
        
        content = self.readme_path.read_text(encoding='utf-8')
        skills = []
        current_category = "Uncategorized"
        
        github_pattern = r'\[([^\]]+)\]\((https://github\.com/[^)]+)\)'
        
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
                    })
        
        return skills
    
    def _is_valid_skill_url(self, url: str) -> bool:
        invalid_patterns = [
            r'github\.com/[^/]+/awesome',
            r'github\.com/[^/]+/skills/tree/main$',
            r'github\.com/[^/]+$',
        ]
        for pattern in invalid_patterns:
            if re.search(pattern, url):
                return False
        return True


# ==================== 统计分析 ====================

class StatsAnalyzer:
    """统计分析器"""
    
    def __init__(self):
        self.skills: List[SkillStats] = []
    
    def add_skill(self, skill: SkillStats):
        self.skills.append(skill)
    
    def analyze(self) -> Dict:
        """执行统计分析"""
        if not self.skills:
            return {}
        
        # Stars 统计
        stars_list = [s.stars for s in self.skills if s.stars > 0]
        
        # 更新频率统计
        days_list = [s.days_since_update for s in self.skills if s.days_since_update is not None]
        
        # 内容长度统计
        lines_list = [s.skill_md_lines for s in self.skills if s.skill_md_lines > 0]
        
        # 分类统计
        category_stats = defaultdict(lambda: {'count': 0, 'stars_sum': 0, 'active': 0})
        for s in self.skills:
            cat = s.category
            category_stats[cat]['count'] += 1
            category_stats[cat]['stars_sum'] += s.stars
            if s.is_active:
                category_stats[cat]['active'] += 1
        
        # 来源统计
        source_stats = defaultdict(lambda: {'count': 0, 'stars_sum': 0})
        for s in self.skills:
            source_stats[s.source]['count'] += 1
            source_stats[s.source]['stars_sum'] += s.stars
        
        return {
            'total': len(self.skills),
            'stars': self._calc_distribution(stars_list, [0, 10, 50, 100, 500, 1000]),
            'update_frequency': self._calc_distribution(days_list, [30, 90, 180, 365, 730]),
            'content_length': self._calc_distribution(lines_list, [50, 100, 200, 500, 1000]),
            'category_stats': dict(category_stats),
            'source_stats': dict(source_stats),
            'top_by_stars': sorted(self.skills, key=lambda x: x.stars, reverse=True)[:20],
            'top_by_length': sorted(self.skills, key=lambda x: x.skill_md_lines, reverse=True)[:20],
            'most_recent': sorted([s for s in self.skills if s.days_since_update is not None], 
                                 key=lambda x: x.days_since_update)[:20],
        }
    
    def _calc_distribution(self, values: List[int], bins: List[int]) -> Dict:
        """计算分布"""
        if not values:
            return {}
        
        distribution = {}
        prev = 0
        for bin_val in bins:
            key = f"{prev}-{bin_val}" if prev > 0 else f"<{bin_val}"
            count = sum(1 for v in values if prev <= v < bin_val)
            distribution[key] = count
            prev = bin_val
        
        # >= 最大值
        key = f">={bins[-1]}"
        distribution[key] = sum(1 for v in values if v >= bins[-1])
        
        # 统计指标
        distribution['_stats'] = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'median': sorted(values)[len(values)//2],
        }
        
        return distribution


# ==================== 报告生成 ====================

def generate_report(stats: Dict, output_path: str):
    """生成统计报告"""
    
    report = f"""# Skill 元数据统计报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总览

| 指标 | 数值 |
|------|------|
| 总技能数 | {stats.get('total', 0)} |

---

## ⭐ Stars 分布

"""
    
    # Stars 分布
    stars_dist = stats.get('stars', {})
    if stars_dist:
        report += "### 分布表\n\n| 范围 | 数量 | 占比 |\n|------|------|------|\n"
        total = sum(v for k, v in stars_dist.items() if not k.startswith('_'))
        for key, count in stars_dist.items():
            if not key.startswith('_'):
                pct = count/total*100 if total > 0 else 0
                report += f"| {key} | {count} | {pct:.1f}% |\n"
        
        if '_stats' in stars_dist:
            s = stars_dist['_stats']
            report += f"\n### 统计指标\n\n| 指标 | 数值 |\n|------|------|\n"
            report += f"| 最小值 | {s['min']} |\n"
            report += f"| 最大值 | {s['max']} |\n"
            report += f"| 平均值 | {s['avg']:.1f} |\n"
            report += f"| 中位数 | {s['median']} |\n"
    
    report += "\n---\n\n## 📅 更新频率分布\n\n"
    
    # 更新频率
    update_dist = stats.get('update_frequency', {})
    if update_dist:
        report += "### 分布表（按天数）\n\n| 范围 | 数量 | 占比 |\n|------|------|------|\n"
        total = sum(v for k, v in update_dist.items() if not k.startswith('_'))
        for key, count in update_dist.items():
            if not key.startswith('_'):
                pct = count/total*100 if total > 0 else 0
                report += f"| {key} 天 | {count} | {pct:.1f}% |\n"
        
        if '_stats' in update_dist:
            s = update_dist['_stats']
            report += f"\n### 统计指标\n\n| 指标 | 数值 |\n|------|------|\n"
            report += f"| 最近 | {s['min']} 天前 |\n"
            report += f"| 最久 | {s['max']} 天前 |\n"
            report += f"| 平均 | {s['avg']:.1f} 天前 |\n"
            report += f"| 中位数 | {s['median']} 天前 |\n"
    
    report += "\n---\n\n## 📄 内容长度分布\n\n"
    
    # 内容长度
    length_dist = stats.get('content_length', {})
    if length_dist:
        report += "### 分布表（按行数）\n\n| 范围 | 数量 | 占比 |\n|------|------|------|\n"
        total = sum(v for k, v in length_dist.items() if not k.startswith('_'))
        for key, count in length_dist.items():
            if not key.startswith('_'):
                pct = count/total*100 if total > 0 else 0
                report += f"| {key} 行 | {count} | {pct:.1f}% |\n"
        
        if '_stats' in length_dist:
            s = length_dist['_stats']
            report += f"\n### 统计指标\n\n| 指标 | 数值 |\n|------|------|\n"
            report += f"| 最短 | {s['min']} 行 |\n"
            report += f"| 最长 | {s['max']} 行 |\n"
            report += f"| 平均 | {s['avg']:.1f} 行 |\n"
            report += f"| 中位数 | {s['median']} 行 |\n"
    
    # 分类统计
    report += "\n---\n\n## 📂 分类统计\n\n"
    report += "| 分类 | 数量 | 总 Stars | 平均 Stars | 活跃数 (180 天内) |\n|------|------|---------|-----------|----------------|\n"
    
    category_stats = stats.get('category_stats', {})
    for cat, data in sorted(category_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        avg_stars = data['stars_sum'] / data['count'] if data['count'] > 0 else 0
        report += f"| {cat} | {data['count']} | {data['stars_sum']} | {avg_stars:.1f} | {data['active']} |\n"
    
    # 来源统计
    report += "\n---\n\n## 📍 来源统计\n\n"
    report += "| 来源 | 数量 | 总 Stars | 平均 Stars |\n|------|------|---------|-----------|\n"
    
    source_stats = stats.get('source_stats', {})
    for src, data in sorted(source_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        avg_stars = data['stars_sum'] / data['count'] if data['count'] > 0 else 0
        report += f"| {src} | {data['count']} | {data['stars_sum']} | {avg_stars:.1f} |\n"
    
    # Top 20 by Stars
    report += "\n---\n\n## 🏆 Top 20 by Stars\n\n"
    report += "| 排名 | 名称 | 分类 | Stars | 来源 |\n|------|------|------|-------|------|\n"
    
    for i, s in enumerate(stats.get('top_by_stars', [])[:20], 1):
        report += f"| {i} | {s.name} | {s.category} | {s.stars} | {s.source} |\n"
    
    # Top 20 by Length
    report += "\n---\n\n## 📄 Top 20 by 内容长度\n\n"
    report += "| 排名 | 名称 | 分类 | 行数 | Stars |\n|------|------|------|------|-------|\n"
    
    for i, s in enumerate(stats.get('top_by_length', [])[:20], 1):
        report += f"| {i} | {s.name} | {s.category} | {s.skill_md_lines} | {s.stars} |\n"
    
    # 最近更新
    report += "\n---\n\n## 🕐 最近更新的 Top 20\n\n"
    report += "| 排名 | 名称 | 分类 | 更新 | Stars |\n|------|------|------|------|-------|\n"
    
    for i, s in enumerate(stats.get('most_recent', [])[:20], 1):
        days = s.days_since_update
        update_str = f"{days} 天前" if days is not None else "未知"
        report += f"| {i} | {s.name} | {s.category} | {update_str} | {s.stars} |\n"
    
    Path(output_path).write_text(report, encoding='utf-8')


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(description='Skill 元数据统计工具')
    parser.add_argument('--repos', type=str, default='./repos',
                       help='awesome-list 仓库目录')
    parser.add_argument('--output', type=str, default='./stats_report.md',
                       help='输出报告路径')
    parser.add_argument('--github-token', type=str, default=None,
                       help='GitHub API Token（可选，提高速率限制）')
    parser.add_argument('--sample', type=int, default=0,
                       help='抽样数量（0=全部）')
    
    args = parser.parse_args()
    
    fetcher = GitHubStatsFetcher(token=args.github_token)
    analyzer = StatsAnalyzer()
    
    repos_to_scan = [
        ('awesome-openclaw-skills', 'awesome-openclaw-skills'),
        ('awesome-agent-skills', 'awesome-agent-skills'),
    ]
    
    all_skills_raw = []
    
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
            skill = SkillStats(
                name=skill_data.get('name', 'Unknown'),
                repo_url=skill_data.get('github_url', ''),
                category=skill_data.get('category', 'Uncategorized'),
                source=source_name,
            )
            all_skills_raw.append(skill)
    
    # 抽样
    if args.sample > 0 and args.sample < len(all_skills_raw):
        import random
        random.shuffle(all_skills_raw)
        all_skills_raw = all_skills_raw[:args.sample]
        print(f"\n📊 抽样：{args.sample} 个技能\n")
    
    print(f"\n🔍 开始获取元数据...\n")
    
    # 获取元数据
    for i, skill in enumerate(all_skills_raw):
        if i % 50 == 0:
            print(f"  进度：{i}/{len(all_skills_raw)} ({i/len(all_skills_raw)*100:.1f}%)")
        
        # 获取 GitHub 统计
        stats = fetcher.fetch_repo_stats(skill.repo_url)
        if stats:
            skill.stars = stats.get('stars', 0)
            skill.forks = stats.get('forks', 0)
            skill.last_update = stats.get('last_update', '')
            skill.created_at = stats.get('created_at', '')
            
            # 计算更新天数
            if skill.last_update:
                try:
                    update_date = datetime.fromisoformat(skill.last_update.replace('Z', '+00:00'))
                    skill.days_since_update = (datetime.now(update_date.tzinfo) - update_date).days
                    skill.is_active = skill.days_since_update < 180
                except:
                    pass
        
        # 获取 SKILL.md 内容
        content = fetcher.fetch_skill_md(skill.repo_url)
        if content:
            skill.skill_md_lines = len(content.split('\n'))
            skill.skill_md_size = len(content.encode('utf-8'))
        
        analyzer.add_skill(skill)
    
    print(f"\n📈 生成统计报告...\n")
    
    # 分析
    stats = analyzer.analyze()
    
    # 生成报告
    generate_report(stats, args.output)
    print(f"✅ 报告已保存：{args.output}")
    
    # 保存原始数据
    raw_output = args.output.replace('.md', '_raw.json')
    raw_data = {
        'timestamp': datetime.now().isoformat(),
        'skills': [asdict(s) for s in analyzer.skills],
    }
    with open(raw_output, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    print(f"📦 原始数据已保存：{raw_output}")
    
    # 打印摘要
    print(f"\n{'='*60}")
    print(f"📊 统计摘要")
    print(f"{'='*60}")
    print(f"总技能数：{stats.get('total', 0)}")
    
    stars_dist = stats.get('stars', {})
    if '_stats' in stars_dist:
        s = stars_dist['_stats']
        print(f"\nStars:")
        print(f"  平均：{s['avg']:.1f}")
        print(f"  中位数：{s['median']}")
        print(f"  范围：{s['min']} - {s['max']}")
    
    update_dist = stats.get('update_frequency', {})
    if '_stats' in update_dist:
        s = update_dist['_stats']
        print(f"\n更新频率:")
        print(f"  平均：{s['avg']:.1f} 天前")
        print(f"  中位数：{s['median']} 天前")
    
    length_dist = stats.get('content_length', {})
    if '_stats' in length_dist:
        s = length_dist['_stats']
        print(f"\n内容长度:")
        print(f"  平均：{s['avg']:.1f} 行")
        print(f"  中位数：{s['median']} 行")


if __name__ == '__main__':
    main()
