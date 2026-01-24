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
        if debate_occurred:
            if verbose:
                print(f"\n⚡ 评分差异 {score_diff:.1f} >= {self.debate_threshold}，触发辩论！")
            
            # 运行完整辩论机制
            debate_rounds, bullish, bearish = self._run_debate(
                bullish, bearish, context, verbose
            )
        
        return ResearcherDebate(
            bullish=bullish,
            bearish=bearish,
            score_diff=score_diff,
            debate_occurred=debate_occurred,
            debate_rounds=debate_rounds
        )
    
    def _run_debate(
        self,
        bullish: AgentOutput,
        bearish: AgentOutput,
        context: str,
        verbose: bool
    ) -> tuple:
        """运行完整的辩论机制
        
        Args:
            bullish: 多头研究员的初始观点
            bearish: 空头研究员的初始观点
            context: 分析师报告上下文
            verbose: 是否打印详细信息
            
        Returns:
            (debate_rounds, updated_bullish, updated_bearish)
        """
        debate_rounds = []
        
        for round_num in range(1, self.max_debate_rounds + 1):
            if verbose:
                print(f"\n--- 辩论第 {round_num} 轮 ---")
            
            # 多头反驳空头
            if verbose:
                print("[多头] 反驳中...")
            bull_rebuttal_prompt = ChatPromptTemplate.from_messages([
                ("system", """你是看涨研究员，请针对空头的观点进行反驳。
保持理性和专业，用数据和事实说话。
反驳后请重新给出你的评分(1-10分)。"""),
                ("user", f"""原始分析报告:
{context}

空头观点:
{bearish.content}

请针对空头的主要论点进行反驳，强化你的看涨理由。
格式:
【反驳要点】
1. ...
2. ...

【更新后评分】
评分: X/10分
信心水平: 高/中/低""")
            ])
            bull_response = (bull_rebuttal_prompt | self.llm).invoke({})
            
            # 空头反驳多头
            if verbose:
                print("[空头] 反驳中...")
            bear_rebuttal_prompt = ChatPromptTemplate.from_messages([
                ("system", """你是看跌研究员，请针对多头的观点进行反驳。
保持理性和专业，用数据和事实说话。
反驳后请重新给出你的评分(1-10分，分数越低越看跌)。"""),
                ("user", f"""原始分析报告:
{context}

多头观点:
{bullish.content}

请针对多头的主要论点进行反驳，强化你的看跌理由。
格式:
【反驳要点】
1. ...
2. ...

【更新后评分】
评分: X/10分
信心水平: 高/中/低""")
            ])
            bear_response = (bear_rebuttal_prompt | self.llm).invoke({})
            
            # 记录辩论轮次
            debate_rounds.append({
                "round": round_num,
                "bullish_rebuttal": bull_response.content,
                "bearish_rebuttal": bear_response.content,
                "bullish_score": self._extract_score(bull_response.content),
                "bearish_score": self._extract_score(bear_response.content)
            })
            
            # 更新观点
            bullish = AgentOutput(
                role=AgentRole.BULLISH_RESEARCHER,
                content=f"{bullish.content}\n\n【第{round_num}轮辩论补充】\n{bull_response.content}",
                score=self._extract_score(bull_response.content)
            )
            bearish = AgentOutput(
                role=AgentRole.BEARISH_RESEARCHER,
                content=f"{bearish.content}\n\n【第{round_num}轮辩论补充】\n{bear_response.content}",
                score=self._extract_score(bear_response.content)
            )
            
            if verbose:
                print(f"第{round_num}轮辩论完成: 多头评分 {bullish.score}/10, 空头评分 {bearish.score}/10")
            
            # 如果评分差异收敛，提前结束辩论
            new_diff = abs(bullish.score - bearish.score)
            if new_diff < self.debate_threshold * 0.5:
                if verbose:
                    print(f"评分差异收敛至 {new_diff:.1f}，提前结束辩论")
                break
        
        return debate_rounds, bullish, bearish
    
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
            r'评分[：:]\s*(\d+(?:\.\d+)?)\s*/\s*10',
            r'(\d+(?:\.\d+)?)\s*/\s*10\s*分',
            r'综合评分[：:]\s*(\d+(?:\.\d+)?)',
            r'评分[：:]\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*分',
            r'(?:得分|打分)[：:]\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    score = float(match.group(1))
                    # 如果分数大于10，可能是百分制，转换一下
                    if score > 10:
                        score = score / 10
                    return min(max(score, 0), 10)
                except:
                    pass
        
        return 5.0
    
    def _extract_recommendation(self, content: str) -> str:
        """提取投资建议 - 增强版
        
        使用多层次匹配策略:
        1. 优先匹配明确的决策语句
        2. 考虑否定词前缀
        3. 基于关键词评分
        """
        import re
        
        # 优先级1: 查找明确的综合建议语句
        explicit_patterns = [
            r'综合建议[：:]\s*(买入|持有|卖出|观望|规避)',
            r'最终.*?建议[：:]\s*(买入|持有|卖出|观望|规避)',
            r'交易决策[：:]\s*(买入|持有|卖出|观望|规避)',
            r'决策[：:]\s*(买入|持有|卖出|观望|规避)',
            r'投资建议[：:]\s*(买入|持有|卖出|观望|规避)',
        ]
        
        for pattern in explicit_patterns:
            match = re.search(pattern, content)
            if match:
                result = match.group(1)
                if result in ['观望', '规避']:
                    return '持有'
                return result
        
        # 优先级2: 考虑否定词 + 关键词评分
        buy_score = 0
        sell_score = 0
        hold_score = 0
        
        # 否定前缀检测
        negative_buy_patterns = ['不建议买入', '不宜买入', '避免买入', '暂不买入', '不要买入', '禁止买入']
        for pattern in negative_buy_patterns:
            if pattern in content:
                sell_score += 3  # 否定买入 = 倾向卖出/持有
        
        negative_sell_patterns = ['不建议卖出', '不宜卖出', '避免卖出']
        for pattern in negative_sell_patterns:
            if pattern in content:
                buy_score += 2
        
        # 正向关键词评分
        strong_buy_keywords = ['强烈买入', '强烈推荐买入', '重仓买入', '积极买入']
        buy_keywords = ['建议买入', '可以买入', '逢低买入', '买入机会', '适合买入']
        strong_sell_keywords = ['强烈卖出', '立即卖出', '清仓', '全部卖出', '尽快离场']
        sell_keywords = ['建议卖出', '减仓', '逢高卖出', '建议规避', '回避', '远离']
        hold_keywords = ['持有', '观望', '等待', '暂时观望', '维持现状', '不动']
        
        for kw in strong_buy_keywords:
            if kw in content:
                buy_score += 3
        for kw in buy_keywords:
            if kw in content:
                buy_score += 1
        for kw in strong_sell_keywords:
            if kw in content:
                sell_score += 3
        for kw in sell_keywords:
            if kw in content:
                sell_score += 1
        for kw in hold_keywords:
            if kw in content:
                hold_score += 1
        
        # 根据分数判断
        max_score = max(buy_score, sell_score, hold_score)
        
        if max_score == 0:
            return "持有"  # 默认持有（保守策略）
        
        # 优先级: 卖出 > 持有 > 买入（保守原则）
        if sell_score == max_score:
            return "卖出"
        elif hold_score == max_score:
            return "持有"
        elif buy_score == max_score:
            return "买入"
        else:
            return "持有"
    
    def _extract_position(self, content: str) -> str:
        """提取仓位建议 - 增强版"""
        import re
        
        # 明确的仓位建议匹配
        patterns = [
            r'建议仓位[：:]\s*(轻仓|半仓|重仓|空仓|观望)',
            r'仓位建议[：:]\s*(轻仓|半仓|重仓|空仓|观望)',
            r'(轻仓|半仓|重仓|空仓).*?(?:买入|持有)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                pos = match.group(1)
                if pos == '空仓' or pos == '观望':
                    return '观望'
                return pos
        
        # 百分比匹配
        pct_match = re.search(r'(\d+)[-–]?(\d*)%.*?仓位', content)
        if pct_match:
            pct = int(pct_match.group(1))
            if pct >= 70:
                return "重仓"
            elif pct >= 40:
                return "半仓"
            elif pct >= 10:
                return "轻仓"
            else:
                return "观望"
        
        # 关键词判断
        if "重仓" in content or "大仓位" in content:
            return "重仓"
        elif "半仓" in content or "中等仓位" in content:
            return "半仓"
        elif "轻仓" in content or "小仓位" in content or "试探" in content:
            return "轻仓"
        elif "空仓" in content or "观望" in content or "规避" in content:
            return "观望"
        else:
            return "轻仓"  # 默认轻仓（保守策略）
    
    def _extract_confidence(self, content: str) -> str:
        """提取信心水平 - 增强版"""
        import re
        
        # 明确的信心水平匹配
        patterns = [
            r'信心水平[：:]\s*(高|中|低)',
            r'信心[：:]\s*(高|中|低)',
            r'把握[：:]\s*(高|中|低|大|小)',
            r'确定性[：:]\s*(高|中|低)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                level = match.group(1)
                if level in ['大']:
                    return '高'
                elif level in ['小']:
                    return '低'
                return level
        
        # 关键词判断
        high_confidence = ['高信心', '非常有把握', '确定性高', '高度确定', '强烈建议']
        low_confidence = ['低信心', '把握不大', '确定性低', '不确定', '谨慎']
        
        for kw in high_confidence:
            if kw in content:
                return "高"
        for kw in low_confidence:
            if kw in content:
                return "低"
        
        return "中"  # 默认中等信心
    
    def _extract_position_suggestions(self, content: str) -> Dict[str, str]:
        """提取不同风险偏好的仓位建议 - 增强版"""
        import re
        
        result = {
            "激进型": "30-50%",
            "稳健型": "20-30%",
            "保守型": "10-20%"
        }
        
        # 尝试从内容中提取具体百分比
        patterns = {
            "激进型": [r'激进[型派].*?[：:]\s*(\d+[-–]\d+%|\d+%)', r'激进.*?仓位.*?(\d+[-–]\d+%|\d+%)'],
            "稳健型": [r'稳健[型派].*?[：:]\s*(\d+[-–]\d+%|\d+%)', r'稳健.*?仓位.*?(\d+[-–]\d+%|\d+%)'],
            "保守型": [r'保守[型派].*?[：:]\s*(\d+[-–]\d+%|\d+%)', r'保守.*?仓位.*?(\d+[-–]\d+%|\d+%)'],
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, content)
                if match:
                    result[key] = match.group(1).replace('–', '-')
                    break
        
        # 如果内容中有明确的卖出/规避建议，调低仓位
        if any(word in content for word in ['卖出', '规避', '远离', '不建议']):
            result = {
                "激进型": "0-10%",
                "稳健型": "0%",
                "保守型": "0%"
            }
        
        return result
