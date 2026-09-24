import uuid
import os
from pathlib import Path
from typing import Dict
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import io

from app.parsers.erp_parser import parse_erp_pdf
from app.parsers.santander_parser import parse_santander_pdf
from app.engine.reconciliation import run_reconciliation
from app.export.excel_exporter import create_excel_report
from app.generators.sample_generator import generate_sample_erp_pdf, generate_sample_santander_pdf
from app.models.schemas import ReconciliationResponse

app = FastAPI(
    title="Conciliador Bancário Rigoroso",
    description="Motor determinístico de conciliação bancária 100% em memória orientado a Data e Valor (D+0 a D+5).",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IN_MEMORY_SESSIONS: Dict[str, ReconciliationResponse] = {}

# Caminho para o build do frontend (gerado por `npm run build`)
_FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"

# Em produção (Railway), serve os assets estáticos do React
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="assets")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Conciliador Bancario Rigoroso", "tolerancia": "D+0 a D+5"}

@app.post("/api/reconcile")
async def reconcile_files(
    sistema_pdf: UploadFile = File(..., description="Extrato do ERP (SISTEMA.pdf)"),
    santander_pdf: UploadFile = File(..., description="Extrato Bancário Santander (SANTANDER.pdf)")
):
    if not sistema_pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo do sistema deve ser um PDF válido.")
    if not santander_pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo do Santander deve ser um PDF válido.")

    try:
        erp_bytes = await sistema_pdf.read()
        bank_bytes = await santander_pdf.read()

        erp_records, erp_header, erp_footer = parse_erp_pdf(erp_bytes)
        bank_records, bank_meta = parse_santander_pdf(bank_bytes)

        if not erp_records:
            raise HTTPException(status_code=422, detail="Nenhum lançamento foi identificado no PDF do ERP.")
        if not bank_records:
            raise HTTPException(status_code=422, detail="Nenhuma transação foi identificada no PDF do Santander.")

        response_data = run_reconciliation(
            erp_records=erp_records,
            bank_records=bank_records,
            erp_header=erp_header,
            erp_footer=erp_footer,
            bank_meta=bank_meta,
        )

        session_id = str(uuid.uuid4())
        IN_MEMORY_SESSIONS[session_id] = response_data
        
        if len(IN_MEMORY_SESSIONS) > 50:
            oldest_key = next(iter(IN_MEMORY_SESSIONS))
            del IN_MEMORY_SESSIONS[oldest_key]

        return {
            "session_id": session_id,
            "data": response_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento dos PDFs: {str(e)}")


@app.post("/api/reconcile-sample")
def reconcile_sample():
    try:
        erp_bytes = generate_sample_erp_pdf()
        bank_bytes = generate_sample_santander_pdf()

        erp_records, erp_header, erp_footer = parse_erp_pdf(erp_bytes)
        bank_records, bank_meta = parse_santander_pdf(bank_bytes)

        response_data = run_reconciliation(
            erp_records=erp_records,
            bank_records=bank_records,
            erp_header=erp_header,
            erp_footer=erp_footer,
            bank_meta=bank_meta,
        )

        session_id = str(uuid.uuid4())
        IN_MEMORY_SESSIONS[session_id] = response_data

        return {
            "session_id": session_id,
            "data": response_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados de exemplo: {str(e)}")


@app.get("/api/sample-files/{file_type}")
def download_sample_pdf(file_type: str):
    if file_type == "erp":
        pdf_bytes = generate_sample_erp_pdf()
        filename = "SISTEMA_EXEMPLO.pdf"
    elif file_type == "santander":
        pdf_bytes = generate_sample_santander_pdf()
        filename = "SANTANDER_EXEMPLO.pdf"
    else:
        raise HTTPException(status_code=404, detail="Tipo de arquivo inválido.")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/export-excel/{session_id}")
def export_excel(session_id: str):
    if session_id not in IN_MEMORY_SESSIONS:
        raise HTTPException(status_code=404, detail="Sessão de conciliação expirada ou não encontrada em memória.")

    reconciliation_result = IN_MEMORY_SESSIONS[session_id]
    excel_bytes = create_excel_report(reconciliation_result)

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Relatorio_Conciliacao_Bancaria.xlsx"}
    )


# ---------------------------------------------------------------------------
# SPA Catch-all — serve o index.html do React para qualquer rota não-API
# Necessário para que o React Router funcione em produção (Railway)
# ---------------------------------------------------------------------------
@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    index_file = _FRONTEND_DIST / "index.html"
    if _FRONTEND_DIST.exists() and index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Conciliador Bancário API — acesse /docs para a documentação."}
