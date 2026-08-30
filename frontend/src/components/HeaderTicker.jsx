import React from 'react';
import { TrendingUp, TrendingDown, Zap } from 'lucide-react';

export default function HeaderTicker({ tickers, onSelectSymbol, selectedSymbol }) {
  if (!tickers || tickers.length === 0) return null;

  return (
    <div className="w-full bg-[#080a0f] border-b border-slate-800/80 px-4 py-2.5 flex items-center gap-3 overflow-x-auto select-none">
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-cyan-950/40 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-bold shrink-0">
        <Zap className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
        <span>LIVE RADAR</span>
      </div>

      <div className="flex items-center gap-2.5 shrink-0">
        {tickers.slice(0, 10).map((t) => {
          const isUp = t.change_percent >= 0;
          const isSelected = selectedSymbol === t.symbol;
          return (
            <button
              key={t.symbol}
              onClick={() => onSelectSymbol(t.symbol)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-mono transition-all cursor-pointer ${
                isSelected
                  ? 'bg-slate-800 border-cyan-500/80 text-white shadow-sm shadow-cyan-500/20'
                  : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50'
              }`}
            >
              <span className="font-bold text-slate-200">{t.symbol.replace('USDT', '')}</span>
              <span className="text-slate-400">${t.price >= 1 ? t.price.toLocaleString() : t.price}</span>
              <span
                className={`flex items-center text-[11px] font-semibold ${
                  isUp ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {isUp ? <TrendingUp className="w-3 h-3 mr-0.5" /> : <TrendingDown className="w-3 h-3 mr-0.5" />}
                {isUp ? '+' : ''}
                {t.change_percent.toFixed(2)}%
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
