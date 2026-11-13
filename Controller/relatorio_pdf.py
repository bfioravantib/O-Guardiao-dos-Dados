"""Relatórios em PDF (estatísticas por pergunta, registro de jornadas e avaliações do quiz), com gráficos."""
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from Model.config import NOTA_MAXIMA
from Model.repositorio import agora, percentual_acerto

NOME_APP = 'O Guardião dos Dados'
LARGURA_UTIL = A4[0] - 4 * cm

AZUL = colors.HexColor('#1e526b')
AZUL_ESCURO = colors.HexColor('#102e3f')
VERDE = colors.HexColor('#216e43')
VERMELHO = colors.HexColor('#b43428')
BORDA = colors.HexColor('#ded3bc')
FUNDO_CABECALHO = colors.HexColor('#f3ede0')
SUAVE = colors.HexColor('#5a6770')
CINZA = colors.HexColor('#d9d9d9')
OURO = colors.HexColor('#c89223')
CINZA_ANONIMO = colors.HexColor('#8a9aa3')

_base = getSampleStyleSheet()
ESTILO_TITULO = ParagraphStyle('titulo', parent=_base['Title'], textColor=AZUL_ESCURO, fontSize=20, spaceAfter=4)
ESTILO_SUBTITULO = ParagraphStyle('subtitulo', parent=_base['Normal'], textColor=SUAVE, alignment=TA_CENTER, spaceAfter=14)
ESTILO_SECAO = ParagraphStyle('secao', parent=_base['Heading2'], textColor=AZUL_ESCURO, spaceBefore=12, spaceAfter=6)
ESTILO_ITEM = ParagraphStyle('item', parent=_base['Heading4'], textColor=AZUL, spaceBefore=0, spaceAfter=2)
ESTILO_TEXTO = ParagraphStyle('texto', parent=_base['Normal'], fontSize=9.5, leading=12.5)
ESTILO_NOTA = ParagraphStyle('nota', parent=ESTILO_TEXTO, textColor=SUAVE, fontSize=8.5)
ESTILO_CELULA = ParagraphStyle('celula', parent=ESTILO_TEXTO, fontSize=9, leading=11.5)


def _seguro(valor):
    """Troca caracteres que a fonte padrão (Helvetica) não desenha."""
    return str(valor).encode('cp1252', 'replace').decode('cp1252')


def _texto(valor):
    """Texto seguro e escapado para usar num Paragraph."""
    return escape(_seguro(valor))


def _encurtar(texto, largura, fonte='Helvetica', tamanho=9):
    """Corta o texto com reticências para caber na largura dada."""
    texto = _seguro(texto)
    if stringWidth(texto, fonte, tamanho) <= largura:
        return texto
    while texto and stringWidth(texto + '…', fonte, tamanho) > largura:
        texto = texto[:-1]
    return texto.rstrip() + '…'


def _rotulo_participante(participante):
    """Nome exibido no PDF (jornadas sem nome aparecem como 'Sem identificação')."""
    return participante['nome'] or 'Sem identificação'


def _barras_participantes(participantes, media_geral, por_bloco=18):
    """Gráfico de barras horizontais (média de cada participante), com linha tracejada na média geral.

    Divide em blocos de 'por_bloco' participantes para que cada desenho caiba numa página.
    """
    altura_linha = 0.62 * cm
    col_nome, col_valor, folga = 4.4 * cm, 1.4 * cm, 0.3 * cm
    x_trilho = col_nome + folga
    largura_trilho = LARGURA_UTIL - x_trilho - folga - col_valor
    desenhos = []
    for inicio in range(0, len(participantes), por_bloco):
        bloco = participantes[inicio:inicio + por_bloco]
        altura = len(bloco) * altura_linha + 0.5 * cm
        desenho = Drawing(LARGURA_UTIL, altura)
        for i, p in enumerate(bloco):
            y = altura - 0.5 * cm - (i + 1) * altura_linha
            meio = y + altura_linha / 2
            fonte = 'Helvetica-Oblique' if p['anonimo'] else 'Helvetica'
            desenho.add(String(0, meio - 3, _encurtar(_rotulo_participante(p), col_nome, fonte), fontName=fonte, fontSize=9))
            desenho.add(Rect(x_trilho, meio - 5, largura_trilho, 10, fillColor=FUNDO_CABECALHO, strokeColor=BORDA, strokeWidth=0.5))
            if p['media']:
                desenho.add(Rect(x_trilho, meio - 5, largura_trilho * p['media'] / 100, 10,
                                 fillColor=CINZA_ANONIMO if p['anonimo'] else AZUL, strokeColor=None))
            desenho.add(String(LARGURA_UTIL, meio - 3, f"{p['media']}%", textAnchor='end', fontName='Helvetica-Bold', fontSize=9))
        if media_geral is not None:
            x = x_trilho + largura_trilho * media_geral / 100
            desenho.add(Line(x, 0, x, altura - 0.45 * cm, strokeColor=OURO, strokeWidth=1.2, strokeDashArray=[3, 2]))
            desenho.add(String(x, altura - 0.35 * cm, f'média geral {media_geral}%', textAnchor='middle',
                               fontName='Helvetica', fontSize=7.5, fillColor=OURO))
        desenhos.append(desenho)
    return desenhos


