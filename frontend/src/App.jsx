import React, { useState, useEffect } from 'react';
import {
  Search, Settings, Activity, Briefcase,
  Newspaper, BarChart2, TrendingUp, TrendingDown,
  Shield, Zap, Scale, ArrowRight, Lock,
  AlertTriangle, Cpu, SlidersHorizontal, ChevronDown,
  ArrowLeft
} from 'lucide-react';

// 简单的 Markdown 转 HTML 函数
const simpleMarkdownToHtml = (text) => {
  if (!text) return '';

  return text
    // 转义 HTML 特殊字符
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // 处理粗体 **text**
    .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold">$1</strong>')
    // 处理斜体 *text*
    .replace(/\*([^*]+)\*/g, '<em class="italic">$1</em>')
    // 处理标题 ### text
    .replace(/^### (.+)$/gm, '<h3 class="font-medium text-base mt-3 mb-1">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="font-semibold text-lg mt-4 mb-2">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="font-bold text-xl mt-4 mb-2">$1</h1>')
    // 处理换行
    .replace(/\n/g, '<br/>');
};

// --- Custom Hooks for Animations ---

// 1. 数字滚动效果 Hook
const useCountUp = (end, duration = 1000, start = 0) => {
  const [count, setCount] = useState(start);

  useEffect(() => {
    let startTime = null;
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 4);
      setCount(start + (end - start) * ease);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    requestAnimationFrame(animate);
  }, [end, duration, start]);

  return count;
};

// 2. 打字机效果 Component - 支持简单 Markdown 渲染
const TypewriterText = ({ text, speed = 10, className }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    setDisplayedText("");
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayedText((prev) => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, speed);
    return () => clearInterval(timer);
  }, [text, speed]);

  // 使用简单的 Markdown 转 HTML
  return (
    <div
      className={`markdown-content leading-relaxed ${className}`}
      dangerouslySetInnerHTML={{ __html: simpleMarkdownToHtml(displayedText) }}
    />
  );
};

// --- UI Components ---

const Header = () => (
  <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 border-b border-gray-200/50 transition-all duration-300">
    <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <div className="flex items-center gap-3 group cursor-default">
        <div className="w-9 h-9 bg-black rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-black/20 group-hover:scale-105 transition-transform duration-300">
          S
        </div>
        <span className="font-semibold text-xl tracking-tight text-gray-900 group-hover:text-gray-600 transition-colors">
          AI Stock Insight
        </span>
      </div>
      <div className="flex items-center gap-2 text-xs font-medium px-3 py-1.5 bg-gray-100/80 rounded-full text-gray-500 border border-gray-200/50">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-[pulse_2s_infinite]"></div>
        <span>系统就绪</span>
      </div>
    </div>
  </header>
);

const Card = ({ title, icon: Icon, children, delay = 0 }) => (
  <div
    className="bg-white rounded-3xl border border-gray-100 p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_24px_rgba(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-500 ease-out opacity-0 animate-slideUp"
    style={{ animationDelay: `${delay}ms` }}
  >
    <div className="flex items-center gap-3 mb-4">
      <div className="p-2.5 bg-gray-50 rounded-2xl text-gray-900 shadow-sm">
        <Icon size={18} strokeWidth={2} />
      </div>
      <h3 className="font-bold text-gray-900 tracking-tight">{title}</h3>
    </div>
    <div className="text-gray-600 text-sm leading-7">
      {typeof children === 'string' ? <TypewriterText text={children} speed={5} /> : children}
    </div>
  </div>
);

const ScoreDisplay = ({ score, colorClass }) => {
  const value = useCountUp(score || 0, 1500);
  return <span className={`text-3xl font-bold tracking-tighter ${colorClass}`}>{value.toFixed(1)}</span>;
};

const DebateBar = ({ bullScore, bearScore }) => {
  const total = (bullScore || 0) + (bearScore || 0);
  const bullPercent = total > 0 ? ((bullScore || 0) / total) * 100 : 50;
  const [width, setWidth] = useState(50);

  useEffect(() => {
    const timer = setTimeout(() => setWidth(bullPercent), 500);
    return () => clearTimeout(timer);
  }, [bullPercent]);

  return (
    <div className="h-4 w-full bg-gray-100 rounded-full overflow-hidden flex relative mt-4">
      <div
        className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 transition-all duration-1000 ease-out relative"
        style={{ width: `${width}%` }}
      >
        {width > 10 && <div className="absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-white/20 to-transparent"></div>}
      </div>
      <div className="flex-1 bg-gray-200 h-full relative">
        <div className="absolute inset-y-0 left-0 w-1 bg-white/50 z-10 skew-x-12"></div>
      </div>
    </div>
  );
};

