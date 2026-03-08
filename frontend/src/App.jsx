import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Search, Settings, Activity, Briefcase,
  Newspaper, BarChart2, TrendingUp, TrendingDown,
  Shield, Zap, Scale, ArrowRight, Lock,
  AlertTriangle, Cpu, SlidersHorizontal, ChevronDown,
  ArrowLeft, Sparkles, CheckCircle2, GitCompare, Plus, X, Trophy
} from 'lucide-react';



// 后端API地址 - 从配置文件动态读取（由 start_lan.sh 生成）
// 动态计算后端 URL（绕过 Vite 代理，避免流式缓冲问题）
// 后端始终在同一台机器的 8000 端口，CORS 已允许 *
const BACKEND_URL = window.APP_CONFIG?.BACKEND_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

// --- Styles & Fonts ---
const GlobalStyles = () => (
  <style>
    {`
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

      body {
        font-family: 'Inter', sans-serif;
      }

      /* 优化滚动条 */
      ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
      }

      ::-webkit-scrollbar-track {
        background: transparent;
      }

      ::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 3px;
      }

      /* 核心优化：iOS 风格物理动效 
         1. 加入 blur 滤镜，模拟高速运动的视觉残留
         2. 使用 cubic-bezier(0.16, 1, 0.3, 1) 模拟磁力吸附感
      */
      @keyframes slideUpFade {
        0% {
          opacity: 0;
          transform: translateY(30px) scale(0.96);
          filter: blur(10px);
        }
        100% {
          opacity: 1;
          transform: translateY(0) scale(1);
          filter: blur(0px);
        }
      }

      @keyframes fadeIn {
        from { opacity: 0; filter: blur(5px); }
        to { opacity: 1; filter: blur(0); }
      }

      /* 线条生长动画 */
      @keyframes drawLine {
        from { height: 0%; opacity: 0; }
        to { height: 100%; opacity: 1; }
      }

      @keyframes pulse-soft {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(0.95); }
      }

      @keyframes blob {
        0% { transform: translate(0px, 0px) scale(1); }
        33% { transform: translate(30px, -50px) scale(1.1); }
        66% { transform: translate(-20px, 20px) scale(0.9); }
        100% { transform: translate(0px, 0px) scale(1); }
      }

      /* 柔和呼吸光标 */
      @keyframes blink-soft {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
      }

      /* Apple-style Easing - 急加速、慢减速的曲线 */
      .animate-slideUp {
        animation: slideUpFade 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }

      .animate-fadeIn {
        animation: fadeIn 0.8s ease-out forwards;
      }

      .animate-drawLine {
        animation: drawLine 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }

      .animate-blob {
        animation: blob 10s infinite;
      }

      .animate-blink {
        animation: blink-soft 1s ease-in-out infinite;
      }

      .delay-100 { animation-delay: 100ms; }
      .delay-200 { animation-delay: 200ms; }
      .delay-300 { animation-delay: 300ms; }
      .delay-500 { animation-delay: 500ms; }

      .animation-delay-2000 { animation-delay: 2s; }
      .animation-delay-4000 { animation-delay: 4s; }

      /* 玻璃拟态增强 */
      .glass-panel {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5);
      }

      .text-balance {
        text-wrap: balance;
      }
    `}
  </style>
);

// Markdown 自定义样式组件
const markdownComponents = {
  h1: ({ node, ...props }) => <h1 className="font-bold text-xl mt-4 mb-2 text-gray-900" {...props} />,
  h2: ({ node, ...props }) => <h2 className="font-semibold text-lg mt-4 mb-2 text-gray-900" {...props} />,
  h3: ({ node, ...props }) => <h3 className="font-medium text-base mt-3 mb-1 text-gray-900" {...props} />,
  h4: ({ node, ...props }) => <h4 className="font-medium text-sm mt-2 mb-1 text-gray-800" {...props} />,
  p: ({ node, ...props }) => <p className="mb-2 leading-relaxed" {...props} />,
  strong: ({ node, ...props }) => <strong className="font-semibold text-gray-900" {...props} />,
  em: ({ node, ...props }) => <em className="italic" {...props} />,
  ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
  ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
  li: ({ node, ...props }) => <li className="ml-2" {...props} />,
  // 代码块：直接显示预格式化内容，不用代码样式
  code: ({ node, inline, children, ...props }) => {
    if (inline) {
      return <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm" {...props}>{children}</code>;
    }
    // 块级代码：当作预格式化文本，保留换行
    return <pre className="whitespace-pre-wrap text-sm leading-relaxed" {...props}>{children}</pre>;
  },
  // pre 标签：直接渲染子元素，不添加额外样式
  pre: ({ node, children, ...props }) => <>{children}</>,
  blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-gray-300 pl-4 italic my-2" {...props} />,
};

