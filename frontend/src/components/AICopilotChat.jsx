import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Sparkles, HelpCircle } from 'lucide-react';

export default function AICopilotChat({ selectedSymbol }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: `Halo! Saya adalah **AI Trading Copilot**. Anda dapat menanyakan analisa teknikal, deteksi aliran bandar/whale, atau rekomendasi strategi untuk ${selectedSymbol} maupun aset lainnya.`
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (customText) => {
    const textToSend = customText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg = { role: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/copilot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          symbol: selectedSymbol,
          timeframe: '1h'
        })
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: data.reply || 'Maaf, tidak dapat memproses analisa saat ini.' }
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Terjadi kesalahan koneksi ke backend AI server.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="terminal-glass rounded-xl p-5 border border-slate-800 flex flex-col h-[520px]">
      <div className="flex items-center gap-2 pb-3 mb-3 border-b border-slate-800/80">
        <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white font-mono flex items-center gap-1.5">
            AI TRADING COPILOT
          </h3>
          <p className="text-xs text-slate-400">Asisten analisis real-time & konsultasi strategi</p>
        </div>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-2 font-sans text-xs">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.role === 'assistant' && (
              <div className="w-6 h-6 rounded-full bg-cyan-950 border border-cyan-500/40 text-cyan-400 flex items-center justify-center shrink-0 mt-0.5">
                <Sparkles className="w-3.5 h-3.5" />
              </div>
            )}
            <div
              className={`p-3 rounded-xl max-w-[85%] leading-relaxed ${
                m.role === 'user'
                  ? 'bg-cyan-600 text-white rounded-tr-none font-medium'
                  : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-tl-none'
              }`}
            >
              <p className="whitespace-pre-line">{m.text}</p>
            </div>
            {m.role === 'user' && (
              <div className="w-6 h-6 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-2.5 justify-start">
            <div className="w-6 h-6 rounded-full bg-cyan-950 border border-cyan-500/40 text-cyan-400 flex items-center justify-center shrink-0">
              <Sparkles className="w-3.5 h-3.5 animate-spin" />
            </div>
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-400 text-xs">
              Menganalisis market structure, indikator teknikal, dan order flow {selectedSymbol}...
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Quick Prompts */}
      <div className="flex items-center gap-1.5 overflow-x-auto py-2 border-t border-slate-800/60 shrink-0">
        {[
          `Analisa ${selectedSymbol} sekarang`,
          'Deteksi whale flow terbesar',
          'Rekomendasi scalping 15m',
          'Apakah aman entry saat ini?'
        ].map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            className="text-[11px] font-mono px-2.5 py-1 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 shrink-0 cursor-pointer transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2 pt-2"
      >
        <input
          type="text"
          placeholder={`Tanyakan apa saja tentang market atau ${selectedSymbol}...`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-50 text-xs font-mono font-semibold transition-colors cursor-pointer flex items-center gap-1"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Kirim</span>
        </button>
      </form>
    </div>
  );
}
