import React, { useState } from 'react';
import { Filter, Sparkles, TrendingUp, TrendingDown, ArrowUpRight, Search } from 'lucide-react';

export default function MarketScreener({ signals, onSelectSymbol }) {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const filteredSignals = signals.filter((s) => {
    const matchesSearch = s.symbol.toLowerCase().includes(search.toLowerCase());
    if (!matchesSearch) return false;

    if (filter === 'BUY') return s.action === 'LONG';
    if (filter === 'SELL') return s.action === 'SHORT';
    if (filter === 'HIGH_CONF') return s.confidence >= 75;
    if (filter === 'OVERSOLD') return s.indicators?.rsi <= 35;
    if (filter === 'OVERBOUGHT') return s.indicators?.rsi >= 65;
    return true;
  });

  return (
    <div className="terminal-glass rounded-xl p-5 border border-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            AI QUANT & TECHNICAL MARKET SCREENER
          </h3>
          <p className="text-xs text-slate-400">Pemindai real-time multi-indikator & konfluensi bandar</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Cari koin (BTC, ETH)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-44"
            />
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-3 select-none">
        {[
          { key: 'ALL', label: 'Semua Koin' },
          { key: 'BUY', label: '🟢 Buy Setup' },
          { key: 'SELL', label: '🔴 Sell Setup' },
          { key: 'HIGH_CONF', label: '⚡ High Confidence (≥75%)' },
          { key: 'OVERSOLD', label: '📉 RSI Oversold (≤35)' },
          { key: 'OVERBOUGHT', label: '📈 RSI Overbought (≥65)' }
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all shrink-0 cursor-pointer ${
              filter === tab.key
                ? 'bg-cyan-600/30 border border-cyan-500/80 text-cyan-300 font-semibold'
                : 'bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase bg-slate-900/40">
              <th className="py-2.5 px-3">Asset</th>
              <th className="py-2.5 px-3">Harga</th>
              <th className="py-2.5 px-3">AI Signal</th>
              <th className="py-2.5 px-3">Confidence</th>
              <th className="py-2.5 px-3">RSI (14)</th>
              <th className="py-2.5 px-3">SuperTrend</th>
              <th className="py-2.5 px-3">Whale Flow</th>
              <th className="py-2.5 px-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredSignals.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-500">
                  Tidak ada koin yang cocok dengan filter.
                </td>
              </tr>
            ) : (
              filteredSignals.map((s) => {
                const isBuy = s.action === 'LONG';
                const isSell = s.action === 'SHORT';
                return (
                  <tr key={s.symbol} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3 font-bold text-white flex items-center gap-1.5">
                      <span>{s.symbol}</span>
                      <span className="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                        {s.timeframe || '1h'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-200">${s.current_price?.toLocaleString()}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[11px] font-bold border ${
                          isBuy
                            ? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/40'
                            : isSell
                            ? 'bg-rose-950/60 text-rose-400 border-rose-500/40'
                            : 'bg-slate-800 text-slate-400 border-slate-700'
                        }`}
                      >
                        {s.signal}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-amber-400 font-semibold">{s.confidence}%</span>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={
                          s.indicators?.rsi <= 35
                            ? 'text-emerald-400 font-bold'
                            : s.indicators?.rsi >= 65
                            ? 'text-rose-400 font-bold'
                            : 'text-slate-300'
                        }
                      >
                        {s.indicators?.rsi}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={
                          s.indicators?.supertrend_bullish ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'
                        }
                      >
                        {s.indicators?.supertrend_bullish ? 'BULLISH' : 'BEARISH'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      <span className="text-[11px] text-slate-400">
                        {s.whale_summary?.flow_status?.replace('(BULLISH)', '').replace('(BEARISH)', '') || 'N/A'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => onSelectSymbol(s.symbol)}
                        className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-cyan-300 hover:bg-cyan-950/50 hover:border-cyan-500 transition-colors text-[11px] cursor-pointer inline-flex items-center gap-1"
                      >
                        <span>Chart</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
