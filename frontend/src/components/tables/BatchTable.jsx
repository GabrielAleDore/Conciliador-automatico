import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Layers, CornerDownRight, CheckCircle2 } from 'lucide-react';
import { formatCurrency, formatDateBR } from '../../utils/formatters';

export default function BatchTable({ data }) {
  const [expandedIds, setExpandedIds] = useState(() => {
    const initial = {};
    if (data && data.length > 0) initial[data[0].id] = true;
    return initial;
  });

  const toggleExpand = (id) => {
    setExpandedIds(prev => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-500 text-xs">
        Nenhum agrupamento de lote (1 banco : N sistema) foi identificado neste período.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-xs text-slate-400 mb-2">
        Identificação de <span className="text-white font-semibold">{data.length}</span> lote(s) onde 1 lançamento no banco liquidou a soma de N faturas do ERP via algoritmo <span className="text-cyan-400 font-mono font-medium">Subset-Sum</span>.
      </div>

      <div className="space-y-3">
        {data.map(group => {
          const isExpanded = !!expandedIds[group.id];
          const b = group.banco_item;
          const erpItems = group.erp_itens || [];
          const bankVal = parseFloat(b.valor);

          return (
            <div
              key={group.id}
              className="rounded-xl border border-slate-800 bg-slate-900/70 overflow-hidden shadow-sm transition hover:border-slate-700"
            >
              {/* Linha Pai (Banco) */}
              <div
                onClick={() => toggleExpand(group.id)}
                className="p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 cursor-pointer hover:bg-slate-800/40 select-none transition"
              >
                <div className="flex items-center gap-3">
                  <button className="p-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white transition shrink-0">
                    {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  </button>

                  <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 shrink-0">
                    <Layers className="h-4 w-4" />
                  </div>

                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-slate-200">
                        {formatDateBR(b.data)}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                        BANCO SANTANDER (CONSOLIDADO)
                      </span>
                    </div>
                    <p className="text-xs font-medium text-white mt-0.5 max-w-xl">
                      {b.descricao}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4 self-end md:self-center">
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block uppercase tracking-wider">
                      Valor Liquidado
                    </span>
                    <span className={`font-mono text-sm font-bold ${bankVal < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {formatCurrency(bankVal)}
                    </span>
                  </div>

                  <div className="px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700/80 text-[11px] font-medium text-slate-300 flex items-center gap-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                    {erpItems.length} faturas ERP
                  </div>
                </div>
              </div>

              {/* Filhas (ERP) */}
              {isExpanded && (
                <div className="border-t border-slate-800/80 bg-slate-950/60 p-4">
                  <div className="flex items-center gap-2 mb-3 text-xs font-semibold text-slate-300">
                    <CornerDownRight className="h-3.5 w-3.5 text-cyan-400" />
                    Desdobramento Contábil dos {erpItems.length} lançamentos que somam este valor:
                  </div>

                  <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-900/50">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-slate-800 text-[10px] uppercase font-semibold text-slate-400 bg-slate-900/90">
                          <th className="py-2 px-3">Data Lcto</th>
                          <th className="py-2 px-3">Descrição / Favorecido (ERP)</th>
                          <th className="py-2 px-3 text-right">Valor Parcela (R$)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/40">
                        {erpItems.map(item => {
                          const val = parseFloat(item.valor);
                          return (
                            <tr key={item.id} className="hover:bg-slate-800/20 transition">
                              <td className="py-2 px-3 font-mono font-semibold text-slate-200">
                                {formatDateBR(item.data)}
                              </td>
                              <td className="py-2 px-3 font-medium text-slate-300">
                                {item.descricao}
                              </td>
                              <td className={`py-2 px-3 text-right font-mono font-bold ${val < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                {formatCurrency(val)}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                      <tfoot>
                        <tr className="border-t border-slate-800 bg-slate-900 font-semibold text-slate-200 text-xs">
                          <td colSpan={2} className="py-2.5 px-3 text-right">
                            SOMA DAS PARCELAS ERP:
                          </td>
                          <td className="py-2.5 px-3 text-right font-mono text-emerald-400 font-bold">
                            {formatCurrency(group.total_erp)}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
