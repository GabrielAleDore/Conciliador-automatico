import uuid
from datetime import date
from decimal import Decimal
from typing import List, Dict, Tuple, Optional, Any

from app.models.schemas import (
    Lancamento,
    ParConciliado,
    GrupoLote,
    DivergenciaValor,
    DashboardResumo,
    ReconciliationResponse,
)
from app.engine.normalizer import parse_date
from app.engine.subset_sum import find_exact_subset_sum

def run_reconciliation(
    erp_records: List[Lancamento],
    bank_records: List[Lancamento],
    erp_header: Dict[str, Any],
    erp_footer: Dict[str, Any],
    bank_meta: Dict[str, Any],
) -> ReconciliationResponse:
    """
    Motor determinístico de conciliação bancária 100% em memória,
    estritamente orientado por DATA e VALOR.
    Tolerância de compensação bancária: D+0 a D+5.
    Aritmética estritamente com decimal.Decimal.
    """
    matched_1_1: List[ParConciliado] = []
    matched_batch: List[GrupoLote] = []
    divergencias: List[DivergenciaValor] = []

    matched_erp_ids = set()
    matched_bank_ids = set()

    # Mapeamento para parsing de datas e valores em Decimal
    erp_data_map: Dict[str, Tuple[date, Decimal]] = {}
    for r in erp_records:
        dt = parse_date(r.data) or date(2026, 1, 1)
        val = Decimal(r.valor)
        erp_data_map[r.id] = (dt, val)

    bank_data_map: Dict[str, Tuple[date, Decimal]] = {}
    for b in bank_records:
        dt = parse_date(b.data) or date(2026, 1, 1)
        val = Decimal(b.valor)
        bank_data_map[b.id] = (dt, val)

    # -------------------------------------------------------------
    # FASE 1: Casamento 1 para 1 baseado em VALOR e DATA (D+0 a D+5)
    # -------------------------------------------------------------
    candidates_1_1 = []

    for b in bank_records:
        b_dt, b_val = bank_data_map[b.id]
        for e in erp_records:
            e_dt, e_val = erp_data_map[e.id]

            # 1. VALOR EXATO com sinal idêntico
            if b_val != e_val:
                continue

            # 2. TOLERÂNCIA DE DATA: D+0 a D+5 (com tolerância de -1 dia para fuso/data de compensação)
            delta_days = (b_dt - e_dt).days
            if not (-1 <= delta_days <= 5):
                continue

            # Verificação de documento caso exista para desempate
            doc_match = False
            if e.documento and len(e.documento.strip()) >= 3:
                doc_clean = e.documento.strip().lstrip("0")
                if doc_clean and (
                    (b.documento and doc_clean in b.documento.lstrip("0"))
                    or doc_clean in b.descricao
                ):
                    doc_match = True

            # Score de proximidade: delta 0 tem preferência, depois menor diferença de dias
            score = 100.0 - (abs(delta_days) * 10.0)
            if doc_match:
                score += 50.0

            candidates_1_1.append({
                "score": score,
                "diff_dias": delta_days,
                "match_tipo": "DATA_VALOR_DOC" if doc_match else "DATA_VALOR_EXATO",
                "erp": e,
                "bank": b,
            })

    # Ordena pelo melhor score
    candidates_1_1.sort(key=lambda x: x["score"], reverse=True)

    for cand in candidates_1_1:
        e = cand["erp"]
        b = cand["bank"]
        if e.id in matched_erp_ids or b.id in matched_bank_ids:
            continue

        matched_erp_ids.add(e.id)
        matched_bank_ids.add(b.id)

        matched_1_1.append(
            ParConciliado(
                id=str(uuid.uuid4()),
                erp_item=e,
                banco_item=b,
                diff_dias=cand["diff_dias"],
                match_tipo=cand["match_tipo"],
            )
        )

    # -------------------------------------------------------------
    # FASE 2: Agrupamento em Lote (1 Banco : N Sistema) via Subset-Sum
    # -------------------------------------------------------------
    unmatched_banks = [b for b in bank_records if b.id not in matched_bank_ids]

    for b in unmatched_banks:
        b_dt, b_val = bank_data_map[b.id]
        
        # Ignora tarifas bancárias automáticas
        if b.categoria in ["TARIFA", "IOF", "RENDIMENTO"]:
            continue

        target_abs = abs(b_val)
        # Itens do ERP com mesmo sinal dentro de uma janela temporal (+/- 7 dias)
        available_erp = [
            e for e in erp_records
            if e.id not in matched_erp_ids
            and erp_data_map[e.id][1] * b_val > 0  # mesmo sinal
            and abs((bank_data_map[b.id][0] - erp_data_map[e.id][0]).days) <= 7
        ]

        if len(available_erp) < 2:
            continue

        subset = find_exact_subset_sum(
            candidates=available_erp,
            target=target_abs,
            value_getter=lambda x: abs(erp_data_map[x.id][1]),
            max_k=10
        )

        if subset and len(subset) >= 2:
            sum_subset = sum((erp_data_map[item.id][1] for item in subset), Decimal("0.00"))
            if sum_subset == b_val:
                matched_bank_ids.add(b.id)
                for item in subset:
                    matched_erp_ids.add(item.id)

                matched_batch.append(
                    GrupoLote(
                        id=str(uuid.uuid4()),
                        banco_item=b,
                        erp_itens=subset,
                        total_erp=str(sum_subset),
                        diff_valor="0.00",
                    )
                )

    # -------------------------------------------------------------
    # FASE 3: Classificação de Resíduos e Divergências
    # -------------------------------------------------------------
    remaining_banks = [b for b in bank_records if b.id not in matched_bank_ids]
    remaining_erps = [e for e in erp_records if e.id not in matched_erp_ids]

    # Procura divergências de valor: mesma data (D+0 a D+5) e mesmo sinal, com valor divergente
    for b in list(remaining_banks):
        b_dt, b_val = bank_data_map[b.id]
        best_match = None
        min_delta = 999

        for e in remaining_erps:
            if e.id in matched_erp_ids:
                continue
            e_dt, e_val = erp_data_map[e.id]

            if b_val * e_val <= 0:
                continue

            delta_days = (b_dt - e_dt).days
            if -1 <= delta_days <= 5 and abs(delta_days) < min_delta:
                # Se ordens de grandeza são próximas
                diff = b_val - e_val
                if abs(diff) < max(abs(b_val), abs(e_val)) * Decimal("0.3"): # diferença de até 30%
                    min_delta = abs(delta_days)
                    best_match = (e, b, diff, delta_days)

        if best_match:
            e, b, diff, delta_days = best_match
            matched_bank_ids.add(b.id)
            matched_erp_ids.add(e.id)
            remaining_banks.remove(b)
            remaining_erps.remove(e)

            tipo = "CENTAVOS" if abs(diff) < Decimal("1.00") else "DIVERGENCIA_VALOR"
            divergencias.append(
                DivergenciaValor(
                    id=str(uuid.uuid4()),
                    erp_item=e,
                    banco_item=b,
                    diff_valor=f"{diff:+.2f}",
                    diff_dias=delta_days,
                    tipo=tipo,
                )
            )

    pendencias_sistema = [e for e in erp_records if e.id not in matched_erp_ids]
    exclusivos_banco = [b for b in bank_records if b.id not in matched_bank_ids]

    # Ordenação cronológica
    matched_1_1.sort(key=lambda x: x.erp_item.data)
    matched_batch.sort(key=lambda x: x.banco_item.data)
    pendencias_sistema.sort(key=lambda x: x.data)
    exclusivos_banco.sort(key=lambda x: x.data)
    divergencias.sort(key=lambda x: x.banco_item.data)

    # -------------------------------------------------------------
    # CÁLCULOS DO DASHBOARD E FECHAMENTO CONTÁBIL
    # -------------------------------------------------------------
    saldo_ini_erp = Decimal(str(erp_header.get("saldo_anterior", "0.00")))
    saldo_ini_banco = Decimal(str(bank_meta.get("saldo_inicial", "0.00")))
    if saldo_ini_banco == Decimal("0.00") and bank_records:
        first_b = bank_records[0]
        if first_b.saldo is not None:
            saldo_ini_banco = Decimal(first_b.saldo) - Decimal(first_b.valor)

    tot_entradas_erp = sum(
        (Decimal(e.valor) for e in erp_records if Decimal(e.valor) > 0),
        Decimal("0.00")
    )
    tot_saidas_erp = sum(
        (Decimal(e.valor) for e in erp_records if Decimal(e.valor) < 0),
        Decimal("0.00")
    )

    tot_entradas_banco = sum(
        (Decimal(b.valor) for b in bank_records if Decimal(b.valor) > 0),
        Decimal("0.00")
    )
    tot_saidas_banco = sum(
        (Decimal(b.valor) for b in bank_records if Decimal(b.valor) < 0),
        Decimal("0.00")
    )

    saldo_fim_declarado_erp = Decimal(str(erp_footer.get("saldo_final", str(saldo_ini_erp + tot_entradas_erp + tot_saidas_erp))))
    saldo_fim_banco = (
        Decimal(str(bank_records[-1].saldo))
        if bank_records and bank_records[-1].saldo is not None
        else (saldo_ini_banco + tot_entradas_banco + tot_saidas_banco)
    )
    saldo_fim_calculado = saldo_ini_banco + tot_entradas_banco + tot_saidas_banco

    total_linhas = len(erp_records) + len(bank_records)
    total_conciliadas = (
        (len(matched_1_1) * 2)
        + sum(1 + len(grp.erp_itens) for grp in matched_batch)
    )
    percentual = round((total_conciliadas / total_linhas * 100.0), 1) if total_linhas > 0 else 100.0

    saldo_inicial_confere = (saldo_ini_erp == saldo_ini_banco)
    saldo_final_confere = (saldo_fim_declarado_erp == saldo_fim_banco) and (len(divergencias) == 0)

    balanco_fechado = (
        saldo_final_confere
        and len(divergencias) == 0
        and len(pendencias_sistema) == 0
    )

    if balanco_fechado:
        status_geral = "BALANCO_FECHADO"
        status_mensagem = "Todos os lançamentos foram conciliados com sucesso. Saldos conferem."
    else:
        status_geral = "DIVERGENCIA_ENCONTRADA"
        razoes = []
        if len(divergencias) > 0:
            razoes.append(f"{len(divergencias)} divergência(s) de valores")
        if len(pendencias_sistema) > 0:
            razoes.append(f"{len(pendencias_sistema)} pendência(s) em aberto no ERP")
        if len(exclusivos_banco) > 0:
            razoes.append(f"{len(exclusivos_banco)} lançamento(s) exclusivos do banco (tarifas/rendimentos)")
        if not saldo_final_confere:
            razoes.append("diferença entre saldos finais")
        status_mensagem = "Atenção: " + ", ".join(razoes) + "."

    dashboard = DashboardResumo(
        saldo_inicial_sistema=f"{saldo_ini_erp:.2f}",
        saldo_inicial_banco=f"{saldo_ini_banco:.2f}",
        saldo_inicial_confere=saldo_inicial_confere,
        total_entradas_sistema=f"{tot_entradas_erp:.2f}",
        total_saidas_sistema=f"{tot_saidas_erp:.2f}",
        total_entradas_banco=f"{tot_entradas_banco:.2f}",
        total_saidas_banco=f"{tot_saidas_banco:.2f}",
        saldo_final_sistema=f"{saldo_fim_declarado_erp:.2f}",
        saldo_final_banco=f"{saldo_fim_banco:.2f}",
        saldo_final_calculado=f"{saldo_fim_calculado:.2f}",
        saldo_final_declarado=f"{saldo_fim_declarado_erp:.2f}",
        saldo_final_confere=saldo_final_confere,
        percentual_conciliado=percentual,
        status_geral=status_geral,
        status_mensagem=status_mensagem,
        total_itens_erp=len(erp_records),
        total_itens_banco=len(bank_records),
        total_conciliados_1_1=len(matched_1_1),
        total_agrupados_lote=len(matched_batch),
        total_pendencias_erp=len(pendencias_sistema),
        total_exclusivos_banco=len(exclusivos_banco),
        total_divergencias=len(divergencias),
    )

    return ReconciliationResponse(
        dashboard=dashboard,
        conciliados_1_1=matched_1_1,
        conciliados_lote=matched_batch,
        pendencias_sistema=pendencias_sistema,
        exclusivos_banco=exclusivos_banco,
        divergencias_valor=divergencias,
        erp_header=erp_header,
        erp_footer=erp_footer,
    )