def _percentual(taxa):
    return '–' if taxa is None else f'{taxa}%'


def _pizza(acertos, erros, diametro=4 * cm):
    """Gráfico de pizza acertos x erros (verde e vermelho), ou um círculo cinza quando não há respostas."""
    desenho = Drawing(diametro, diametro)
    raio = diametro / 2
    if not acertos + erros:
        desenho.add(Circle(raio, raio, raio, fillColor=CINZA, strokeColor=None))
        desenho.add(String(raio, raio - 3, 'Sem respostas', textAnchor='middle', fontName='Helvetica', fontSize=8, fillColor=SUAVE))
        return desenho

    fatias = [(valor, cor) for valor, cor in ((acertos, VERDE), (erros, VERMELHO)) if valor]
    pizza = Pie()
    pizza.x = pizza.y = 0
    pizza.width = pizza.height = diametro
    pizza.data = [valor for valor, _ in fatias]
    pizza.labels = None
    pizza.startAngle = 90
    pizza.direction = 'clockwise'
    pizza.slices.strokeColor = colors.white
    pizza.slices.strokeWidth = 1
    for i, (_, cor) in enumerate(fatias):
        pizza.slices[i].fillColor = cor
    desenho.add(pizza)
    return desenho


def _legenda(acertos, erros):
    """Tabela pequena com a cor, o rótulo, a quantidade e o percentual de acertos e erros."""
    total = acertos + erros
    pct_acertos = percentual_acerto(acertos, total)
    pct_erros = 100 - pct_acertos if total else None
    tabela = Table(
        [['', 'Acertos', str(acertos), _percentual(pct_acertos)],
         ['', 'Erros', str(erros), _percentual(pct_erros)],
         ['', 'Total', str(total), '']],
        colWidths=[0.35 * cm, 1.8 * cm, 1.2 * cm, 1.3 * cm],
    )
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), VERDE),
        ('BACKGROUND', (0, 1), (0, 1), VERMELHO),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('LINEABOVE', (1, 2), (-1, 2), 0.5, BORDA),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return tabela


def _bloco_grafico(acertos, erros, conteudo_ao_lado, diametro=4 * cm):
    """Pizza à esquerda e, à direita, os flowables de conteudo_ao_lado (texto, legenda...)."""
    coluna_pizza = diametro + 0.8 * cm
    bloco = Table([[_pizza(acertos, erros, diametro), conteudo_ao_lado]],
                  colWidths=[coluna_pizza, LARGURA_UTIL - coluna_pizza])
    bloco.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return bloco


def _tabela_dados(cabecalho, linhas, larguras, colunas_numericas):
    tabela = Table([cabecalho] + linhas, colWidths=larguras, repeatRows=1)
    estilo = [
        ('BACKGROUND', (0, 0), (-1, 0), FUNDO_CABECALHO),
        ('TEXTCOLOR', (0, 0), (-1, 0), AZUL_ESCURO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDA),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    for coluna in colunas_numericas:
        estilo.append(('ALIGN', (coluna, 0), (coluna, -1), 'RIGHT'))
    tabela.setStyle(TableStyle(estilo))
    return tabela


def _rodape(canvas, documento):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(SUAVE)
    canvas.drawString(documento.leftMargin, 1.2 * cm, f'{NOME_APP} · {documento.title}')
    canvas.drawRightString(A4[0] - documento.rightMargin, 1.2 * cm, f'Página {documento.page}')
    canvas.restoreState()


def _gerar(titulo, elementos):
    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer, pagesize=A4, title=titulo, author=NOME_APP,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
    )
    cabecalho = [
        Paragraph(_texto(NOME_APP), ESTILO_TITULO),
        Paragraph(f'{_texto(titulo)} · gerado em {agora():%d/%m/%Y %H:%M}', ESTILO_SUBTITULO),
    ]
    documento.build(cabecalho + elementos, onFirstPage=_rodape, onLaterPages=_rodape)
    return buffer.getvalue()


