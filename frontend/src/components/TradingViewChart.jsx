import React, { useEffect, useRef } from 'react';

export default function TradingViewChart({ symbol = 'BTCUSDT', interval = '60' }) {
  const containerRef = useRef(null);

  useEffect(() => {
    // Format symbol for TradingView (e.g., BINANCE:BTCUSDT)
    const cleanSymbol = symbol.toUpperCase().replace('/', '').replace('-', '');
    const tvSymbol = `BINANCE:${cleanSymbol}`;

    const container = containerRef.current;
    if (!container) return;

    // Clear previous widget
    container.innerHTML = '';

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.type = 'text/javascript';
    script.async = true;
    script.onload = () => {
      if (typeof window.TradingView !== 'undefined' && container) {
        new window.TradingView.widget({
          autosize: true,
          symbol: tvSymbol,
          interval: interval === '1h' ? '60' : interval === '15m' ? '15' : interval === '4h' ? '240' : '60',
          timezone: 'Asia/Jakarta',
          theme: 'dark',
          style: '1',
          locale: 'id',
          enable_publishing: false,
          allow_symbol_change: true,
          container_id: container.id,
          studies: [
            'RSI@tv-basicstudies',
            'MASimple@tv-basicstudies',
            'Volume@tv-basicstudies'
          ],
          hide_side_toolbar: false,
          toolbar_bg: '#0d1117',
          backgroundColor: '#090d14',
          gridColor: '#1e293b'
        });
      }
    };

    container.appendChild(script);

    return () => {
      if (container) container.innerHTML = '';
    };
  }, [symbol, interval]);

  return (
    <div className="w-full h-full min-h-[460px] rounded-xl overflow-hidden border border-slate-800 bg-[#090d14] relative">
      <div id={`tv_chart_${symbol}`} ref={containerRef} className="w-full h-full min-h-[460px]" />
    </div>
  );
}
