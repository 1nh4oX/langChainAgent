"""
Enhanced Multi-Agent Trading System
增强版多Agent交易分析系统

实现完整的4层agent架构:
- Layer 1: Analyst Team (4个专业分析师)
- Layer 2: Researcher Team (多空辩论)
- Layer 3: Trader Agent (交易决策)
- Layer 4: Risk Management + Portfolio Manager (风险评估和最终决策)
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.tools import (
    # Technical Analyst tools
    get_stock_history,
    get_stock_technical_indicators,
    get_industry_comparison,
    # Fundamentals Analyst tools
    get_company_financials,
    calculate_intrinsic_value,
    get_performance_metrics,
    identify_red_flags,
    # Sentiment Analyst tools
    analyze_social_media_sentiment,
    get_public_sentiment_score,
    track_market_mood,
    # News Analyst tools
    analyze_news_sentiment,
    get_macroeconomic_indicators,
    assess_event_impact,
    get_global_market_news,
)

from src.agent.agent_prompts_enhanced import get_prompt_by_role


class AgentRole(Enum):
    """Enhanced Agent角色枚举"""
    # Analyst Team
    FUNDAMENTALS_ANALYST = "fundamentals_analyst"
    SENTIMENT_ANALYST = "sentiment_analyst"
    NEWS_ANALYST = "news_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    
    # Researcher Team
    BULLISH_RESEARCHER = "bullish_researcher"
    BEARISH_RESEARCHER = "bearish_researcher"
    
    # Decision Layer
    TRADER = "trader"
    RISK_MANAGER_AGGRESSIVE = "risk_manager_aggressive"
    RISK_MANAGER_NEUTRAL = "risk_manager_neutral"
    RISK_MANAGER_CONSERVATIVE = "risk_manager_conservative"
    PORTFOLIO_MANAGER = "portfolio_manager"
    
    # Moderator
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
class AnalystTeamReport:
    """分析师团队报告"""
    fundamentals: AgentOutput
    sentiment: AgentOutput
    news: AgentOutput
    technical: AgentOutput
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class ResearcherDebate:
    """研究员辩论记录"""
    bullish: AgentOutput
    bearish: AgentOutput
    score_diff: float
    debate_occurred: bool
    debate_rounds: List = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class TraderDecision:
    """交易员决策"""
    decision: AgentOutput
    recommendation: str  # 买入/持有/卖出
    suggested_position: str  # 轻仓/半仓/重仓)
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class RiskAssessment:
    """风险评估(3个视角)"""
    aggressive: AgentOutput
    neutral: AgentOutput
    conservative: AgentOutput
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class FinalDecision:
    """最终决策"""
    decision: AgentOutput
    recommendation: str
    confidence: str
    position_suggestions: Dict[str, str]  # 不同风险偏好的仓位建议
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class EnhancedAnalysisResult:
    """完整的增强版分析结果"""
    symbol: str
    # Layer 1: Analyst Team
    analyst_team: AnalystTeamReport
    # Layer 2: Researcher Team
    researcher_debate: ResearcherDebate
    # Layer 3: Trader
    trader_decision: TraderDecision
    # Layer 4: Risk & Portfolio
    risk_assessment: RiskAssessment
    final_decision: FinalDecision
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class EnhancedMultiAgentSystem:
    """
    增强版多Agent交易分析系统
    
    4层架构:
    1. Analyst Team: 4个专业分析师并行工作
    2. Researcher Team: 多空辩论
    3. Trader: 交易决策
    4. Risk Management + Portfolio Manager: 最终决策
    """
    
    def __init__(
        self,
        model: str = "Qwen/Qwen2.5-7B-Instruct",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        debate_threshold: float = 3.0,
        max_debate_rounds: int = 2,
        temperature: float = 0.7
    ):
        """
        初始化增强版多Agent系统
        
        Args:
            model: 使用的LLM模型
            api_key: API密钥
            base_url: API地址
            debate_threshold: 触发辩论的评分差异阈值
            max_debate_rounds: 最大辩论轮次
            temperature: LLM温度参数
        """
        load_dotenv()
        
        # LLM配置
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key or os.getenv("api-key"),
            base_url=base_url or os.getenv("base-url"),
            temperature=temperature
        )
        
        # 参数配置
        self.debate_threshold = debate_threshold
        self.max_debate_rounds = max_debate_rounds
    
    def run_analysis(
        self,
        symbol: str,
        verbose: bool = True
    ) -> EnhancedAnalysisResult:
        """
        运行完整的增强版多Agent分析流程
        
        Args:
            symbol: 股票代码
            verbose: 是否打印详细信息
            
        Returns:
            EnhancedAnalysisResult对象
        """
        # ========== Layer 1: Analyst Team ==========
        if verbose:
            print(f"\n{'='*70}")
            print("📊 第1层: 分析师团队并行分析")
            print(f"{'='*70}")
        
        analyst_team = self._run_analyst_team(symbol, verbose)
        
        # ========== Layer 2: Researcher Team ==========
        if verbose:
            print(f"\n{'='*70}")
            print("🗣️  第2层: 研究员团队辩论")
            print(f"{'='*70}")
        
        researcher_debate = self._run_researcher_team(symbol, analyst_team, verbose)
        
        # ========== Layer 3: Trader ==========
        if verbose:
            print(f"\n{'='*70}")
            print("💼 第3层: 交易员决策")
            print(f"{'='*70}")
        
        trader_decision = self._run_trader(symbol, analyst_team, researcher_debate, verbose)
        
        # ========== Layer 4: Risk & Portfolio ==========
        if verbose:
            print(f"\n{'='*70}")
            print("⚖️  第4层: 风险评估与最终决策")
            print(f"{'='*70}")
        
        risk_assessment = self._run_risk_management(trader_decision, verbose)
        final_decision = self._run_portfolio_manager(
            symbol, analyst_team, researcher_debate, trader_decision, risk_assessment, verbose
        )
        
        # 构建完整结果
        result = EnhancedAnalysisResult(
            symbol=symbol,
            analyst_team=analyst_team,
            researcher_debate=researcher_debate,
            trader_decision=trader_decision,
            risk_assessment=risk_assessment,
            final_decision=final_decision
        )
        
        if verbose:
            print(f"\n{'='*70}")
            print("✅ 完整分析流程结束")
            print(f"{'='*70}")
        
        return result
    
    # ==================== Layer 1: Analyst Team ====================
    
    def _run_analyst_team(
        self,
        symbol: str,
        verbose: bool
    ) -> AnalystTeamReport:
        """运行分析师团队（4个专业分析师并行）"""
        
        # Fundamentals Analyst
        if verbose:
            print("\n[1/4] 基本面分析师...")
        fundamentals = self._run_fundamentals_analyst(symbol, verbose)
        
        # Sentiment Analyst
        if verbose:
            print("\n[2/4] 情绪分析师...")
        sentiment = self._run_sentiment_analyst(symbol, verbose)
        
        # News Analyst
        if verbose:
            print("\n[3/4] 新闻分析师...")
        news = self._run_news_analyst(symbol, verbose)
        
        # Technical Analyst
        if verbose:
            print("\n[4/4] 技术分析师...")
        technical = self._run_technical_analyst(symbol, verbose)
        
        return AnalystTeamReport(
            fundamentals=fundamentals,
            sentiment=sentiment,
            news=news,
            technical=technical
        )
    
    def _run_fundamentals_analyst(self, symbol: str, verbose: bool) -> AgentOutput:
        """基本面分析师"""
        try:
            # 获取财务数据
            financials = get_company_financials.invoke({"symbol": symbol})
            intrinsic_value = calculate_intrinsic_value.invoke({"symbol": symbol})
            metrics = get_performance_metrics.invoke({"symbol": symbol})
            red_flags = identify_red_flags.invoke({"symbol": symbol})
            
            # LLM分析
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("fundamentals_analyst")),
                ("user", f"""请分析股票 {symbol} 的基本面:

