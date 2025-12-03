# 🔄 项目重构迁移指南

## 📋 概述

项目已从单文件结构重构为标准的 GitHub 项目结构，便于团队协作和持续开发。

## ✅ 完成的工作

### 1. 新的目录结构 ✨

```
stock-analysis-agent/
├── src/                    # 📦 源代码（模块化）
│   ├── agent/              # Agent 核心
│   ├── tools/              # 工具集
│   ├── config/             # 配置管理
│   └── utils/              # 工具函数
├── scripts/                # 🛠️ 脚本工具
├── tests/                  # 🧪 测试（预留）
├── data/                   # 💾 数据目录
├── docs/                   # 📚 完整文档
├── examples/               # 📖 示例代码
├── ui/                     # 🎨 UI界面（预留）
└── app.py                  # 🚀 新的主入口
```

### 2. 代码模块化 🎯

#### 旧结构（单文件）
```
main.py                 # 所有代码在一个文件
stock_tools.py          # 工具函数
collect_news.py         # 脚本
```

#### 新结构（模块化）
```python
# src/agent/stock_agent.py - Agent 类
class StockAnalysisAgent:
    def __init__(self, model, api_key, ...): pass
    def run(self, query): pass
    def add_tool(self, tool): pass

# src/tools/stock_data.py - 工具模块
@tool
def get_stock_history(symbol): pass
# ... 5 个工具

# src/config/settings.py - 配置管理
class Settings:
    @classmethod
    def from_env(cls): pass

# src/utils/ - 工具函数
def save_to_csv(...): pass
def get_date_range(...): pass
```

### 3. 项目管理文件 📄

| 文件 | 作用 |
|------|------|
| `.gitignore` | Git 忽略规则（数据文件、环境等） |
| `LICENSE` | MIT 许可证 |
| `.env.example` | 配置模板（多个免费 API 方案） |
| `setup.py` | 包安装配置 |
| `CONTRIBUTING.md` | 贡献指南（开发流程、代码规范） |
| `README_NEW.md` | 新的项目说明（专业 GitHub 风格） |

### 4. 完整文档 📚

| 文档 | 内容 |
|------|------|
| `docs/API.md` | 完整的 API 文档 |
| `docs/PROJECT_STRUCTURE.md` | 项目结构说明 |
| `docs/CHANGELOG.md` | 版本更新历史 |
| `CONTRIBUTING.md` | 开发贡献指南 |

### 5. 示例代码 📖

| 示例 | 说明 |
|------|------|
| `examples/basic_usage.py` | 6个基础到高级示例 |
| `examples/add_custom_tool.py` | 自定义工具完整示例 |

## 🔧 如何使用新结构

### 方式1: 使用新的主程序

```bash
# 交互式运行（推荐）
python app.py

# 采集新闻
python scripts/collect_news.py

# 运行示例
python examples/basic_usage.py
```

### 方式2: 作为包使用

```python
# 在你的代码中导入
from src.agent import StockAnalysisAgent
from src.tools import get_stock_history, get_stock_news
from src.config import get_settings

# 使用 Agent
agent = StockAnalysisAgent()
result = agent.run("分析贵州茅台")

# 直接使用工具
data = get_stock_history.invoke({"symbol": "600519"})
```

### 方式3: 安装为包

```bash
# 开发模式安装
pip install -e .

# 然后可以在任何地方导入
from src.agent import StockAnalysisAgent
```

## 📦 旧文件处理

### 迁移脚本

运行迁移脚本自动整理旧文件：

```bash
python scripts/migrate_old_files.py
```

脚本会：
- ✅ 移动数据文件到 `data/raw/`
- ✅ 移动文档到 `docs/`
- ✅ 备份旧代码到 `old_files/`
- ✅ 保留原文件的时间戳

### 手动整理

如果不想运行脚本，可以手动整理：

```bash
# 移动数据文件
mv *.csv *.json *.xlsx data/raw/
mv *_report_*.txt data/raw/

# 移动文档
mv 作业报告.md 作业提交-打印版.txt docs/

# 备份旧代码（确认新代码正常后可删除）
mkdir -p old_files
cp main.py stock_tools.py collect_news.py old_files/
```

## 🎯 团队协作

### Git 工作流

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd stock-analysis-agent

# 2. 创建功能分支
git checkout -b feature/your-feature

# 3. 进行开发
# 编辑 src/tools/ 添加新工具
# 更新 docs/API.md 文档

# 4. 提交代码
git add .
git commit -m "feat: add new analysis tool"
git push origin feature/your-feature

# 5. 创建 Pull Request
# 在 GitHub 上创建 PR 供团队审查
```

### 开发规范

1. **代码风格**: 遵循 PEP 8
2. **提交信息**: 使用 Conventional Commits
3. **文档**: 更新相关文档
4. **测试**: 添加测试（在 `tests/` 目录）

详见 `CONTRIBUTING.md`

## 🚀 扩展功能

### 添加新工具

```python
# 1. 在 src/tools/ 创建或编辑文件
# src/tools/financial_tools.py

from langchain_core.tools import tool

