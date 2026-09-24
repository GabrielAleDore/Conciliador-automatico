import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  ArrowUpRight, 
  ArrowDownRight, 
  Wallet, 
  TrendingUp, 
  Percent, 
  FileSpreadsheet
} from 'lucide-react';
import { formatCurrency } from '../utils/formatters';

export default function ClosingDashboard({ dashboard, erpHeader, onExportExcel, isExporting }) {
  if (!dashboard) return null;

  const isClosed = dashboard.status_geral === 'BALANCO_FECHADO';

  return (
    <div className="mb-8">
      {/* Banner de Status */}
      <div
        className={`rounded-2xl p-5 mb-6 border transition-all shadow-lg ${
          isClosed
            ? 'bg-gradient-to-r from-emerald-950/40 via-emerald-900/20 to-slate-900/50 border-emerald-500/30 text-emerald-200'
            : 'bg-gradient-to-r from-amber-950/40 via-slate-900/60 to-rose-950/30 border-amber-500/40 text-amber-200'
        }`}
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div
              className={`p-2.5 rounded-xl shrink-0 mt-0.5 ${
                isClosed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
              }`}
            >
              {isClosed ? <CheckCircle2 className="h-6 w-6" /> : <AlertTriangle className="h-6 w-6" />}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span
                  className={`text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                    isClosed
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}
                >
                  {isClosed ? 'Balanço Fechado' : 'Divergência Encontrada'}
                </span>
                {erpHeader?.periodo && (
                  <span className="text-xs text-slate-400">
                    Período: {erpHeader.periodo}
                  </span>
                )}
                {erpHeader?.conta && (
                  <span className="text-xs text-slate-400">
                    Conta: {erpHeader.conta}
                  </span>
                )}
              </div>
              <p className="text-sm font-medium text-white">
                {dashboard.status_mensagem}
              </p>
            </div>
          </div>

          <button
            onClick={onExportExcel}
            disabled={isExporting}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-xs bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 transition cursor-pointer shrink-0 disabled:opacity-50"
          >
            {isExporting ? (
              <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <FileSpreadsheet className="h-4 w-4" />
            )}
            Exportar Relatório (.xlsx)
          </button>
        </div>
      </div>

      {/* Grid de 4 Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Saldo Inicial */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4.5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Wallet className="h-3.5 w-3.5 text-blue-400" /> Saldo Inicial
            </span>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                dashboard.saldo_inicial_confere
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
              }`}
            >
              {dashboard.saldo_inicial_confere ? 'Bateu (OK)' : 'Divergente'}
            </span>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-slate-400">Sistema ERP:</span>
              <span className="text-sm font-bold text-white">
                {formatCurrency(dashboard.saldo_inicial_sistema)}
              </span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-slate-400">Extrato Santander:</span>
              <span className="text-sm font-bold text-white">
                {formatCurrency(dashboard.saldo_inicial_banco)}
              </span>
            </div>
          </div>
        </div>

        {/* Card 2: Movimentação */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4.5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-cyan-400" /> Movimentação
            </span>
            <span className="text-[10px] text-slate-400">
              ERP / Banco
            </span>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <ArrowUpRight className="h-3.5 w-3.5 text-emerald-400" /> Entradas:
              </span>
              <div className="text-right">
                <span className="text-xs font-bold text-emerald-400">
                  {formatCurrency(dashboard.total_entradas_sistema)}
                </span>
                <span className="text-[10px] text-slate-400 block">
                  Banco: {formatCurrency(dashboard.total_entradas_banco)}
                </span>
              </div>
            </div>

            <div className="flex justify-between items-baseline">
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <ArrowDownRight className="h-3.5 w-3.5 text-rose-400" /> Saídas:
              </span>
              <div className="text-right">
                <span className="text-xs font-bold text-rose-400">
                  {formatCurrency(dashboard.total_saidas_sistema)}
                </span>
                <span className="text-[10px] text-slate-400 block">
                  Banco: {formatCurrency(dashboard.total_saidas_banco)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Card 3: Saldo Final */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4.5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Wallet className="h-3.5 w-3.5 text-indigo-400" /> Saldo Final
            </span>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                dashboard.saldo_final_confere
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}
            >
              {dashboard.saldo_final_confere ? 'Fechado' : 'Ajuste Requerido'}
            </span>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-slate-400">Declarado ERP:</span>
              <span className="text-sm font-bold text-white">
                {formatCurrency(dashboard.saldo_final_declarado)}
              </span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-slate-400">Extrato Santander:</span>
              <span className="text-sm font-bold text-white">
                {formatCurrency(dashboard.saldo_final_banco)}
              </span>
            </div>
          </div>
        </div>

        {/* Card 4: Taxa de Conciliação */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4.5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Percent className="h-3.5 w-3.5 text-emerald-400" /> Conciliação
            </span>
            <span className="text-xs font-bold text-white">
              {dashboard.total_conciliados_1_1 + dashboard.total_agrupados_lote} lotes/pares
            </span>
          </div>

          <div>
            <div className="flex items-baseline justify-between mb-1.5">
              <span className="text-2xl font-black text-white tracking-tight">
                {dashboard.percentual_conciliado}%
              </span>
              <span className="text-[11px] text-slate-400">
                {dashboard.total_itens_erp} ERP &bull; {dashboard.total_itens_banco} Banco
              </span>
            </div>

            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full transition-all duration-500 rounded-full ${
                  dashboard.percentual_conciliado >= 90
                    ? 'bg-emerald-500'
                    : dashboard.percentual_conciliado >= 60
                    ? 'bg-amber-500'
                    : 'bg-rose-500'
                }`}
                style={{ width: `${Math.min(100, Math.max(5, dashboard.percentual_conciliado))}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
