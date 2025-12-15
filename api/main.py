import os
import sys
import json
import asyncio
from typing import AsyncGenerator, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.multi_agent_system_enhanced import (
    EnhancedMultiAgentSystem,
    AnalystTeamReport
)

app = FastAPI(title="AI Stock Analysis API", version="2.0.0")

# 允许跨域 - 部署后需要限制为前端域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",
        "*"  # 开发时允许所有，生产环境应该限制
    ],
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

@app.get("/")
async def root():
    return {"message": "AI Stock Analysis API", "docs": "/docs"}

async def analysis_generator(request: AnalyzeRequest) -> AsyncGenerator[str, None]:
    """生成器，流式返回增强版分析进度"""
    
    # 获取股票名称 - 使用新浪财经 API（更稳定，不受代理影响）
    stock_name = ""
    try:
        import requests
        
        # 使用不信任环境代理的 Session
        session = requests.Session()
        session.trust_env = False  # 不读取环境变量中的代理设置
        
        # 根据股票代码确定市场前缀
        if request.symbol.startswith('6'):
            sina_symbol = f"sh{request.symbol}"  # 上海
        else:
            sina_symbol = f"sz{request.symbol}"  # 深圳
        
        # 使用新浪财经 API
        url = f"https://hq.sinajs.cn/list={sina_symbol}"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        
        try:
            resp = session.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                # 解析新浪返回格式: var hq_str_sh600519="贵州茅台,..."
                content = resp.content.decode('gbk')  # 新浪使用 GBK 编码
                if '="' in content:
                    data_part = content.split('="')[1].split('",')[0]
                    if ',' in data_part:
                        stock_name = data_part.split(',')[0]
        except:
            pass
        
        session.close()
        
        # 如果还是获取不到，使用默认值
        if not stock_name:
            stock_name = f"股票 {request.symbol}"
            
    except Exception as e:
        stock_name = f"股票 {request.symbol}"
    
    yield json.dumps({
        "type": "status", 
        "message": "🚀 正在初始化增强版多Agent系统...", 
        "step": "init",
        "layer": 0,
        "stock_name": stock_name
    }) + "\n"
    
    try:
        # 检查 API Key
        effective_api_key = request.api_key or os.getenv("api-key") or os.getenv("OPENAI_API_KEY")
        effective_base_url = request.base_url or os.getenv("base-url") or "https://api.siliconflow.cn/v1"
        
        # 调试日志
        print(f"[DEBUG] Symbol: {request.symbol}")
        print(f"[DEBUG] Model: {request.model}")
        print(f"[DEBUG] Base URL: {effective_base_url}")
        print(f"[DEBUG] API Key provided: {'Yes' if effective_api_key else 'No'}")
        
        if not effective_api_key:
            yield json.dumps({
                "type": "error",
                "message": "❌ 请在设置中输入 API Key！未设置 API Key 无法调用大模型。"
            }) + "\n"
            return
        
        if request.api_key:
            os.environ["OPENAI_API_KEY"] = request.api_key
            os.environ["api-key"] = request.api_key
        
        system = EnhancedMultiAgentSystem(
            model=request.model,
            api_key=effective_api_key,
            base_url=effective_base_url,
            debate_threshold=request.debate_threshold,
            max_debate_rounds=request.max_rounds
        )

        yield json.dumps({
            "type": "status",
            "message": "✅ 系统初始化完成",
            "step": "initialized",
            "layer": 0,
            "stock_name": stock_name
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
        
        # News Analyst
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Stock Analysis API...")
    print("📊 4-Layer Multi-Agent System (11 Agents)") 
    print("📖 API Docs: http://localhost:8000/docs")
    
    # Railway uses PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
