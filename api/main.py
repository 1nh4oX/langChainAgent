import os
import sys
import json
import asyncio
from typing import AsyncGenerator, Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.multi_agent_system_enhanced import (
    EnhancedMultiAgentSystem,
    AnalystTeamReport
)

app = FastAPI(title="AI Stock Analysis API", version="2.0.0")

# 允许跨域 - 开发模式允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发时允许所有,生产环境应该限制为具体域名
    allow_credentials=False,  # 使用通配符时必须设为 False
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

class CompareRequest(BaseModel):
    """多股对比分析请求"""
    symbols: List[str]  # 最多5只股票代码
    api_key: Optional[str] = None
    base_url: str = "https://api.siliconflow.cn/v1"
    model: str = "Qwen/Qwen2.5-7B-Instruct"
    debate_threshold: float = 3.0
    max_rounds: int = 1  # 对比分析默认仅1轮辩论，节省时间

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0-enhanced"}

@app.get("/")
async def root():
    return {"message": "AI Stock Analysis API", "docs": "/docs"}

async def analysis_generator(request: AnalyzeRequest) -> AsyncGenerator[str, None]:
    """生成器，流式返回增强版分析进度"""
    
    # ─── 立即发送第一个事件，让前端立即知道请求被接受 ─────────────
    # 注意：第一个 yield 必须在任何网络调用之前，否则异步生成器会阻塞
    yield json.dumps({
        "type": "status",
        "message": "🚀 正在初始化增强版多Agent系统...",
        "step": "init",
        "layer": 0,
        "stock_name": f"股票 {request.symbol}"  # 先用占位名
    }) + "\n"

    # ─── 异步获取股票名称（不阻塞流） ────────────────────────────────
    def _fetch_stock_name(symbol: str) -> str:
        try:
            import requests as _req
            session = _req.Session()
            session.trust_env = False
            prefix = "sh" if symbol.startswith('6') else "sz"
            resp = session.get(
                f"https://hq.sinajs.cn/list={prefix}{symbol}",
                headers={'Referer': 'https://finance.sina.com.cn', 'User-Agent': 'Mozilla/5.0'},
                timeout=5
            )
            session.close()
            if resp.status_code == 200:
                content = resp.content.decode('gbk')
                if '="' in content:
                    data_part = content.split('="')[1].split('",')[0]
                    if ',' in data_part:
                        name = data_part.split(',')[0]
                        if name:
                            return name
        except Exception:
            pass
        return ""

    stock_name = await asyncio.to_thread(_fetch_stock_name, request.symbol)
    if not stock_name:
        stock_name = f"股票 {request.symbol}"

    
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
        
        yield json.dumps({
            "type": "status",
            "message": "⚡ 5大分析师正在并行深度研究...",
            "step": "fundamentals_analyst",
            "role": "fundamentals_analyst",
            "layer": 1
        }) + "\n"

        async def run_analyst(role_name, func):
            res = await asyncio.to_thread(func, request.symbol, verbose=False)
            return role_name, res

        tasks = [
            run_analyst("fundamentals_analyst", system._run_fundamentals_analyst),
            run_analyst("sentiment_analyst", system._run_sentiment_analyst),
            run_analyst("news_analyst", system._run_news_analyst),
            run_analyst("technical_analyst", system._run_technical_analyst),
            run_analyst("quant_analyst", system._run_quant_analyst),
        ]

        results = {}
        for completed_task in asyncio.as_completed(tasks):
            role_name, res = await completed_task
            results[role_name] = res
            
            data_dict = {
                "content": res.content,
                "timestamp": res.timestamp
            }
            if hasattr(res, 'score'):
                data_dict["score"] = res.score
                
            yield json.dumps({
                "type": "agent_output",
                "role": role_name,
                "layer": 1,
                "data": data_dict
            }) + "\n"

        fundamentals = results["fundamentals_analyst"]
        sentiment = results["sentiment_analyst"]
        news = results["news_analyst"]
        technical = results["technical_analyst"]
        quant = results["quant_analyst"]
        
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
            technical=technical,
            quant=quant
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
                    "quant": quant.score,
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


