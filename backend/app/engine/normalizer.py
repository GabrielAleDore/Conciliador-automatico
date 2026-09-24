import re
import unicodedata
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple

def strip_accents(text: str) -> str:
    """Remove acentos e caracteres diacríticos."""
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def parse_date(date_str: str) -> Optional[date]:
    """
    Converte datas de formatos comuns (DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD) para date.
    Exemplo: '01/04/26' -> date(2026, 4, 1), '30/04/2026' -> date(2026, 4, 30).
    """
    if not date_str:
        return None
    cleaned = date_str.strip()
    
    patterns = [
        ("%d/%m/%Y", False),
        ("%d/%m/%y", True),
        ("%Y-%m-%d", False),
        ("%d-%m-%Y", False),
        ("%d-%m-%y", True),
    ]
    
    for fmt, is_2digit in patterns:
        try:
            dt = datetime.strptime(cleaned, fmt).date()
            if is_2digit and dt.year < 2000:
                dt = dt.replace(year=dt.year + 100)
            return dt
        except ValueError:
            continue
            
    match = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})', cleaned)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if year < 100:
            year += 2000
        try:
            return date(year, month, day)
        except ValueError:
            pass

    return None

def parse_brazilian_currency(val_str: str) -> Tuple[Decimal, str]:
    """
    Converte strings monetárias brasileiras para Decimal com sinal.
    Suporta:
      - '1.050,00 D' -> Decimal('-1050.00'), 'D'
      - '350.000,00 C' -> Decimal('350000.00'), 'C'
      - '-502,00' -> Decimal('-502.00'), 'D'
      - '9.000,00' -> Decimal('9000.00'), 'C'
    """
    if not val_str:
        return Decimal("0.00"), "C"

    s = val_str.strip().upper()
    is_debit = False
    
    # Checa indicador 'D' ou 'C' no final ou início
    if s.endswith("D") or s.startswith("D"):
        is_debit = True
        s = s.replace("D", "").strip()
    elif s.endswith("C") or s.startswith("C"):
        is_debit = False
        s = s.replace("C", "").strip()
    elif "-" in s:
        is_debit = True
        s = s.replace("-", "").strip()
    elif "+" in s:
        is_debit = False
        s = s.replace("+", "").strip()

    # Limpeza de caracteres não numéricos exceto '.' e ','
    s = re.sub(r'[^\d,\.]', '', s)
    if not s:
        return Decimal("0.00"), "C"

    # Formato brasileiro: 1.234.567,89 -> remove pontos de milhar e troca vírgula por ponto
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")

    try:
        dec = Decimal(s)
        if is_debit:
            dec = -abs(dec)
            tipo = "D"
        else:
            dec = abs(dec)
            tipo = "C"
        return dec.quantize(Decimal("0.01")), tipo
    except InvalidOperation:
        return Decimal("0.00"), "C"

BANK_CATEGORY_PATTERNS = [
    (r'\b(TARIFA|TAR\b|CESTA|PACOTE DE SERVICOS|MANUTENCAO DE CONTA)\b', "TARIFA"),
    (r'\b(IOF|IMP OPER FINANC)\b', "IOF"),
    (r'\b(JUROS|ENCARGOS|CHEQUE ESPECIAL|LIMITE DE CREDITO)\b', "JUROS"),
    (r'\b(REMUNERACAO APLIC|RENDIMENTO|RESGATE APLIC|APLICACAO AUTOMATICA|APLIC AUT)\b', "RENDIMENTO"),
    (r'\b(ESTORNO|DEVOLUCAO)\b', "ESTORNO"),
    (r'\b(BOLETO|PAGAMENTO DE BOLETO|TITULO|COBRANCA)\b', "BOLETO"),
    (r'\b(PIX)\b', "PIX"),
    (r'\b(TED|DOC|TRANSFERENCIA)\b', "TRANSFERENCIA"),
]

def detect_bank_category(hist: str) -> Optional[str]:
    """Identifica se o lançamento bancário é uma categoria específica (Tarifa, IOF, etc)."""
    if not hist:
        return None
    raw_clean = strip_accents(hist).upper().strip()
    for pattern, cat in BANK_CATEGORY_PATTERNS:
        if re.search(pattern, raw_clean, re.IGNORECASE):
            return cat
    return None
