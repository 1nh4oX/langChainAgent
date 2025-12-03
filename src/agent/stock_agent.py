"""
Stock Analysis Agent
股票分析 Agent 核心实现
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, ToolMessage

from src.tools import (
    get_stock_history,
    get_stock_news,
    get_stock_technical_indicators,
    get_industry_comparison,
    analyze_stock_comprehensive
)


class StockAnalysisAgent:
    """
    股票分析 Agent
    
    支持多轮工具调用和推理，提供专业的股票分析服务。
    
    Attributes:
        llm: 大语言模型
        tools: 可用的工具列表
        tool_map: 工具名称到工具对象的映射
        max_iterations: 最大迭代次数
    """
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一个专业的A股股票分析助手，具备以下能力：

🎯 分析流程（请按此顺序思考）：
1. 理解用户需求：用户想了解什么？（基本面/技术面/新闻面/综合）
2. 选择合适工具：
   - get_stock_history: 查看历史价格走势
   - get_stock_news: 获取最新新闻资讯
   - get_stock_technical_indicators: 计算技术指标（均线、涨跌幅）
   - get_industry_comparison: 了解行业地位和估值
   - analyze_stock_comprehensive: 一键获取综合信息
3. 工具调用策略：
   - 简单查询：使用1-2个工具
   - 深度分析：使用3-4个工具，全面评估
   - 必须基于工具返回的真实数据，禁止编造
4. 输出专业报告：
   - 数据呈现清晰（表格/列表）
   - 分析客观专业
   - 给出明确结论和建议

⚠️ 重要原则：
- 所有数据必须来自工具调用结果
- 如果工具调用失败，诚实告知用户
- 不进行股票推荐，只做客观分析
- 分析时要结合多个维度（技术+基本面+新闻）"""
    
    def __init__(
        self, 
        model: str = "Qwen/Qwen2.5-7B-Instruct",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.3,
        max_iterations: int = 10
    ):
        """
        初始化 Stock Analysis Agent
        
        Args:
            model: 模型名称
            api_key: API密钥（如果不提供，从环境变量读取）
            base_url: API基础URL（如果不提供，从环境变量读取）
            temperature: 温度参数
            max_iterations: 最大迭代次数
        """
        # 加载环境变量
        load_dotenv()
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key or os.getenv("api-key"),
            base_url=base_url or os.getenv("base-url"),
            temperature=temperature
        )
        
        # 准备工具
        self.tools = [
            get_stock_history,
            get_stock_news,
            get_stock_technical_indicators,
            get_industry_comparison,
            analyze_stock_comprehensive
        ]
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # 绑定工具到 LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 构建 Prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("user", "{input}"),
        ])
        
        # 创建 Agent Runnable
        self.agent_runnable = self.prompt | self.llm_with_tools
        
        self.max_iterations = max_iterations
    
    def run(self, query: str, verbose: bool = True) -> Dict[str, str]:
        """
        运行 Agent 执行查询
        
        Args:
            query: 用户查询
            verbose: 是否打印详细信息
            
        Returns:
            包含 'output' 和 'iterations' 的字典
        """
        input_dict = {
            "input": query,
            "agent_scratchpad": []
        }
        
        result = self._run_loop(input_dict, verbose=verbose)
        return result
    
    def _run_loop(
        self, 
        input_dict: Dict, 
        iteration: int = 0,
        verbose: bool = True
    ) -> Dict[str, str]:
        """
        Agent 执行循环（递归实现）
        
        Args:
            input_dict: 输入字典，包含 input 和 agent_scratchpad
            iteration: 当前迭代次数
            verbose: 是否打印详细信息
            
        Returns:
            包含 'output' 和 'iterations' 的字典
        """
        # 检查是否达到最大迭代次数
        if iteration >= self.max_iterations:
            return {
                "output": "Agent 执行次数过多，无法得出结论，请尝试具体化问题。",
                "iterations": iteration
            }
        
        # 调用 LLM
        llm_output = self.agent_runnable.invoke(input_dict)
        
        # 检查是否需要调用工具
        if not llm_output.tool_calls:
            return {
                "output": llm_output.content,
                "iterations": iteration + 1
            }
        
        # 执行工具调用
        tool_messages = []
        for tool_call in llm_output.tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["args"]
            
            if tool_name in self.tool_map:
                if verbose:
                    print(f"\n[Tool Execution] Invoking: {tool_name}")
                    print(f"  Args: {tool_input}")
                
                try:
                    tool_output = self.tool_map[tool_name].invoke(tool_input)
                    
                    if verbose:
                        print(f"  Result size: {len(str(tool_output))} chars")
                    
                    tool_messages.append(
                        ToolMessage(
                            content=str(tool_output),
                            tool_call_id=tool_call["id"]
                        )
                    )
                except Exception as e:
                    error_msg = f"Tool execution failed: {str(e)}"
                    if verbose:
                        print(f"  Error: {error_msg}")
                    tool_messages.append(
                        ToolMessage(
                            content=error_msg,
                            tool_call_id=tool_call["id"]
                        )
                    )
            else:
                error_msg = f"Error: Tool {tool_name} not found."
                tool_messages.append(AIMessage(content=error_msg))
        
        # 更新 scratchpad 并递归调用
        new_scratchpad = input_dict.get("agent_scratchpad", []) + [llm_output] + tool_messages
        
        return self._run_loop(
            {"input": input_dict["input"], "agent_scratchpad": new_scratchpad},
            iteration=iteration + 1,
            verbose=verbose
        )
    
    def add_tool(self, tool):
        """
        添加新工具
        
        Args:
            tool: LangChain tool对象
        """
        self.tools.append(tool)
        self.tool_map[tool.name] = tool
        # 重新绑定工具
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.agent_runnable = self.prompt | self.llm_with_tools


def run_agent_loop(input_dict: Dict, max_iterations: int = 10) -> Dict[str, str]:
    """
    便捷函数：运行 Agent 循环（保持向后兼容）
    
    Args:
        input_dict: 包含 'input' 和 'agent_scratchpad' 的字典
        max_iterations: 最大迭代次数
        
    Returns:
        包含 'output' 的字典
    """
    agent = StockAnalysisAgent(max_iterations=max_iterations)
    result = agent.run(input_dict["input"])
    return {"output": result["output"]}


if __name__ == "__main__":
    # 测试代码
    agent = StockAnalysisAgent()
    result = agent.run("查询贵州茅台（600519）的最新情况")
    print("\n" + "="*60)
    print("Agent 输出:")
    print("="*60)
    print(result["output"])
    print(f"\n总迭代次数: {result['iterations']}")


