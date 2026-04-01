#!/usr/bin/env python3
"""快速生成元数据 JSON（不调用 GitHub API）"""

import json
from pathlib import Path
from datetime import datetime
from skill_stats import AwesomeListParser

def main():
    all_skills = []
    
    # 解析 awesome-openclaw-skills
    print("解析 awesome-openclaw-skills...")
    parser1 = AwesomeListParser('./repos/awesome-openclaw-skills')
    skills1 = parser1.parse()
    print(f"  找到 {len(skills1)} 个技能")
    
    for s in skills1:
        all_skills.append({
            'name': s.get('name', ''),
            'repo_url': s.get('github_url') or s.get('clawhub_url', ''),
            'category': s.get('category', 'Unknown'),
            'source': 'awesome-openclaw-skills',
            'stars': 0,  # 未知
            'skill_md_lines': 0,  # 未知
        })
    
    # 解析 awesome-agent-skills
    print("解析 awesome-agent-skills...")
    parser2 = AwesomeListParser('./repos/awesome-agent-skills')
    skills2 = parser2.parse()
    print(f"  找到 {len(skills2)} 个技能")
    
    for s in skills2:
        all_skills.append({
            'name': s.get('name', ''),
            'repo_url': s.get('github_url', ''),
            'category': s.get('category', 'Unknown'),
            'source': 'awesome-agent-skills',
            'stars': 0,
            'skill_md_lines': 0,
        })
    
    # 保存
    output = {
        'timestamp': datetime.now().isoformat(),
        'skills': all_skills,
    }
    
    with open('./quick_stats_raw.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存：quick_stats_raw.json ({len(all_skills)} 个技能)")

if __name__ == '__main__':
    main()
