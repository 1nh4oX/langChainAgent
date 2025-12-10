"""
Multi-Agent Trading System Core
多Agent交易分析系统 - 核心模块

实现多Agent协作、辩论机制和工作流编排
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from src.tools import (
    get_stock_history,
    get_stock_news,
    get_stock_technical_indicators,
    get_industry_comparison,
    analyze_stock_comprehensive
)
from src.agent.agent_prompts import get_prompt_by_role


class AgentRole(Enum):
    """Agent角色枚举"""
    DATA_ANALYST = "data_analyst"
    NEWS_RESEARCHER = "news_researcher"
    BULL_REVIEWER = "bull_reviewer"
    BEAR_REVIEWER = "bear_reviewer"
    DEBATE_MODERATOR = "debate_moderator"


@dataclass
class AgentOutput:
    """单个Agent的输出"""
    role: AgentRole
    content: str
    score: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebateRound:
    """辩论轮次记录"""
    round_number: int
    bull_argument: str
    bear_argument: str
    moderator_summary: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class AnalysisResult:
    """完整分析结果"""
    symbol: str
    final_recommendation: str
    confidence: str
    brief_analysis: str
    key_data: Dict[str, Any]
    all_agent_outputs: List[AgentOutput]
    debate_rounds: List[DebateRound]
    debate_occurred: bool
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class MultiAgentTradingSystem:
    """
    多Agent交易分析系统
    
    协调多个Agent进行股票分析，包括数据分析、新闻研究、
    多空评审、辩论机制等
    """
    
    def __init__(
        self,
        analysis_model: str = "Qwen/Qwen2.5-7B-Instruct",
        analysis_api_key: Optional[str] = None,
        analysis_base_url: Optional[str] = None,
        debate_model: Optional[str] = None,
        debate_api_key: Optional[str] = None,
        debate_base_url: Optional[str] = None,
        use_same_model: bool = True,
        debate_threshold: float = 3.0,
        max_debate_rounds: int = 3,
        temperature: float = 0.7
    ):
        """
        初始化多Agent系统
        
        Args:
            analysis_model: 分析环节使用的模型
            analysis_api_key: 分析模型API密钥
            analysis_base_url: 分析模型API地址
            debate_model: 辩论环节使用的模型(如为None且use_same_model=True，使用分析模型)
            debate_api_key: 辩论模型API密钥
            debate_base_url: 辩论模型API地址
            use_same_model: 是否使用相同模型
            debate_threshold: 触发辩论的评分差异阈值
            max_debate_rounds: 最大辩论轮次
            temperature: 温度参数
        """
        load_dotenv()
        
        # 分析环节LLM
        self.analysis_llm = ChatOpenAI(
            model=analysis_model,
            api_key=analysis_api_key or os.getenv("api-key"),
            base_url=analysis_base_url or os.getenv("base-url"),
            temperature=temperature
        )
        
        # 辩论环节LLM
        if use_same_model or debate_model is None:
            self.debate_llm = self.analysis_llm
        else:
            self.debate_llm = ChatOpenAI(
                model=debate_model,
                api_key=debate_api_key or analysis_api_key or os.getenv("api-key"),
                base_url=debate_base_url or analysis_base_url or os.getenv("base-url"),
                temperature=temperature
            )
        
        # 工具准备
        self.tools = [
            get_stock_history,
            get_stock_news,
            get_stock_technical_indicators,
            get_industry_comparison,
            analyze_stock_comprehensive
        ]
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # 配置参数
        self.debate_threshold = debate_threshold
        self.max_debate_rounds = max_debate_rounds
        
        # 绑定工具到LLM
        self.analysis_llm_with_tools = self.analysis_llm.bind_tools(self.tools)
    
    def run_analysis(
        self, 
        symbol: str, 
        verbose: bool = True
    ) -> AnalysisResult:
        """
        运行完整的多Agent分析流程
        
        Args:
            symbol: 股票代码
            verbose: 是否打印详细信息
            
        Returns:
            AnalysisResult对象，包含完整分析结果
        """
        all_outputs = []
        
        # 1. 数据分析师
        if verbose:
            print(f"\n{'='*60}")
            print("🔍 步骤1: 数据分析师正在分析...")
            print(f"{'='*60}")
        
        data_analysis = self._run_data_analyst(symbol, verbose)
        all_outputs.append(data_analysis)
        
        if verbose:
            print(f"\n✅ 数据分析完成")
            print(f"评分: {data_analysis.score}/10")
        
        # 2. 新闻研究员
        if verbose:
            print(f"\n{'='*60}")
            print("📰 步骤2: 新闻研究员正在分析...")
            print(f"{'='*60}")
        
        news_analysis = self._run_news_researcher(symbol, data_analysis.content, verbose)
        all_outputs.append(news_analysis)
        
        if verbose:
            print(f"\n✅ 新闻分析完成")
        
        # 3. 双评审Agent
        if verbose:
            print(f"\n{'='*60}")
            print("⚖️  步骤3: 多空评审正在进行...")
            print(f"{'='*60}")
        
        bull_review, bear_review = self._run_reviewers(
            symbol, 
            data_analysis.content, 
            news_analysis.content,
            verbose
        )
        all_outputs.extend([bull_review, bear_review])
        
        if verbose:
            print(f"\n✅ 评审完成")
            print(f"多头评分: {bull_review.score}/10")
            print(f"空头评分: {bear_review.score}/10")
            print(f"评分差异: {abs(bull_review.score - bear_review.score):.1f}")
        
        # 4. 判断是否需要辩论
        debate_rounds = []
        score_diff = abs(bull_review.score - bear_review.score)
        debate_occurred = score_diff >= self.debate_threshold
        
        if debate_occurred:
            if verbose:
                print(f"\n{'='*60}")
                print(f"🗣️  步骤4: 触发辩论 (差异{score_diff:.1f} >= 阈值{self.debate_threshold})")
                print(f"{'='*60}")
            
            debate_rounds = self._run_debate(
                symbol,
                data_analysis.content,
                news_analysis.content,
                bull_review,
                bear_review,
                verbose
            )
        else:
            if verbose:
                print(f"\n✅ 评分接近，无需辩论 (差异{score_diff:.1f} < 阈值{self.debate_threshold})")
        
        # 5. 生成最终报告
        if verbose:
            print(f"\n{'='*60}")
            print("📊 生成最终报告...")
            print(f"{'='*60}")
        
        final_result = self._generate_final_report(
            symbol,
            all_outputs,
            debate_rounds,
            debate_occurred,
            verbose
        )
        
        if verbose:
            print(f"\n{'='*60}")
            print("✅ 分析完成!")
            print(f"{'='*60}\n")
        
        return final_result
    
    def _run_data_analyst(self, symbol: str, verbose: bool = True) -> AgentOutput:
        """运行数据分析师Agent"""
        # 简化版:直接使用综合分析工具获取数据,然后让LLM分析
        try:
            # 获取综合数据
            raw_data = analyze_stock_comprehensive.invoke({"symbol": symbol})
            
            # 让LLM分析数据并打分
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("data_analyst")),
                ("user", f"""这是股票 {symbol} 的综合数据:

