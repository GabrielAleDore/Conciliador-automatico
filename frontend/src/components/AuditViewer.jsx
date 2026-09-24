import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Layers, 
  Clock, 
  Tag, 
  AlertTriangle 
} from 'lucide-react';

import MatchedTable from './tables/MatchedTable';
import BatchTable from './tables/BatchTable';
import PendingErpTable from './tables/PendingErpTable';
import BankOnlyTable from './tables/BankOnlyTable';
import DivergentTable from './tables/DivergentTable';

export default function AuditViewer({ result }) {
  const [activeTab, setActiveTab] = useState('matched');

  if (!result) return null;

  const {
    conciliados_1_1 = [],
    conciliados_lote = [],
    pendencias_sistema = [],
    exclusivos_banco = [],
    divergencias_valor = [],
  } = result;

  const tabs = [
    {
      id: 'matched',
      label: 'Conciliados (1:1)',
      count: conciliados_1_1.length,
      icon: CheckCircle2,
      color: 'emerald',
    },
    {
      id: 'batch',
      label: 'Agrupados em Lote (1:N)',
      count: conciliados_lote.length,
      icon: Layers,
      color: 'cyan',
    },
    {
      id: 'pending',
      label: 'Pendências do Sistema',
      count: pendencias_sistema.length,
      icon: Clock,
      color: 'amber',
    },
    {
      id: 'bank_only',
      label: 'Não Lançados no Sistema',
      count: exclusivos_banco.length,
      icon: Tag,
      color: 'purple',
    },
    {
      id: 'divergent',
      label: 'Divergências de Valores',
      count: divergencias_valor.length,
      icon: AlertTriangle,
      color: 'rose',
    },
  ];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center gap-2 overflow-x-auto pb-4 border-b border-slate-800 scrollbar-none mb-6">
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          let activeClass = 'bg-blue-600/10 text-blue-400 border-blue-500/30';
          if (tab.color === 'emerald') activeClass = 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
          if (tab.color === 'cyan') activeClass = 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30';
          if (tab.color === 'amber') activeClass = 'bg-amber-500/15 text-amber-300 border-amber-500/30';
          if (tab.color === 'purple') activeClass = 'bg-purple-500/15 text-purple-300 border-purple-500/30';
          if (tab.color === 'rose') activeClass = 'bg-rose-500/15 text-rose-300 border-rose-500/30';

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition cursor-pointer border ${
                isActive
                  ? `${activeClass} shadow-md`
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
              <span
                className={`ml-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
                  isActive
                    ? 'bg-white/10 text-white'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      <div>
        {activeTab === 'matched' && <MatchedTable data={conciliados_1_1} />}
        {activeTab === 'batch' && <BatchTable data={conciliados_lote} />}
        {activeTab === 'pending' && <PendingErpTable data={pendencias_sistema} />}
        {activeTab === 'bank_only' && <BankOnlyTable data={exclusivos_banco} />}
        {activeTab === 'divergent' && <DivergentTable data={divergencias_valor} />}
      </div>
    </div>
  );
}
