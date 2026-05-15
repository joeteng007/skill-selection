#!/usr/bin/env python3
"""
发布检查技能 - 自动检查是否符合发布标准
用法: python3 release_checker.py <skill_path>
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 必需文件清单
REQUIRED_FILES = {
    "core": [
        "cli.py",
        "install.sh",
    ],
    "config": [
        "detection_rules.json",
    ],
    "docs": [
        "README.md",
        "SKILL.md",
        "RELEASE.md",
    ]
}

# 可选文件
OPTIONAL_FILES = [
    "requirements.txt",
    "setup.py",
    "LICENSE",
    "CLAUDE.md",
]

class ReleaseChecker:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.results = {
            "skill": str(skill_path),
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "required": [],
            "optional": [],
            "quality": [],
            "score": 0,
            "verdict": ""
        }
    
    def check_required_files(self):
        """检查必需文件"""
        missing = []
        found = []
        
        for category, files in REQUIRED_FILES.items():
            for f in files:
                if (self.skill_path / f).exists():
                    found.append(f"{category}/{f}")
                else:
                    missing.append(f"{category}/{f}")
        
        self.results["required"] = {
            "found": found,
            "missing": missing,
            "complete": len(missing) == 0
        }
        return len(missing) == 0
    
    def check_optional_files(self):
        """检查可选文件"""
        found = []
        for f in OPTIONAL_FILES:
            if (self.skill_path / f).exists():
                found.append(f)
        
        self.results["optional"] = {
            "found": found,
            "count": len(found),
            "total": len(OPTIONAL_FILES)
        }
    
    def check_quality(self):
        """检查质量标准"""
        quality_checks = []
        
        # 检查 CLI 可执行
        cli = self.skill_path / "cli.py"
        if cli.exists():
            content = cli.read_text()
            if "def main" in content and "__name__" in content:
                quality_checks.append({"check": "CLI有main入口", "pass": True})
        
        # 检查 JSON 语法
        rules = self.skill_path / "detection_rules.json"
        if rules.exists():
            try:
                json.loads(rules.read_text())
                quality_checks.append({"check": "规则JSON语法正确", "pass": True})
            except:
                quality_checks.append({"check": "规则JSON语法正确", "pass": False})
        
        # 检查 README 包含关键内容
        readme = self.skill_path / "README.md"
        if readme.exists():
            content = readme.read_text().lower()
            has_install = "安装" in content or "install" in content.lower()
            has_usage = "使用" in content or "usage" in content.lower()
            if has_install and has_usage:
                quality_checks.append({"check": "README包含安装和使用说明", "pass": True})
            else:
                quality_checks.append({"check": "README包含安装和使用说明", "pass": False})
        
        # 检查版本号
        release = self.skill_path / "RELEASE.md"
        if release.exists():
            content = release.read_text()
            if "v" in content and ("2026" in content or "20" in content):
                quality_checks.append({"check": "RELEASE.md包含版本信息", "pass": True})
        
        self.results["quality"] = quality_checks
        
        passed = sum(1 for q in quality_checks if q["pass"])
        total = len(quality_checks)
        return passed == total and total > 0
    
    def calculate_score(self):
        """计算发布准备度分数"""
        score = 0
        
        # 必需文件 (50分)
        if self.results["required"]["complete"]:
            score += 50
        else:
            score += 50 * (len(self.results["required"]["found"]) / max(1, len(REQUIRED_FILES["core"]) + len(REQUIRED_FILES["config"]) + len(REQUIRED_FILES["docs"])))
        
        # 可选文件 (20分)
        opt_ratio = self.results["optional"]["count"] / max(1, self.results["optional"]["total"])
        score += 20 * opt_ratio
        
        # 质量检查 (30分)
        quality_passed = sum(1 for q in self.results["quality"] if q["pass"])
        quality_total = len(self.results["quality"])
        if quality_total > 0:
            score += 30 * (quality_passed / quality_total)
        
        self.results["score"] = int(score)
        
        if score >= 90:
            self.results["verdict"] = "✅ 准备就绪"
        elif score >= 70:
            self.results["verdict"] = "⚠️ 建议完善"
        else:
            self.results["verdict"] = "❌ 不建议发布"
        
        return score
    
    def run(self):
        """执行检查"""
        print(f"\n🔍 检查: {self.skill_path.name}")
        print("=" * 50)
        
        # 执行各项检查
        self.check_required_files()
        self.check_optional_files()
        self.check_quality()
        score = self.calculate_score()
        
        # 打印结果
        print(f"\n📋 必需文件:")
        if self.results["required"]["complete"]:
            print(f"   ✅ 完整 ({len(self.results['required']['found'])}个)")
        else:
            print(f"   ❌ 缺失 {len(self.results['required']['missing'])}个:")
            for f in self.results["required"]["missing"]:
                print(f"      - {f}")
        
        print(f"\n📦 可选文件:")
        print(f"   已包含 {self.results['optional']['count']}/{self.results['optional']['total']}")
        
        print(f"\n✅ 质量检查:")
        for q in self.results["quality"]:
            emoji = "✅" if q["pass"] else "❌"
            print(f"   {emoji} {q['check']}")
        
        print(f"\n📊 准备度: {score}/100 - {self.results['verdict']}")
        print("=" * 50)
        
        return self.results

def main():
    if len(sys.argv) < 2:
        print("用法: python3 release_checker.py <skill_path>")
        print("示例: python3 release_checker.py ~/.openclaw/workspace/skills/agent-security-skill-scanner")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    checker = ReleaseChecker(skill_path)
    results = checker.run()
    
    # 保存结果
    output_path = Path(skill_path) / "release_check_result.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📄 报告已保存: {output_path}")
    
    # 返回状态码
    sys.exit(0 if results["score"] >= 70 else 1)

if __name__ == "__main__":
    main()