【财务数据】
{financials}

【内在价值评估】
{intrinsic_value}

【业绩指标】
{metrics}

【财务风险识别】
{red_flags}

请给出基本面评分(1-10分)和分析。""")
            ])
            
            response = (prompt | self.llm).invoke({})
            score = self._extract_score(response.content)
            
            return AgentOutput(
                role=AgentRole.FUNDAMENTALS_ANALYST,
                content=response.content,
                score=score
            )
        except Exception as e:
            return AgentOutput(
                role=AgentRole.FUNDAMENTALS_ANALYST,
                content=f"基本面分析失败: {str(e)}",
                score=5.0
            )
    
    def _run_sentiment_analyst(self, symbol: str, verbose: bool) -> AgentOutput:
        """情绪分析师"""
        try:
            # 获取情绪数据
            social_sentiment = analyze_social_media_sentiment.invoke({"symbol": symbol})
            sentiment_score = get_public_sentiment_score.invoke({"symbol": symbol})
            market_mood = track_market_mood.invoke({})
            
            # LLM分析
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("sentiment_analyst")),
                ("user", f"""请分析股票 {symbol} 的市场情绪:

【社交媒体情绪】
{social_sentiment}

【公众情绪评分】
{sentiment_score}

【市场整体情绪】
{market_mood}

