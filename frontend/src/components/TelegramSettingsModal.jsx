import React, { useState } from 'react';
import { Send, CheckCircle2, AlertCircle, X, ExternalLink, Bot, Key, MessageSquare } from 'lucide-react';

export default function TelegramSettingsModal({ isOpen, onClose, telegramStatus }) {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  if (!isOpen) return null;

  const handleTestSend = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch('/api/telegram/test', { method: 'POST' });
      const data = await res.json();
      setTestResult(data);
    } catch (e) {
      setTestResult({ success: false, message: 'Gagal menghubungi server backend.' });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0e131d] border border-slate-700 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-[#090d14]">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white font-mono">PENGATURAN TELEGRAM BOT</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 space-y-4 font-sans text-xs">
          {/* Status Indicator */}
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-slate-400 block text-[11px]">Status Integrasi Telegram:</span>
              <span
                className={`font-mono font-bold text-xs flex items-center gap-1.5 mt-0.5 ${
                  telegramStatus?.bot_username ? 'text-emerald-400' : 'text-amber-400'
                }`}
              >
                {telegramStatus?.bot_username ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Terhubung (@{telegramStatus.bot_username})
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3.5 h-3.5" />
                    Belum Dikonfigurasi (Mock/Simulator Mode)
                  </>
                )}
              </span>
            </div>

            <button
              onClick={handleTestSend}
              disabled={testing}
              className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5"
            >
              <Send className="w-3 h-3" />
              <span>{testing ? 'Mengirim...' : 'Uji Kirim'}</span>
            </button>
          </div>

          {/* Test Result Feedback */}
          {testResult && (
            <div
              className={`p-3 rounded-lg border text-xs font-mono flex items-start gap-2 ${
                testResult.success
                  ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                  : 'bg-rose-950/40 border-rose-500/40 text-rose-300'
              }`}
            >
              {testResult.success ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              )}
              <span>{testResult.message}</span>
            </div>
          )}

          {/* Setup Guide */}
          <div className="space-y-2.5 pt-2 border-t border-slate-800">
            <h4 className="font-mono font-semibold text-slate-200 flex items-center gap-1.5">
              <Key className="w-3.5 h-3.5 text-cyan-400" />
              Panduan Menghubungkan Bot Telegram Sendiri:
            </h4>
            <ol className="list-decimal list-inside space-y-1.5 text-slate-400 text-xs leading-relaxed">
              <li>
                Buka Telegram dan cari <strong>@BotFather</strong>. Ketik <code>/newbot</code> untuk membuat bot baru dan dapatkan <strong>HTTP API Token</strong>.
              </li>
              <li>
                Cari <strong>@userinfobot</strong> di Telegram atau buat grup/channel baru untuk mendapatkan <strong>Chat ID</strong> Anda.
              </li>
              <li>
                Buka file <code className="bg-slate-800 px-1 py-0.5 rounded text-cyan-300">.env</code> di direktori root bot dan isi:
                <pre className="mt-1 p-2 rounded bg-black/60 font-mono text-[11px] text-slate-300 border border-slate-800">
TELEGRAM_BOT_TOKEN=your_token_here&#10;TELEGRAM_CHAT_ID=your_chat_id_here
                </pre>
              </li>
              <li>Simpan file dan restart server. Semua alert otomatis akan langsung masuk ke Telegram Anda!</li>
            </ol>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-[#090d14] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono text-xs cursor-pointer transition-colors"
          >
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
}
