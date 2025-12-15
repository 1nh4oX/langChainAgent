import React, { useState } from 'react';
import {
  Search, Settings, Activity, Briefcase,
  Newspaper, BarChart2, TrendingUp, TrendingDown,
  Shield, Zap, Scale, ArrowRight, Lock
} from 'lucide-react';

// API 地址 - 部署后需要改为 Railway 后端地址
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/analyze';

const Header = () => (
  <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-gray-100">
    <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center text-white font-bold text-lg">
          A
        </div>
        <span className="font-semibold text-xl tracking-tight text-gray-900">AI Stock Insight</span>
      </div>
      <div className="flex items-center gap-4 text-sm font-medium text-gray-500">
        <span className="hidden sm:inline">V 2.0.1</span>
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
        <span>System Ready</span>
      </div>
    </div>
  </header>
);

const Card = ({ title, icon: Icon, children, className = "", loading = false }) => (
  <div className={`bg-white rounded-3xl border border-gray-100 shadow-sm p-6 transition-all duration-500 ${className} ${loading ? 'opacity-50 blur-[2px]' : 'opacity-100 blur-0'}`}>
    <div className="flex items-center gap-3 mb-4">
      <div className="p-2 bg-gray-50 rounded-xl text-gray-900">
        <Icon size={20} strokeWidth={1.5} />
      </div>
      <h3 className="font-semibold text-gray-900">{title}</h3>
      {loading && <div className="ml-auto w-4 h-4 border-2 border-gray-200 border-t-black rounded-full animate-spin"></div>}
    </div>
    <div className="text-gray-600 text-sm leading-relaxed whitespace-pre-line">
      {children}
    </div>
  </div>
);