请给出情绪面分析和投资启示。""")
            ])
            
            response = (prompt | self.llm).invoke({})
            
            return AgentOutput(
                role=AgentRole.SENTIMENT_ANALYST,
                content=response.content
            )
        except Exception as e:
            return AgentOutput(
                role=AgentRole.SENTIMENT_ANALYST,
                content=f"情绪分析失败: {str(e)}"
            )
    
    def _run_news_analyst(self, symbol: str, verbose: bool) -> AgentOutput:
        """新闻分析师"""
        try:
            # 获取新闻数据
            news_sentiment = analyze_news_sentiment.invoke({"symbol": symbol, "max_news": 10})
            macro_indicators = get_macroeconomic_indicators.invoke({})
            event_impact = assess_event_impact.invoke({"symbol": symbol})
            global_news = get_global_market_news.invoke({"max_news": 5})
            
            # LLM分析
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("news_analyst")),
                ("user", f"""请分析股票 {symbol} 的新闻面:

【新闻情感分析】
{news_sentiment}

【宏观经济指标】
{macro_indicators}

【事件影响评估】
{event_impact}

【全球市场动态】
{global_news}

请给出新闻面综合判断。""")
            ])
            
            response = (prompt | self.llm).invoke({})
            
            return AgentOutput(
                role=AgentRole.NEWS_ANALYST,
                content=response.content
            )
        except Exception as e:
            return AgentOutput(
                role=AgentRole.NEWS_ANALYST,
                content=f"新闻分析失败: {str(e)}"
            )
    
    def _run_technical_analyst(self, symbol: str, verbose: bool) -> AgentOutput:
        """技术分析师"""
        try:
            # 获取技术数据
            indicators = get_stock_technical_indicators.invoke({"symbol": symbol})
            history = get_stock_history.invoke({"symbol": symbol})
            industry = get_industry_comparison.invoke({"symbol": symbol})
            
            # LLM分析
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_prompt_by_role("technical_analyst")),
                ("user", f"""请分析股票 {symbol} 的技术面:

【技术指标】
{indicators}

【历史行情】
{history}

【行业对比】
{industry}

请给出技术面评分(1-10分)和分析。""")
            ])
            
            response = (prompt | self.llm).invoke({})
            score = self._extract_score(response.content)
            
            return AgentOutput(
                role=AgentRole.TECHNICAL_ANALYST,
                content=response.content,
                score=score
            )
        except Exception as e:
            return AgentOutput(
                role=AgentRole.TECHNICAL_ANALYST,
                content=f"技术分析失败: {str(e)}",
                score=5.0
            )
    
    # ==================== Layer 2: Researcher Team ====================
    
    def _run_researcher_team(
        self,
        symbol: str,
        analyst_team: AnalystTeamReport,
        verbose: bool
    ) -> ResearcherDebate:
        """运行研究员团队（多空辩论）"""
        
        # 汇总分析师报告
        context = f"""【基本面分析】
{analyst_team.fundamentals.content}

