import React, { useState, useEffect } from 'react';
import { Waves, ArrowUpRight, ArrowDownRight, RefreshCw, DollarSign, ShieldAlert } from 'lucide-react';

export default function WhaleRadar({ onSelectSymbol }) {
  const [whaleData, setWhaleData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchWhales = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/whale/activity');
      const data = await res.json();
      if (data.whales) {
        setWhaleData(data.whales);
      }
    } catch (e) {
      console.error('Error fetching whale data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWhales();
    const interval = setInterval(fetchWhales, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="terminal-glass rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
            <Waves className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
              WHALE & INSTITUTIONAL FLOW RADAR
            </h3>
            <p className="text-xs text-slate-400">Deteksi transaksi besar & akumulasi bandar (Trades &gt; $50K)</p>
          </div>
        </div>

        <button
          onClick={fetchWhales}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono hover:bg-slate-700 transition-colors cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {whaleData.length === 0 ? (
        <div className="py-12 text-center text-slate-500 font-mono text-xs">
          {loading ? 'Memindai transaksi whale...' : 'Tidak ada transaksi anomali whale saat ini.'}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {whaleData.map((item) => {
            const isBullish = item.whale_buy_ratio >= 55;
            const isBearish = item.whale_buy_ratio <= 45;
            return (
              <div
                key={item.symbol}
                className="bg-[#090d14]/90 p-4 rounded-xl border border-slate-800 hover:border-indigo-500/50 transition-all cursor-pointer"
                onClick={() => onSelectSymbol(item.symbol)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-white font-mono">{item.symbol}</span>
                  <span
                    className={`text-[11px] font-mono px-2 py-0.5 rounded border font-semibold ${
                      isBullish
                        ? 'bg-emerald-950/50 text-emerald-400 border-emerald-500/40'
                        : isBearish
                        ? 'bg-rose-950/50 text-rose-400 border-rose-500/40'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    {item.flow_status}
                  </span>
                </div>

                {/* Progress ratio bar */}
                <div className="my-2.5">
                  <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                    <span>Buy: {item.whale_buy_ratio}%</span>
                    <span>Sell: {(100 - item.whale_buy_ratio).toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-rose-950/80 overflow-hidden flex">
                    <div
                      className="bg-emerald-500 h-full transition-all duration-500"
                      style={{ width: `${item.whale_buy_ratio}%` }}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400 mt-3 pt-2 border-t border-slate-800/80">
                  <div>
                    <span className="text-slate-500 block text-[10px]">Whale Buy Vol:</span>
                    <span className="text-emerald-400 font-semibold">
                      ${item.total_whale_buy_usd?.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Whale Sell Vol:</span>
                    <span className="text-rose-400 font-semibold">
                      ${item.total_whale_sell_usd?.toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* Recent whale trade feed */}
                {item.recent_whale_trades && item.recent_whale_trades.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-slate-800/80">
                    <span className="text-[10px] text-slate-500 font-mono block mb-1.5">Transaski Terkini:</span>
                    <div className="space-y-1 max-h-24 overflow-y-auto pr-1">
                      {item.recent_whale_trades.slice(0, 3).map((trade, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between text-[10px] font-mono py-0.5 px-1.5 rounded bg-slate-900/80 border border-slate-800/60"
                        >
                          <span
                            className={
                              trade.side === 'BUY' ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'
                            }
                          >
                            {trade.side} ${trade.price?.toLocaleString()}
                          </span>
                          <span className="text-slate-300 font-semibold">
                            ${trade.usd_value?.toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