const Badge = ({ type, text }) => {
  const styles = {
    green: "bg-emerald-50 text-emerald-700 border-emerald-100",
    red: "bg-rose-50 text-rose-700 border-rose-100",
    gray: "bg-gray-100 text-gray-600 border-gray-200",
    blue: "bg-blue-50 text-blue-700 border-blue-100"
  };
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[type] || styles.gray}`}>
      {text}
    </span>
  );
};

export default function App() {
  // --- State ---
  const [stockCode, setStockCode] = useState('600519');
  const [apiKey, setApiKey] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);

  // Settings State
  const [threshold, setThreshold] = useState(3.0);
  const [rounds, setRounds] = useState(2);

  // Analysis Result State
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // --- Logic ---
  const handleAnalyze = async () => {
    if (!stockCode || stockCode.length !== 6) {
      alert("请输入有效的6位股票代码");
      return;
    }

    setIsAnalyzing(true);
    setResult(null);
    setError(null);
    setProgress(5);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: stockCode,
          api_key: apiKey || null,
          debate_threshold: parseFloat(threshold),
          max_rounds: parseInt(rounds),
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data = JSON.parse(line);
              handleStreamData(data);
            } catch (e) {
              console.error('Error parsing JSON:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleStreamData = (data) => {
    console.log('Stream:', data);

    switch (data.type) {
      case 'status':
        updateProgress(data.step, data.layer);
        break;
      case 'agent_output':
        updateAgentOutput(data.role, data.data);
        break;
      case 'risk_assessment':
        setResult(prev => ({
          ...prev,
          layer4: {
            aggressive: data.data.aggressive,
            balanced: data.data.neutral,
            conservative: data.data.conservative
          }
        }));
        break;
      case 'final_result':
        setResult(prev => ({
          ...prev,
          layer3: {
            ...(prev?.layer3 || {}),
            action: data.data.recommendation,
            confidence: data.data.confidence
          }
        }));
        setProgress(100);
        break;
      case 'error':
        setError(data.message);
        break;
    }
  };

  const updateProgress = (step, layer) => {
    const progressMap = {
      'init': 5, 'initialized': 10,
      'fundamentals_analyst': 15, 'sentiment_analyst': 20,
      'news_analyst': 25, 'technical_analyst': 30,
      'researcher_debate': 45, 'trader': 65,
      'risk_assessment': 80, 'portfolio_manager': 90, 'complete': 100
    };
    if (progressMap[step]) setProgress(progressMap[step]);
    else if (layer) setProgress({ 1: 15, 2: 40, 3: 65, 4: 85 }[layer] || progress);
  };

  const updateAgentOutput = (role, data) => {
    switch (role) {
      case 'fundamentals_analyst':
        setResult(prev => ({
          ...prev,
          layer1: { ...(prev?.layer1 || {}), fundamental: data.content }
        }));
        break;
      case 'sentiment_analyst':
        setResult(prev => ({
          ...prev,
          layer1: { ...(prev?.layer1 || {}), sentiment: data.content }
        }));
        break;
      case 'news_analyst':
        setResult(prev => ({
          ...prev,
          layer1: { ...(prev?.layer1 || {}), news: data.content }
        }));
        break;
      case 'technical_analyst':
        setResult(prev => ({
          ...prev,
          layer1: { ...(prev?.layer1 || {}), technical: data.content }
        }));
        break;
      case 'bullish_researcher':
        setResult(prev => ({
          ...prev,
          layer2: {
            ...(prev?.layer2 || {}),
            bullScore: data.score,
            bullView: data.content
          }
        }));
        break;
      case 'bearish_researcher':
        setResult(prev => ({
          ...prev,
          layer2: {
            ...(prev?.layer2 || {}),
            bearScore: data.score,
            bearView: data.content
          }
        }));
        break;
      case 'trader':
        setResult(prev => ({
          ...prev,
          layer3: {
            ...(prev?.layer3 || {}),
            reasoning: data.content,
            action: data.recommendation || prev?.layer3?.action,
            confidence: prev?.layer3?.confidence || "MEDIUM"
          }
        }));
        break;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-black selection:text-white">
      <Header />

      <main className="max-w-5xl mx-auto px-6 py-12 space-y-12">

        {/* --- Hero Input Section --- */}
        <section className="relative z-10 max-w-2xl mx-auto text-center space-y-8">
          <div className="space-y-2">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-gray-900">
              市场洞察，<span className="text-gray-400">一触即发</span>
            </h1>
            <p className="text-gray-500 text-lg">多智能体深度博弈分析系统</p>
          </div>

          <div className="bg-white p-2 rounded-[2rem] border border-gray-200 shadow-xl shadow-gray-200/50 flex flex-col md:flex-row items-center gap-2 transition-all focus-within:ring-4 focus-within:ring-gray-100">
            <div className="flex-1 flex items-center px-4 w-full h-14 md:h-auto">
              <Search className="text-gray-400 mr-3" size={20} />
              <input
                type="text"
                placeholder="股票代码 (e.g. 600519)"
                className="w-full h-full bg-transparent outline-none text-lg font-medium placeholder:text-gray-300"
                value={stockCode}
                onChange={(e) => setStockCode(e.target.value)}
                maxLength={6}
              />
            </div>

            <div className="w-px h-8 bg-gray-100 hidden md:block"></div>

            <button
              onClick={() => setIsSettingsOpen(!isSettingsOpen)}
              className="px-4 text-gray-400 hover:text-gray-600 transition-colors hidden md:block"
            >
              <Settings size={20} />
            </button>

            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="w-full md:w-auto px-8 h-12 bg-black text-white rounded-3xl font-medium hover:bg-gray-800 active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing
                </>
              ) : (
                <>
                  开始分析 <ArrowRight size={18} />
                </>
              )}
            </button>
          </div>

          {/* Settings Panel (Collapsible) */}
          <div className={`overflow-hidden transition-all duration-300 ease-in-out ${isSettingsOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
            <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-lg text-left grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                  <Lock size={14} /> API Key
                </label>
                <input
                  type="password"
                  placeholder="sk-xxxxxxxx"
                  className="w-full p-3 bg-gray-50 rounded-xl border border-transparent focus:bg-white focus:border-gray-200 outline-none transition-all text-sm"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
              </div>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-gray-700">辩论阈值 (Threshold)</span>
                    <span className="text-gray-500">{threshold}</span>
                  </div>
                  <input
                    type="range" min="1" max="10" step="0.5"
                    value={threshold} onChange={(e) => setThreshold(e.target.value)}
                    className="w-full h-2 bg-gray-100 rounded-lg appearance-none cursor-pointer accent-black"
                  />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-gray-700">最大回合 (Rounds)</span>
                    <span className="text-gray-500">{rounds}</span>
                  </div>
                  <input
                    type="range" min="1" max="5" step="1"
                    value={rounds} onChange={(e) => setRounds(e.target.value)}
                    className="w-full h-2 bg-gray-100 rounded-lg appearance-none cursor-pointer accent-black"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* --- Progress Bar --- */}
        {isAnalyzing && (
          <div className="max-w-xl mx-auto space-y-2">
            <div className="flex justify-between text-xs font-medium text-gray-400 uppercase tracking-wider">
              <span>Initializing</span>
              <span>Reasoning</span>
              <span>Finalizing</span>
            </div>
            <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-black transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-2xl p-4 text-red-700">
            ❌ 错误: {error}
          </div>
        )}

        {/* --- Analysis Content --- */}
        {result && (
          <div className="space-y-12">

            {/* Layer 1: The Analysts */}
            <section>
              <div className="flex items-center gap-2 mb-6">
                <div className="w-1 h-6 bg-gray-900 rounded-full"></div>
                <h2 className="text-xl font-bold text-gray-900">Layer 1: 分析师团队</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card title="基本面分析" icon={Briefcase} loading={!result.layer1?.fundamental}>
                  {result.layer1?.fundamental || "Waiting for data..."}
                </Card>
                <Card title="情绪分析" icon={Activity} loading={!result.layer1?.sentiment}>
                  {result.layer1?.sentiment || "Scanning social media..."}
                </Card>
                <Card title="新闻资讯" icon={Newspaper} loading={!result.layer1?.news}>
                  {result.layer1?.news || "Aggregating news sources..."}
                </Card>
                <Card title="技术指标" icon={BarChart2} loading={!result.layer1?.technical}>
                  {result.layer1?.technical || "Calculating indicators..."}
                </Card>
              </div>
            </section>

            {/* Layer 2: The Debate */}
            {result.layer1 && (
              <section>
                <div className="flex items-center gap-2 mb-6">
                  <div className="w-1 h-6 bg-gray-900 rounded-full"></div>
                  <h2 className="text-xl font-bold text-gray-900">Layer 2: 观点博弈</h2>
                </div>
                <div className="bg-white rounded-[2rem] border border-gray-100 shadow-sm overflow-hidden">
                  <div className="grid grid-cols-1 md:grid-cols-2">

                    {/* Bull Case */}
                    <div className="p-8 border-b md:border-b-0 md:border-r border-gray-50 relative group">
                      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50"></div>
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full">
                          <TrendingUp size={16} />
                          <span className="font-bold text-sm">看多 (Bull)</span>
                        </div>
                        <div className="text-2xl font-bold text-gray-900">
                          {result.layer2?.bullScore?.toFixed(1) || "-"}
                        </div>
                      </div>
                      <p className="text-gray-600 leading-relaxed text-sm">
                        {result.layer2?.bullView || "Analyst constructing bullish arguments..."}
                      </p>
                    </div>

                    {/* Bear Case */}
                    <div className="p-8 relative">
                      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-rose-500 to-transparent opacity-50"></div>
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-2 text-rose-600 bg-rose-50 px-3 py-1 rounded-full">
                          <TrendingDown size={16} />
                          <span className="font-bold text-sm">看空 (Bear)</span>
                        </div>
                        <div className="text-2xl font-bold text-gray-900">
                          {result.layer2?.bearScore?.toFixed(1) || "-"}
                        </div>
                      </div>
                      <p className="text-gray-600 leading-relaxed text-sm">
                        {result.layer2?.bearView || "Analyst constructing bearish arguments..."}
                      </p>
                    </div>

                  </div>

                  {/* Debate Trigger Info */}
                  <div className="bg-gray-50 px-6 py-3 flex items-center justify-between text-xs text-gray-400 border-t border-gray-100">
                    <div className="flex items-center gap-2">
                      <Scale size={14} />
                      <span>Debate Threshold: {threshold}</span>
                    </div>
                    {result.layer2 && result.layer2.bullScore && result.layer2.bearScore && (
                      <span>Delta: {Math.abs(result.layer2.bullScore - result.layer2.bearScore).toFixed(1)}</span>
                    )}
                  </div>
                </div>
              </section>
            )}

            {/* Layer 3: Final Decision */}
            {result.layer2 && (
              <section>
                <div className="flex items-center gap-2 mb-6">
                  <div className="w-1 h-6 bg-gray-900 rounded-full"></div>
                  <h2 className="text-xl font-bold text-gray-900">Layer 3: 交易决策</h2>
                </div>

                <div className="relative overflow-hidden bg-black text-white rounded-[2.5rem] p-10 shadow-2xl shadow-gray-200">
                  {/* Subtle Background Pattern */}
                  <div className="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-gray-800 rounded-full blur-[80px] opacity-50"></div>

                  <div className="relative z-10 flex flex-col md:flex-row items-center md:items-start justify-between gap-8">
                    <div className="text-center md:text-left space-y-2">
                      <span className="text-gray-400 text-sm font-medium tracking-widest uppercase">Recommendation</span>
                      <div className="text-5xl md:text-7xl font-bold tracking-tighter">
                        {result.layer3?.action || "COMPUTING..."}
                      </div>
                      {result.layer3 && (
                        <div className="flex items-center justify-center md:justify-start gap-3 mt-4">
                          <Badge
                            type={result.layer3.action === 'BUY' || result.layer3.action?.includes('买入') ? 'green' :
                              result.layer3.action === 'SELL' || result.layer3.action?.includes('卖出') ? 'red' : 'gray'}
                            text={`Confidence: ${result.layer3.confidence || 'MEDIUM'}`}
                          />
                          <span className="text-gray-400 text-sm">Based on 4-Agent Consensus</span>
                        </div>
                      )}
                    </div>

                    <div className="max-w-md bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Zap size={16} className="text-yellow-400" />
                        核心逻辑
                      </h4>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {result.layer3?.reasoning || "Finalizing strategy..."}
                      </p>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Layer 4: Risk Strategies */}
            {result.layer3 && (
              <section>
                <div className="flex items-center gap-2 mb-6">
                  <div className="w-1 h-6 bg-gray-900 rounded-full"></div>
                  <h2 className="text-xl font-bold text-gray-900">Layer 4: 仓位风控</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-rose-500"></div>
                    <div className="flex items-center gap-2 mb-4 text-rose-600">
                      <TrendingUp size={20} />
                      <h3 className="font-bold">激进型</h3>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {result.layer4?.aggressive || "Loading..."}
                    </p>
                  </div>

                  <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                    <div className="flex items-center gap-2 mb-4 text-blue-600">
                      <Scale size={20} />
                      <h3 className="font-bold">稳健型</h3>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {result.layer4?.balanced || "Loading..."}
                    </p>
                  </div>

                  <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
                    <div className="flex items-center gap-2 mb-4 text-emerald-600">
                      <Shield size={20} />
                      <h3 className="font-bold">保守型</h3>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {result.layer4?.conservative || "Loading..."}
                    </p>
                  </div>
                </div>
              </section>
            )}

          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="py-12 text-center text-gray-400 text-sm border-t border-gray-100 bg-white">
        <p>© 2024 AI Stock Insight. Powered by LLM Agents & AkShare.</p>
      </footer>
    </div>
  );
}