// 预处理LLM输出内容，移除代码块包裹，转换中文括号为加粗格式
const cleanMarkdownContent = (content) => {
  if (!content || typeof content !== 'string') return content;

  // 移除开头和结尾的 ``` 代码块标记
  let cleaned = content.trim();

  // 移除开头的 ``` 或 ```markdown 等
  cleaned = cleaned.replace(/^```[\w]*\n?/gm, '');
  // 移除结尾的 ```
  cleaned = cleaned.replace(/\n?```$/gm, '');

  // 将【标题】格式转换为 **标题** 格式，使其更醒目
  cleaned = cleaned.replace(/【([^】]+)】/g, '**$1**');

  return cleaned.trim();
};

// --- Custom Hooks ---

const useCountUp = (end, duration = 1500, start = 0) => {
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

const TypewriterText = ({ text, targetDuration = 2500, className }) => {
  const [displayedText, setDisplayedText] = useState("");

  // 预处理内容，移除代码块包裹
  const cleanedText = cleanMarkdownContent(text);

  useEffect(() => {
    setDisplayedText("");
    if (!cleanedText || cleanedText.length === 0) return;

    // 根据文本长度动态计算速度，确保在目标时间内完成
    // 最小速度 5ms（快），最大速度 50ms（慢）
    const calculatedSpeed = Math.max(5, Math.min(50, targetDuration / cleanedText.length));

    let i = 0;
    const timer = setInterval(() => {
      if (i < cleanedText.length) {
        setDisplayedText((prev) => prev + cleanedText.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, calculatedSpeed);
    return () => clearInterval(timer);
  }, [cleanedText, targetDuration]);

  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={markdownComponents}
      >
        {displayedText}
      </ReactMarkdown>
    </div>
  );
};

// --- UI Components ---

// 标题打字机组件 - 包含随机回退和补全动画
const TypewriterTitle = () => {
  const [text, setText] = useState("");
  const fullText = "Sentry";

  useEffect(() => {
    let timeout;

    const animate = (currentStr, isDeleting, deleteTarget) => {
      let typeSpeed = isDeleting ? 100 : 150;

      // 1. 完成输入完整单词
      if (!isDeleting && currentStr === fullText) {
        typeSpeed = 2500;
        timeout = setTimeout(() => {
          const keepCount = Math.floor(Math.random() * (fullText.length - 2)) + 1;
          animate(currentStr, true, keepCount);
        }, typeSpeed);
        return;
      }

      // 2. 完成删除任务
      if (isDeleting && currentStr.length === deleteTarget) {
        typeSpeed = 500;
        timeout = setTimeout(() => {
          animate(currentStr, false, 0);
        }, typeSpeed);
        return;
      }

      // 3. 执行打字或删除动作
      timeout = setTimeout(() => {
        const nextText = isDeleting
          ? currentStr.slice(0, -1)
          : fullText.substring(0, currentStr.length + 1);

        setText(nextText);
        animate(nextText, isDeleting, deleteTarget);
      }, typeSpeed);
    };

    timeout = setTimeout(() => animate("", false, 0), 800);
    return () => clearTimeout(timeout);
  }, []);

  return (
    <span className="text-gray-300">
      {text}
      <span className="inline-block w-[8px] md:w-[10px] h-[0.75em] bg-gray-300 ml-2 animate-blink rounded-[3px]" style={{ verticalAlign: '-0.05em' }}></span>
    </span>
  );
};

const Header = () => (
  <header className="sticky top-0 z-50 transition-all duration-300">
    <div className="absolute inset-0 bg-white/70 backdrop-blur-xl border-b border-gray-200/50"></div>

    <div className="relative max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
      <div className="flex items-center gap-3 group cursor-default">
        <div className="w-9 h-9 bg-black rounded-[10px] flex items-center justify-center text-white shadow-lg shadow-black/10 group-hover:scale-105 transition-transform duration-500 ease-out">
          <Sparkles size={18} fill="white" className="text-white" />
        </div>
        <span className="font-semibold text-xl tracking-tight text-gray-900">
          AI Stock Insight
        </span>
      </div>
      <div className="flex items-center gap-2 text-[11px] font-bold tracking-wider px-3 py-1.5 bg-gray-50/80 rounded-full text-gray-400 border border-gray-100 uppercase">
        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse"></div>
        System Ready
      </div>
    </div>
  </header>
);

// 流体时间轴连接器 - 线条像水流一样向下生长
const TimelineConnector = ({ active }) => (
  <div className="absolute left-[-29px] top-8 bottom-0 w-px bg-gray-100 flex flex-col items-center overflow-hidden">
    {active && (
      <div className="w-1.5 h-full bg-gradient-to-b from-gray-200 to-transparent animate-drawLine origin-top" />
    )}
  </div>
);

// 使用 iOS 标准贝塞尔曲线的步骤指示器
const StepIndicator = ({ active, completed, number }) => (
  <div className={`absolute left-[-42px] top-0 w-7 h-7 rounded-full flex items-center justify-center text-xs
    font-bold border-[3px] z-10 transition-all duration-700 ${completed ? 'bg-black border-black text-white' :
      active ? 'bg-white border-black text-black scale-110 shadow-lg' : 'bg-white border-gray-200 text-gray-300'
    }`} style={{ transitionTimingFunction: 'cubic-bezier(0.16, 1, 0.3, 1)' }}>
    {completed ? <CheckCircle2 size={12} /> : number}
  </div>
);

const Card = ({ title, icon: Icon, children, className = "", delay = 0 }) => (
  <div
    className={`bg-white rounded-[24px] p-8 border border-gray-100/80 shadow-[0_8px_40px_rgba(0,0,0,0.03)]
      hover:shadow-[0_20px_60px_rgba(0,0,0,0.06)] hover:-translate-y-1 hover:border-gray-200 transition-all
      duration-700 ease-out opacity-0 animate-slideUp group ${className}`}
    style={{ animationDelay: `${delay}ms` }}
  >
    <div className="flex items-center gap-3.5 mb-5">
      <div className="p-2.5 bg-gray-50 rounded-xl text-gray-900 group-hover:bg-black group-hover:text-white transition-colors duration-500">
        <Icon size={18} strokeWidth={2} />
      </div>
      <h3 className="font-semibold text-gray-900 tracking-tight text-base">{title}</h3>
    </div>
    <div className="text-gray-600 text-[15px] leading-7 font-normal">
      {typeof children === 'string' ? <TypewriterText text={children} /> : children}
    </div>
  </div>
);

const ScoreDisplay = ({ score, colorClass }) => {
  const value = useCountUp(score || 0, 1500);
  return <span className={`text-5xl font-bold tracking-tighter tabular-nums ${colorClass}`}>{value.toFixed(1)}</span>;
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
    <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden flex relative mt-5">
      <div
        className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 relative transition-all duration-1000 ease-[cubic-bezier(0.2,0.8,0.2,1)]"
        style={{ width: `${width}%` }}
      >
        <div className="absolute inset-y-0 right-0 w-px bg-white/50 shadow-[0_0_10px_rgba(255,255,255,0.8)]"></div>
      </div>
      {/* 中线标记 */}
      <div className="absolute left-1/2 top-0 bottom-0 w-px bg-white z-10 mix-blend-overlay"></div>
    </div>
  );
};

export default function App() {
  const [stockCode, setStockCode] = useState('600519');
  const [stockName, setStockName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [stage, setStage] = useState(0);

  // 分析模式：'single' = 单股分析，'compare' = 对比分析
  const [mode, setMode] = useState('single');
  // 对比分析状态
  const [compareSymbols, setCompareSymbols] = useState(['600519', '000001', '']);
  const [isComparing, setIsComparing] = useState(false);
  const [compareResult, setCompareResult] = useState(null);
  const [compareError, setCompareError] = useState(null);
  const [compareProgress, setCompareProgress] = useState(null); // { done, total, symbols, partial }

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

  const handleCompare = async () => {
    const validSymbols = compareSymbols.filter(s => s.trim().length === 6);
    if (validSymbols.length < 2) {
      alert("请至少输入2个有效的6位股票代码");
      return;
    }

    setIsComparing(true);
    setCompareResult(null);
    setCompareError(null);
    setCompareProgress(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/compare`, {
        method: 'POST',
        credentials: 'omit',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbols: validSymbols,
          base_url: apiUrl,
          api_key: apiKey || null,
          model: getCurrentModel(),
          debate_threshold: parseFloat(threshold),
          max_rounds: 1,
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
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            console.log('[Compare Stream]', data.type, data);
            if (data.type === 'compare_start') {
              setCompareProgress({ done: 0, total: data.total, symbols: data.symbols, partial: [] });
            } else if (data.type === 'stock_done') {
              setCompareProgress(prev => ({
                ...prev,
                done: data.done,
                total: data.total,
                partial: [...(prev?.partial || []), data.result],
              }));
            } else if (data.type === 'compare_result') {
              console.log('[Compare Result] rankings:', data.rankings, 'failed:', data.failed);
              setCompareResult(data);
              setCompareProgress(null);
            } else if (data.type === 'error') {
              setCompareError(data.message + (data.traceback ? '\n' + data.traceback : ''));
            }
          } catch (e) { console.warn('[Compare] JSON parse error', e, line); }
        }
      }
    } catch (err) {
      setCompareError(err.message);
    } finally {
      setIsComparing(false);
    }
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
      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        credentials: 'omit',
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
      step === 'news_analyst' || step === 'technical_analyst' || step === 'quant_analyst') {
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
      case 'quant_analyst':
        setResult(prev => ({
          ...prev,
          layer1: { ...(prev?.layer1 || {}), quant: data.content, quantScore: data.score }
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
    <div className="min-h-screen bg-[#FBFBFD] text-gray-900 relative overflow-x-hidden selection:bg-emerald-100 selection:text-emerald-900 pb-32">
      <GlobalStyles />

      {/* --- Ambient Background --- */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-200/30 rounded-full mix-blend-multiply filter blur-[100px] animate-blob"></div>
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-200/30 rounded-full mix-blend-multiply filter blur-[100px] animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-[-20%] left-[20%] w-[40%] h-[40%] bg-emerald-100/40 rounded-full mix-blend-multiply filter blur-[100px] animate-blob animation-delay-4000"></div>
      </div>

      <Header />

      <main className="relative z-10 max-w-6xl mx-auto px-8 pt-16 space-y-20">

        {/* --- Landing & Input --- */}
        {stage === 0 && (
          <section className="text-center space-y-10 relative">
            <div className="space-y-6 animate-slideUp">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-gray-200 shadow-sm text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">
                <Cpu size={14} /> AI-Powered Analysis
              </div>
              <h1 className="text-7xl md:text-8xl font-bold tracking-tight text-gray-900">
                Market <TypewriterTitle />
              </h1>
              <p className="text-gray-500 text-2xl font-normal max-w-2xl mx-auto leading-relaxed text-balance">
                多智能体深度博弈系统，为您提供专业的投资洞察。
              </p>
            </div>

            {/* 模式切换 Tab */}
            <div className="flex justify-center">
              <div className="inline-flex bg-gray-100 rounded-2xl p-1.5 gap-1">
                <button
                  onClick={() => setMode('single')}
                  className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${mode === 'single'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                  <Search size={15} /> 单股深度分析
                </button>
                <button
                  onClick={() => setMode('compare')}
                  className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${mode === 'compare'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                  <GitCompare size={15} /> 多股对比择优
                </button>
              </div>
            </div>

            <div className="max-w-2xl mx-auto">
              <div className={`glass-panel rounded-[28px] shadow-[0_20px_50px_rgba(0,0,0,0.04)] transition-all duration-500 overflow-hidden ${showSettings ? 'shadow-[0_30px_60px_rgba(0,0,0,0.08)]' : ''}`}>

                {/* 单股分析输入 */}
                {mode === 'single' && (
                  <div className="p-3 flex items-center">
                    <div className="pl-6 pr-4 text-gray-400">
                      <Search size={24} strokeWidth={2} />
                    </div>
                    <input
                      type="text"
                      placeholder="股票代码 (e.g. 600519)"
                      className="w-full bg-transparent outline-none text-2xl font-medium placeholder:text-gray-300 h-14 tracking-tight tabular-nums"
                      value={stockCode}
                      onChange={(e) => setStockCode(e.target.value)}
                      maxLength={6}
                    />
                    <button
                      onClick={() => setShowSettings(!showSettings)}
                      className={`p-4 rounded-full transition-all mr-2 hover:bg-gray-100 text-gray-400 ${showSettings ? 'bg-gray-100 text-gray-900' : ''}`}
                    >
                      <Settings size={22} strokeWidth={2} />
                    </button>
                    <button
                      onClick={handleAnalyze}
                      disabled={isAnalyzing || stockCode.length < 6}
                      className="h-14 px-8 bg-black text-white rounded-[20px] font-semibold text-lg flex items-center gap-2 hover:bg-gray-800 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-lg shadow-black/20"
                    >
                      {isAnalyzing ? (
                        <div className="w-5 h-5 border-[2.5px] border-white/30 border-t-white rounded-full animate-spin" />
                      ) : (
                        <ArrowRight size={24} strokeWidth={2.5} />
                      )}
                    </button>
                  </div>
                )}

                {/* 多股对比输入 */}
                {mode === 'compare' && (
                  <div className="p-6 space-y-4">
                    <div className="text-left mb-2">
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">输入2-5只股票代码进行横向对比</p>
                    </div>
                    {compareSymbols.map((sym, idx) => (
                      <div key={idx} className="flex items-center gap-3">
                        <span className="w-6 h-6 rounded-full bg-gray-100 text-xs font-bold text-gray-500 flex items-center justify-center flex-shrink-0">{idx + 1}</span>
                        <input
                          type="text"
                          placeholder={`股票代码 ${idx + 1} (e.g. 60${String(idx).padStart(4, '0')})`}
                          className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-lg font-medium outline-none focus:border-gray-400 tabular-nums transition-colors"
                          value={sym}
                          maxLength={6}
                          onChange={(e) => {
                            const updated = [...compareSymbols];
                            updated[idx] = e.target.value;
                            setCompareSymbols(updated);
                          }}
                        />
                        {compareSymbols.length > 2 && (
                          <button
                            onClick={() => setCompareSymbols(prev => prev.filter((_, i) => i !== idx))}
                            className="p-2 rounded-xl hover:bg-red-50 text-gray-300 hover:text-red-400 transition-colors"
                          >
                            <X size={18} />
                          </button>
                        )}
                      </div>
                    ))}
                    {compareSymbols.length < 5 && (
                      <button
                        onClick={() => setCompareSymbols(prev => [...prev, ''])}
                        className="w-full py-3 border-2 border-dashed border-gray-200 rounded-xl text-sm text-gray-400 hover:border-gray-300 hover:text-gray-500 transition-colors flex items-center justify-center gap-2"
                      >
                        <Plus size={16} /> 添加更多股票（最多5只）
                      </button>
                    )}
                    <div className="flex gap-3 pt-2">
                      <button
                        onClick={() => setShowSettings(!showSettings)}
                        className={`p-3 rounded-xl transition-all hover:bg-gray-100 text-gray-400 border border-gray-200 ${showSettings ? 'bg-gray-100 text-gray-900' : ''}`}
                      >
                        <Settings size={20} strokeWidth={2} />
                      </button>
                      <button
                        onClick={handleCompare}
                        disabled={isComparing || compareSymbols.filter(s => s.length === 6).length < 2}
                        className="flex-1 h-12 bg-black text-white rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-gray-800 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-black/20"
                      >
                        {isComparing ? (
                          <><div className="w-4 h-4 border-[2.5px] border-white/30 border-t-white rounded-full animate-spin" /> 分析对比中...</>
                        ) : (
                          <><GitCompare size={18} /> 开始对比分析</>
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {/* Settings Panel */}
                <div className={`transition-all duration-500 overflow-hidden ease-[cubic-bezier(0.2,0.8,0.2,1)] ${showSettings ? 'max-h-[600px] opacity-100 border-t border-gray-100' : 'max-h-0 opacity-0'}`}>
                  <div className="p-8 bg-gray-50/50 space-y-6">
                    <div className="grid grid-cols-2 gap-8">
                      {/* API URL */}
                      <div className="space-y-3 col-span-2">
                        <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">API URL</label>
                        <input
                          type="text"
                          value={apiUrl}
                          onChange={(e) => setApiUrl(e.target.value)}
                          className="w-full bg-white p-3 rounded-2xl border border-gray-200 text-sm font-medium"
                          placeholder="https://api.example.com/v1"
                        />
                      </div>

                      {/* API Key */}
                      <div className="space-y-3 col-span-2">
                        <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">API Key</label>
                        <div className="relative">
                          <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                          <input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="w-full bg-white p-3 pl-10 rounded-2xl border border-gray-200 text-sm font-medium"
                            placeholder="sk-..."
                          />
                        </div>
                      </div>

                      {/* Model Select */}
                      <div className="space-y-3 col-span-2">
                        <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Model</label>
                        <div className="relative">
                          <select
                            value={model}
                            onChange={(e) => setModel(e.target.value)}
                            className="w-full bg-white p-3 rounded-2xl border border-gray-200 text-sm font-medium appearance-none cursor-pointer"
                          >
                            <option value="Qwen/Qwen2.5-7B-Instruct">Qwen 2.5 7B</option>
                            <option value="Qwen/Qwen2.5-72B-Instruct">Qwen 2.5 72B</option>
                            <option value="deepseek-ai/DeepSeek-V2.5">DeepSeek V2.5</option>
                            <option value="THUDM/glm-4-9b-chat">GLM-4 9B</option>
                            <option value="custom">自定义模型...</option>
                          </select>
                          <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                        </div>
                        {model === 'custom' && (
                          <input
                            type="text"
                            value={customModel}
                            onChange={(e) => setCustomModel(e.target.value)}
                            placeholder="模型名称"
                            className="w-full bg-white p-3 rounded-2xl border border-gray-200 text-sm font-medium mt-2"
                          />
                        )}
                      </div>

                      {/* Threshold */}
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

                      {/* Rounds */}
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

            {/* 对比结果展示 */}
            {mode === 'compare' && (compareResult || isComparing || compareError) && (
              <div className="max-w-2xl mx-auto space-y-6 animate-slideUp">
                {/* 实时进度 */}
                {isComparing && (
                  <div className="glass-panel rounded-2xl p-6 space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-5 h-5 border-[2.5px] border-gray-200 border-t-gray-600 rounded-full animate-spin flex-shrink-0" />
                      <p className="text-sm font-semibold text-gray-700">
                        {compareProgress
                          ? `多智能体并行分析中... ${compareProgress.done}/${compareProgress.total} 完成`
                          : '正在启动分析系统...'}
                      </p>
                    </div>
                    {compareProgress && (
                      <>
                        {/* 总进度条 */}
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gray-900 rounded-full transition-all duration-500"
                            style={{ width: `${(compareProgress.done / compareProgress.total) * 100}%` }}
                          />
                        </div>
                        {/* 每只股票状态 */}
                        <div className="grid grid-cols-2 gap-2">
                          {compareProgress.symbols.map(sym => {
                            const done = compareProgress.partial?.some(r => r.symbol === sym);
                            const failed = compareProgress.partial?.find(r => r.symbol === sym && !r.success);
                            return (
                              <div key={sym} className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium transition-all ${done ? (failed ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-700') : 'bg-gray-50 text-gray-400'}`}>
                                {done
                                  ? (failed ? '❌' : '✅')
                                  : <div className="w-3 h-3 border border-gray-300 border-t-gray-500 rounded-full animate-spin" />}
                                <span className="tabular-nums">{sym}</span>
                                {done && !failed && compareProgress.partial.find(r => r.symbol === sym)?.composite_score != null && (
                                  <span className="ml-auto font-bold">{compareProgress.partial.find(r => r.symbol === sym).composite_score.toFixed(1)}</span>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </>
                    )}
                  </div>
                )}
                {compareError && (
                  <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-red-700 text-sm">
                    ❌ {compareError}
                  </div>
                )}
                {compareResult && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h2 className="text-2xl font-bold text-gray-900">对比分析结果</h2>
                      <button onClick={() => { setCompareResult(null); setCompareError(null); setCompareProgress(null); }} className="text-xs text-gray-400 hover:text-gray-600 transition-colors">清除</button>
                    </div>
                    {/* Top Pick */}
                    {compareResult.top_pick && (
                      <div className="glass-panel rounded-2xl p-5 border-2 border-yellow-300/60 bg-yellow-50/40 flex items-center gap-4">
                        <Trophy size={28} className="text-yellow-500 flex-shrink-0" />
                        <div>
                          <p className="text-xs font-bold text-yellow-600 uppercase tracking-widest">最优推荐</p>
                          <p className="text-xl font-bold text-gray-900">{compareResult.top_pick.name || compareResult.top_pick.symbol} <span className="text-gray-400 font-medium text-base">{compareResult.top_pick.symbol}</span></p>
                          <p className="text-sm text-gray-500 mt-0.5">{compareResult.summary}</p>
                        </div>
                        <div className="ml-auto text-right flex-shrink-0">
                          <p className="text-3xl font-bold text-gray-900">{(compareResult.top_pick.composite_score || 0).toFixed(1)}</p>
                          <p className="text-xs text-gray-400 font-medium">综合评分</p>
                        </div>
                      </div>
                    )}
                    {/* Ranking Cards */}
                    <div className="space-y-3">
                      {compareResult.rankings && compareResult.rankings.map((stock, i) => (
                        <div key={stock.symbol} className={`glass-panel rounded-2xl p-4 flex items-center gap-4 ${i === 0 ? 'ring-1 ring-yellow-200' : ''}`}>
                          <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${i === 0 ? 'bg-yellow-400 text-white' : i === 1 ? 'bg-gray-300 text-gray-700' : i === 2 ? 'bg-amber-600/70 text-white' : 'bg-gray-100 text-gray-500'}`}>
                            {i + 1}
                          </span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-bold text-gray-900">{stock.name || stock.symbol}</span>
                              <span className="text-xs text-gray-400 tabular-nums">{stock.symbol}</span>
                              {stock.strategy_type && (
                                <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full text-xs font-semibold">{stock.strategy_type}</span>
                              )}
                              {stock.drive_attribute && (
                                <span className="px-2 py-0.5 bg-purple-50 text-purple-600 rounded-full text-xs font-semibold">{stock.drive_attribute}</span>
                              )}
                              <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${stock.recommendation === '买入' || stock.recommendation === '强烈买入' ? 'bg-green-100 text-green-700' :
                                stock.recommendation === '卖出' || stock.recommendation === '强烈卖出' ? 'bg-red-100 text-red-700' :
                                  'bg-gray-100 text-gray-600'
                                }`}>{stock.recommendation || '—'}</span>
                            </div>
                            {/* Score bar - scores are 0-10, multiply by 10 for % width */}
                            <div className="mt-2 grid grid-cols-5 gap-1 text-center">
                              {[['基本面', stock.scores?.fundamentals], ['技术面', stock.scores?.technical], ['量化', stock.scores?.quant], ['多方', stock.scores?.bullish], ['空方', stock.scores?.bearish]].map(([label, val]) => (
                                <div key={label}>
                                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-gray-900 rounded-full transition-all duration-700" style={{ width: `${Math.min(100, (val || 0) * 10)}%` }} />
                                  </div>
                                  <p className="text-[9px] text-gray-400 mt-0.5">{label} {val != null ? val.toFixed(1) : '—'}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <p className="text-2xl font-bold text-gray-900">{(stock.composite_score || 0).toFixed(1)}</p>
                            <p className="text-[10px] text-gray-400">综合分</p>
                          </div>
                        </div>
                      ))}
                    </div>
                    {/* Failed Stocks */}
                    {compareResult.failed && compareResult.failed.length > 0 && (
                      <div className="space-y-2 mt-2">
                        <p className="text-xs font-bold text-red-400 uppercase tracking-widest">分析失败</p>
                        {compareResult.failed.map(f => (
                          <div key={f.symbol} className="bg-red-50 border border-red-100 rounded-2xl p-3 text-sm text-red-700">
                            <span className="font-bold mr-2">{f.symbol}</span>
                            {f.error ? f.error.split('\n')[0] : '未知错误'}
                          </div>
                        ))}
                      </div>
                    )}
                    {/* No Rankings */}
                    {(!compareResult.rankings || compareResult.rankings.length === 0) && (!compareResult.failed || compareResult.failed.length === 0) && (
                      <div className="text-center text-gray-400 py-8">暂无分析结果</div>
                    )}
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-lg mx-auto bg-red-50 border border-red-200 rounded-2xl p-4 text-red-700 animate-slideUp">
            ❌ 错误: {error}
          </div>
        )}

        {/* --- Analysis Dashboard --- */}
        {stage >= 1 && (
          <div className="space-y-12 relative animate-slideUp">

            {/* Stock Header */}
            <div className="flex items-center justify-between pb-8 border-b border-gray-200/60 relative">
              <div className="flex items-center gap-6">
                <button
                  onClick={resetAnalysis}
                  className="p-3 -ml-3 text-gray-400 hover:text-black hover:bg-white hover:shadow-sm rounded-full transition-all duration-300"
                >
                  <ArrowLeft size={24} />
                </button>
                <div>
                  <h2 className="text-5xl md:text-6xl font-bold text-gray-900 tracking-tight leading-none mb-2">
                    {stockName || '加载中...'}
                  </h2>
                  <div className="flex items-center gap-3">
                    <span className="text-2xl text-gray-400 font-medium tracking-wide tabular-nums">{stockCode}</span>
                    <span className="px-2.5 py-0.5 bg-gray-100 rounded text-xs font-semibold text-gray-500">SHA</span>
                  </div>
                </div>
              </div>

              {isAnalyzing && (
                <div className="absolute right-0 top-2 flex items-center gap-3">
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-400 uppercase tracking-wider">Processing</span>
                </div>
              )}
            </div>

            <div className="relative pl-6 md:pl-0">
              {/* 左侧贯穿线 */}
              <div className="absolute left-[-2px] md:left-[-40px] top-4 bottom-0 w-px bg-gray-100 hidden md:block"></div>

              {/* Layer 1: Analysis Grid */}
              <section className="relative mb-16">
                <StepIndicator number="1" active={stage >= 1} completed={stage > 1} />
                <TimelineConnector active={stage >= 1} />

                <div className="mb-6 flex items-center gap-3 animate-fadeIn">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest">Data Analysis</h3>
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
                <section className="relative mb-16">
                  <StepIndicator number="2" active={stage >= 2} completed={stage > 2} />
                  <TimelineConnector active={stage >= 2} />

                  <div className="mb-6 flex items-center gap-3 animate-fadeIn">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest">Bull vs Bear</h3>
                  </div>

                  <div className="bg-white rounded-[32px] border border-gray-100 shadow-[0_8px_30px_rgba(0,0,0,0.04)] p-8 md:p-10 animate-slideUp overflow-hidden relative">
                    <div className="mb-10">
                      <div className="flex justify-between items-end mb-3 px-1">
                        <div className="text-emerald-600 font-bold flex flex-col">
                          <span className="text-[11px] uppercase tracking-widest text-emerald-600/50 mb-1 font-semibold">Bull Strength</span>
                          <ScoreDisplay score={result?.layer2?.bullScore} colorClass="text-emerald-600" />
                        </div>
                        <div className="text-rose-500 font-bold flex flex-col text-right">
                          <span className="text-[11px] uppercase tracking-widest text-rose-500/50 mb-1 font-semibold">Bear Strength</span>
                          <ScoreDisplay score={result?.layer2?.bearScore} colorClass="text-rose-500" />
                        </div>
                      </div>
                      <DebateBar bullScore={result?.layer2?.bullScore} bearScore={result?.layer2?.bearScore} />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10 md:gap-16 relative z-10">
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 text-emerald-700 font-bold text-xs uppercase tracking-wider bg-emerald-50/50 w-fit px-3 py-1.5 rounded-full border border-emerald-100/50">
                          <TrendingUp size={14} strokeWidth={2.5} /> Bull Case
                        </div>
                        <div className="text-gray-600 text-[15px] leading-7 font-normal">
                          {result?.layer2?.bullView ? (
                            <TypewriterText text={result.layer2.bullView} />
                          ) : "正在构建看多论点..."}
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 text-rose-700 font-bold text-xs uppercase tracking-wider bg-rose-50/50 w-fit px-3 py-1.5 rounded-full border border-rose-100/50">
                          <TrendingDown size={14} strokeWidth={2.5} /> Bear Case
                        </div>
                        <div className="text-gray-600 text-[15px] leading-7 font-normal">
                          {result?.layer2?.bearView ? (
                            <TypewriterText text={result.layer2.bearView} />
                          ) : "正在构建看空论点..."}
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
              )}

              {/* Layer 3: Decision */}
              {stage >= 3 && (
                <section className="relative mb-16">
                  <StepIndicator number="3" active={stage >= 3} completed={stage > 3} />
                  <TimelineConnector active={stage >= 3} />

                  <div className="mb-6 flex items-center gap-3 animate-fadeIn">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest">Final Verdict</h3>
                  </div>

                  <div className="bg-white rounded-[32px] p-8 md:p-12 shadow-[0_20px_60px_-10px_rgba(0,0,0,0.07)] border border-gray-100 animate-slideUp relative overflow-hidden group hover:shadow-[0_30px_80px_-10px_rgba(0,0,0,0.1)] transition-all duration-500">
                    <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-gradient-to-br from-gray-50 to-white rounded-bl-full -z-10 opacity-50"></div>

                    <div className="relative z-10 flex flex-col md:flex-row gap-10 items-start">
                      <div className="flex-shrink-0 flex flex-col items-center md:items-start min-w-[160px]">
                        <span className="text-gray-400 text-[10px] font-bold tracking-[0.2em] uppercase mb-2">Signal</span>
                        <div className="text-7xl font-bold tracking-tighter text-gray-900 mb-4 animate-[pulse_3s_infinite]">
                          {result?.layer3?.action || "计算中..."}
                        </div>
                        {result?.layer3?.confidence && (
                          <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100">
                            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                            <span className="text-xs font-bold text-emerald-800 tracking-wide uppercase">
                              Confidence: {result.layer3.confidence}
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="w-px h-[140px] bg-gradient-to-b from-gray-100 via-gray-200 to-gray-100 hidden md:block"></div>

                      <div className="flex-1 space-y-4 pt-2">
                        <div className="flex items-center gap-2 text-gray-400 text-xs font-bold uppercase tracking-widest">
                          <Zap size={14} className="text-amber-400 fill-amber-400" />
                          Execution Logic
                        </div>
                        <div className="text-lg text-gray-700 font-normal leading-8 text-balance">
                          {result?.layer3?.reasoning ? (
                            <TypewriterText text={result.layer3.reasoning} />
                          ) : "正在生成交易逻辑..."}
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
              )}

              {/* Layer 4: Strategies */}
              {stage >= 4 && (
                <section className="relative">
                  <StepIndicator number="4" active={stage >= 4} completed={true} />

                  <div className="mb-6 flex items-center gap-3 animate-fadeIn">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest">Risk Strategy</h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                      { title: "Aggressive", icon: AlertTriangle, color: "rose", text: result?.layer4?.aggressive || "加载中..." },
                      { title: "Balanced", icon: Scale, color: "blue", text: result?.layer4?.balanced || "加载中..." },
                      { title: "Conservative", icon: Shield, color: "emerald", text: result?.layer4?.conservative || "加载中..." }
                    ].map((item, idx) => (
                      <div
                        key={item.title}
                        className={`bg-white p-7 rounded-[28px] border border-gray-100/80 shadow-[0_4px_20px_rgba(0,0,0,0.02)]
                          hover:shadow-[0_15px_40px_rgba(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300 animate-slideUp group`}
                        style={{ animationDelay: `${idx * 150}ms` }}
                      >
                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-5
                          transition-colors duration-300 ${item.color === 'rose' ? 'bg-rose-50 text-rose-600 group-hover:bg-rose-600 group-hover:text-white' :
                            item.color === 'blue' ? 'bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white' :
                              'bg-emerald-50 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white'
                          }`}>
                          <item.icon size={22} strokeWidth={2} />
                        </div>
                        <h4 className="text-lg font-bold text-gray-900 mb-3 tracking-tight">{item.title}</h4>
                        <p className="text-[14px] text-gray-500 leading-relaxed whitespace-pre-line font-medium">{item.text}</p>
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>

          </div>
        )}
      </main>
    </div>
  );
}
