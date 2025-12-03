"""
Date Utilities
日期处理工具
"""

import datetime
from typing import Tuple


def get_current_date(fmt: str = "%Y%m%d") -> str:
    """
    获取当前日期
    
    Args:
        fmt: 日期格式，默认 YYYYMMDD
        
    Returns:
        格式化的日期字符串
    """
    return datetime.datetime.now().strftime(fmt)


def get_date_range(days: int = 30, fmt: str = "%Y%m%d") -> Tuple[str, str]:
    """
    获取日期范围
    
    Args:
        days: 天数
        fmt: 日期格式
        
    Returns:
        (start_date, end_date) 元组
    """
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    return start_date.strftime(fmt), end_date.strftime(fmt)


def format_date(date_str: str, input_fmt: str = "%Y%m%d", output_fmt: str = "%Y-%m-%d") -> str:
    """
    转换日期格式
    
    Args:
        date_str: 输入日期字符串
        input_fmt: 输入格式
        output_fmt: 输出格式
        
    Returns:
        转换后的日期字符串
    """
    date_obj = datetime.datetime.strptime(date_str, input_fmt)
    return date_obj.strftime(output_fmt)