{raw_data}

请基于以上数据进行分析,给出初步评分(1-10分)和关键发现。""")
            ])
            
            response = (prompt | self.analysis_llm).invoke({})
            score = self._extract_score(response.content)
            
            return AgentOutput(
                role=AgentRole.DATA_ANALYST,
                content=response.content,
                score=score,
                metadata={"symbol": symbol}
            )
        except Exception as e:
            return AgentOutput(
                role=AgentRole.DATA_ANALYST,
                content=f"数据分析失败: {str(e)}",
                score=5.0,
                metadata={"symbol": symbol}
            )
    
    def _run_news_researcher(
        self,  
        symbol: str, 
        data_analysis: str, 
        verbose: bool = True
    ) -> AgentOutput:
        """运行新闻研究员Agent"""
        # 简化版:直接获取新闻数据,然后让LLM分析
        try:
            # 获取新闻数据
            news_data = get_stock_news.invoke({"symbol": symbol, "max_news": 10})
            
            # 让LLM分析新闻并给建议
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("news_researcher")),
                ("user", f"""数据分析师的分析结果:
{data_analysis}

股票 {symbol} 的最新新闻:
{news_data}

请结合数据分析和新闻,给出投资建议(买入/持有/卖出)和前景预测。""")
            ])
            
            response = (prompt | self.analysis_llm).invoke({})
            
            return AgentOutput(
                role=AgentRole.NEWS_RESEARCHER,
                content=response.content,
                metadata={"symbol": symbol}
            )
        except Exception as e:
            return AgentOutput(
                role=AgentRole.NEWS_RESEARCHER,
                content=f"新闻分析失败: {str(e)}",
                metadata={"symbol": symbol}
            )
    
    def _run_reviewers(
        self,
        symbol: str,
        data_analysis: str,
        news_analysis: str,
        verbose: bool = True
    ) -> Tuple[AgentOutput, AgentOutput]:
        """运行双评审Agent"""
        context = f"""【数据分析】
{data_analysis}

