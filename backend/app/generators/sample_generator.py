import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_sample_erp_pdf() -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )
    styles = getSampleStyleSheet()

    style_meta = ParagraphStyle(
        'HeaderMeta',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155'),
    )
    style_cell = ParagraphStyle(
        'Cell',
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#0F172A'),
    )
    style_cell_bold = ParagraphStyle(
        'CellBold',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#0F172A'),
    )

    elements = []

    header_html = """
    <b>SISTEMA ERP - EXTRATO DE MOVIMENTAÇÃO CONTÁBIL</b><br/>
    Conta: 0001-998877-6 &nbsp;&nbsp;|&nbsp;&nbsp; Centro de Custo: MATRIZ OPERACIONAL - SP &nbsp;&nbsp;|&nbsp;&nbsp; Saldo Anterior: 50.000,00 C<br/>
    Período: 01/04/2026 a 30/04/2026 &nbsp;&nbsp;|&nbsp;&nbsp; Data Inicial: 01/04/2026 &nbsp;&nbsp;|&nbsp;&nbsp; Data Final: 30/04/2026
    """
    elements.append(Paragraph(header_html, style_meta))
    elements.append(Spacer(1, 10))

    table_data = [
        [
            Paragraph("<b>Data Lcto</b>", style_cell_bold),
            Paragraph("<b>Favorecido / Razão Social</b>", style_cell_bold),
            Paragraph("<b>Tipo Doc.</b>", style_cell_bold),
            Paragraph("<b>Forma Pagto</b>", style_cell_bold),
            Paragraph("<b>Num. Doc.</b>", style_cell_bold),
            Paragraph("<b>Num. Pag.</b>", style_cell_bold),
            Paragraph("<b>Emissão</b>", style_cell_bold),
            Paragraph("<b>Valor</b>", style_cell_bold),
            Paragraph("<b>Saldo</b>", style_cell_bold),
        ],
        [Paragraph("02/04/26", style_cell), Paragraph("MAX HIDRAULICA LTDA", style_cell), Paragraph("NOTA FISCAL", style_cell), Paragraph("BOLETO", style_cell), Paragraph("882190", style_cell), Paragraph("101", style_cell), Paragraph("28/03/26", style_cell), Paragraph("502,00 D", style_cell), Paragraph("49.498,00 C", style_cell)],
        [Paragraph("05/04/26", style_cell), Paragraph("CLIENTE GLOBAL ATACADISTA S/A", style_cell), Paragraph("FATURA", style_cell), Paragraph("PIX/DEPOSITO", style_cell), Paragraph("445901", style_cell), Paragraph("102", style_cell), Paragraph("05/04/26", style_cell), Paragraph("350.000,00 C", style_cell), Paragraph("399.498,00 C", style_cell)],
        [Paragraph("08/04/26", style_cell), Paragraph("CONSULTORIA TECH SOLUTIONS", style_cell), Paragraph("CONTRATO", style_cell), Paragraph("TED", style_cell), Paragraph("120934", style_cell), Paragraph("103", style_cell), Paragraph("08/04/26", style_cell), Paragraph("12.450,00 D", style_cell), Paragraph("387.048,00 C", style_cell)],
        # Lote 1:N quitado em 1 Pix no banco de R$ 1.500,00
        [Paragraph("14/04/26", style_cell), Paragraph("DISTRIBUIDORA DE ALIMENTOS ABC", style_cell), Paragraph("NOTA FISCAL", style_cell), Paragraph("PIX/DEPOSITO", style_cell), Paragraph("554101", style_cell), Paragraph("104", style_cell), Paragraph("10/04/26", style_cell), Paragraph("500,00 D", style_cell), Paragraph("386.548,00 C", style_cell)],
        [Paragraph("14/04/26", style_cell), Paragraph("DISTRIBUIDORA DE ALIMENTOS ABC", style_cell), Paragraph("NOTA FISCAL", style_cell), Paragraph("PIX/DEPOSITO", style_cell), Paragraph("554102", style_cell), Paragraph("105", style_cell), Paragraph("11/04/26", style_cell), Paragraph("700,00 D", style_cell), Paragraph("385.848,00 C", style_cell)],
        [Paragraph("14/04/26", style_cell), Paragraph("DISTRIBUIDORA DE ALIMENTOS ABC", style_cell), Paragraph("NOTA FISCAL", style_cell), Paragraph("PIX/DEPOSITO", style_cell), Paragraph("554103", style_cell), Paragraph("106", style_cell), Paragraph("12/04/26", style_cell), Paragraph("300,00 D", style_cell), Paragraph("385.548,00 C", style_cell)],
        # Compensado em D+4 (dentro da nova tolerância D+0 a D+5)
        [Paragraph("16/04/26", style_cell), Paragraph("SEGURADORA ALLIANZ PAULISTA", style_cell), Paragraph("APOLICE", style_cell), Paragraph("BOLETO", style_cell), Paragraph("991023", style_cell), Paragraph("107", style_cell), Paragraph("15/04/26", style_cell), Paragraph("2.840,00 D", style_cell), Paragraph("382.708,00 C", style_cell)],
        # Divergência de centavos/juros no banco
        [Paragraph("22/04/26", style_cell), Paragraph("PAPELARIA MODELO EIRELI", style_cell), Paragraph("NOTA FISCAL", style_cell), Paragraph("BOLETO", style_cell), Paragraph("771239", style_cell), Paragraph("108", style_cell), Paragraph("20/04/26", style_cell), Paragraph("320,00 D", style_cell), Paragraph("382.388,00 C", style_cell)],
        # Pendência no ERP (não compensado)
        [Paragraph("28/04/26", style_cell), Paragraph("FORNECEDOR ELETRICA CENTRAL", style_cell), Paragraph("NOTA FISCAL", style_cell), Paragraph("BOLETO", style_cell), Paragraph("332145", style_cell), Paragraph("109", style_cell), Paragraph("26/04/26", style_cell), Paragraph("850,00 D", style_cell), Paragraph("381.538,00 C", style_cell)],
    ]

    t = Table(table_data, colWidths=[55, 160, 75, 75, 55, 45, 55, 70, 75])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))

    footer_html = """
    <b>RESUMO E TOTALIZADORES DO PERÍODO:</b><br/>
    Saldo Inicial: 50.000,00 C &nbsp;&nbsp;|&nbsp;&nbsp; 
    Total de Entradas: 350.000,00 C &nbsp;&nbsp;|&nbsp;&nbsp; 
    Total de Saídas: 18.462,00 D &nbsp;&nbsp;|&nbsp;&nbsp; 
    Saldo Final: 381.538,00 C
    """
    elements.append(Paragraph(footer_html, style_meta))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_sample_santander_pdf() -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=25,
        rightMargin=25,
        topMargin=25,
        bottomMargin=25,
    )
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        'HeaderTitleSan',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#CC0000'),
    )
    style_meta = ParagraphStyle(
        'HeaderMetaSan',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#333333'),
    )
    style_cell = ParagraphStyle(
        'CellSan',
        fontName='Helvetica',
        fontSize=7,
        leading=10,
        textColor=colors.HexColor('#1E293B'),
    )
    style_cell_bold = ParagraphStyle(
        'CellBoldSan',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=10,
        textColor=colors.HexColor('#1E293B'),
    )

    elements = []
    elements.append(Paragraph("<b>Banco Santander (Brasil) S.A. - Extrato de Conta Corrente</b>", style_title))
    header_info = """
    Agência: 3344 &nbsp;&nbsp;|&nbsp;&nbsp; Conta Corrente: 0001-998877-6 &nbsp;&nbsp;|&nbsp;&nbsp; Correntista: EMPRESA MODELO LTDA<br/>
    Período: 01/04/2026 a 30/04/2026 &nbsp;&nbsp;|&nbsp;&nbsp; Saldo Inicial: 50.000,00
    """
    elements.append(Paragraph(header_info, style_meta))
    elements.append(Spacer(1, 12))

    table_data = [
        [
            Paragraph("<b>Data</b>", style_cell_bold),
            Paragraph("<b>Histórico</b>", style_cell_bold),
            Paragraph("<b>Documento</b>", style_cell_bold),
            Paragraph("<b>Valor (R$)</b>", style_cell_bold),
            Paragraph("<b>Saldo (R$)</b>", style_cell_bold),
        ],
        [Paragraph("02/04/2026", style_cell), Paragraph("Pagamento De Boleto Outros Bancos MAX HIDRAULICA LTDA", style_cell), Paragraph("000882190", style_cell), Paragraph("-502,00", style_cell), Paragraph("49.498,00", style_cell)],
        [Paragraph("05/04/2026", style_cell), Paragraph("Pix Recebido CLIENTE GLOBAL ATACADISTA S/A", style_cell), Paragraph("000445901", style_cell), Paragraph("350.000,00", style_cell), Paragraph("399.498,00", style_cell)],
        [Paragraph("08/04/2026", style_cell), Paragraph("Ted Enviada CONSULTORIA TECH SOLUTIONS LTDA", style_cell), Paragraph("000120934", style_cell), Paragraph("-12.450,00", style_cell), Paragraph("387.048,00", style_cell)],
        # Lote 1:N consolidado
        [Paragraph("14/04/2026", style_cell), Paragraph("Pix Enviado DISTRIBUIDORA DE ALIMENTOS ABC LTDA PAGTO LOTES FATURAS", style_cell), Paragraph("000994100", style_cell), Paragraph("-1.500,00", style_cell), Paragraph("385.548,00", style_cell)],
        # Exclusivos Santander
        [Paragraph("15/04/2026", style_cell), Paragraph("Tarifa Bancaria Cesta Servicos Mensal PJ", style_cell), Paragraph("000000", style_cell), Paragraph("-45,00", style_cell), Paragraph("385.503,00", style_cell)],
        [Paragraph("15/04/2026", style_cell), Paragraph("IOF Imposto Sobre Operacoes Financeiras", style_cell), Paragraph("000000", style_cell), Paragraph("-12,30", style_cell), Paragraph("385.490,70", style_cell)],
        # Compensado em D+4 (ERP foi 16/04, liquidado em 20/04 - D+4)
        [Paragraph("20/04/2026", style_cell), Paragraph("Pagamento De Boleto SEGURADORA ALLIANZ PAULISTA", style_cell), Paragraph("000991023", style_cell), Paragraph("-2.840,00", style_cell), Paragraph("382.650,70", style_cell)],
        # Divergência de valor (ERP = 320,00, Santander = -325,50)
        [Paragraph("22/04/2026", style_cell), Paragraph("Pagamento De Boleto Outros Bancos PAPELARIA MODELO", style_cell), Paragraph("000771239", style_cell), Paragraph("-325,50", style_cell), Paragraph("382.325,20", style_cell)],
        # Rendimento aplicação CDB
        [Paragraph("30/04/2026", style_cell), Paragraph("Remuneracao Aplicacao Automatica CDB DI Santander", style_cell), Paragraph("000000", style_cell), Paragraph("189,45", style_cell), Paragraph("382.514,65", style_cell)],
    ]

    t = Table(table_data, colWidths=[65, 260, 65, 75, 75])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
