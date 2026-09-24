import React, { useState } from 'react';
import Header from './components/Header';
import FileUploader from './components/FileUploader';
import ClosingDashboard from './components/ClosingDashboard';
import AuditViewer from './components/AuditViewer';

export default function App() {
  const [erpFile, setErpFile] = useState(null);
  const [bankFile, setBankFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [result, setResult] = useState(null);

  const handleProcess = async () => {
    if (!erpFile || !bankFile) {
      setError('Por favor, selecione ambos os arquivos (ERP e Santander).');
      return;
    }

    setIsProcessing(true);
    setError(null);

    const formData = new FormData();
    formData.append('sistema_pdf', erpFile);
    formData.append('santander_pdf', bankFile);

    try {
      const response = await fetch('/api/reconcile', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Erro HTTP ${response.status}: Falha no processamento.`);
      }

      const resJson = await response.json();
      setSessionId(resJson.session_id);
      setResult(resJson.data);
    } catch (err) {
      setError(err.message || 'Erro inesperado ao conciliar os extratos.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLoadSample = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await fetch('/api/reconcile-sample', {
        method: 'POST',
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Falha ao carregar dados de exemplo.');
      }

      const resJson = await response.json();
      setSessionId(resJson.session_id);
      setResult(resJson.data);
    } catch (err) {
      setError(err.message || 'Erro ao carregar dados de demonstração.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExportExcel = async () => {
    if (!sessionId) return;
    setIsExporting(true);

    try {
      const response = await fetch(`/api/export-excel/${sessionId}`);
      if (!response.ok) {
        throw new Error('Erro ao gerar relatório Excel.');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Relatorio_Conciliacao_Bancaria.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Falha no download do Excel: ${err.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleReset = () => {
    setErpFile(null);
    setBankFile(null);
    setResult(null);
    setSessionId(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-500 selection:text-white">
      <Header
        onLoadSample={handleLoadSample}
        onReset={handleReset}
        isProcessing={isProcessing}
        hasResults={!!result}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!result ? (
          <FileUploader
            erpFile={erpFile}
            setErpFile={setErpFile}
            bankFile={bankFile}
            setBankFile={setBankFile}
            onProcess={handleProcess}
            isProcessing={isProcessing}
            error={error}
          />
        ) : (
          <div className="space-y-6">
            <ClosingDashboard
              dashboard={result.dashboard}
              erpHeader={result.erp_header}
              onExportExcel={handleExportExcel}
              isExporting={isExporting}
            />

            <AuditViewer result={result} />
          </div>
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            Conciliador Bancário Rigoroso &bull; Foco em Data e Valor &bull; Decimal Nativo
          </div>
          <div>
            Compensação Bancária D+0 a D+5 &bull; Algoritmo Subset-Sum para Lotes
          </div>
        </div>
      </footer>
    </div>
  );
}
