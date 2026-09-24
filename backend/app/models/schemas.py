from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Lancamento(BaseModel):
    id: str
    data: str             # YYYY-MM-DD
    data_original: str    # ex: "01/04/26" ou "30/04/2026"
    descricao: str        # Favorecido ou Histórico (para leitura visual)
    valor: str            # String Decimal com sinal, ex: "-1050.00" ou "350000.00"
    tipo: str             # "D" ou "C"
    documento: Optional[str] = None
    saldo: Optional[str] = None
    categoria: Optional[str] = None # Para banco: TARIFA, IOF, RENDIMENTO, etc.

class ParConciliado(BaseModel):
    id: str
    erp_item: Lancamento
    banco_item: Lancamento
    diff_dias: int
    match_tipo: str       # "DATA_VALOR_EXATO" ou "DATA_VALOR_DOC"

class GrupoLote(BaseModel):
    id: str
    banco_item: Lancamento
    erp_itens: List[Lancamento]
    total_erp: str
    diff_valor: str       # "0.00"

class DivergenciaValor(BaseModel):
    id: str
    erp_item: Lancamento
    banco_item: Lancamento
    diff_valor: str
    diff_dias: int
    tipo: str             # "CENTAVOS" ou "DIVERGENCIA_VALOR"

class DashboardResumo(BaseModel):
    saldo_inicial_sistema: str
    saldo_inicial_banco: str
    saldo_inicial_confere: bool
    total_entradas_sistema: str
    total_saidas_sistema: str
    total_entradas_banco: str
    total_saidas_banco: str
    saldo_final_sistema: str
    saldo_final_banco: str
    saldo_final_calculado: str
    saldo_final_declarado: str
    saldo_final_confere: bool
    percentual_conciliado: float
    status_geral: str     # "BALANCO_FECHADO" ou "DIVERGENCIA_ENCONTRADA"
    status_mensagem: str
    total_itens_erp: int
    total_itens_banco: int
    total_conciliados_1_1: int
    total_agrupados_lote: int
    total_pendencias_erp: int
    total_exclusivos_banco: int
    total_divergencias: int

class ReconciliationResponse(BaseModel):
    dashboard: DashboardResumo
    conciliados_1_1: List[ParConciliado]
    conciliados_lote: List[GrupoLote]
    pendencias_sistema: List[Lancamento]
    exclusivos_banco: List[Lancamento]
    divergencias_valor: List[DivergenciaValor]
    erp_header: Dict[str, Any]
    erp_footer: Dict[str, Any]
