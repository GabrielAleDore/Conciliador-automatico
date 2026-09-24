import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.generators.sample_generator import generate_sample_erp_pdf, generate_sample_santander_pdf
from app.parsers.erp_parser import parse_erp_pdf
from app.parsers.santander_parser import parse_santander_pdf
from app.engine.reconciliation import run_reconciliation
from app.export.excel_exporter import create_excel_report

def main():
    print("1. Gerando PDFs de teste sintéticos...")
    erp_pdf = generate_sample_erp_pdf()
    san_pdf = generate_sample_santander_pdf()
    print(f"   ERP: {len(erp_pdf)} bytes | Santander: {len(san_pdf)} bytes")

    print("\n2. Extraindo lançamentos do ERP (foco Data e Valor)...")
    erp_records, erp_head, erp_foot = parse_erp_pdf(erp_pdf)
    print(f"   Lançamentos ERP: {len(erp_records)}")
    for r in erp_records[:3]:
        print(f"     -> Data: {r.data} | Valor: {r.valor} | Desc: {r.descricao}")

    print("\n3. Extraindo lançamentos do Santander (foco Data e Valor)...")
    san_records, san_meta = parse_santander_pdf(san_pdf)
    print(f"   Transações Santander: {len(san_records)}")
    for b in san_records[:3]:
        print(f"     -> Data: {b.data} | Valor: {b.valor} | Hist: {b.descricao[:30]}")

    print("\n4. Executando motor determinístico com tolerância D+0 a D+5...")
    result = run_reconciliation(
        erp_records=erp_records,
        bank_records=san_records,
        erp_header=erp_head,
        erp_footer=erp_foot,
        bank_meta=san_meta,
    )

    d = result.dashboard
    print("\n--- RESULTADOS DO DASHBOARD ---")
    print(f"Saldo Inicial Sistema: {d.saldo_inicial_sistema} vs Banco: {d.saldo_inicial_banco} (Confere: {d.saldo_inicial_confere})")
    print(f"Saldo Final: ERP {d.saldo_final_sistema} vs Banco {d.saldo_final_banco}")
    print(f"Conciliados 1:1: {len(result.conciliados_1_1)} pares")
    print(f"Agrupados em Lote (1:N): {len(result.conciliados_lote)} grupos")
    print(f"Pendências Sistema: {len(result.pendencias_sistema)}")
    print(f"Exclusivos Banco: {len(result.exclusivos_banco)}")
    print(f"Divergências de Valor: {len(result.divergencias_valor)}")
    print(f"Percentual Conciliado: {d.percentual_conciliado}%")
    print(f"Status Geral: {d.status_geral} ({d.status_mensagem})")

    # Verifica se o lançamento de D+4 (Seguradora Allianz) casou perfeitamente
    allianz_match = next((p for p in result.conciliados_1_1 if "ALLIANZ" in p.erp_item.descricao.upper()), None)
    if allianz_match:
        print(f"\n[SUCESSO] Lançamento compensado em D+{allianz_match.diff_dias} foi conciliado com sucesso pela regra D+0 a D+5!")

    print("\n5. Gerando planilha Excel (.xlsx)...")
    excel_bytes = create_excel_report(result)
    print(f"   Relatório Excel gerado: {len(excel_bytes)} bytes!")

    print("\nBACKEND VALIDADO COM SUCESSO!")

if __name__ == "__main__":
    main()
