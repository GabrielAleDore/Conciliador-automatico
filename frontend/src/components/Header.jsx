import React from 'react';
import { Scale, Sparkles, RefreshCw, FileText, ShieldCheck, Clock } from 'lucide-react';

export default function Header({ onLoadSample, onReset, isProcessing, hasResults }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          
          <div className="flex items-center gap-3.5">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 via-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20 ring-1 ring-white/20">
              <Scale className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white m-0">
                  Conciliador Bancário Rigoroso
                </h1>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <ShieldCheck className="h-3 w-3" /> 100% em Memória
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-500/10 text-blue-300 border border-blue-500/20">
                  <Clock className="h-3 w-3" /> D+0 a D+5
                </span>
              </div>
              <p className="text-xs text-slate-400 m-0">
                Auditoria determinística com foco essencial em <b>Data e Valor</b> &bull; Decimal nativo
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap">
            <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-lg border border-slate-700/60 text-xs">
              <span className="text-slate-400 px-2 font-medium">Amostras:</span>
              <a
                href="/api/sample-files/erp"
                target="_blank"
                rel="noreferrer"
                download="SISTEMA_EXEMPLO.pdf"
                className="flex items-center gap-1 px-2 py-1 rounded bg-slate-700/60 hover:bg-slate-700 text-slate-300 hover:text-white transition"
              >
                <FileText className="h-3.5 w-3.5 text-blue-400" /> ERP.pdf
              </a>
              <a
                href="/api/sample-files/santander"
                target="_blank"
                rel="noreferrer"
                download="SANTANDER_EXEMPLO.pdf"
                className="flex items-center gap-1 px-2 py-1 rounded bg-slate-700/60 hover:bg-slate-700 text-slate-300 hover:text-white transition"
              >
                <FileText className="h-3.5 w-3.5 text-red-400" /> Santander.pdf
              </a>
            </div>

            <button
              onClick={onLoadSample}
              disabled={isProcessing}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white shadow-md shadow-blue-600/20 transition disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              <Sparkles className="h-3.5 w-3.5" />
              Carregar Demonstração
            </button>

            {hasResults && (
              <button
                onClick={onReset}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition cursor-pointer"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Novo Arquivo
              </button>
            )}
          </div>

        </div>
      </div>
    </header>
  );
}