@tool
def get_financial_report(symbol: str) -> str:
    """获取财务报表"""
    # 实现逻辑
    return "财务数据"

# 2. 在 src/tools/__init__.py 导出
from .financial_tools import get_financial_report

__all__ = [
    # ... 现有工具
    'get_financial_report',
]

# 3. 在 Agent 中使用
from src.agent import StockAnalysisAgent

agent = StockAnalysisAgent()
agent.add_tool(get_financial_report)  # 动态添加
```

### 开发 Web UI

```bash
# 1. 安装 Streamlit
pip install streamlit

# 2. 在 ui/ 目录创建 app.py
# ui/streamlit_app.py

import streamlit as st
from src.agent import StockAnalysisAgent

st.title("📊 股票分析 Agent")

agent = StockAnalysisAgent()
query = st.text_input("输入你的问题:")

if query:
    result = agent.run(query)
    st.write(result['output'])

# 3. 运行
streamlit run ui/streamlit_app.py
```

### 添加数据可视化

```python
# 在 src/utils/ 添加可视化函数
# src/utils/visualization.py

import matplotlib.pyplot as plt
import pandas as pd

def plot_stock_trend(df: pd.DataFrame) -> None:
    """绘制股票走势图"""
    plt.figure(figsize=(12, 6))
    plt.plot(df['日期'], df['收盘'], label='收盘价')
    plt.plot(df['日期'], df['MA5'], label='MA5')
    plt.plot(df['日期'], df['MA10'], label='MA10')
    plt.legend()
    plt.title('股票走势图')
    plt.show()
```

## 📊 新旧对比

| 方面 | 旧结构 | 新结构 | 优势 |
|------|--------|--------|------|
| 代码组织 | 单文件 | 模块化 | ✅ 易维护、可扩展 |
| 文档 | README | 完整文档 | ✅ 专业、详细 |
| 示例 | 无 | 多个示例 | ✅ 易上手 |
| 配置管理 | 分散 | 集中管理 | ✅ 统一配置 |
| 工具函数 | 混在一起 | 独立模块 | ✅ 复用方便 |
| 团队协作 | 困难 | 标准流程 | ✅ Git工作流 |
| 测试 | 无结构 | tests/ 目录 | ✅ 规范测试 |
| 扩展性 | 低 | 高 | ✅ 易添加功能 |

## ✨ 新功能支持

新结构支持以下扩展：

### 1. 插件系统
```python
# 工具可以动态加载
agent.add_tool(my_custom_tool)
```

### 2. 配置管理
```python
# 统一的配置接口
from src.config import get_settings
settings = get_settings()
```

### 3. 工具函数复用
```python
# 独立的工具函数可以在任何地方使用
from src.utils import save_to_csv, get_date_range
```

### 4. 类型安全
```python
# 所有函数都有类型提示
def get_stock_history(symbol: str) -> str:
    pass
```

## 🔍 注意事项

### 1. 导入路径变化

**旧代码:**
```python
from stock_tools import get_stock_history
```

**新代码:**
```python
from src.tools import get_stock_history
```

### 2. Agent 使用变化

**旧代码:**
```python
response = run_agent_loop({"input": query, "agent_scratchpad": []})
```

**新代码:**
```python
agent = StockAnalysisAgent()
result = agent.run(query)
```

### 3. 配置文件

**旧方式:**
```python
api_key = os.getenv("api-key")
```

**新方式:**
```python
from src.config import get_settings
settings = get_settings()
api_key = settings.api_key
```

## 📚 学习资源

- **项目结构**: 查看 `docs/PROJECT_STRUCTURE.md`
- **API 文档**: 查看 `docs/API.md`
- **代码示例**: 查看 `examples/` 目录
- **贡献指南**: 查看 `CONTRIBUTING.md`
- **更新日志**: 查看 `docs/CHANGELOG.md`

## 🤝 参与开发

1. 阅读 `CONTRIBUTING.md` 了解开发流程
2. 查看 GitHub Issues 找任务
3. 创建功能分支开发
4. 提交 Pull Request
5. 代码审查和合并

## ❓ 常见问题

### Q: 旧代码还能用吗？
A: 能，但建议迁移到新结构。旧文件已备份在 `old_files/` 目录。

### Q: 如何快速开始？
A: 运行 `python app.py` 即可使用新版本。

### Q: 如何添加自定义工具？
A: 查看 `examples/add_custom_tool.py` 示例。

### Q: 数据文件在哪？
A: 运行 `python scripts/migrate_old_files.py` 会移动到 `data/raw/` 目录。

### Q: 如何贡献代码？
A: 参考 `CONTRIBUTING.md` 中的详细说明。

## 🎉 下一步

1. ✅ 测试新结构是否正常：`python app.py`
2. ✅ 运行示例代码：`python examples/basic_usage.py`
3. ✅ 整理旧文件：`python scripts/migrate_old_files.py`
4. ✅ 初始化 Git 仓库（如果还没有）
5. ✅ 推送到 GitHub
6. ✅ 邀请团队成员协作

---

**祝你们的项目越来越好！** 🚀

有任何问题欢迎提 Issue 或查看文档！


