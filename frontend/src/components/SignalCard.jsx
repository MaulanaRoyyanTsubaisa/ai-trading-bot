import React, { useState } from 'react';
import { Send, Target, ShieldAlert, Sparkles, Activity, CheckCircle2, Waves, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function SignalCard({ signal, onSelectSymbol, onDispatchTelegram }) {
  const [sending, setSending] = useState(false);
  const [sentSuccess, setSentSuccess] = useState(false);

  const isBuy = signal.action === 'LONG';
  const isSell = signal.action === 'SHORT';
  const isStrong = signal.signal.includes('STRONG');

  const badgeColor = isBuy
    ? isStrong
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-emerald-500/20 shadow-sm'
      : 'bg-emerald-950/40 text-emerald-300 border-emerald-700/50'
    : isSell
    ? isStrong
      ? 'bg-rose-500/20 text-rose-400 border-rose-500/40 shadow-rose-500/20 shadow-sm'
      : 'bg-rose-950/40 text-rose-300 border-rose-700/50'
    : 'bg-slate-800 text-slate-400 border-slate-700';

  const handleSendTelegram = async () => {
    setSending(true);
    const ok = await onDispatchTelegram(signal);
    setSending(false);
    if (ok) {
      setSentSuccess(true);
      setTimeout(() => setSentSuccess(false), 3000);
    }
  };

  return (
    <div className="terminal-glass rounded-xl p-5 relative overflow-hidden transition-all duration-300 hover:border-slate-700/80 group">
      {/* Glow highlight bar based on signal */}
      <div
        className={`absolute top-0 left-0 right-0 h-1 ${
          isBuy ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : isSell ? 'bg-gradient-to-r from-rose-500 to-amber-500' : 'bg-slate-700'
        }`}
      />

      {/* Card Header */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onSelectSymbol(signal.symbol)}
              className="text-lg font-bold text-white hover:text-cyan-400 font-mono flex items-center gap-1 transition-colors cursor-pointer"
            >
              {signal.symbol}
              <ArrowUpRight className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" />
            </button>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 font-mono">
              {signal.timeframe || '1h'}
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Price: <span className="text-slate-200 font-semibold">${signal.current_price?.toLocaleString()}</span>
          </p>
        </div>

        <div className="flex flex-col items-end gap-1.5">
          <div className={`px-3 py-1 rounded-full border text-xs font-bold font-mono tracking-wider ${badgeColor}`}>
            {signal.signal}
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Confidence: <strong className="text-amber-400">{signal.confidence}%</strong></span>
          </div>
        </div>
      </div>

      {/* Targets & Risk Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 my-4 bg-[#090d14]/80 p-3 rounded-lg border border-slate-800/80 font-mono text-xs">
        <div>
          <span className="text-slate-500 block text-[10px] uppercase">Entry Zone</span>
          <span className="text-cyan-300 font-medium">{signal.entry_zone}</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase flex items-center gap-1">
            <Target className="w-3 h-3 text-emerald-400" /> Target TP1 / TP2
          </span>
          <span className="text-emerald-400 font-medium">
            ${signal.take_profit_1} / ${signal.take_profit_2}
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase flex items-center gap-1">
            <ShieldAlert className="w-3 h-3 text-rose-400" /> Stop Loss
          </span>
          <span className="text-rose-400 font-medium">${signal.stop_loss}</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase">Risk/Reward</span>
          <span className="text-amber-300 font-medium">{signal.risk_reward_ratio}</span>
        </div>
      </div>

      {/* Whale Flow & Catalysts */}
      <div className="flex flex-wrap items-center gap-1.5 mb-3.5">
        {signal.whale_summary?.flow_status && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-indigo-950/40 border border-indigo-700/40 text-indigo-300 text-[11px] font-mono">
            <Waves className="w-3 h-3 text-indigo-400" />
            {signal.whale_summary.flow_status}
          </span>
        )}
        {signal.catalysts?.map((c, i) => (
          <span
            key={i}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-800/80 border border-slate-700/60 text-slate-300 text-[11px] font-mono"
          >
            <Activity className="w-2.5 h-2.5 text-cyan-400" />
            {c}
          </span>
        ))}
      </div>

      {/* AI Rationale Box */}
      {signal.ai_rationale && (
        <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-300 leading-relaxed font-sans mb-4">
          <div className="flex items-center gap-1.5 text-cyan-400 font-mono font-semibold text-[11px] mb-1.5">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI ANALYST INSIGHT</span>
          </div>
          <p className="whitespace-pre-line text-slate-300 text-xs">{signal.ai_rationale}</p>
        </div>
      )}

      {/* Bottom Dispatch Button */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
        <span className="text-[11px] text-slate-500 font-mono">
          Updated: {new Date(signal.timestamp * 1000).toLocaleTimeString()}
        </span>

        <button
          onClick={handleSendTelegram}
          disabled={sending}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium transition-all cursor-pointer ${
            sentSuccess
              ? 'bg-emerald-600 text-white'
              : 'bg-cyan-600/20 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-600/30'
          }`}
        >
          {sentSuccess ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Terkirim ke Telegram!</span>
            </>
          ) : (
            <>
              <Send className="w-3.5 h-3.5" />
              <span>{sending ? 'Mengirim...' : 'Kirim Alert Telegram'}</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
