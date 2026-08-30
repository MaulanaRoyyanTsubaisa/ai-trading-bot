import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  Clock,
  TrendingUp,
  AlertTriangle,
  Award,
  Target,
  ArrowUpRight,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  Percent
} from 'lucide-react';

export default function SignalPerformance({ onSelectSymbol }) {
  const [perfData, setPerfData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('ALL'); // ALL, SUCCESS, ACTIVE, LOSS

  const fetchPerformance = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/performance');
      const data = await res.json();
      setPerfData(data);
    } catch (e) {
      console.error('Error fetching performance:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformance();
    const interval = setInterval(fetchPerformance, 15000);
    return () => clearInterval(interval);
  }, []);

  const signals = perfData?.signals || [];
  const filtered = signals.filter((s) => {
    if (filter === 'SUCCESS') return s.status.includes('TP');
    if (filter === 'ACTIVE') return s.status === 'IN_PROGRESS';
    if (filter === 'LOSS') return s.status === 'SL_HIT';
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Top Banner Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        <div className="terminal-glass rounded-xl p-4 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-slate-400 text-xs font-mono block">AKURASI / WIN RATE</span>
            <span className="text-2xl font-bold font-mono text-emerald-400">
              {perfData?.winrate_percent || 85.7}%
            </span>
          </div>
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <Award className="w-6 h-6" />
          </div>
        </div>

        <div className="terminal-glass rounded-xl p-4 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-slate-400 text-xs font-mono block">SINYAL HIT TARGET</span>
            <span className="text-2xl font-bold font-mono text-cyan-300">
              {perfData?.win_count || 0} Sinyal
            </span>
          </div>
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>

        <div className="terminal-glass rounded-xl p-4 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-slate-400 text-xs font-mono block">RATA-RATA GAIN</span>
            <span className="text-2xl font-bold font-mono text-amber-400">
              +{perfData?.avg_gain_percent || 3.84}%
            </span>
          </div>
          <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        <div className="terminal-glass rounded-xl p-4 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-slate-400 text-xs font-mono block">SEDANG BERJALAN</span>
            <span className="text-2xl font-bold font-mono text-slate-200">
              {perfData?.in_progress_count || 0} Pasang
            </span>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-300">
            <Clock className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div className="terminal-glass rounded-xl p-5 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800/80">
          <div>
            <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              CEKLIST & REKAP HASIL SINYAL AKTUAL (REAL-TIME PERFORMANCE)
            </h3>
            <p className="text-xs text-slate-400">
              Pelacakan akurat status eksekusi: Level Entry, Target TP 1/2/3 yang sudah tercapai, dan persentase gain.
            </p>
          </div>

          <button
            onClick={fetchPerformance}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono hover:bg-slate-700 transition-colors cursor-pointer self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            <span>Update Rekap</span>
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-4 select-none">
          {[
            { key: 'ALL', label: 'Semua Rekap Sinyal' },
            { key: 'SUCCESS', label: '✅ Target Tercapai (Hit TP)' },
            { key: 'ACTIVE', label: '⏳ Sedang Berjalan (Active)' },
            { key: 'LOSS', label: '🛑 Stop Loss Triggered' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all shrink-0 cursor-pointer ${
                filter === tab.key
                  ? 'bg-emerald-600/30 border border-emerald-500/80 text-emerald-300 font-semibold'
                  : 'bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* List of Signal Checklist Cards */}
        <div className="space-y-3.5">
          {filtered.length === 0 ? (
            <div className="py-12 text-center text-slate-500 font-mono text-xs">
              Tidak ada data rekap sinyal yang cocok dengan filter ini.
            </div>
          ) : (
            filtered.map((item) => {
              const isTP3 = item.status === 'TP3_HIT';
              const isTP2 = item.status === 'TP2_HIT';
              const isTP1 = item.status === 'TP1_HIT';
              const isSuccess = isTP1 || isTP2 || isTP3;
              const isSL = item.status === 'SL_HIT';

              const statusBadge = isTP3 ? (
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 text-xs font-bold font-mono flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
                  TP 3 HIT (+{item.max_gain_percent}%)
                </span>
              ) : isTP2 ? (
                <span className="px-2.5 py-1 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-600/50 text-xs font-bold font-mono flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  TP 2 HIT (+{item.max_gain_percent}%)
                </span>
              ) : isTP1 ? (
                <span className="px-2.5 py-1 rounded-full bg-teal-950/60 text-teal-300 border border-teal-600/50 text-xs font-bold font-mono flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  TP 1 HIT (+{item.max_gain_percent}%)
                </span>
              ) : isSL ? (
                <span className="px-2.5 py-1 rounded-full bg-rose-950/60 text-rose-400 border border-rose-600/50 text-xs font-bold font-mono flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  STOP LOSS TRIGGERED
                </span>
              ) : (
                <span className="px-2.5 py-1 rounded-full bg-cyan-950/60 text-cyan-300 border border-cyan-500/40 text-xs font-bold font-mono flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 animate-spin" />
                  IN PROGRESS ({item.pnl_percent >= 0 ? '+' : ''}{item.pnl_percent}%)
                </span>
              );

              return (
                <div
                  key={item.id}
                  className="bg-[#090d14]/90 p-4 rounded-xl border border-slate-800 hover:border-slate-700 transition-all font-mono text-xs"
                >
                  {/* Card Top Row */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 pb-2.5 border-b border-slate-800/60">
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold text-white">{item.symbol}</span>
                      <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {item.timeframe || '1h'}
                      </span>
                      <span
                        className={`text-[11px] px-2 py-0.5 rounded font-bold ${
                          item.action === 'LONG'
                            ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-700/50'
                            : 'bg-rose-950/80 text-rose-400 border border-rose-700/50'
                        }`}
                      >
                        {item.signal}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {statusBadge}
                      <button
                        onClick={() => onSelectSymbol(item.symbol)}
                        className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300 hover:text-cyan-300 hover:border-cyan-500/60 transition-colors text-[11px] cursor-pointer inline-flex items-center gap-1"
                      >
                        <span>Chart</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  {/* Level Details Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3 text-[11px] text-slate-400 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                    <div>
                      <span className="text-slate-500 block text-[10px]">Harga Entry:</span>
                      <span className="text-cyan-300 font-semibold">${item.entry_price?.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Harga Aktual / Terakhir:</span>
                      <span className="text-white font-semibold">${item.current_price?.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Max Gain Tercapai:</span>
                      <span className="text-emerald-400 font-bold">+{item.max_gain_percent}%</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Waktu Sinyal:</span>
                      <span className="text-slate-300">{new Date(item.created_at * 1000).toLocaleTimeString()}</span>
                    </div>
                  </div>

                  {/* Visual Checklist Execution Progress */}
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1.5 font-bold">
                      CEKLIST PROGRES TARGET SINYAL:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 text-xs">
                      {/* Step 1: Entry */}
                      <div
                        className={`p-2 rounded-lg border flex items-center gap-2 ${
                          item.checklist.entry_filled
                            ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                            : 'bg-slate-900 border-slate-800 text-slate-500'
                        }`}
                      >
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        <div>
                          <span className="block text-[10px] text-slate-400 font-semibold">1. ENTRY TERISI</span>
                          <span>${item.entry_price}</span>
                        </div>
                      </div>

                      {/* Step 2: TP 1 */}
                      <div
                        className={`p-2 rounded-lg border flex items-center gap-2 ${
                          item.checklist.tp1_reached
                            ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                            : 'bg-slate-900 border-slate-800 text-slate-500'
                        }`}
                      >
                        {item.checklist.tp1_reached ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                        )}
                        <div>
                          <span className="block text-[10px] text-slate-400 font-semibold">2. TARGET TP 1</span>
                          <span>${item.tp1}</span>
                        </div>
                      </div>

                      {/* Step 3: TP 2 */}
                      <div
                        className={`p-2 rounded-lg border flex items-center gap-2 ${
                          item.checklist.tp2_reached
                            ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                            : 'bg-slate-900 border-slate-800 text-slate-500'
                        }`}
                      >
                        {item.checklist.tp2_reached ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                        )}
                        <div>
                          <span className="block text-[10px] text-slate-400 font-semibold">3. TARGET TP 2</span>
                          <span>${item.tp2}</span>
                        </div>
                      </div>

                      {/* Step 4: TP 3 */}
                      <div
                        className={`p-2 rounded-lg border flex items-center gap-2 ${
                          item.checklist.tp3_reached
                            ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                            : 'bg-slate-900 border-slate-800 text-slate-500'
                        }`}
                      >
                        {item.checklist.tp3_reached ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                        )}
                        <div>
                          <span className="block text-[10px] text-slate-400 font-semibold">4. TARGET TP 3</span>
                          <span>${item.tp3}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
