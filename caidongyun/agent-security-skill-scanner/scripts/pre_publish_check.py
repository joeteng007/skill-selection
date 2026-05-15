#!/usr/bin/env python3
"""
发布前自动检查脚本
在推送前检测问题并给出解决方案
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class PublishChecker:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def check_large_files(self):
        """检查是否有大文件 (>50MB)"""
        print(f"\n{BLUE}📦 检查大文件...{RESET}")
        
        # 检查当前未提交的大文件
        large_files = []
        for f in self.repo_path.rglob("*"):
            if f.is_file():
                size_mb = f.stat().st_size / (1024 * 1024)
                if size_mb > 50 and not self.is_ignored(f):
                    large_files.append((f, size_mb))
        
        if large_files:
            for f, size in sorted(large_files, key=lambda x: -x[1]):
                self.warnings.append({
                    "type": "large_file",
                    "file": str(f.relative_to(self.repo_path)),
                    "size": f"{size:.1f}MB",
                    "severity": "HIGH"
                })
                print(f"  ⚠️  {f.relative_to(self.repo_path)}: {size:.1f}MB")
        else:
            print(f"  {GREEN}✅ 无大文件{RESET}")
            self.passed.append("无大文件")
            
    def is_ignored(self, file_path):
        """检查文件是否被gitignore"""
        try:
            result = subprocess.run(
                ["git", "check-ignore", "-q", str(file_path)],
                cwd=self.repo_path,
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
            
    def check_sensitive_info(self):
        """检查敏感信息"""
        print(f"\n{BLUE}🔐 检查敏感信息...{RESET}")
        
        patterns = [
            ("token", ["TOKEN", "token", "TOKEN_"]),
            ("key", ["API_KEY", "SECRET_KEY", "PRIVATE_KEY"]),
            ("password", ["PASSWORD", "password=", "pwd"]),
            ("github", ["ghp_", "github_pat_"]),
        ]
        
        found = []
        for ext in ["*.py", "*.js", "*.json", "*.yaml", "*.yml", "*.md", "*.sh"]:
            for f in self.repo_path.glob(f"**/{ext}"):
                if "node_modules" in str(f) or ".git" in str(f):
                    continue
                try:
                    content = f.read_text(errors='ignore')
                    for pattern_name, patterns_list in patterns:
                        for p in patterns_list:
                            if p in content and "YOUR_" not in content:
                                # 排除注释中的示例
                                lines = [l for l in content.split('\n') if p in l and not l.strip().startswith('#')]
                                if lines:
                                    found.append((f, pattern_name, p))
                                    break
                except:
                    pass
        
        # 检查.git/config等敏感文件
        sensitive_files = [".git/config", ".git/credentials", "*.pem", "*.key"]
        for sf in sensitive_files:
            if (self.repo_path / sf).exists():
                found.append((sf, "sensitive_file", sf))
        
        if found:
            for f, ptype, pattern in set(found):
                self.issues.append({
                    "type": "sensitive_info",
                    "file": str(f),
                    "pattern": pattern,
                    "severity": "CRITICAL"
                })
                print(f"  {RED}❌ 发现敏感信息: {f} ({pattern}){RESET}")
        else:
            print(f"  {GREEN}✅ 无敏感信息{RESET}")
            self.passed.append("无敏感信息")
            
    def check_git_status(self):
        """检查Git状态"""
        print(f"\n{BLUE}📊 检查Git状态...{RESET}")
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                print(f"  📝 待提交: {len(lines)} 个文件")
                
                # 检查是否有测试输出文件
                test_outputs = [l for l in lines if any(x in l for x in ["iteration", "report", ".log"])]
                if test_outputs:
                    self.warnings.append({
                        "type": "test_outputs",
                        "files": len(test_outputs),
                        "severity": "MEDIUM"
                    })
                    print(f"  ⚠️  包含测试输出文件: {len(test_outputs)} 个")
            else:
                print(f"  {GREEN}✅ 无待提交文件{RESET}")
                self.passed.append("Git状态正常")
        except Exception as e:
            print(f"  ⚠️ 无法检查Git状态: {e}")
            
    def check_required_files(self):
        """检查必需文件"""
        print(f"\n{BLUE}📋 检查必需文件...{RESET}")
        
        required = {
            "cli.py": "主入口",
            "README.md": "使用说明",
            "SKILL.md": "Skill定义",
            "RELEASE.md": "发布说明",
            "detection_rules.json": "检测规则"
        }
        
        for fname, desc in required.items():
            if (self.repo_path / fname).exists():
                print(f"  {GREEN}✅ {fname}{RESET}")
            else:
                self.warnings.append({
                    "type": "missing_file",
                    "file": fname,
                    "desc": desc,
                    "severity": "HIGH"
                })
                print(f"  {RED}❌ 缺失: {fname} ({desc}){RESET}")
                
    def check_file_count(self):
        """检查文件数量"""
        print(f"\n{BLUE}📁 检查文件数量...{RESET}")
        
        files = list(self.repo_path.rglob("*"))
        total_files = len([f for f in files if f.is_file() and ".git" not in str(f)])
        total_dirs = len([f for f in files if f.is_dir() and ".git" not in str(f)])
        
        print(f"  📊 总文件: {total_files}, 总目录: {total_dirs}")
        
        if total_files > 1000:
            self.warnings.append({
                "type": "too_many_files",
                "count": total_files,
                "severity": "MEDIUM"
            })
            print(f"  ⚠️ 文件数量较多，可能影响推送速度")
            
    def generate_report(self):
        """生成检查报告"""
        print(f"\n{'='*60}")
        print(f"{BLUE}🔍 发布前检查报告{RESET}")
        print(f"{'='*60}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 问题汇总
        if self.issues:
            print(f"\n{RED}❌ 问题 (必须解决){RESET}")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. [{issue['severity']}] {issue['type']}")
                if 'file' in issue:
                    print(f"     文件: {issue['file']}")
                if 'pattern' in issue:
                    print(f"     模式: {issue['pattern']}")
                if 'desc' in issue:
                    print(f"     说明: {issue['desc']}")
                    
        # 警告
        if self.warnings:
            print(f"\n{YELLOW}⚠️ 警告 (建议处理){RESET}")
            for i, warn in enumerate(self.warnings, 1):
                print(f"  {i}. [{warn['severity']}] {warn['type']}")
                if 'file' in warn:
                    print(f"     文件: {warn['file']}")
                if 'size' in warn:
                    print(f"     大小: {warn['size']}")
                if 'count' in warn:
                    print(f"     数量: {warn['count']}")
                    
        # 通过项
        if self.passed:
            print(f"\n{GREEN}✅ 通过 ({len(self.passed)}){RESET}")
            for p in self.passed:
                print(f"  - {p}")
                
        # 总结
        print(f"\n{'='*60}")
        if self.issues:
            print(f"{RED}❌ 发布检查未通过 - 有 {len(self.issues)} 个问题必须解决{RESET}")
            return False
        elif self.warnings:
            print(f"{YELLOW}⚠️ 发布检查通过 - 但有 {len(self.warnings)} 个警告{RESET}")
            return True
        else:
            print(f"{GREEN}✅ 发布检查通过 - 无问题{RESET}")
            return True
            
    def suggest_fixes(self):
        """提供修复建议"""
        if not self.issues and not self.warnings:
            return
            
        print(f"\n{BLUE}🔧 修复建议:{RESET}")
        
        for issue in self.issues + self.warnings:
            itype = issue['type']
            
            if itype == "large_file":
                print(f"  • 大文件: 使用 .gitignore 排除或删除本地文件")
            elif itype == "sensitive_info":
                print(f"  • 敏感信息: 从代码中移除，使用环境变量")
            elif itype == "test_outputs":
                print(f"  • 测试输出: 运行 rm -rf iteration*.json reports/")
            elif itype == "missing_file":
                print(f"  • 缺失文件: 创建 {issue['file']}")
            elif itype == "too_many_files":
                print(f"  • 文件过多: 考虑拆分为多个仓库")
                
        print(f"\n{BLUE}📝 快速命令:{RESET}")
        print(f"  # 清理测试文件")
        print(f"  rm -rf iteration*.json reports/ *.log")
        print(f"  ")
        print(f"  # 检查大文件")
        print(f"  du -sh *")
        print(f"  ")
        print(f"  # 强制提交")
        print(f"  git add . && git commit -m 'fix: 发布前清理'")

def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    checker = PublishChecker(repo_path)
    
    print(f"{BLUE}🔍 开始发布前检查...{RESET}")
    
    # 执行各项检查
    checker.check_large_files()
    checker.check_sensitive_info()
    checker.check_git_status()
    checker.check_required_files()
    checker.check_file_count()
    
    # 生成报告
    passed = checker.generate_report()
    
    # 提供修复建议
    checker.suggest_fixes()
    
    # 返回状态码
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