【情绪分析】
{analyst_team.sentiment.content}

【新闻分析】
{analyst_team.news.content}

【技术分析】
{analyst_team.technical.content}"""
        
        # Bullish Researcher
        if verbose:
            print("\n[多头研究员] 分析中...")
        bullish_prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("bullish_researcher")),
            ("user", f"基于以下分析报告，请给出多头观点:\n\n{context}")
        ])
        bullish_response = (bullish_prompt | self.llm).invoke({})
        bullish_score = self._extract_score(bullish_response.content)
        
        bullish = AgentOutput(
            role=AgentRole.BULLISH_RESEARCHER,
            content=bullish_response.content,
            score=bullish_score
        )
        
        # Bearish Researcher
        if verbose:
            print("[空头研究员] 分析中...")
        bearish_prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("bearish_researcher")),
            ("user", f"基于以下分析报告，请给出空头观点:\n\n{context}")
        ])
        bearish_response = (bearish_prompt | self.llm).invoke({})
        bearish_score = self._extract_score(bearish_response.content)
        
        bearish = AgentOutput(
            role=AgentRole.BEARISH_RESEARCHER,
            content=bearish_response.content,
            score=bearish_score
        )
        
        # 判断是否需要辩论
        score_diff = abs(bullish_score - bearish_score)
        debate_occurred = score_diff >= self.debate_threshold
        
        debate_rounds = []
        if debate_occurred and verbose:
            print(f"\n⚡ 评分差异 {score_diff:.1f} >= {self.debate_threshold}，触发辩论！")
            # 简化版辩论（可以在这里调用更详细的辩论流程）
            # TODO: 实现完整的辩论机制
        
        return ResearcherDebate(
            bullish=bullish,
            bearish=bearish,
            score_diff=score_diff,
            debate_occurred=debate_occurred,
            debate_rounds=debate_rounds
        )
    
    # ==================== Layer 3: Trader ====================
    
    def _run_trader(
        self,
        symbol: str,
        analyst_team: AnalystTeamReport,
        researcher_debate: ResearcherDebate,
        verbose: bool
    ) -> TraderDecision:
        """交易员决策"""
        
        context = f"""【分析师团队报告摘要】
基本面: {analyst_team.fundamentals.content[:200]}...
情绪面: {analyst_team.sentiment.content[:200]}...
新闻面: {analyst_team.news.content[:200]}...
技术面: {analyst_team.technical.content[:200]}...

【研究员辩论】
多头观点(评分{researcher_debate.bullish.score}/10):
{researcher_debate.bullish.content}

空头观点(评分{researcher_debate.bearish.score}/10):
{researcher_debate.bearish.content}

