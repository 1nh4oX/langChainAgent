# API接口文档 - 增强版多Agent系统

> 前后端接口规范说明 v2.0

---

## 📋 目录

1. [接口概述](#接口概述)
2. [API端点](#api端点)
3. [请求格式](#请求格式)
4. [响应格式](#响应格式)
5. [事件类型](#事件类型)
6. [数据结构](#数据结构)
7. [前端集成示例](#前端集成示例)
8. [错误处理](#错误处理)

---

## 接口概述

### 技术栈
- **后端**: FastAPI + Python 3.9+
- **通信协议**: HTTP/HTTPS
- **数据格式**: NDJSON (换行分隔的JSON流)
- **编码**: UTF-8

### 基础信息
- **Base URL**: `http://localhost:8000` (本地) 或 `https://your-domain.vercel.app` (生产)
- **API Prefix**: `/api`
- **Content-Type**: `application/json` (请求) / `application/x-ndjson` (响应)

---

## API端点

### 1. Health Check

检查服务器状态

**端点**: `GET /api/health`

**请求**:
```http
GET /api/health HTTP/1.1
Host: localhost:8000
```

**响应**:
```json
{
  "status": "ok",
  "version": "2.0.0-enhanced"
}
```

---

### 2. 股票分析 (主要接口)

执行完整的4层11个Agent分析流程

**端点**: `POST /api/analyze`

**请求头**:
```http
POST /api/analyze HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

**请求Body**:
```json
{
  "symbol": "600519",              // 必填：6位股票代码
  "api_key": "your_key",           // 可选：LLM API密钥
  "base_url": "https://...",       // 可选：LLM API地址
  "model": "Qwen/Qwen2.5-7B",      // 可选：模型名称
  "debate_threshold": 3.0,         // 可选：辩论触发阈值 (默认3.0)
  "max_rounds": 2                  // 可选：最大辩论轮次 (默认2)
}
```

**响应**: NDJSON 流式输出 (详见下节)

---

## 请求格式

### 完整请求示例

```javascript
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    symbol: '600519',
    debate_threshold: 3.0,
    max_rounds: 2
  })
});
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `symbol` | string | ✅ | - | 6位A股代码 (如600519) |
| `api_key` | string | ❌ | 环境变量 | LLM API密钥 |
| `base_url` | string | ❌ | 环境变量 | API服务地址 |
| `model` | string | ❌ | Qwen/Qwen2.5-7B | 使用的模型 |
| `debate_threshold` | float | ❌ | 3.0 | 多空评分差>=此值触发辩论 |
| `max_rounds` | int | ❌ | 2 | 辩论最大轮次 (1-3) |

---

## 响应格式

### NDJSON流式响应

响应采用**NDJSON**格式（换行分隔的JSON），每行是一个独立的JSON对象。

**特点**:
- ✅ 实时推送：每个Agent完成后立即推送
- ✅ 进度可视：前端可实时显示分析进度
- ✅ 低延迟：无需等待整个分析完成

**示例流**:
```ndjson
{"type":"status","message":"🚀 正在初始化增强版多Agent系统...","step":"init","layer":0}
{"type":"layer_start","layer":1,"name":"Analyst Team","message":"📊 第1层: 分析师团队并行分析"}
{"type":"status","message":"💼 基本面分析师正在评估财务健康度...","step":"fundamentals_analyst","role":"fundamentals_analyst","layer":1}
{"type":"agent_output","role":"fundamentals_analyst","layer":1,"data":{...}}
...
{"type":"final_result","data":{...}}
{"type":"status","message":"🎉 增强版分析完成！","step":"complete"}
```

---

## 事件类型

### 1. `status` - 状态更新

系统状态或进度信息

```json
{
  "type": "status",
  "message": "💼 基本面分析师正在评估财务健康度...",
  "step": "fundamentals_analyst",
  "role": "fundamentals_analyst",
  "layer": 1
}
```

**字段说明**:
- `message`: 状态描述文本
- `step`: 当前步骤标识
- `role`: (可选) 当前执行的Agent角色
- `layer`: (可选) 当前所在层级 (0-4)

### 2. `layer_start` - 层级开始

标记进入新的分析层级

```json
{
  "type": "layer_start",
  "layer": 1,
  "name": "Analyst Team",
  "message": "📊 第1层: 分析师团队并行分析"
}
```

**字段说明**:
- `layer`: 层级编号 (1-4)
- `name`: 层级名称
- `message`: 层级描述

### 3. `agent_output` - Agent输出

单个Agent的分析结果

```json
{
  "type": "agent_output",
  "role": "fundamentals_analyst",
  "layer": 1,
  "data": {
    "content": "【财务健康度】\n盈利能力: ROE=25.3%, 净利率=48.2%\n...",
    "score": 8.5,
    "timestamp": "15:30:45"
  }
}
```

**字段说明**:
- `role`: Agent角色 (详见[Agent角色列表](#agent角色列表))
- `layer`: 所属层级
- `data.content`: 分析内容 (Markdown格式)
- `data.score`: (可选) 评分 (1-10)
- `data.timestamp`: 时间戳

### 4. `debate_triggered` - 辩论触发

多空评分差异达到阈值，触发辩论

```json
{
  "type": "debate_triggered",
  "data": {
    "score_diff": 4.2,
    "message": "🔥 触发辩论! (分歧度: 4.2)"
  }
}
```

### 5. `risk_assessment` - 风险评估

3个风险管理视角的评估结果

```json
{
  "type": "risk_assessment",
  "data": {
    "aggressive": "激进派评估内容...",
    "neutral": "中立派评估内容...",
    "conservative": "保守派评估内容..."
  }
}
```

### 6. `final_result` - 最终结果

投资组合经理的最终决策

```json
{
  "type": "final_result",
  "data": {
    "recommendation": "买入",
    "confidence": "高",
    "content": "【最终投资决策】综合建议: 买入...",
    "position_suggestions": {
      "激进型": "50-70%",
      "稳健型": "30-50%",
      "保守型": "10-30%"
    },
    "scores": {
      "fundamentals": 8.5,
      "technical": 7.2,
      "bullish": 8.0,
      "bearish": 4.0,
      "score_diff": 4.0
    }
  }
}
```

### 7. `error` - 错误

分析过程中的错误

```json
{
  "type": "error",
  "message": "基本面分析失败: 网络超时",
  "traceback": "..."
}
```

---

## 数据结构

### Agent角色列表

#### Layer 1: Analyst Team (分析师团队)

| 角色ID | 名称 | 有评分 | 说明 |
|--------|------|--------|------|
| `fundamentals_analyst` | 基本面分析师 | ✅ | 财务健康度、估值分析 |
| `sentiment_analyst` | 情绪分析师 | ❌ | 社交媒体、市场情绪 |
| `news_analyst` | 新闻分析师 | ❌ | 新闻情感、宏观经济 |
| `technical_analyst` | 技术分析师 | ✅ | MACD、RSI、均线 |

#### Layer 2: Researcher Team (研究员团队)

| 角色ID | 名称 | 有评分 | 说明 |
|--------|------|--------|------|
| `bullish_researcher` | 看涨研究员 | ✅ | 多头观点、上涨理由 |
| `bearish_researcher` | 看跌研究员 | ✅ | 空头观点、风险点 |

#### Layer 3: Trader (交易员)

| 角色ID | 名称 | 有评分 | 说明 |
|--------|------|--------|------|
| `trader` | 交易员 | ❌ | 交易决策、仓位建议 |

**额外字段**:
- `recommendation`: 买入/持有/卖出
- `position`: 轻仓/半仓/重仓

#### Layer 4: Risk & Portfolio (风险与投资组合)

风险评估通过 `risk_assessment` 事件返回，不是单独的agent_output

最终决策通过 `final_result` 事件返回

---

### 完整事件流程图

```
┌─────────────────────────────────────────────────────────────┐
│ 1. status (init)                                            │
│ 2. status (initialized)                                     │
├─────────────────────────────────────────────────────────────┤
│ 3. layer_start (layer=1, Analyst Team)                      │
│ 4. status (fundamentals_analyst) → agent_output             │
│ 5. status (sentiment_analyst) → agent_output                │
│ 6. status (news_analyst) → agent_output                     │
│ 7. status (technical_analyst) → agent_output                │
├─────────────────────────────────────────────────────────────┤
│ 8. layer_start (layer=2, Researcher Team)                   │
│ 9. status (researcher_debate) → agent_output (bullish)      │
│ 10. agent_output (bearish)                                  │
│ 11. [可选] debate_triggered                                 │
├─────────────────────────────────────────────────────────────┤
│ 12. layer_start (layer=3, Trader)                           │
│ 13. status (trader) → agent_output                          │
├─────────────────────────────────────────────────────────────┤
│ 14. layer_start (layer=4, Risk & Portfolio)                 │
│ 15. status (risk_assessment) → risk_assessment              │
│ 16. status (portfolio_manager) → final_result               │
├─────────────────────────────────────────────────────────────┤
│ 17. status (complete)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 前端集成示例

### 1. 读取NDJSON流

```javascript
async function analyzeStock(symbol) {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // 保留不完整的行

    for (const line of lines) {
      if (line.trim()) {
        const event = JSON.parse(line);
        handleEvent(event);
      }
    }
  }
}
```

### 2. 事件处理

```javascript
function handleEvent(event) {
  switch (event.type) {
    case 'status':
      updateStatus(event.message);
      updateProgress(event.step, event.layer);
      break;

    case 'layer_start':
      showLayerHeader(event.layer, event.name);
      break;

    case 'agent_output':
      updateAgentCard(event.role, event.data);
      break;

    case 'debate_triggered':
      showDebateNotification(event.data);
      break;

    case 'risk_assessment':
      updateRiskCards(event.data);
      break;

    case 'final_result':
      showFinalResult(event.data);
      break;

    case 'error':
      showError(event.message);
      break;
  }
}
```

### 3. 进度追踪

```javascript
function updateProgress(step, layer) {
  const progressMap = {
    'init': 5,
    'initialized': 10,
    // Layer 1 (10-35%)
    'fundamentals_analyst': 15,
    'sentiment_analyst': 20,
    'news_analyst': 25,
    'technical_analyst': 30,
    // Layer 2 (35-55%)
    'researcher_debate': 45,
    // Layer 3 (55-75%)
    'trader': 65,
    // Layer 4 (75-95%)
    'risk_assessment': 80,
    'portfolio_manager': 90,
    'complete': 100
  };

  const progress = progressMap[step] || 0;
  document.getElementById('progressBar').style.width = `${progress}%`;
}
```

### 4. Agent卡片更新

```javascript
function updateAgentCard(role, data) {
  const cardId = `card-${role}`;
  const textId = `text-${role}`;
  
  // 更新内容 (使用marked.js渲染Markdown)
  const textEl = document.getElementById(textId);
  textEl.innerHTML = marked.parse(data.content);
  
  // 更新评分
  if (data.score !== undefined) {
    const scoreEl = document.getElementById(`score-${role}`);
    scoreEl.textContent = data.score.toFixed(1);
    
    // 颜色编码
    if (data.score >= 7) scoreEl.style.color = '#4ade80'; // 绿色
    else if (data.score >= 5) scoreEl.style.color = '#fbbf24'; // 黄色
    else scoreEl.style.color = '#f87171'; // 红色
  }
  
  // 添加动画效果
  const card = document.getElementById(cardId);
  card.style.animation = 'pulse 0.3s';
  setTimeout(() => card.style.animation = '', 300);
}
```

### 5. 最终结果展示

```javascript
function showFinalResult(data) {
  // 显示最终决策卡片
  const card = document.getElementById('finalResult');
  card.classList.remove('hidden');
  
  // 更新建议
  document.getElementById('finalVerdict').textContent = data.recommendation;
  document.getElementById('confidenceLevel').textContent = `${data.confidence} CONFIDENCE`;
  
  // 更新评分
  document.getElementById('fundamentalsScore').textContent = 
    data.scores.fundamentals?.toFixed(1) || '-';
  document.getElementById('technicalScore').textContent = 
    data.scores.technical?.toFixed(1) || '-';
  
  // 更新仓位建议
  document.getElementById('aggressivePos').textContent = 
    data.position_suggestions['激进型'] || '-';
  document.getElementById('neutralPos').textContent = 
    data.position_suggestions['稳健型'] || '-';
  document.getElementById('conservativePos').textContent = 
    data.position_suggestions['保守型'] || '-';
  
  // 滚动到结果位置
  card.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
```

---

## 错误处理

### 常见错误类型

| 错误 | 状态码 | 说明 | 处理方式 |
|------|--------|------|----------|
| 连接失败 | - | 服务器未启动 | 提示用户检查服务器 |
| 400 Bad Request | 400 | 请求参数错误 | 检查symbol格式 |
| 500 Server Error | 500 | 服务器内部错误 | 显示错误消息 |
| 网络超时 | - | 请求超时 | 设置timeout重试 |

### 错误处理示例

```javascript
try {
  await analyzeStock(symbol);
} catch (error) {
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    alert('无法连接到服务器，请确保服务器正在运行');
  } else if (error.response?.status === 400) {
    alert('股票代码格式错误，请输入6位数字');
  } else {
    console.error('分析失败:', error);
    alert(`分析失败: ${error.message}`);
  }
}
```

### 超时设置

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 120000); // 2分钟超时

try {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol }),
    signal: controller.signal
  });
  clearTimeout(timeoutId);
  // 处理响应...
} catch (error) {
  if (error.name === 'AbortError') {
    alert('分析超时，请稍后重试');
  }
}
```

---

## 附录

### A. 完整TypeScript类型定义

```typescript
// Request
interface AnalyzeRequest {
  symbol: string;
  api_key?: string;
  base_url?: string;
  model?: string;
  debate_threshold?: number;
  max_rounds?: number;
}

// Events
type EventType = 
  | 'status' 
  | 'layer_start' 
  | 'agent_output' 
  | 'debate_triggered' 
  | 'risk_assessment' 
  | 'final_result' 
  | 'error';

interface StatusEvent {
  type: 'status';
  message: string;
  step: string;
  role?: string;
  layer?: number;
}

interface LayerStartEvent {
  type: 'layer_start';
  layer: number;
  name: string;
  message: string;
}

interface AgentOutputEvent {
  type: 'agent_output';
  role: string;
  layer: number;
  data: {
    content: string;
    score?: number;
    timestamp: string;
    recommendation?: string; // trader专用
    position?: string; // trader专用
  };
}

interface DebateTriggeredEvent {
  type: 'debate_triggered';
  data: {
    score_diff: number;
    message: string;
  };
}

interface RiskAssessmentEvent {
  type: 'risk_assessment';
  data: {
    aggressive: string;
    neutral: string;
    conservative: string;
  };
}

interface FinalResultEvent {
  type: 'final_result';
  data: {
    recommendation: string;
    confidence: string;
    content: string;
    position_suggestions: {
      [key: string]: string;
    };
    scores: {
      fundamentals?: number;
      technical?: number;
      bullish?: number;
      bearish?: number;
      score_diff?: number;
    };
  };
}

interface ErrorEvent {
  type: 'error';
  message: string;
  traceback?: string;
}

type Event = 
  | StatusEvent 
  | LayerStartEvent 
  | AgentOutputEvent 
  | DebateTriggeredEvent 
  | RiskAssessmentEvent 
  | FinalResultEvent 
  | ErrorEvent;
```

### B. 测试端点

```bash
# 测试健康检查
curl http://localhost:8000/api/health

# 测试分析接口
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"600519","debate_threshold":3.0}'
```

---

## 📞 技术支持

如有疑问，请查阅:
- [完整README](README.md)
- [Vercel部署指南](VERCEL_DEPLOY.md)
- [系统架构文档](walkthrough.md)

---

**文档版本**: v2.0  
**最后更新**: 2025-12-11  
**维护者**: AI Multi-Agent Trading System Team
