import io
import re
import uuid
from decimal import Decimal
from typing import List, Dict, Any, Tuple
import pdfplumber

from app.models.schemas import Lancamento
from app.engine.normalizer import parse_date, parse_brazilian_currency, detect_bank_category

def parse_santander_pdf(pdf_bytes: bytes) -> Tuple[List[Lancamento], Dict[str, Any]]:
    """
    Extrai do extrato bancário Santander em PDF primariamente DATA e VALOR,
    além do histórico descritivo.
    """
    records: List[Lancamento] = []
    meta_data: Dict[str, Any] = {
        "banco": "Banco Santander (Brasil) S.A.",
        "saldo_inicial": "0.00",
        "saldo_final": "0.00",
    }

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        all_text = ""
        raw_tables = []
        for page in pdf.pages:
            p_text = page.extract_text() or ""
            all_text += p_text + "\n"
            extracted = page.extract_tables()
            if extracted:
                raw_tables.extend(extracted)

        # Saldo Anterior
        m_saldo_ant = re.search(r'Saldo\s+(?:Anterior|Inicial)[:\-]?\s*(?:R\$\s*)?([\d\.,\-+]+)', all_text, re.IGNORECASE)
        if m_saldo_ant:
            val_dec, _ = parse_brazilian_currency(m_saldo_ant.group(1))
            meta_data["saldo_inicial"] = str(val_dec)

        table_rows_found = False
        for table in raw_tables:
            for row in table:
                if not row or len(row) < 3:
                    continue
                clean_row = [str(c).replace('\n', ' ').strip() if c else "" for c in row]
                
                dt = parse_date(clean_row[0])
                if not dt:
                    continue

                if "DATA" in clean_row[0].upper():
                    continue

                data_orig = clean_row[0]
                historico = clean_row[1] if len(clean_row) > 1 else ""
                documento = clean_row[2] if len(clean_row) > 2 else ""
                valor_str = clean_row[3] if len(clean_row) > 3 else ""
                saldo_str = clean_row[4] if len(clean_row) > 4 else None

                val_dec, op = parse_brazilian_currency(valor_str)
                s_dec_str = str(parse_brazilian_currency(saldo_str)[0]) if saldo_str else None
                cat = detect_bank_category(historico)

                records.append(
                    Lancamento(
                        id=f"SAN_{len(records)+1}_{str(uuid.uuid4())[:8]}",
                        data=dt.strftime("%Y-%m-%d"),
                        data_original=data_orig,
                        descricao=historico,
                        valor=str(val_dec),
                        tipo=op,
                        documento=documento,
                        saldo=s_dec_str,
                        categoria=cat,
                    )
                )
                table_rows_found = True

        # Fallback linha a linha com suporte a texto quebrado
        if not table_rows_found or len(records) == 0:
            lines = all_text.splitlines()
            current_dict = None

            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue

                m_date = re.match(r'^(\d{1,2}/\d{1,2}/\d{2,4})\b', line_str)
                if m_date:
                    if current_dict:
                        val_dec, op = parse_brazilian_currency(current_dict["valor_raw"])
                        s_dec_str = str(parse_brazilian_currency(current_dict["saldo_raw"])[0]) if current_dict.get("saldo_raw") else None
                        cat = detect_bank_category(current_dict["historico"])
                        records.append(
                            Lancamento(
                                id=f"SAN_{len(records)+1}_{str(uuid.uuid4())[:8]}",
                                data=current_dict["dt"].strftime("%Y-%m-%d"),
                                data_original=current_dict["data_orig"],
                                descricao=current_dict["historico"],
                                valor=str(val_dec),
                                tipo=op,
                                documento=current_dict["documento"],
                                saldo=s_dec_str,
                                categoria=cat,
                            )
                        )
                        current_dict = None

                    dt = parse_date(m_date.group(1))
                    if not dt:
                        continue

                    rest = line_str[len(m_date.group(0)):].strip()
                    money_matches = list(re.finditer(r'([+\-]?\s*[\d\.]+,\d{2})', rest))
                    if money_matches:
                        if len(money_matches) >= 2:
                            val_raw = money_matches[-2].group(1)
                            saldo_raw = money_matches[-1].group(1)
                            text_part = rest[:money_matches[-2].start()].strip()
                        else:
                            val_raw = money_matches[-1].group(1)
                            saldo_raw = None
                            text_part = rest[:money_matches[-1].start()].strip()

                        m_doc = re.search(r'\b(\d{4,12})\b', text_part)
                        doc_str = m_doc.group(1) if m_doc else ""
                        hist_str = text_part
                        if m_doc:
                            hist_str = text_part[:m_doc.start()] + text_part[m_doc.end():]
                            hist_str = re.sub(r'\s+', ' ', hist_str).strip()

                        current_dict = {
                            "dt": dt,
                            "data_orig": m_date.group(1),
                            "historico": hist_str,
                            "documento": doc_str,
                            "valor_raw": val_raw,
                            "saldo_raw": saldo_raw,
                        }
                elif current_dict is not None:
                    if not re.search(r'(folha|página|santander|ouvidoria|sac)\b', line_str, re.IGNORECASE):
                        current_dict["historico"] += " " + line_str

            if current_dict:
                val_dec, op = parse_brazilian_currency(current_dict["valor_raw"])
                s_dec_str = str(parse_brazilian_currency(current_dict["saldo_raw"])[0]) if current_dict.get("saldo_raw") else None
                cat = detect_bank_category(current_dict["historico"])
                records.append(
                    Lancamento(
                        id=f"SAN_{len(records)+1}_{str(uuid.uuid4())[:8]}",
                        data=current_dict["dt"].strftime("%Y-%m-%d"),
                        data_original=current_dict["data_orig"],
                        descricao=current_dict["historico"],
                        valor=str(val_dec),
                        tipo=op,
                        documento=current_dict["documento"],
                        saldo=s_dec_str,
                        categoria=cat,
                    )
                )

    if records and records[-1].saldo is not None:
        meta_data["saldo_final"] = records[-1].saldo

    return records, meta_data