【新闻研究】
{news_analysis}"""
        
        # 多头评审
        bull_prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("bull_reviewer")),
            ("user", f"请评审以下分析:\n{context}")
        ])
        
        bull_response = (bull_prompt | self.debate_llm).invoke({})
        bull_score = self._extract_score(bull_response.content)
        
        bull_output = AgentOutput(
            role=AgentRole.BULL_REVIEWER,
            content=bull_response.content,
            score=bull_score,
            metadata={"symbol": symbol}
        )
        
        # 空头评审
        bear_prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("bear_reviewer")),
            ("user", f"请评审以下分析:\n{context}")
        ])
        
        bear_response = (bear_prompt | self.debate_llm).invoke({})
        bear_score = self._extract_score(bear_response.content)
        
        bear_output = AgentOutput(
            role=AgentRole.BEAR_REVIEWER,
            content=bear_response.content,
            score=bear_score,
            metadata={"symbol": symbol}
        )
        
        return bull_output, bear_output
    
    def _run_debate(
        self,
        symbol: str,
        data_analysis: str,
        news_analysis: str,
        bull_review: AgentOutput,
        bear_review: AgentOutput,
        verbose: bool = True
    ) -> List[DebateRound]:
        """运行辩论流程"""
        debate_rounds = []
        
        # 辩论上下文
        context = f"""【数据分析】
{data_analysis}

【新闻研究】
{news_analysis}

【多头观点】(评分: {bull_review.score}/10)
{bull_review.content}

【空头观点】(评分: {bear_review.score}/10)
{bear_review.content}"""
        
        for round_num in range(1, self.max_debate_rounds + 1):
            if verbose:
                print(f"\n--- 第 {round_num} 轮辩论 ---")
            
            # 辩论协调员引导
            moderator_prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("debate_moderator")),
                ("user", f"""这是第 {round_num} 轮辩论。

{context}

{''.join([f'【第{r.round_number}轮辩论总结】{r.moderator_summary}' for r in debate_rounds])}

请主持本轮辩论，提炼核心分歧点。""")
            ])
            
            moderator_response = (moderator_prompt | self.debate_llm).invoke({})
            
            # 多头论证
            bull_debate_prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("bull_reviewer")),
                ("user", f"""辩论主持人的引导:
{moderator_response.content}

请针对核心分歧点，进一步论证你的看涨观点。""")
            ])
            
            bull_argument = (bull_debate_prompt | self.debate_llm).invoke({}).content
            
            # 空头论证
            bear_debate_prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("bear_reviewer")),
                ("user", f"""辩论主持人的引导:
{moderator_response.content}

