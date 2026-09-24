import React, { useMemo, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table';
import { ArrowUpDown, ChevronLeft, ChevronRight, Search, Tag } from 'lucide-react';
import { formatCurrency, formatDateBR } from '../../utils/formatters';

export default function BankOnlyTable({ data }) {
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState([]);

  const columns = useMemo(() => [
    {
      accessorKey: 'data',
      header: 'Data Transação',
      cell: info => (
        <span className="font-mono text-xs font-semibold text-slate-200">
          {formatDateBR(info.getValue())}
        </span>
      ),
    },
    {
      accessorKey: 'valor',
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
      accessorKey: 'descricao',
      header: 'Histórico no Extrato',
      cell: info => (
        <span className="text-xs text-slate-300 font-medium max-w-sm block">
          {info.getValue()}
        </span>
      ),
    },
    {
      accessorKey: 'categoria',
      header: 'Categoria',
      cell: info => {
        const cat = info.getValue() || 'DÉBITO BANCÁRIO';
        let colorClass = 'bg-slate-800 text-slate-300 border-slate-700';
        if (cat === 'TARIFA') colorClass = 'bg-purple-500/10 text-purple-300 border-purple-500/20';
        if (cat === 'IOF') colorClass = 'bg-amber-500/10 text-amber-300 border-amber-500/20';
        if (cat === 'JUROS') colorClass = 'bg-rose-500/10 text-rose-300 border-rose-500/20';
        if (cat === 'RENDIMENTO') colorClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20';

        return (
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${colorClass}`}>
            <Tag className="h-3 w-3" /> {cat}
          </span>
        );
      },
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
            placeholder="Filtrar por data, valor ou histórico..."
            className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-purple-500 transition"
          />
        </div>
        <div className="text-xs text-slate-400">
          Total Exclusivo Santander: <span className="font-semibold text-purple-400">{data.length}</span> lançamentos
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60">
        <table className="w-full text-left border-collapse">
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id} className="border-b border-slate-800 bg-slate-900/90 text-slate-400 text-[11px] font-semibold">
                {headerGroup.headers.map(header => (
                  <th key={header.id} className="py-2.5 px-3 uppercase tracking-wider">
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
                <td colSpan={4} className="py-8 text-center text-slate-500 text-xs">
                  Nenhum lançamento exclusivo do banco encontrado.
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