def _resumo_geral(resumo, linhas_extras=()):
    """Bloco "Visão geral": pizza com o total de acertos x erros e os números principais."""
    linhas = [['Jornadas concluídas', str(resumo['partidas'])],
              ['Respostas registradas', str(resumo['respostas'])],
              *linhas_extras,
              ['Taxa de acerto geral', _percentual(resumo['taxa'])]]
    numeros = Table(linhas, colWidths=[4.6 * cm, 2 * cm])
    numeros.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDA),
    ]))
    return [
        Paragraph('Visão geral', ESTILO_SECAO),
        _bloco_grafico(resumo['acertos'], resumo['erros'], [numeros, Spacer(1, 6), _legenda(resumo['acertos'], resumo['erros'])], 4.5 * cm),
    ]


def relatorio_estatisticas(resumo, estatisticas, filtrado):
    """PDF de acerto por pergunta. 'estatisticas' já vem filtrada pelas perguntas escolhidas na tela."""
    elementos = _resumo_geral(resumo)

    elementos.append(Paragraph('Acerto por pergunta', ESTILO_SECAO))
    if filtrado:
        elementos.append(Paragraph(f'Relatório com {len(estatisticas)} pergunta(s) selecionada(s).', ESTILO_NOTA))
        elementos.append(Spacer(1, 4))
    linhas = [
        [str(e['numero']),
         Paragraph(_texto(e['enunciado']) + (' <i>(excluída)</i>' if e['excluida'] else ''), ESTILO_CELULA),
         str(e['respostas']), str(e['acertos']), str(e['erros']), _percentual(e['taxa'])]
        for e in estatisticas
    ]
    elementos.append(_tabela_dados(
        ['#', 'Pergunta', 'Respostas', 'Acertos', 'Erros', 'Taxa'], linhas,
        [0.8 * cm, 8.6 * cm, 1.9 * cm, 1.6 * cm, 1.4 * cm, 1.3 * cm], colunas_numericas=(2, 3, 4, 5),
    ))

    elementos.append(Paragraph('Gráficos por pergunta', ESTILO_SECAO))
    for e in estatisticas:
        texto = [
            Paragraph(f'Pergunta {e["numero"]}' + (' (excluída)' if e['excluida'] else ''), ESTILO_ITEM),
            Paragraph(_texto(e['enunciado']), ESTILO_TEXTO),
            Spacer(1, 6),
            _legenda(e['acertos'], e['erros']),
        ]
        elementos.append(KeepTogether([_bloco_grafico(e['acertos'], e['erros'], texto, 3.6 * cm), Spacer(1, 10)]))
    return _gerar('Estatísticas de acerto por pergunta', elementos)


def relatorio_jornadas(resumo, partidas, participantes):
    """PDF do registro de acertos de cada conclusão do questionário."""
    taxas = [p['taxa'] for p in partidas if p['taxa'] is not None]
    media_geral = percentual_acerto(sum(taxas), len(taxas) * 100) if taxas else None
    extras = []
    if taxas:
        extras = [['Média de aproveitamento', f'{media_geral}%'],
                  ['Melhor resultado', f'{max(taxas)}%']]
    elementos = _resumo_geral(resumo, extras)

    if participantes:
        elementos.append(Paragraph('Média por participante', ESTILO_SECAO))
        elementos.append(Paragraph('Média de aproveitamento das jornadas de cada participante. '
                                   'A linha tracejada marca a média geral.', ESTILO_NOTA))
        elementos.append(Spacer(1, 6))
        elementos.extend(_barras_participantes(participantes, media_geral))
        elementos.append(Spacer(1, 8))
        linhas = [
            [Paragraph(('<i>%s</i>' if p['anonimo'] else '%s') % _texto(_rotulo_participante(p)), ESTILO_CELULA),
             str(p['jornadas']), f"{p['media_acertos']:.1f}".replace('.', ','), f"{p['media']}%"]
            for p in participantes
        ]
        elementos.append(_tabela_dados(
            ['Participante', 'Jornadas', 'Acertos por jornada', 'Aproveitamento médio'], linhas,
            [7 * cm, 2.2 * cm, 3.6 * cm, 4.2 * cm], colunas_numericas=(1, 2, 3),
        ))

    elementos.append(Paragraph('Registro de jornadas', ESTILO_SECAO))
    if partidas:
        linhas = [
            [str(p['numero']),
             Paragraph(_texto(p['participante']) if p['participante'] else '<i>Sem identificação</i>', ESTILO_CELULA),
             p['data'].strftime('%d/%m/%Y %H:%M'), str(p['acertos']), str(p['erros']), str(p['total']),
             _percentual(p['taxa'])]
            for p in partidas
        ]
        elementos.append(_tabela_dados(
            ['#', 'Participante', 'Data', 'Acertos', 'Erros', 'Total', 'Aprov.'], linhas,
            [1 * cm, 5.2 * cm, 3.2 * cm, 1.8 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm], colunas_numericas=(3, 4, 5, 6),
        ))
    else:
        elementos.append(Paragraph('Nenhuma jornada registrada ainda.', ESTILO_NOTA))
    return _gerar('Registro de jornadas', elementos)