def _run_single_analysis_for_compare(symbol: str, system: EnhancedMultiAgentSystem) -> dict:
    """为对比分析运行单股的完整分析，返回可序列化的结果摘要"""
    try:
        result = system.run_analysis(symbol, verbose=False)
        # 获取阴阳归因字段（从Portfolio Manager输出中提取）
        import re
        strategy_type = "未能识别"
        drive_attr = "未知"
        pm_content = result.final_decision.decision.content
        st_match = re.search(r'策略类型[：:]\s*([^\n\r]+)', pm_content)
        da_match = re.search(r'驱动属性[：:]\s*([^\n\r]+)', pm_content)
        if st_match:
            strategy_type = st_match.group(1).strip()
        if da_match:
            drive_attr = da_match.group(1).strip()
        
        return {
            "symbol": symbol,
            "success": True,
            "recommendation": result.final_decision.recommendation,
            "confidence": result.final_decision.confidence,
            "position_suggestions": result.final_decision.position_suggestions,
            "strategy_type": strategy_type,
            "drive_attribute": drive_attr,
            "scores": {
                "fundamentals": result.analyst_team.fundamentals.score,
                "technical": result.analyst_team.technical.score,
                "quant": result.analyst_team.quant.score if result.analyst_team.quant else None,
                "bullish": result.researcher_debate.bullish.score,
                "bearish": result.researcher_debate.bearish.score,
            },
            "final_content": result.final_decision.decision.content,
            "trader_recommendation": result.trader_decision.recommendation,
            "debate_occurred": result.researcher_debate.debate_occurred,
        }
    except Exception as e:
        import traceback
        return {
            "symbol": symbol,
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


async def compare_generator(request: CompareRequest):
    """NDJSON 流式对比分析：每完成一只股票立即推送进度"""
    symbols = request.symbols[:5]

    effective_api_key = request.api_key or os.getenv("api-key") or os.getenv("OPENAI_API_KEY")
    effective_base_url = request.base_url or os.getenv("base-url") or "https://api.siliconflow.cn/v1"

    if not effective_api_key:
        yield json.dumps({"type": "error", "message": "请提供 API Key"}) + "\n"
        return

    yield json.dumps({
        "type": "compare_start",
        "total": len(symbols),
        "symbols": symbols,
        "message": f"🚀 开始并行分析 {len(symbols)} 只股票..."
    }) + "\n"

    def make_system():
        return EnhancedMultiAgentSystem(
            model=request.model,
            api_key=effective_api_key,
            base_url=effective_base_url,
            debate_threshold=request.debate_threshold,
            max_debate_rounds=request.max_rounds
        )

    def calc_composite(r: dict) -> float:
        s = r.get("scores", {})
        weights = {"fundamentals": 0.25, "technical": 0.20, "quant": 0.20,
                   "bullish": 0.20, "bearish": 0.15}
        total, w_sum = 0.0, 0.0
        for key, w in weights.items():
            val = s.get(key)
            if val is not None:
                total += val * w
                w_sum += w
        return round(total / w_sum, 2) if w_sum > 0 else 0.0

    # 并行启动所有分析任务，用 as_completed 逐个收结果
    try:
        coros = [asyncio.to_thread(_run_single_analysis_for_compare, sym, make_system()) for sym in symbols]
        
        # We need a way to map futures back to symbols.
        # However, asyncio.to_thread doesn't return the symbol, so we wrap it.
        async def run_with_sym(sym, sys):
            res = await asyncio.to_thread(_run_single_analysis_for_compare, sym, sys)
            return sym, res

        tasks = [run_with_sym(sym, make_system()) for sym in symbols]

        completed_results = []
        done_count = 0

        for completed_task in asyncio.as_completed(tasks):
            try:
                sym, r = await completed_task
            except Exception as e:
                # If the wrapper itself failed
                r = {"success": False, "error": str(e)}
                sym = "Unknown"

                r = {"symbol": sym, "success": False, "error": str(e)}

            done_count += 1
            if r.get("success"):
                r["composite_score"] = calc_composite(r)
            
            yield json.dumps({
                "type": "stock_done",
                "done": done_count,
                "total": len(symbols),
                "symbol": sym,
                "result": r,
                "message": f"✅ {sym} 分析完成 ({done_count}/{len(symbols)})"
            }) + "\n"

            completed_results.append(r)

        # 最终排序汇总
        successful = sorted(
            [r for r in completed_results if r.get("success")],
            key=lambda x: x["composite_score"],
            reverse=True
        )
        failed = [r for r in completed_results if not r.get("success")]

        yield json.dumps({
            "type": "compare_result",
            "total": len(symbols),
            "success_count": len(successful),
            "rankings": successful,
            "failed": failed,
            "top_pick": successful[0] if successful else None,
            "summary": (
                f"共分析 {len(successful)} 只股票。"
                f"综合推荐: {successful[0]['symbol']} "
                f"(综合评分 {successful[0]['composite_score']}/10，"
                f"建议: {successful[0]['recommendation']}，"
                f"策略类型: {successful[0]['strategy_type']})"
                if successful else "所有股票分析均失败，请检查代码和网络连接。"
            )
        }) + "\n"

    except Exception as e:
        import traceback
        yield json.dumps({
            "type": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }) + "\n"


@app.post("/api/compare")
async def compare_stocks(request: CompareRequest):
    """多股对比分析（NDJSON 流式，实时推送每只股票进度）"""
    if not request.symbols:
        return JSONResponse(status_code=400, content={"error": "请提供至少1只股票代码"})
    return StreamingResponse(
        compare_generator(request),
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