多头的论证:
{bull_argument}

请针对核心分歧点，进一步论证你的看跌观点并回应多头。""")
            ])
            
            bear_argument = (bear_debate_prompt | self.debate_llm).invoke({}).content
            
            # 记录本轮辩论
            debate_round = DebateRound(
                round_number=round_num,
                bull_argument=bull_argument,
                bear_argument=bear_argument,
                moderator_summary=moderator_response.content
            )
            debate_rounds.append(debate_round)
            
            if verbose:
                print(f"✅ 第 {round_num} 轮辩论完成")
        
        return debate_rounds
    
    def _generate_final_report(
        self,
        symbol: str,
        all_outputs: List[AgentOutput],
        debate_rounds: List[DebateRound],
        debate_occurred: bool,
        verbose: bool = True
    ) -> AnalysisResult:
        """生成最终分析报告"""
        # 汇总所有分析
        full_context = "\n\n".join([
            f"【{output.role.value}】\n{output.content}" 
            for output in all_outputs
        ])
        
        if debate_rounds:
            debate_summary = "\n\n".join([
                f"【第{r.round_number}轮辩论】\n主持人: {r.moderator_summary}\n多头: {r.bull_argument}\n空头: {r.bear_argument}"
                for r in debate_rounds
            ])
            full_context += f"\n\n【辩论过程】\n{debate_summary}"
        
        # 生成最终建议
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是投资委员会主席，需要综合所有分析和辩论，给出最终投资建议。

要求:
1. 综合建议: 买入/持有/卖出
2. 信心水平: 高/中/低
3. 简明理由: 2-3句话
4. 关键数据: 最重要的3个数据点
5. 风险提示: 主要风险

格式要简洁专业。"""),
            ("user", f"请基于以下所有分析，给出最终投资建议:\n\n{full_context}")
        ])
        
        final_response = (final_prompt | self.debate_llm).invoke({})
        
        # 提取关键信息
        recommendation = self._extract_recommendation(final_response.content)
        confidence = self._extract_confidence(final_response.content)
        
        # 构建结果
        result = AnalysisResult(
            symbol=symbol,
            final_recommendation=recommendation,
            confidence=confidence,
            brief_analysis=final_response.content,
            key_data={
                "data_analyst_score": all_outputs[0].score,
                "bull_score": all_outputs[2].score,
                "bear_score": all_outputs[3].score,
                "score_diff": abs(all_outputs[2].score - all_outputs[3].score)
            },
            all_agent_outputs=all_outputs,
            debate_rounds=debate_rounds,
            debate_occurred=debate_occurred
        )
        
        return result
    
    def _extract_score(self, content: str) -> float:
        """从内容中提取评分"""
        import re
        # 匹配 "评分: X/10" 或 "X/10分" 等格式
        patterns = [
            r'评分[：:]\s*(\d+(?:\.\d+)?)\s*/\s*10',
            r'(\d+(?:\.\d+)?)\s*/\s*10\s*分',
            r'综合评分[：:]\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    score = float(match.group(1))
                    return min(max(score, 0), 10)  # 限制在0-10之间
                except:
                    pass
        
        return 5.0  # 默认中等评分
    
    def _extract_recommendation(self, content: str) -> str:
        """从内容中提取投资建议"""
        content_lower = content.lower()
        if "买入" in content or "buy" in content_lower:
            return "买入"
        elif "卖出" in content or "sell" in content_lower:
            return "卖出"
        else:
            return "持有"
    
    def _extract_confidence(self, content: str) -> str:
        """从内容中提取信心水平"""
        if "高信心" in content or "信心水平: 高" in content or "信心水平:高" in content:
            return "高"
        elif "低信心" in content or "信心水平: 低" in content or "信心水平:低" in content:
            return "低"
        else:
            return "中"
