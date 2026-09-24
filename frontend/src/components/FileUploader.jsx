import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, ArrowRight, AlertCircle, X, Zap, Layers, Clock } from 'lucide-react';

export default function FileUploader({
  erpFile,
  setErpFile,
  bankFile,
  setBankFile,
  onProcess,
  isProcessing,
  error
}) {
  const [dragErp, setDragErp] = useState(false);
  const [dragBank, setDragBank] = useState(false);

  const handleDropErp = (e) => {
    e.preventDefault();
    setDragErp(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.toLowerCase().endsWith('.pdf')) {
        setErpFile(file);
      }
    }
  };

  const handleDropBank = (e) => {
    e.preventDefault();
    setDragBank(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.toLowerCase().endsWith('.pdf')) {
        setBankFile(file);
      }
    }
  };

  const canProcess = erpFile && bankFile && !isProcessing;

  return (
    <div className="max-w-4xl mx-auto my-8 px-4">
      <div className="text-center mb-8">
        <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mb-2">
          Conciliação Financeira por Data & Valor
        </h2>
        <p className="text-slate-400 text-sm max-w-xl mx-auto">
          Faça o upload dos dois extratos para conciliação em memória com precisão absoluta de centavos e janela de compensação bancária <b>D+0 a D+5</b>.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-3 text-rose-300 text-sm">
          <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold">Erro no Processamento:</span> {error}
          </div>
        </div>
      )}

      {/* Grid com Dropzones */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Card 1: SISTEMA ERP */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragErp(true); }}
          onDragLeave={() => setDragErp(false)}
          onDrop={handleDropErp}
          className={`relative rounded-2xl border-2 transition-all p-6 flex flex-col items-center justify-center text-center min-h-[220px] ${
            dragErp
              ? 'border-blue-500 bg-blue-500/10 scale-[1.01]'
              : erpFile
              ? 'border-blue-500/50 bg-blue-950/20'
              : 'border-dashed border-slate-700 hover:border-slate-500 bg-slate-900/50'
          }`}
        >
          <input
            type="file"
            id="erp-input"
            accept=".pdf"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && setErpFile(e.target.files[0])}
          />

          {erpFile ? (
            <div className="flex flex-col items-center">
              <div className="h-12 w-12 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center mb-3">
                <CheckCircle2 className="h-6 w-6 text-blue-400" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-blue-400 mb-1">
                Extrato do Sistema ERP
              </span>
              <p className="text-sm font-medium text-white max-w-[220px] truncate mb-1">
                {erpFile.name}
              </p>
              <span className="text-xs text-slate-400 mb-3">
                {(erpFile.size / 1024).toFixed(1)} KB
              </span>
              <button
                onClick={() => setErpFile(null)}
                className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-rose-400 transition"
              >
                <X className="h-3.5 w-3.5" /> Remover arquivo
              </button>
            </div>
          ) : (
            <label htmlFor="erp-input" className="cursor-pointer flex flex-col items-center">
              <div className="h-12 w-12 rounded-xl bg-slate-800 text-blue-400 flex items-center justify-center mb-3 ring-1 ring-slate-700 hover:scale-105 transition">
                <UploadCloud className="h-6 w-6" />
              </div>
              <span className="text-sm font-semibold text-white mb-1">
                1. Extrato do Sistema ERP
              </span>
              <p className="text-xs text-slate-400 mb-3">
                Arquivo <code className="text-blue-300">SISTEMA.pdf</code>
              </p>
              <span className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 transition">
                Selecionar Arquivo
              </span>
            </label>
          )}
        </div>

        {/* Card 2: SANTANDER BANCO */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragBank(true); }}
          onDragLeave={() => setDragBank(false)}
          onDrop={handleDropBank}
          className={`relative rounded-2xl border-2 transition-all p-6 flex flex-col items-center justify-center text-center min-h-[220px] ${
            dragBank
              ? 'border-red-500 bg-red-500/10 scale-[1.01]'
              : bankFile
              ? 'border-red-500/50 bg-red-950/20'
              : 'border-dashed border-slate-700 hover:border-slate-500 bg-slate-900/50'
          }`}
        >
          <input
            type="file"
            id="bank-input"
            accept=".pdf"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && setBankFile(e.target.files[0])}
          />

          {bankFile ? (
            <div className="flex flex-col items-center">
              <div className="h-12 w-12 rounded-xl bg-red-500/20 text-red-400 flex items-center justify-center mb-3">
                <CheckCircle2 className="h-6 w-6 text-red-400" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-red-400 mb-1">
                Extrato Bancário Santander
              </span>
              <p className="text-sm font-medium text-white max-w-[220px] truncate mb-1">
                {bankFile.name}
              </p>
              <span className="text-xs text-slate-400 mb-3">
                {(bankFile.size / 1024).toFixed(1)} KB
              </span>
              <button
                onClick={() => setBankFile(null)}
                className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-rose-400 transition"
              >
                <X className="h-3.5 w-3.5" /> Remover arquivo
              </button>
            </div>
          ) : (
            <label htmlFor="bank-input" className="cursor-pointer flex flex-col items-center">
              <div className="h-12 w-12 rounded-xl bg-slate-800 text-red-400 flex items-center justify-center mb-3 ring-1 ring-slate-700 hover:scale-105 transition">
                <UploadCloud className="h-6 w-6" />
              </div>
              <span className="text-sm font-semibold text-white mb-1">
                2. Extrato Bancário Santander
              </span>
              <p className="text-xs text-slate-400 mb-3">
                Arquivo <code className="text-red-300">SANTANDER.pdf</code>
              </p>
              <span className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 transition">
                Selecionar Arquivo
              </span>
            </label>
          )}
        </div>
      </div>

      <div className="flex flex-col items-center justify-center gap-4">
        <button
          onClick={onProcess}
          disabled={!canProcess}
          className={`w-full sm:w-auto min-w-[280px] px-8 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2.5 shadow-xl transition-all cursor-pointer ${
            canProcess
              ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5'
              : 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
          }`}
        >
          {isProcessing ? (
            <>
              <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Conciliando por Data e Valor...
            </>
          ) : (
            <>
              Processar Conciliação
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>

        {!canProcess && !isProcessing && (
          <p className="text-xs text-slate-500">
            Selecione ambos os arquivos PDF para iniciar.
          </p>
        )}
      </div>

      <div className="mt-12 pt-8 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 shrink-0">
            <Zap className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-white mb-1">Aritmética com Decimal</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Cálculo estrito de centavos, livre de inconsistências de ponto flutuante.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
            <Layers className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-white mb-1">Subset-Sum (Lotes 1:N)</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Detecta pagamentos únicos consolidados no banco que quitam múltiplas faturas no ERP.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 shrink-0">
            <Clock className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-white mb-1">Compensação D+0 a D+5</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Acomoda compensação bancária e finais de semana em até 5 dias após o lançamento.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
