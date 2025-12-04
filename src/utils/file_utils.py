"""
File Utilities
文件处理工具
"""

import json
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List


def save_to_csv(data: pd.DataFrame, filepath: str, encoding: str = 'utf-8-sig') -> None:
    """
    保存 DataFrame 到 CSV 文件
    
    Args:
        data: DataFrame对象
        filepath: 文件路径
        encoding: 编码格式，默认 utf-8-sig（支持Excel打开中文）
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(filepath, index=False, encoding=encoding)
    # print(f"✅ CSV 文件已保存: {filepath}")


def save_to_json(data: Any, filepath: str, indent: int = 2) -> None:
    """
    保存数据到 JSON 文件
    
    Args:
        data: 要保存的数据
        filepath: 文件路径
        indent: 缩进空格数
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        if isinstance(data, pd.DataFrame):
            data.to_json(f, orient='records', force_ascii=False, indent=indent)
        else:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    
    # print(f"✅ JSON 文件已保存: {filepath}")


def load_from_json(filepath: str) -> Any:
    """
    从 JSON 文件加载数据
    
    Args:
        filepath: 文件路径
        
    Returns:
        加载的数据
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)



