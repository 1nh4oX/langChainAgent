"""
Settings Management
配置管理
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Settings:
    """
    应用配置类
    
    Attributes:
        api_key: LLM API密钥
        base_url: LLM API基础URL
        model: 模型名称
        temperature: 温度参数
        max_iterations: Agent最大迭代次数
        data_dir: 数据目录
    """
    api_key: str
    base_url: str
    model: str = "Qwen/Qwen2.5-7B-Instruct"
    temperature: float = 0.3
    max_iterations: int = 10
    data_dir: str = "data"
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """
        从环境变量加载配置
        
        Returns:
            Settings对象
        """
        load_dotenv()
        
        return cls(
            api_key=os.getenv("api-key", ""),
            base_url=os.getenv("base-url", ""),
            model=os.getenv("model", "Qwen/Qwen2.5-7B-Instruct"),
            temperature=float(os.getenv("temperature", "0.3")),
            max_iterations=int(os.getenv("max_iterations", "10")),
            data_dir=os.getenv("data_dir", "data")
        )


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    获取全局配置实例（单例模式）
    
    Returns:
        Settings对象
    """
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


