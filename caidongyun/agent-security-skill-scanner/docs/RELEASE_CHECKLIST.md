# Skill Scanner 对外发布清单规范

> 版本: 1.0  
> 日期: 2026-03-15  
> 目的: 定义完整对外发布的必要文件清单

---

## 一、必要文件清单 (必须包含)

### 1. 核心脚本

| 文件 | 说明 | 必需 |
|------|------|------|
| `cli.py` | 主命令行入口 | ✅ |
| `scanner_cli.py` | 扫描器 CLI | ✅ |
| `static_analyzer.py` | 静态分析引擎 | ✅ |
| `dynamic_detector.py` | 动态检测引擎 | ✅ |
| `risk_scanner.py` | 风险扫描引擎 | ✅ |
| `install.sh` | 安装脚本 | ✅ |

### 2. 配置数据

| 文件 | 说明 | 必需 |
|------|------|------|
| `detection_rules.json` | 检测规则库 | ✅ |
| `skill.yaml` | Skill 配置 | ✅ |
| `public.json` | 公共配置 | ✅ |

### 3. 文档

| 文件 | 说明 | 必需 |
|------|------|------|
| `README.md` | 使用说明 | ✅ |
| `SKILL.md` | Skill 定义 | ✅ |
| `RELEASE.md` | 发布说明 | ✅ |
| `LICENSE` | 开源协议 | ✅ |

### 4. 支持模块 (如有)

| 文件 | 说明 | 必需 |
|------|------|------|
| `detectors/` | 检测模块目录 | 可选 |
| `reporters/` | 报告生成模块 | 可选 |
| `data/` | 数据目录 | 可选 |

---

## 二、可选文件

| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python 依赖 |
| `setup.py` | 安装配置 |
| `CAPABILITIES.md` | 功能能力文档 |
| `STATISTICS.md` | 统计数据 |
| `README.en.md` | 英文文档 |

---

## 三、发布版本命名规范

```
agent-security-skill-scanner-{版本号}/
├── cli.py                    # 主入口
├── scanner_cli.py            # 扫描CLI
├── static_analyzer.py         # 静态分析
├── dynamic_detector.py        # 动态检测
├── risk_scanner.py            # 风险扫描
├── detection_rules.json       # 规则库 (核心)
├── install.sh                 # 安装脚本
├── SKILL.md                   # Skill定义
├── README.md                  # 使用说明
├── RELEASE.md                 # 发布说明
└── LICENSE                    # MIT协议
```

---

## 四、版本号规则

| 类型 | 格式 | 说明 |
|------|------|------|
| 主版本 | vX.0.0 | 重大架构变更 |
| 副版本 | v2.X.0 | 新增功能 |
| 修订 | v2.1.X | Bug修复/规则更新 |

---

## 五、质量标准

### 必须通过
- [ ] 所有核心脚本可执行
- [ ] 规则库 JSON 无语法错误
- [ ] README 包含安装和使用说明
- [ ] LICENSE 存在

### 建议通过
- [ ] 运行 `python cli.py --help` 正常
- [ ] 运行 `python cli.py scan <test>` 正常
- [ ] 包含 RELEASE.md 更新日志

---

## 六、发布前检查清单

### ⚠️ 必须检查

| 检查项 | 说明 | 命令 |
|--------|------|------|
| [ ] 无大文件 | 检查是否有 >100MB 的文件 | `du -sh *` |
| [ ] 无敏感信息 | 检查是否有 Token/密钥 | `grep -r "token\\|key\\|secret" .` |
| [ ] 无临时文件 | 检查是否有测试日志/输出 | `ls *.log *.json` |
| [ ] .gitignore 正确 | 确认已排除不需提交的文件 | `cat .gitignore` |

### 🚫 禁止提交

```
# 禁止提交的文件类型
*.log           # 日志文件
*.tmp           # 临时文件
*.json          # 测试输出 (除了配置文件)
release/        # 发布包目录
reports/        # 报告目录
node_modules/  # 依赖目录
__pycache__/   # Python缓存
.DS_Store      # 系统文件
*.sqlite       # 数据库文件
```

### ✅ 正确流程

```bash
# 1. 清理本地测试文件
rm -rf *.log reports/ iteration*.json

# 2. 检查大小
du -sh *

# 3. 检查敏感信息
grep -r "token\|key\|secret" --include="*.py" .

# 4. 运行发布检查
python3 scripts/release_checker.py .

# 5. 提交代码
git add .
git commit -m "v2.x.x: 发布说明"

# 6. 创建版本标签
git tag -a v2.x.x -m "v2.x.x"

# 7. 推送到仓库
git push origin v2.x.x
```

---

*本规范定义了 Skill Scanner 对外发布的最低标准*