export default function App() {
  const [stockCode, setStockCode] = useState('600519');
  const [stockName, setStockName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [stage, setStage] = useState(0);

  // LLM Settings State
  const [apiKey, setApiKey] = useState('');
  const [apiUrl, setApiUrl] = useState('https://api.siliconflow.cn/v1');
  const [model, setModel] = useState('Qwen/Qwen2.5-7B-Instruct');
  const [customModel, setCustomModel] = useState('');
  const [threshold, setThreshold] = useState(3.0);
  const [rounds, setRounds] = useState(2);

  // Analysis Result State
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const getCurrentModel = () => model === 'custom' ? customModel : model;

  const resetAnalysis = () => {
    setStage(0);
    setIsAnalyzing(false);
    setStockName('');
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (stockCode.length !== 6) {
      alert("请输入有效的6位股票代码");
      return;
    }

    setIsAnalyzing(true);
    setStage(1);
    setResult(null);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: stockCode,
          base_url: apiUrl,
          api_key: apiKey || null,
          model: getCurrentModel(),
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
        if (data.stock_name) {
          setStockName(data.stock_name);
        }
        updateStage(data.step);
        break;
      case 'agent_output':
        updateAgentOutput(data.role, data.data);
        break;
      case 'risk_assessment':
        setStage(4);
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
        break;
      case 'error':
        setError(data.message);
        break;
    }
  };

  const updateStage = (step) => {
    if (step === 'fundamentals_analyst' || step === 'sentiment_analyst' ||
      step === 'news_analyst' || step === 'technical_analyst') {
      setStage(1);
    } else if (step === 'bullish_researcher' || step === 'bearish_researcher' ||
      step === 'researcher_debate') {
      setStage(2);
    } else if (step === 'trader') {
      setStage(3);
    } else if (step === 'risk_assessment' || step === 'portfolio_manager') {
      setStage(4);
    }
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
        setStage(2);
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
        setStage(3);
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
    <div className="min-h-screen bg-[#FDFDFD] text-gray-900 font-sans selection:bg-black selection:text-white pb-20">
      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .animate-slideUp { animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        .animate-fadeIn { animation: fadeIn 0.5s ease-out forwards; }
      `}</style>

      <Header />

      <main className="max-w-7xl mx-auto px-6 pt-12 space-y-16">

        {/* --- Input Section (只在未开始分析时显示) --- */}
        {stage === 0 && (
          <section className="text-center space-y-8 relative z-20">
            <div className="space-y-4 animate-slideUp" style={{ animationDelay: '0ms' }}>
              <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-gray-900">
                Market<span className="text-gray-300">Sentry</span>
              </h1>
              <p className="text-gray-500 text-lg md:text-xl font-medium max-w-lg mx-auto leading-relaxed">
                深度多智能体博弈系统<br />
                <span className="text-sm opacity-70">基本面 · 技术面 · 情绪面 · 风控</span>
              </p>
            </div>

            <div className="max-w-lg mx-auto animate-slideUp" style={{ animationDelay: '100ms' }}>
              <div className={`bg-white rounded-[2rem] shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-gray-100 transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] overflow-hidden ${showSettings ? 'shadow-[0_20px_40px_rgba(0,0,0,0.1)]' : 'hover:shadow-lg'}`}>

                {/* Primary Input Bar */}
                <div className="p-2.5 flex items-center relative z-20 bg-white">
                  <div className="pl-5 pr-2 text-gray-400">
                    <Search size={22} />
                  </div>
                  <input
                    type="text"
                    placeholder="股票代码 (600519)"
                    className="w-full bg-transparent outline-none text-xl font-medium placeholder:text-gray-300 h-12"
                    value={stockCode}
                    onChange={(e) => setStockCode(e.target.value)}
                    maxLength={6}
                  />
                  <button
                    onClick={() => setShowSettings(!showSettings)}
                    className={`p-3 rounded-full transition-all mr-1 duration-300 ${showSettings ? 'bg-gray-100 text-gray-900 rotate-90' : 'text-gray-400 hover:text-gray-800 hover:bg-gray-50'}`}
                  >
                    <Settings size={20} />
                  </button>
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || stockCode.length < 6}
                    className="bg-black text-white px-8 h-12 rounded-[1.5rem] font-semibold flex items-center gap-2 hover:bg-gray-800 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed group shadow-lg shadow-black/20"
                  >
                    {isAnalyzing ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <>
                        Run <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </button>
                </div>

                {/* Expanded Settings Panel - Apple Style */}
                <div className={`transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] ${showSettings ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'}`}>
                  <div className="p-6 pt-2 border-t border-gray-100 bg-white">
                    <div className="grid gap-8 text-left">

                      {/* Model Configuration */}
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">
                          <Cpu size={14} />
                          模型配置
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2 group">
                            <label className="text-xs font-semibold text-gray-500 ml-1">API 地址</label>
                            <input
                              type="text"
                              value={apiUrl}
                              onChange={(e) => setApiUrl(e.target.value)}
                              className="w-full bg-gray-50 group-hover:bg-gray-100 focus:bg-white border border-transparent focus:border-gray-200 focus:ring-4 focus:ring-gray-50 rounded-2xl px-4 py-3 text-sm transition-all outline-none font-medium text-gray-700 placeholder-gray-400"
                              placeholder="https://api.example.com/v1"
                            />
                          </div>

                          <div className="space-y-2 group">
                            <label className="text-xs font-semibold text-gray-500 ml-1">API 密钥</label>
                            <div className="relative">
                              <input
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                className="w-full bg-gray-50 group-hover:bg-gray-100 focus:bg-white border border-transparent focus:border-gray-200 focus:ring-4 focus:ring-gray-50 rounded-2xl px-4 py-3 text-sm transition-all outline-none font-medium text-gray-700 placeholder-gray-400 pl-10"
                                placeholder="sk-..."
                              />
                              <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                            </div>
                          </div>

                          <div className="space-y-2 group md:col-span-2">
                            <label className="text-xs font-semibold text-gray-500 ml-1">选择模型</label>
                            <div className="flex gap-3">
                              <div className="relative flex-1">
                                <select
                                  value={model}
                                  onChange={(e) => setModel(e.target.value)}
                                  className="w-full bg-gray-50 group-hover:bg-gray-100 focus:bg-white border border-transparent focus:border-gray-200 focus:ring-4 focus:ring-gray-50 rounded-2xl px-4 py-3 text-sm appearance-none transition-all outline-none font-medium text-gray-700 cursor-pointer"
                                >
                                  <option value="Qwen/Qwen2.5-7B-Instruct">Qwen 2.5 7B</option>
                                  <option value="Qwen/Qwen2.5-72B-Instruct">Qwen 2.5 72B</option>
                                  <option value="deepseek-ai/DeepSeek-V2.5">DeepSeek V2.5</option>
                                  <option value="THUDM/glm-4-9b-chat">GLM-4 9B</option>
                                  <option value="custom">自定义模型...</option>
                                </select>
                                <ChevronDown size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                              </div>

                              {model === 'custom' && (
                                <input
                                  type="text"
                                  value={customModel}
                                  onChange={(e) => setCustomModel(e.target.value)}
                                  placeholder="模型名称"
                                  className="flex-1 bg-white border border-gray-200 focus:border-black rounded-2xl px-4 py-3 text-sm transition-all outline-none font-medium animate-fadeIn"
                                />
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="h-px bg-gray-100 w-full" />

                      {/* Analysis Parameters */}
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">
                          <SlidersHorizontal size={14} />
                          分析参数
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-1">
                          <div className="space-y-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm font-medium text-gray-700">辩论阈值</span>
                              <span className="text-xs font-bold bg-black text-white px-2 py-1 rounded-md min-w-[32px] text-center">{threshold}</span>
                            </div>
                            <input
                              type="range"
                              min="1" max="10" step="0.5"
                              value={threshold}
                              onChange={(e) => setThreshold(e.target.value)}
                              className="w-full h-1.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-black"
                            />
                            <div className="flex justify-between text-[10px] text-gray-400 font-medium uppercase tracking-wider">
                              <span>低争议</span>
                              <span>高冲突</span>
                            </div>
                          </div>

                          <div className="space-y-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm font-medium text-gray-700">最大回合</span>
                              <span className="text-xs font-bold bg-black text-white px-2 py-1 rounded-md min-w-[32px] text-center">{rounds}</span>
                            </div>
                            <input
                              type="range"
                              min="1" max="5" step="1"
                              value={rounds}
                              onChange={(e) => setRounds(e.target.value)}
                              className="w-full h-1.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-black"
                            />
                            <div className="flex justify-between text-[10px] text-gray-400 font-medium uppercase tracking-wider">
                              <span>快速</span>
                              <span>深度</span>
                            </div>
                          </div>
                        </div>
                      </div>

                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-lg mx-auto bg-red-50 border border-red-200 rounded-2xl p-4 text-red-700 animate-slideUp">
            ❌ 错误: {error}
          </div>
        )}

        {/* --- Results Stream (分析开始后显示) --- */}
        {stage >= 1 && (
          <div className="space-y-8 relative animate-slideUp">

            {/* 股票信息头 (代替了搜索框) */}
            <div className="flex items-center justify-between pb-6 border-b border-gray-100">
              <div className="flex items-center gap-4">
                <button onClick={resetAnalysis} className="p-2 -ml-2 text-gray-400 hover:text-black hover:bg-gray-100 rounded-full transition-colors">
                  <ArrowLeft size={24} />
                </button>
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 tracking-tight">{stockName || '加载中...'}</h2>
                  <span className="text-lg text-gray-400 font-medium tracking-wide">{stockCode}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {isAnalyzing ? (
                  <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full text-sm font-medium text-gray-600">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                    分析中...
                  </div>
                ) : (
                  <div className="px-4 py-2 bg-black text-white rounded-full text-sm font-medium">
                    分析完成
                  </div>
                )}
              </div>
            </div>

            {/* Layer 1: Analysis Grid */}
            <section className="space-y-6">
              <div className="flex items-center gap-3 text-gray-400 text-sm font-medium px-2 animate-fadeIn">
                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                LAYER 1 : 数据聚合与初步分析
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <Card title="基本面" icon={Briefcase} delay={100}>
                  {result?.layer1?.fundamental || "正在分析基本面数据..."}
                </Card>
                <Card title="情绪面" icon={Activity} delay={200}>
                  {result?.layer1?.sentiment || "正在扫描社交媒体情绪..."}
                </Card>
                <Card title="新闻资讯" icon={Newspaper} delay={300}>
                  {result?.layer1?.news || "正在聚合新闻来源..."}
                </Card>
                <Card title="技术指标" icon={BarChart2} delay={400}>
                  {result?.layer1?.technical || "正在计算技术指标..."}
                </Card>
              </div>
            </section>

            {/* Layer 2: The Debate */}
            {stage >= 2 && (
              <section className="space-y-6">
                <div className="flex items-center gap-3 text-gray-400 text-sm font-medium px-2 animate-fadeIn">
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                  LAYER 2 : 多空博弈
                </div>
                <div className="bg-white rounded-[2.5rem] border border-gray-100 shadow-sm p-8 animate-slideUp overflow-hidden relative">

                  {/* Visual Score Bar */}
                  <div className="mb-8">
                    <div className="flex justify-between items-end mb-2 px-1">
                      <div className="text-emerald-600 font-bold flex flex-col">
                        <span className="text-xs uppercase tracking-wider text-emerald-600/60 mb-1">看多评分</span>
                        <ScoreDisplay score={result?.layer2?.bullScore} colorClass="text-emerald-600" />
                      </div>
                      <div className="text-rose-500 font-bold flex flex-col text-right">
                        <span className="text-xs uppercase tracking-wider text-rose-500/60 mb-1">看空评分</span>
                        <ScoreDisplay score={result?.layer2?.bearScore} colorClass="text-rose-500" />
                      </div>
                    </div>
                    <DebateBar bullScore={result?.layer2?.bullScore} bearScore={result?.layer2?.bearScore} />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 relative z-10">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-emerald-700 font-semibold text-sm bg-emerald-50 w-fit px-3 py-1 rounded-full">
                        <TrendingUp size={16} /> 看多逻辑
                      </div>
                      <div className="text-gray-600 text-sm leading-relaxed">
                        {result?.layer2?.bullView ? (
                          <TypewriterText text={result.layer2.bullView} speed={20} />
                        ) : "正在构建看多论点..."}
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-rose-700 font-semibold text-sm bg-rose-50 w-fit px-3 py-1 rounded-full">
                        <TrendingDown size={16} /> 看空逻辑
                      </div>
                      <div className="text-gray-600 text-sm leading-relaxed">
                        {result?.layer2?.bearView ? (
                          <TypewriterText text={result.layer2.bearView} speed={20} />
                        ) : "正在构建看空论点..."}
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Layer 3: Decision - 白色背景 */}
            {stage >= 3 && (
              <section className="space-y-6">
                <div className="flex items-center gap-3 text-gray-400 text-sm font-medium px-2 animate-fadeIn">
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                  LAYER 3 : 交易员决策
                </div>

                <div className="bg-white text-gray-900 rounded-[2.5rem] p-8 md:p-12 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.05)] border border-gray-100 animate-slideUp relative overflow-hidden group">
                  {/* Subtle Gradient Background */}
                  <div className="absolute inset-0 bg-gradient-to-br from-gray-50/50 to-white pointer-events-none"></div>

                  <div className="relative z-10 flex flex-col md:flex-row gap-8 items-start">
                    <div className="flex-shrink-0 flex flex-col items-center md:items-start gap-2 min-w-[140px]">
                      <span className="text-gray-400 text-xs font-bold tracking-[0.2em] uppercase">交易信号</span>
                      <div className="text-6xl font-bold tracking-tighter text-gray-900">
                        {result?.layer3?.action || "计算中..."}
                      </div>
                      {result?.layer3?.confidence && (
                        <div className="flex items-center gap-2 mt-2 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-100">
                          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                          <span className="text-xs font-bold text-emerald-700">置信度: {result.layer3.confidence}</span>
                        </div>
                      )}
                    </div>

                    <div className="w-px h-auto bg-gray-100 hidden md:block self-stretch"></div>

                    <div className="flex-1 space-y-4">
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <Zap size={16} className="text-yellow-500 fill-yellow-500" />
                        <span className="font-medium text-gray-500">核心逻辑</span>
                      </div>
                      <div className="text-lg text-gray-800 font-light leading-relaxed">
                        {result?.layer3?.reasoning ? (
                          <TypewriterText text={result.layer3.reasoning} speed={15} />
                        ) : "正在生成交易逻辑..."}
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Layer 4: Strategies */}
            {stage >= 4 && (
              <section className="space-y-6 pb-12">
                <div className="flex items-center gap-3 text-gray-400 text-sm font-medium px-2 animate-fadeIn">
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                  LAYER 4 : 仓位风控建议
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* 激进 */}
                  <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm animate-slideUp hover:border-rose-100 hover:shadow-lg hover:shadow-rose-50/50 transition-all duration-300" style={{ animationDelay: '0ms' }}>
                    <div className="w-10 h-10 bg-rose-50 rounded-2xl flex items-center justify-center text-rose-500 mb-4">
                      <AlertTriangle size={20} />
                    </div>
                    <h4 className="font-bold text-gray-900 mb-2">激进型</h4>
                    <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">{result?.layer4?.aggressive || "加载中..."}</p>
                  </div>
                  {/* 稳健 */}
                  <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm animate-slideUp hover:border-blue-100 hover:shadow-lg hover:shadow-blue-50/50 transition-all duration-300" style={{ animationDelay: '150ms' }}>
                    <div className="w-10 h-10 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-500 mb-4">
                      <Scale size={20} />
                    </div>
                    <h4 className="font-bold text-gray-900 mb-2">稳健型</h4>
                    <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">{result?.layer4?.balanced || "加载中..."}</p>
                  </div>
                  {/* 保守 */}
                  <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm animate-slideUp hover:border-emerald-100 hover:shadow-lg hover:shadow-emerald-50/50 transition-all duration-300" style={{ animationDelay: '300ms' }}>
                    <div className="w-10 h-10 bg-emerald-50 rounded-2xl flex items-center justify-center text-emerald-500 mb-4">
                      <Shield size={20} />
                    </div>
                    <h4 className="font-bold text-gray-900 mb-2">保守型</h4>
                    <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">{result?.layer4?.conservative || "加载中..."}</p>
                  </div>
                </div>
              </section>
            )}

          </div>
        )}
      </main>
    </div>
  );
}
