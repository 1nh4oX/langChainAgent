# API 文档

## StockAnalysisAgent

### 类：`StockAnalysisAgent`

股票分析 Agent 核心类。

```python
from src.agent import StockAnalysisAgent

agent = StockAnalysisAgent(
    model="Qwen/Qwen2.5-7B-Instruct",
    api_key="your-api-key",
    base_url="https://api.siliconflow.cn/v1",
    temperature=0.3,
    max_iterations=10
)
```

#### 参数

- **model** (`str`, optional): 模型名称，默认 `"Qwen/Qwen2.5-7B-Instruct"`
- **api_key** (`str`, optional): API 密钥，默认从环境变量读取
- **base_url** (`str`, optional): API 基础URL，默认从环境变量读取
- **temperature** (`float`, optional): 温度参数，默认 `0.3`
- **max_iterations** (`int`, optional): 最大迭代次数，默认 `10`

#### 方法

##### `run(query: str, verbose: bool = True) -> Dict[str, str]`

运行 Agent 执行查询。

**参数：**
- **query** (`str`): 用户查询
- **verbose** (`bool`, optional): 是否打印详细信息，默认 `True`

**返回：**
- `Dict[str, str]`: 包含 `'output'` 和 `'iterations'` 的字典

**示例：**

```python
result = agent.run("分析贵州茅台的最近走势")
print(result['output'])
print(f"迭代次数: {result['iterations']}")
```

##### `add_tool(tool) -> None`

添加自定义工具。

**参数：**
- **tool**: LangChain tool 对象

**示例：**

```python
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """工具描述"""
    return "result"

agent.add_tool(my_tool)
```

---

## 工具函数

### `get_stock_history`

获取股票历史行情数据。

```python
from src.tools import get_stock_history

result = get_stock_history.invoke({"symbol": "600519"})
```

**参数：**
- **symbol** (`str`): 股票代码（6位数字）

**返回：**
- `str`: Markdown 格式的历史数据表格

---

### `get_stock_news`

获取股票新闻资讯。

```python
from src.tools import get_stock_news

result = get_stock_news.invoke({
    "symbol": "600519",
    "max_news": 10
})
```

**参数：**
- **symbol** (`str`): 股票代码
- **max_news** (`int`, optional): 返回的新闻条数，默认 10

**返回：**
- `str`: 格式化的新闻列表

---

### `get_stock_technical_indicators`

计算股票技术指标。

```python
from src.tools import get_stock_technical_indicators

result = get_stock_technical_indicators.invoke({"symbol": "600519"})
```

**参数：**
- **symbol** (`str`): 股票代码

**返回：**
- `str`: 技术指标分析文本（MA5/MA10/MA20、涨跌幅等）

---

### `get_industry_comparison`

获取行业对比信息。

```python
from src.tools import get_industry_comparison

result = get_industry_comparison.invoke({"symbol": "600519"})
```

**参数：**
- **symbol** (`str`): 股票代码

**返回：**
- `str`: 股票基本信息和行业数据

---

### `analyze_stock_comprehensive`

综合分析。

```python
from src.tools import analyze_stock_comprehensive

result = analyze_stock_comprehensive.invoke({"symbol": "600519"})
```

**参数：**
- **symbol** (`str`): 股票代码

**返回：**
- `str`: 综合分析报告

---

## 工具函数

### 文件操作

#### `save_to_csv(data, filepath, encoding='utf-8-sig')`

保存 DataFrame 到 CSV 文件。

```python
from src.utils import save_to_csv
import pandas as pd

df = pd.DataFrame(...)
save_to_csv(df, "data/output.csv")
```

#### `save_to_json(data, filepath, indent=2)`

保存数据到 JSON 文件。

```python
from src.utils import save_to_json

data = {"key": "value"}
save_to_json(data, "data/output.json")
```

#### `load_from_json(filepath)`

从 JSON 文件加载数据。

```python
from src.utils import load_from_json

data = load_from_json("data/input.json")
```

### 日期处理

#### `get_current_date(fmt="%Y%m%d")`

获取当前日期。

```python
from src.utils import get_current_date

date = get_current_date()  # "20251203"
date_readable = get_current_date("%Y-%m-%d")  # "2025-12-03"
```

#### `get_date_range(days=30, fmt="%Y%m%d")`

获取日期范围。

```python
from src.utils import get_date_range

start, end = get_date_range(30)  # 最近30天
```

#### `format_date(date_str, input_fmt, output_fmt)`

转换日期格式。

```python
from src.utils import format_date

formatted = format_date("20251203", "%Y%m%d", "%Y-%m-%d")
# "2025-12-03"
```

---

## 配置管理

### `get_settings()`

获取全局配置。

```python
from src.config import get_settings

settings = get_settings()
print(settings.api_key)
print(settings.model)
```

**返回属性：**
- `api_key`: API 密钥
- `base_url`: API 基础URL
- `model`: 模型名称
- `temperature`: 温度参数
- `max_iterations`: 最大迭代次数
- `data_dir`: 数据目录

---

## 错误处理

所有工具函数都包含错误处理，返回友好的错误信息字符串。

```python
result = get_stock_history.invoke({"symbol": "invalid"})
# 返回: "获取数据失败: ..."
```

---

## 类型提示

项目使用 Python 类型提示，可以使用 mypy 进行类型检查：

```bash
mypy src/
```




