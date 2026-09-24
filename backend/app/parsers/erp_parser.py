import io
import re
import uuid
from decimal import Decimal
from typing import List, Dict, Any, Tuple
import pdfplumber

from app.models.schemas import Lancamento
from app.engine.normalizer import parse_date, parse_brazilian_currency

def parse_erp_pdf(pdf_bytes: bytes) -> Tuple[List[Lancamento], Dict[str, Any], Dict[str, Any]]:
    """
    Extrai do extrato do ERP (SISTEMA.pdf) primariamente DATA e VALOR,
    além da descrição para identificação visual.
    """
    records: List[Lancamento] = []
    header_data: Dict[str, Any] = {
        "conta": "",
        "centro_custo": "",
        "saldo_anterior": "0.00",
        "periodo": "",
        "data_inicial": "",
        "data_final": "",
    }
    footer_data: Dict[str, Any] = {
        "saldo_inicial": "0.00",
        "total_entradas": "0.00",
        "total_saidas": "0.00",
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

        # Cabeçalho
        m_conta = re.search(r'Conta\s*(?:Corrente)?[:\-]?\s*([0-9A-Za-z\.\-\/]+)', all_text, re.IGNORECASE)
        if m_conta:
            header_data["conta"] = m_conta.group(1).strip()

        m_cc = re.search(r'Centro\s*(?:de)?\s*Custo[:\-]?\s*([^\n\r]+)', all_text, re.IGNORECASE)
        if m_cc:
            header_data["centro_custo"] = m_cc.group(1).split("Saldo")[0].split("Período")[0].strip()

        m_saldo_ant = re.search(r'Saldo\s+Anterior[:\-]?\s*(?:R\$\s*)?([\d\.,]+\s*[CD]?)', all_text, re.IGNORECASE)
        if m_saldo_ant:
            val_dec, _ = parse_brazilian_currency(m_saldo_ant.group(1))
            header_data["saldo_anterior"] = str(val_dec)

        m_periodo = re.search(r'Per[ií]odo[:\-]?\s*(\d{2}/\d{2}/\d{2,4})\s*(?:a|at[eé]|-)\s*(\d{2}/\d{2}/\d{2,4})', all_text, re.IGNORECASE)
        if m_periodo:
            header_data["data_inicial"] = m_periodo.group(1)
            header_data["data_final"] = m_periodo.group(2)
            header_data["periodo"] = f"{m_periodo.group(1)} a {m_periodo.group(2)}"

        # Rodapé
        m_saldo_ini = re.search(r'Saldo\s+Inicial[:\-]?\s*(?:R\$\s*)?([\d\.,]+\s*[CD]?)', all_text, re.IGNORECASE)
        if m_saldo_ini:
            val_dec, _ = parse_brazilian_currency(m_saldo_ini.group(1))
            footer_data["saldo_inicial"] = str(val_dec)
        elif header_data["saldo_anterior"] != "0.00":
            footer_data["saldo_inicial"] = header_data["saldo_anterior"]

        m_entradas = re.search(r'Total\s+(?:de\s+)?Entradas[:\-]?\s*(?:R\$\s*)?([\d\.,]+\s*[CD]?)', all_text, re.IGNORECASE)
        if m_entradas:
            val_dec, _ = parse_brazilian_currency(m_entradas.group(1))
            footer_data["total_entradas"] = str(abs(val_dec))

        m_saidas = re.search(r'Total\s+(?:de\s+)?Sa[ií]das[:\-]?\s*(?:R\$\s*)?([\d\.,]+\s*[CD]?)', all_text, re.IGNORECASE)
        if m_saidas:
            val_dec, _ = parse_brazilian_currency(m_saidas.group(1))
            footer_data["total_saidas"] = str(-abs(val_dec))

        m_saldo_fim = re.search(r'Saldo\s+Final[:\-]?\s*(?:R\$\s*)?([\d\.,]+\s*[CD]?)', all_text, re.IGNORECASE)
        if m_saldo_fim:
            val_dec, _ = parse_brazilian_currency(m_saldo_fim.group(1))
            footer_data["saldo_final"] = str(val_dec)

        # Parsing de Tabelas
        table_rows_found = False
        for table in raw_tables:
            for row in table:
                if not row or len(row) < 3:
                    continue
                clean_row = [str(c).replace('\n', ' ').strip() if c else "" for c in row]
                
                # Procura data
                dt = parse_date(clean_row[0])
                if not dt:
                    continue

                if "DATA" in clean_row[0].upper():
                    continue

                data_orig = clean_row[0]
                descricao = clean_row[1] if len(clean_row) > 1 else "Lançamento ERP"
                doc = clean_row[4] if len(clean_row) > 4 else None

                # Procura coluna de valor com D ou C
                valor_str = ""
                saldo_str = None
                for c in reversed(clean_row):
                    if re.search(r'[\d\.,]+\s*[CD]', c, re.IGNORECASE):
                        if not valor_str:
                            valor_str = c
                        elif saldo_str is None:
                            saldo_str = valor_str
                            valor_str = c

                if not valor_str and len(clean_row) >= 4:
                    valor_str = clean_row[-2] if len(clean_row) >= 5 else clean_row[-1]

                val_dec, op = parse_brazilian_currency(valor_str)
                s_dec_str = str(parse_brazilian_currency(saldo_str)[0]) if saldo_str else None

                records.append(
                    Lancamento(
                        id=f"ERP_{len(records)+1}_{str(uuid.uuid4())[:8]}",
                        data=dt.strftime("%Y-%m-%d"),
                        data_original=data_orig,
                        descricao=descricao,
                        valor=str(val_dec),
                        tipo=op,
                        documento=doc,
                        saldo=s_dec_str,
                    )
                )
                table_rows_found = True

        # Fallback linha a linha se necessário
        if not table_rows_found or len(records) == 0:
            lines = all_text.splitlines()
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue
                m_date = re.match(r'^(\d{1,2}/\d{1,2}/\d{2,4})\b', line_str)
                if m_date:
                    dt = parse_date(m_date.group(1))
                    if dt:
                        m_vals = re.findall(r'([\d\.,]+\s*[CD])', line_str, re.IGNORECASE)
                        if m_vals:
                            val_dec, op = parse_brazilian_currency(m_vals[0])
                            saldo_dec = str(parse_brazilian_currency(m_vals[1])[0]) if len(m_vals) > 1 else None
                            
                            middle = line_str[len(m_date.group(0)):].strip()
                            for v in m_vals:
                                middle = middle.replace(v, "")
                            middle = re.sub(r'\s+', ' ', middle).strip()

                            records.append(
                                Lancamento(
                                    id=f"ERP_{len(records)+1}_{str(uuid.uuid4())[:8]}",
                                    data=dt.strftime("%Y-%m-%d"),
                                    data_original=m_date.group(1),
                                    descricao=middle or "Lançamento ERP",
                                    valor=str(val_dec),
                                    tipo=op,
                                    saldo=saldo_dec,
                                )
                            )

    return records, header_data, footer_data