评分差异: {researcher_debate.score_diff}
{'发生辩论' if researcher_debate.debate_occurred else '未发生辩论'}"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("trader")),
            ("user", f"基于以上所有分析，请给出交易决策:\n\n{context}")
        ])
        
        response = (prompt | self.llm).invoke({})
        
        recommendation = self._extract_recommendation(response.content)
        position = self._extract_position(response.content)
        
        return TraderDecision(
            decision=AgentOutput(
                role=AgentRole.TRADER,
                content=response.content
            ),
            recommendation=recommendation,
            suggested_position=position
        )
    
    # ==================== Layer 4: Risk & Portfolio ====================
    
    def _run_risk_management(
        self,
        trader_decision: TraderDecision,
        verbose: bool
    ) -> RiskAssessment:
        """风险管理团队（3种风格）"""
        
        trader_context = trader_decision.decision.content
        
        # Aggressive
        aggressive_prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("risk_manager_aggressive")),
            ("user", f"评估以下交易决策的风险:\n\n{trader_context}")
        ])
        aggressive_response = (aggressive_prompt | self.llm).invoke({})
        
        # Neutral
        neutral_prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("risk_manager_neutral")),
            ("user", f"评估以下交易决策的风险:\n\n{trader_context}")
        ])
        neutral_response = (neutral_prompt | self.llm).invoke({})
        
        # Conservative
        conservative_prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("risk_manager_conservative")),
            ("user", f"评估以下交易决策的风险:\n\n{trader_context}")
        ])
        conservative_response = (conservative_prompt | self.llm).invoke({})
        
        return RiskAssessment(
            aggressive=AgentOutput(
                role=AgentRole.RISK_MANAGER_AGGRESSIVE,
                content=aggressive_response.content
            ),
            neutral=AgentOutput(
                role=AgentRole.RISK_MANAGER_NEUTRAL,
                content=neutral_response.content
            ),
            conservative=AgentOutput(
                role=AgentRole.RISK_MANAGER_CONSERVATIVE,
                content=conservative_response.content
            )
        )
    
    def _run_portfolio_manager(
        self,
        symbol: str,
        analyst_team: AnalystTeamReport,
        researcher_debate: ResearcherDebate,
        trader_decision: TraderDecision,
        risk_assessment: RiskAssessment,
        verbose: bool
    ) -> FinalDecision:
        """投资组合经理最终决策"""
        
        full_context = f"""【股票代码】{symbol}

【交易员决策】
{trader_decision.decision.content}

【风险评估】
激进派: {risk_assessment.aggressive.content}
中立派: {risk_assessment.neutral.content}
保守派: {risk_assessment.conservative.content}

【分析师评分摘要】
基本面: {analyst_team.fundamentals.score}/10
技术面: {analyst_team.technical.score}/10

【研究员评分】
多头: {researcher_debate.bullish.score}/10
空头: {researcher_debate.bearish.score}/10"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_prompt_by_role("portfolio_manager")),
            ("user", f"请给出最终投资决策:\n\n{full_context}")
        ])
        
        response = (prompt | self.llm).invoke({})
        
        recommendation = self._extract_recommendation(response.content)
        confidence = self._extract_confidence(response.content)
        position_suggestions = self._extract_position_suggestions(response.content)
        
        return FinalDecision(
            decision=AgentOutput(
                role=AgentRole.PORTFOLIO_MANAGER,
                content=response.content
            ),
            recommendation=recommendation,
            confidence=confidence,
            position_suggestions=position_suggestions
        )
    
    # ==================== Helper Functions ====================
    
    def _extract_score(self, content: str) -> float:
        """从内容中提取评分"""
        import re
        patterns = [
            r'评分[：:]\\s*(\\d+(?:\\.\\d+)?)\\s*/\\s*10',
            r'(\\d+(?:\\.\\d+)?)\\s*/\\s*10\\s*分',
            r'综合评分[：:]\\s*(\\d+(?:\\.\\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    score = float(match.group(1))
                    return min(max(score, 0), 10)
                except:
                    pass
        
        return 5.0
    
    def _extract_recommendation(self, content: str) -> str:
        """提取投资建议"""
        if "买入" in content:
            return "买入"
        elif "卖出" in content:
            return "卖出"
        else:
            return "持有"
    
    def _extract_position(self, content: str) -> str:
        """提取仓位建议"""
        if "重仓" in content:
            return "重仓"
        elif "半仓" in content:
            return "半仓"
        else:
            return "轻仓"
    
    def _extract_confidence(self, content: str) -> str:
        """提取信心水平"""
        if "高信心" in content or "信心水平: 高" in content:
            return "高"
        elif "低信心" in content or "信心水平: 低" in content:
            return "低"
        else:
            return "中"
    
    def _extract_position_suggestions(self, content: str) -> Dict[str, str]:
        """提取不同风险偏好的仓位建议"""
        # 简化版：返回默认值
        # TODO: 从LLM输出中解析
        return {
            "激进型": "50-70%",
            "稳健型": "30-50%",
            "保守型": "10-30%"
        }
