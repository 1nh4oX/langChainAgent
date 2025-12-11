import os
import sys
import json
import asyncio
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 添加 src 到路径以便导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.multi_agent_system_enhanced import (
    EnhancedMultiAgentSystem,
    AgentRole
)

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    symbol: str
    api_key: Optional[str] = None
    base_url: str = "https://api.siliconflow.cn/v1"
    model: str = "Qwen/Qwen2.5-7B-Instruct"
    debate_threshold: float = 3.0
    max_rounds: int = 2

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0-enhanced"}

async def analysis_generator(request: AnalyzeRequest) -> AsyncGenerator[str, None]:
    """生成器，流式返回增强版分析进度"""
    
    # 1. 初始化系统
    yield json.dumps({
        "type": "status", 
        "message": "🚀 正在初始化增强版多Agent系统...", 
        "step": "init",
        "layer": 0
    }) + "\n"
    
    try:
        # 设置环境变量
        if request.api_key:
            os.environ["OPENAI_API_KEY"] = request.api_key
            os.environ["api-key"] = request.api_key
        
        system = EnhancedMultiAgentSystem(
            model=request.model,
            api_key=request.api_key,
            base_url=request.base_url,
            debate_threshold=request.debate_threshold,
            max_debate_rounds=request.max_rounds
        )

        yield json.dumps({
            "type": "status",
            "message": "✅ 系统初始化完成",
            "step": "initialized",
            "layer": 0
        }) + "\n"
        
        # ========== Layer 1: Analyst Team ==========
        yield json.dumps({
            "type": "layer_start",
            "layer": 1,
            "name": "Analyst Team",
            "message": "📊 第1层: 分析师团队并行分析"
        }) + "\n"
        
        # Fundamentals Analyst
        yield json.dumps({
            "type": "status",
            "message": "💼 基本面分析师正在评估财务健康度...",
            "step": "fundamentals_analyst",
            "role": "fundamentals_analyst",
            "layer": 1
        }) + "\n"
        
        fundamentals = await asyncio.to_thread(
            system._run_fundamentals_analyst,
            request.symbol,
            verbose=False
        )
        
        yield json.dumps({
            "type": "agent_output",
            "role": "fundamentals_analyst",
            "layer": 1,
            "data": {
                "content": fundamentals.content,
                "score": fundamentals.score,
                "timestamp": fundamentals.timestamp
            }
        }) + "\n"
        
        # Sentiment Analyst
        yield json.dumps({
            "type": "status",
            "message": "💭 情绪分析师正在追踪市场情绪...",
            "step": "sentiment_analyst",
            "role": "sentiment_analyst",
            "layer": 1
        }) + "\n"
        
        sentiment = await asyncio.to_thread(
            system._run_sentiment_analyst,
            request.symbol,
            verbose=False
        )
        
        yield json.dumps({
            "type": "agent_output",
            "role": "sentiment_analyst",
            "layer": 1,
            "data": {
                "content": sentiment.content,
                "timestamp": sentiment.timestamp
            }
        }) + "\n"
        
        # News Analyst 🆕
        yield json.dumps({
            "type": "status",
            "message": "📰 新闻分析师正在分析新闻和宏观经济...",
            "step": "news_analyst",
            "role": "news_analyst",
            "layer": 1
        }) + "\n"
        
        news = await asyncio.to_thread(
            system._run_news_analyst,
            request.symbol,
            verbose=False
        )
        
        yield json.dumps({
            "type": "agent_output",
            "role": "news_analyst",
            "layer": 1,
            "data": {
                "content": news.content,
                "timestamp": news.timestamp
            }
        }) + "\n"
        
        # Technical Analyst
        yield json.dumps({
            "type": "status",
            "message": "📈 技术分析师正在计算MACD和RSI...",
            "step": "technical_analyst",
            "role": "technical_analyst",
            "layer": 1
        }) + "\n"
        
        technical = await asyncio.to_thread(
            system._run_technical_analyst,
            request.symbol,
            verbose=False
        )
        
        yield json.dumps({
            "type": "agent_output",
            "role": "technical_analyst",
            "layer": 1,
            "data": {
                "content": technical.content,
                "score": technical.score,
                "timestamp": technical.timestamp
            }
        }) + "\n"
        
        # ========== Layer 2: Researcher Team ==========
        yield json.dumps({
            "type": "layer_start",
            "layer": 2,
            "name": "Researcher Team",
            "message": "🗣️ 第2层: 研究员团队辩论"
        }) + "\n"
        
        # 构建分析师报告
        from src.agent.multi_agent_system_enhanced import AnalystTeamReport
        analyst_team = AnalystTeamReport(
            fundamentals=fundamentals,
            sentiment=sentiment,
            news=news,
            technical=technical
        )
        
        yield json.dumps({
            "type": "status",
            "message": "⚔️ 多空研究员正在辩论...",
            "step": "researcher_debate",
            "layer": 2
        }) + "\n"
        
        researcher_debate = await asyncio.to_thread(
            system._run_researcher_team,
            request.symbol,
            analyst_team,
            verbose=False
        )
        
        yield json.dumps({
            "type": "agent_output",
            "role": "bullish_researcher",
            "layer": 2,
            "data": {
                "content": researcher_debate.bullish.content,
                "score": researcher_debate.bullish.score,
                "timestamp": researcher_debate.bullish.timestamp
            }
        }) + "\n"
        
        yield json.dumps({
            "type": "agent_output",
            "role": "bearish_researcher",
            "layer": 2,
            "data": {
                "content": researcher_debate.bearish.content,
                "score": researcher_debate.bearish.score,
                "timestamp": researcher_debate.bearish.timestamp
            }
        }) + "\n"
        
        if researcher_debate.debate_occurred:
            yield json.dumps({
                "type": "debate_triggered",
                "data": {
                    "score_diff": researcher_debate.score_diff,
                    "message": f"🔥 触发辩论! (分歧度: {researcher_debate.score_diff:.1f})"
                }
            }) + "\n"
        
        # ========== Layer 3: Trader ==========
        yield json.dumps({
            "type": "layer_start",
            "layer": 3,
            "name": "Trader",
            "message": "💼 第3层: 交易员决策"
        }) + "\n"
        
        yield json.dumps({
            "type": "status",
            "message": "🎯 交易员正在制定交易策略...",
            "step": "trader",
            "layer": 3
        }) + "\n"
        
        trader_decision = await asyncio.to_thread(
            system._run_trader,
            request.symbol,
            analyst_team,
            researcher_debate,
            verbose=False
        )
        
        yield json.dumps({
            "type": "agent_output",
            "role": "trader",
            "layer": 3,
            "data": {
                "content": trader_decision.decision.content,
                "recommendation": trader_decision.recommendation,
                "position": trader_decision.suggested_position,
                "timestamp": trader_decision.decision.timestamp
            }
        }) + "\n"
        
        # ========== Layer 4: Risk + Portfolio ==========
        yield json.dumps({
            "type": "layer_start",
            "layer": 4,
            "name": "Risk Management + Portfolio Manager",
            "message": "⚖️ 第4层: 风险评估与最终决策"
        }) + "\n"
        
        yield json.dumps({
            "type": "status",
            "message": "🛡️ 风险管理团队正在评估...",
            "step": "risk_assessment",
            "layer": 4
        }) + "\n"
        
        risk_assessment = await asyncio.to_thread(
            system._run_risk_management,
            trader_decision,
            verbose=False
        )
        
        yield json.dumps({
            "type": "risk_assessment",
            "data": {
                "aggressive": risk_assessment.aggressive.content,
                "neutral": risk_assessment.neutral.content,
                "conservative": risk_assessment.conservative.content
            }
        }) + "\n"
        
        yield json.dumps({
            "type": "status",
            "message": "👔 投资组合经理正在做出最终决策...",
            "step": "portfolio_manager",
            "layer": 4
        }) + "\n"
        
        final_decision = await asyncio.to_thread(
            system._run_portfolio_manager,
            request.symbol,
            analyst_team,
            researcher_debate,
            trader_decision,
            risk_assessment,
            verbose=False
        )
        
        yield json.dumps({
            "type": "final_result",
            "data": {
                "recommendation": final_decision.recommendation,
                "confidence": final_decision.confidence,
                "content": final_decision.decision.content,
                "position_suggestions": final_decision.position_suggestions,
                "scores": {
                    "fundamentals": fundamentals.score,
                    "technical": technical.score,
                    "bullish": researcher_debate.bullish.score,
                    "bearish": researcher_debate.bearish.score,
                    "score_diff": researcher_debate.score_diff
                }
            }
        }) + "\n"
        
        yield json.dumps({
            "type": "status",
            "message": "🎉 增强版分析完成！",
            "step": "complete"
        }) + "\n"

    except Exception as e:
        import traceback
        yield json.dumps({
            "type": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }) + "\n"

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    return StreamingResponse(
        analysis_generator(request),
        media_type="application/x-ndjson"
    )

# 为了 Vercel 适配和本地开发
if __name__ == "__main__":
    # 本地开发时挂载静态文件
    from fastapi.staticfiles import StaticFiles
    # 检查 public 目录是否存在
    public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
    if os.path.exists(public_dir):
        app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
        print(f"🌍 增强版前端已挂载: http://localhost:8000")
        print(f"🚀 使用4层Agent架构 (11个角色)")
        
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