def _media_nota(media):
    return '–' if media is None else f'{media:.1f}'.replace('.', ',')


def _grafico_notas(criterio):
    """Colunas com quantas avaliações deram cada nota (1 a NOTA_MAXIMA), como na aba Avaliações."""
    largura, altura = LARGURA_UTIL, 4.6 * cm
    base, topo = 1.1 * cm, altura - 0.9 * cm
    passo = largura / NOTA_MAXIMA
    desenho = Drawing(largura, altura)
    desenho.add(String(0, altura - 0.45 * cm, _seguro(criterio['titulo']), fontName='Helvetica-Bold', fontSize=10,
                       fillColor=AZUL_ESCURO))
    desenho.add(String(largura, altura - 0.45 * cm, f"média {_media_nota(criterio['media'])}", textAnchor='end',
                       fontName='Helvetica-Bold', fontSize=10, fillColor=AZUL))
    maior = criterio['maior_contagem']
    for i, qtd in enumerate(criterio['distribuicao']):
        x = i * passo + passo * 0.15
        largura_coluna = passo * 0.7
        altura_coluna = (topo - base - 0.35 * cm) * qtd / maior if maior else 0
        if qtd:
            desenho.add(Rect(x, base, largura_coluna, altura_coluna, fillColor=AZUL, strokeColor=None))
            desenho.add(String(x + largura_coluna / 2, base + altura_coluna + 2, str(qtd), textAnchor='middle',
                               fontName='Helvetica', fontSize=8, fillColor=SUAVE))
        desenho.add(String(x + largura_coluna / 2, base - 0.4 * cm, str(i + 1), textAnchor='middle',
                           fontName='Helvetica-Bold', fontSize=8.5, fillColor=SUAVE))
    desenho.add(Line(0, base, largura, base, strokeColor=BORDA, strokeWidth=1))
    desenho.add(String(0, 0.05 * cm, _seguro(f"1 = {criterio['minimo']}"), fontName='Helvetica', fontSize=7.5, fillColor=SUAVE))
    desenho.add(String(largura, 0.05 * cm, _seguro(f"{NOTA_MAXIMA} = {criterio['maximo']}"), textAnchor='end',
                       fontName='Helvetica', fontSize=7.5, fillColor=SUAVE))
    return desenho


def relatorio_avaliacoes(avaliacoes, criterios, jornadas, taxa_resposta, com_comentario):
    """PDF da validação: médias e distribuição das notas de cada critério e todas as sugestões escritas."""
    numeros = Table(
        [['Avaliações recebidas', str(len(avaliacoes))],
         ['Jornadas concluídas', str(jornadas)],
         ['Jornadas avaliadas', _percentual(taxa_resposta)],
         ['Avaliações com sugestão escrita', str(com_comentario)]],
        colWidths=[6 * cm, 2.4 * cm],
    )
    numeros.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDA),
    ]))
    elementos = [Paragraph('Visão geral', ESTILO_SECAO), numeros, Spacer(1, 10)]
    elementos.append(_tabela_dados(
        ['Pergunta da avaliação', f'Média (1 a {NOTA_MAXIMA})'],
        [[Paragraph(_texto(c['pergunta']), ESTILO_CELULA), _media_nota(c['media'])] for c in criterios],
        [13 * cm, 4 * cm], colunas_numericas=(1,),
    ))

    elementos.append(Paragraph('Distribuição das notas', ESTILO_SECAO))
    elementos.append(Paragraph('Cada coluna mostra quantas pessoas deram aquela nota.', ESTILO_NOTA))
    elementos.append(Spacer(1, 6))
    for criterio in criterios:
        elementos.append(KeepTogether([_grafico_notas(criterio), Spacer(1, 12)]))

    elementos.append(Paragraph('Avaliações e sugestões', ESTILO_SECAO))
    if avaliacoes:
        linhas = [
            [Paragraph(_texto(a['participante']) if a['participante'] else '<i>Sem identificação</i>', ESTILO_CELULA),
             a['data'].strftime('%d/%m/%Y %H:%M'),
             *(str(a[c['chave']]) for c in criterios),
             Paragraph(_texto(a['comentario']).replace('\n', '<br/>') if a['comentario'] else '<i>—</i>', ESTILO_CELULA)]
            for a in avaliacoes
        ]
        elementos.append(_tabela_dados(
            ['Jogador', 'Data', *(c['curto'] for c in criterios), 'Sugestão'], linhas,
            [2.4 * cm, 2.8 * cm, 2 * cm, 1.2 * cm, 1.9 * cm, 6.7 * cm], colunas_numericas=(2, 3, 4),
        ))
    else:
        elementos.append(Paragraph('Nenhuma avaliação recebida ainda.', ESTILO_NOTA))
    return _gerar('Avaliações do quiz', elementos)
