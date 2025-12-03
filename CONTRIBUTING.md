# 贡献指南

感谢你考虑为 Stock Analysis Agent 项目做出贡献！

## 🎯 贡献方式

你可以通过以下方式为项目做贡献：

1. **报告Bug** - 发现问题？[提交 Issue](https://github.com/yourusername/stock-analysis-agent/issues)
2. **建议功能** - 有好想法？告诉我们！
3. **改进文档** - 文档写得不清楚？帮我们改进
4. **提交代码** - 修复 Bug 或添加新功能

## 📋 开发准备

### 环境要求

- Python 3.8+
- Git
- 文本编辑器或 IDE (推荐 VS Code, PyCharm)

### 设置开发环境

```bash
# 1. Fork 并克隆项目
git clone https://github.com/your-username/stock-analysis-agent.git
cd stock-analysis-agent

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 .env 文件
cp .env.example .env
# 编辑 .env 填入你的 API 配置

# 5. 运行测试确保环境正常
python app.py
```

## 🔧 开发流程

### 1. 创建功能分支

```bash
# 从 main 分支创建新分支
git checkout -b feature/your-feature-name

# 或修复 Bug
git checkout -b fix/bug-description
```

### 2. 进行开发

#### 代码规范

- 遵循 [PEP 8](https://pep8.org/) Python 代码规范
- 函数和类添加文档字符串 (docstring)
- 变量命名要有意义
- 保持代码简洁清晰

示例：

```python
def get_stock_data(symbol: str, days: int = 30) -> dict:
    """
    获取股票数据
    
    Args:
        symbol: 股票代码，6位数字
        days: 获取天数，默认30天
        
    Returns:
        包含股票数据的字典
        
    Raises:
        ValueError: 当股票代码格式错误时
        
    Example:
        >>> data = get_stock_data("600519", days=10)
    """
    # 实现逻辑
    pass
```

#### 添加新工具

在 `src/tools/` 目录创建新工具：

```python
from langchain_core.tools import tool

@tool
def your_new_tool(param: str) -> str:
    """
    工具描述（这会被 LLM 看到）
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
    """
    # 实现逻辑
    return "result"
```

不要忘记在 `src/tools/__init__.py` 导出：

```python
from .your_module import your_new_tool

__all__ = [
    # ... 其他工具
    'your_new_tool',
]
```

### 3. 编写测试

在 `tests/` 目录添加测试：

```python
# tests/test_new_tool.py
import pytest
from src.tools import your_new_tool

def test_your_new_tool():
    """测试新工具"""
    result = your_new_tool.invoke({"param": "test"})
    assert result == "expected"

def test_your_new_tool_error():
    """测试错误情况"""
    with pytest.raises(ValueError):
        your_new_tool.invoke({"param": "invalid"})
```

运行测试：

```bash
pytest tests/
```

### 4. 提交代码

```bash
# 添加修改的文件
git add .

# 提交（使用有意义的提交信息）
git commit -m "feat: add new stock analysis tool"

# 推送到你的 fork
git push origin feature/your-feature-name
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` - 新功能
- `fix:` - Bug 修复
- `docs:` - 文档更新
- `style:` - 代码格式调整（不影响功能）
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建/工具相关

示例：

```
feat: add financial report analysis tool
fix: resolve error when stock code is invalid
docs: update README with new features
refactor: simplify agent initialization logic
```

### 5. 创建 Pull Request

1. 访问你的 fork 页面
2. 点击 "Pull Request" 按钮
3. 填写 PR 描述：
   - 解决的问题
   - 实现方法
   - 测试情况
   - 相关 Issue (如果有)

## 📝 代码审查

提交 PR 后，维护者会进行代码审查。请：

- 及时回复评论
- 根据反馈修改代码
- 保持耐心和礼貌

## 🎨 项目规划

### 当前优先级

#### 高优先级 🔴
- [ ] 添加更多股票分析工具（财务指标、资金流向）
- [ ] 实现数据缓存机制
- [ ] 添加单元测试覆盖
- [ ] 改进错误处理

#### 中优先级 🟡
- [ ] Streamlit Web UI
- [ ] API 服务接口
- [ ] 批量分析功能
- [ ] 数据可视化（K线图）

#### 低优先级 🟢
- [ ] 国际化 (i18n)
- [ ] Docker 容器化
- [ ] CI/CD 自动化
- [ ] 性能优化

### 建议的新功能

如果你想贡献但不知道从哪里开始，可以考虑：

1. **新工具**
   - 财务报表分析
   - 龙虎榜数据
   - 大宗交易监控
   - 股东变动追踪
   
2. **功能增强**
   - 添加数据缓存
   - 支持多股票对比
   - 实现流式输出
   - 添加配置UI

3. **文档改进**
   - 添加更多示例
   - 翻译为英文
   - 视频教程
   - API 文档

4. **测试**
   - 增加测试覆盖率
   - 添加集成测试
   - 性能基准测试

## 🐛 报告 Bug

发现 Bug？请 [创建 Issue](https://github.com/yourusername/stock-analysis-agent/issues/new) 并包含：

- **Bug 描述** - 清晰描述问题
- **复现步骤** - 如何触发这个 Bug
- **预期行为** - 应该发生什么
- **实际行为** - 实际发生了什么
- **环境信息** - Python 版本、操作系统等
- **截图/日志** - 如果可能的话

示例：

```markdown
### Bug 描述
调用 get_stock_history 时出现编码错误

### 复现步骤
1. 运行 `python app.py`
2. 输入 "查询贵州茅台"
3. 出现 UnicodeEncodeError

### 环境
- Python: 3.9.0
- OS: Windows 10
- LangChain: 0.1.0

### 错误日志
```
UnicodeEncodeError: 'ascii' codec can't encode characters...
```
```

## 💡 建议功能

有新想法？[创建 Issue](https://github.com/yourusername/stock-analysis-agent/issues/new) 描述：

- **功能描述** - 想要什么功能
- **使用场景** - 为什么需要这个功能
- **建议实现** - 如何实现（可选）

## 📚 资源

- [LangChain 文档](https://python.langchain.com/)
- [AkShare 文档](https://akshare.akfamily.xyz/)
- [Python 风格指南](https://pep8.org/)
- [如何写好 Git Commit](https://chris.beams.io/posts/git-commit/)

## ❓ 问题？

- 查看 [FAQ](docs/FAQ.md)
- 搜索 [Issues](https://github.com/yourusername/stock-analysis-agent/issues)
- 加入讨论 [Discussions](https://github.com/yourusername/stock-analysis-agent/discussions)

## 🙏 感谢

感谢所有贡献者！你们的努力让这个项目更好。

---

再次感谢你的贡献！Happy Coding! 🚀


