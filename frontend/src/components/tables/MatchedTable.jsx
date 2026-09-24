import React, { useMemo, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table';
import { ArrowUpDown, ChevronLeft, ChevronRight, CheckCircle2, Search } from 'lucide-react';
import { formatCurrency, formatDateBR } from '../../utils/formatters';

export default function MatchedTable({ data }) {
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);

  const columns = useMemo(() => [
    {
      header: 'Sistema ERP',
      columns: [
        {
          accessorKey: 'erp_item.data',
          header: 'Data ERP',
          cell: info => (
            <span className="font-mono text-xs font-semibold text-slate-200">
              {formatDateBR(info.getValue())}
            </span>
          ),
        },
        {
          accessorKey: 'erp_item.valor',
          header: 'Valor ERP',
          cell: info => {
            const val = parseFloat(info.getValue());
            return (
              <span className={`font-mono text-xs font-bold ${val < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {formatCurrency(val)}
              </span>
            );
          },
        },
        {
          accessorKey: 'erp_item.descricao',
          header: 'Descrição / Favorecido',
          cell: info => (
            <span className="text-xs text-slate-300">
              {info.getValue()}
            </span>
          ),
        },
      ],
    },
    {
      header: 'Extrato Santander',
      columns: [
        {
          accessorKey: 'banco_item.data',
          header: 'Data Banco',
          cell: info => (
            <span className="font-mono text-xs font-semibold text-slate-200">
              {formatDateBR(info.getValue())}
            </span>
          ),
        },
        {
          accessorKey: 'banco_item.valor',
          header: 'Valor Banco',
          cell: info => {
            const val = parseFloat(info.getValue());
            return (
              <span className={`font-mono text-xs font-bold ${val < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {formatCurrency(val)}
              </span>
            );
          },
        },
        {
          accessorKey: 'banco_item.descricao',
          header: 'Histórico Banco',
          cell: info => (
            <span className="text-xs text-slate-300 max-w-xs truncate block" title={info.getValue()}>
              {info.getValue()}
            </span>
          ),
        },
      ],
    },
    {
      header: 'Compensação',
      columns: [
        {
          accessorKey: 'diff_dias',
          header: 'Janela (D+0 a D+5)',
          cell: info => {
            const d = info.getValue();
            return (
              <span className={`inline-flex px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
                d === 0 ? 'bg-slate-800 text-slate-300' : 'bg-blue-500/15 text-blue-400 border border-blue-500/30'
              }`}>
                {d >= 0 ? `D+${d}` : `D${d}`}
              </span>
            );
          },
        },
      ],
    },
  ], []);

  const table = useReactTable({
    data: data || [],
    columns,
    state: {
      globalFilter,
      sorting,
    },
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: { pageSize: 10 },
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={globalFilter ?? ''}
            onChange={e => setGlobalFilter(e.target.value)}
            placeholder="Filtrar por data, valor ou descrição..."
            className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 transition"
          />
        </div>
        <div className="text-xs text-slate-400">
          Mostrando <span className="font-semibold text-white">{table.getRowModel().rows.length}</span> de <span className="font-semibold text-white">{data.length}</span> conciliados
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60">
        <table className="w-full text-left border-collapse">
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id} className="border-b border-slate-800 bg-slate-900/90 text-slate-400 text-[11px] font-semibold">
                {headerGroup.headers.map(header => (
                  <th key={header.id} colSpan={header.colSpan} className="py-2.5 px-3 uppercase tracking-wider">
                    {header.isPlaceholder ? null : (
                      <div
                        {...{
                          className: header.column.getCanSort()
                            ? 'cursor-pointer select-none flex items-center gap-1 hover:text-white transition'
                            : '',
                          onClick: header.column.getToggleSortingHandler(),
                        }}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() && (
                          <ArrowUpDown className="h-3 w-3 text-slate-500" />
                        )}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map(row => (
                <tr key={row.id} className="hover:bg-slate-800/40 transition">
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="py-2.5 px-3">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                  Nenhum registro encontrado para o filtro.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {table.getPageCount() > 1 && (
        <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
          <div>
            Página <span className="font-semibold text-white">{table.getState().pagination.pageIndex + 1}</span> de <span className="font-semibold text-white">{table.getPageCount()}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="p-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="p-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
