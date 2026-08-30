import React, { useState, useEffect } from 'react';
import {
  Activity,
  Bot,
  Sparkles,
  Waves,
  RefreshCw,
  Send,
  Sliders,
  TrendingUp,
  LineChart,
  ShieldAlert,
  Zap,
  Globe
} from 'lucide-react';

import HeaderTicker from './components/HeaderTicker';
import SignalCard from './components/SignalCard';
import TradingViewChart from './components/TradingViewChart';
import WhaleRadar from './components/WhaleRadar';
import MarketScreener from './components/MarketScreener';
import AICopilotChat from './components/AICopilotChat';
import SignalPerformance from './components/SignalPerformance';
import TelegramSettingsModal from './components/TelegramSettingsModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('TERMINAL'); // 'TERMINAL', 'SCREENER', 'WHALE', 'COPILOT'
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [tickers, setTickers] = useState([]);
  const [signals, setSignals] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [isTelegramModalOpen, setIsTelegramModalOpen] = useState(false);
  const [singleAnalysis, setSingleAnalysis] = useState(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  // Fetch initial tickers & signals
  const fetchMarketData = async () => {
    try {
      const [tickerRes, signalRes, statusRes] = await Promise.all([
        fetch('/api/market/ticker'),
        fetch('/api/signals'),
        fetch('/api/status')
      ]);

      const tickerData = await tickerRes.json();
      const signalData = await signalRes.json();
      const statusData = await statusRes.json();

      if (tickerData.data) setTickers(tickerData.data);
      if (signalData.signals) setSignals(signalData.signals);
      if (statusData) setSystemStatus(statusData);
    } catch (e) {
      console.error('Error fetching market data:', e);
    }
  };

  // Fetch on-demand analysis for selected symbol
  const fetchSymbolAnalysis = async (symbol, tf) => {
    setLoadingAnalysis(true);
    try {
      const res = await fetch(`/api/signals/analyze?symbol=${symbol}&timeframe=${tf}`);
      if (res.ok) {
        const data = await res.json();
        setSingleAnalysis(data);
      }
    } catch (e) {
      console.error('Error analyzing symbol:', e);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  // Trigger full market scan
  const handleTriggerScan = async () => {
    setScanning(true);
    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timeframe })
      });
      const data = await res.json();
      if (data.signals) {
        setSignals(data.signals);
      }
    } catch (e) {
      console.error('Error triggering scan:', e);
    } finally {
      setScanning(false);
    }
  };

  // Dispatch signal to Telegram
  const handleDispatchTelegram = async (signal) => {
    try {
      const res = await fetch('/api/telegram/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signal)
      });
      const data = await res.json();
      return data.success;
    } catch (e) {
      console.error('Telegram dispatch error:', e);
      return false;
    }
  };

  useEffect(() => {
    fetchMarketData();
    const interval = setInterval(fetchMarketData, 20000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchSymbolAnalysis(selectedSymbol, timeframe);
  }, [selectedSymbol, timeframe]);

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col selection:bg-cyan-500/30 selection:text-cyan-300">
      {/* Top Main Navigation */}
      <header className="bg-[#0a0d14] border-b border-slate-800/80 px-4 py-3 shrink-0 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center shadow-md shadow-cyan-500/20">
            <Bot className="w-5 h-5 text-black" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold font-mono tracking-wider text-white">
                ALPHA<span className="text-cyan-400">TERMINAL</span>.AI
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 font-bold">
                PRO V2.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Institutional AI Signals & Flow Terminal</p>
          </div>
        </div>

        {/* Center Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-[#05070a] p-1 rounded-xl border border-slate-800 font-mono text-xs">
          {[
            { key: 'TERMINAL', label: 'Terminal Live', icon: LineChart },
            { key: 'PERFORMANCE', label: 'Rekap Hasil & Ceklist', icon: CheckCircle2 },
            { key: 'SCREENER', label: 'AI Screener', icon: Activity },
            { key: 'WHALE', label: 'Whale Radar', icon: Waves },
            { key: 'COPILOT', label: 'AI Copilot', icon: Sparkles }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                  isActive
                    ? 'bg-slate-800 text-cyan-300 font-semibold border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Controls */}
        <div className="flex items-center gap-2.5">
          {/* Timeframe Selector */}
          <div className="flex items-center bg-[#05070a] p-1 rounded-lg border border-slate-800 text-xs font-mono">
            {['15m', '1h', '4h'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2.5 py-1 rounded transition-colors cursor-pointer ${
                  timeframe === tf ? 'bg-cyan-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* Market Scan Button */}
          <button
            onClick={handleTriggerScan}
            disabled={scanning}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 border border-emerald-500/40 hover:bg-emerald-600/30 text-emerald-300 text-xs font-mono font-semibold transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
            <span>{scanning ? 'Scanning...' : 'Scan Pasar'}</span>
          </button>

          {/* Telegram Settings Toggle */}
          <button
            onClick={() => setIsTelegramModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-mono transition-colors cursor-pointer"
          >
            <Send className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">Bot Telegram</span>
          </button>
        </div>
      </header>

      {/* Real-time Scrolling Ticker */}
      <HeaderTicker
        tickers={tickers}
        onSelectSymbol={setSelectedSymbol}
        selectedSymbol={selectedSymbol}
      />

      {/* Main Content Area */}
      <main className="flex-1 p-4 max-w-[1700px] w-full mx-auto space-y-4">
        {/* Tab 1: TERMINAL VIEW */}
        {activeTab === 'TERMINAL' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
            {/* Left Col (7 cols): Interactive TradingView Chart & Selected Coin Metrics */}
            <div className="lg:col-span-7 space-y-4">
              <div className="terminal-glass rounded-xl p-4 border border-slate-800">
                <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800/80">
                  <div className="flex items-center gap-2 font-mono">
                    <span className="text-lg font-bold text-white">{selectedSymbol}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-semibold border border-slate-700">
                      TIMEFRAME {timeframe.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono">
                    Real-time Candlestick & Technical Indicators
                  </div>
                </div>

                <TradingViewChart symbol={selectedSymbol} interval={timeframe} />
              </div>

              {/* Technical Indicator Summary Bar for Selected Symbol */}
              {singleAnalysis && singleAnalysis.indicators && (
                <div className="terminal-glass rounded-xl p-4 border border-slate-800 font-mono text-xs">
                  <h4 className="font-bold text-white mb-2.5 flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    LIVE QUANTITATIVE CONFLUENCE ({selectedSymbol})
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#090d14] p-3 rounded-lg border border-slate-800/80">
                    <div>
                      <span className="text-slate-500 block text-[10px]">RSI (14):</span>
                      <span
                        className={`font-bold ${
                          singleAnalysis.indicators.rsi <= 35
                            ? 'text-emerald-400'
                            : singleAnalysis.indicators.rsi >= 65
                            ? 'text-rose-400'
                            : 'text-cyan-300'
                        }`}
                      >
                        {singleAnalysis.indicators.rsi}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">SuperTrend:</span>
                      <span
                        className={`font-bold ${
                          singleAnalysis.indicators.supertrend_bullish ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {singleAnalysis.indicators.supertrend_bullish ? 'BULLISH' : 'BEARISH'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Money Flow (CMF):</span>
                      <span className="text-slate-200 font-bold">{singleAnalysis.indicators.cmf}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Volume Spike Ratio:</span>
                      <span className="text-amber-400 font-bold">{singleAnalysis.indicators.volume_ratio}x</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right Col (5 cols): AI Signal Stream & Selected Asset Deep Analysis */}
            <div className="lg:col-span-5 space-y-4">
              {/* Selected Coin Active AI Card */}
              {singleAnalysis && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-cyan-400 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      ANALISA AKTIF {selectedSymbol}
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">Status: Ready</span>
                  </div>
                  <SignalCard
                    signal={singleAnalysis}
                    onSelectSymbol={setSelectedSymbol}
                    onDispatchTelegram={handleDispatchTelegram}
                  />
                </div>
              )}

              {/* Recent High-Confidence Signals Feed */}
              <div className="terminal-glass rounded-xl p-4 border border-slate-800">
                <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800/80">
                  <h3 className="text-sm font-bold text-white font-mono flex items-center gap-1.5">
                    <Zap className="w-4 h-4 text-amber-400" />
                    AI SIGNALS STREAM
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">
                    {signals.length} Sinyal Terdeteksi
                  </span>
                </div>

                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                  {signals.length === 0 ? (
                    <div className="py-12 text-center text-slate-500 font-mono text-xs">
                      {scanning ? 'Sedang memindai market...' : 'Belum ada sinyal terdeteksi. Klik "Scan Pasar" di atas.'}
                    </div>
                  ) : (
                    signals.map((sig) => (
                      <SignalCard
                        key={`${sig.symbol}_${sig.timeframe}`}
                        signal={sig}
                        onSelectSymbol={setSelectedSymbol}
                        onDispatchTelegram={handleDispatchTelegram}
                      />
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab: REKAP HASIL & CEKLIST */}
        {activeTab === 'PERFORMANCE' && (
          <SignalPerformance onSelectSymbol={(sym) => {
            setSelectedSymbol(sym);
            setActiveTab('TERMINAL');
          }} />
        )}

        {/* Tab 2: MARKET SCREENER */}
        {activeTab === 'SCREENER' && (
          <MarketScreener signals={signals} onSelectSymbol={(sym) => {
            setSelectedSymbol(sym);
            setActiveTab('TERMINAL');
          }} />
        )}

        {/* Tab 3: WHALE RADAR */}
        {activeTab === 'WHALE' && (
          <WhaleRadar onSelectSymbol={(sym) => {
            setSelectedSymbol(sym);
            setActiveTab('TERMINAL');
          }} />
        )}

        {/* Tab 4: AI COPILOT */}
        {activeTab === 'COPILOT' && (
          <div className="max-w-4xl mx-auto">
            <AICopilotChat selectedSymbol={selectedSymbol} />
          </div>
        )}
      </main>

      {/* Telegram Configuration Modal */}
      <TelegramSettingsModal
        isOpen={isTelegramModalOpen}
        onClose={() => setIsTelegramModalOpen(false)}
        telegramStatus={systemStatus?.telegram_integration}
      />
    </div>
  );
}
