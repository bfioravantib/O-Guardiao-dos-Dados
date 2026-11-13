"""Gera a apresentação do projeto em PDF (slides 16:9 com a identidade visual do jogo) e o roteiro de fala.

Uso (na raiz do projeto ou de qualquer pasta):
    python -m pip install segno           # só na primeira vez (QR Code do slide final; sem ele o QR é omitido)
    python docs/gerar_apresentacao_pdf.py

Saídas:
    docs/Apresentação - O Guardião dos Dados.pdf   (14 slides, cerca de 10 minutos)
    docs/Roteiro da apresentação.pdf               (o que falar em cada slide, com o tempo sugerido)

Os textos, números e fontes ficam na lista SLIDES abaixo. O link do app fica em LINK_APP.
Como no manual, o Microsoft Edge ou o Google Chrome "imprime" as páginas em PDF (precisa de internet para as fontes).
"""
import shutil
import sys
import tempfile
from html import escape
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_manual_pdf import imprimir_pdf

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DOCS = RAIZ / 'docs'
SAIDA_SLIDES = PASTA_DOCS / 'Apresentação - O Guardião dos Dados.pdf'
SAIDA_ROTEIRO = PASTA_DOCS / 'Roteiro da apresentação.pdf'

LINK_APP = 'https://o-guardiao-dos-dados.vercel.app/'
AUTOR = 'Bruno Fioravanti Barbosa'
CURSO = 'CST em Redes de Computadores · UNINTER'
DISCIPLINA = 'Atividade Extensionista II: Tecnologia Aplicada à Inclusão Digital — Projeto'


def _macro(chamada):
    ambiente = Environment(loader=FileSystemLoader(str(RAIZ / 'View' / 'Página')))
    return ambiente.from_string("{% from '_guardiao.html' import guardiao_svg, titulo_medieval %}" + chamada).render()


def _imagem(nome):
    return (PASTA_DOCS / 'apresentacao' / nome).as_uri()


def _qr_code():
    try:
        import segno
    except ImportError:
        print('Aviso: biblioteca "segno" não instalada; o slide final sai sem QR Code (python -m pip install segno).')
        return ''
    return segno.make(LINK_APP, error='m').svg_inline(scale=7, dark='#102e3f', light='#ffffff', border=2)


def colunas(dados, unidade='', maximo=None, destaque=None):
    """Gráfico de colunas: dados = [(rótulo, valor, texto_do_valor)]."""
    maximo = maximo or max(v for _, v, _ in dados)
    itens = ''.join(
        f'<div class="coluna{" destaque" if i == destaque else ""}">'
        f'<span class="valor">{texto}</span>'
        f'<span class="barra-col" style="height:{valor / maximo * 100:.1f}%"></span>'
        f'<span class="rotulo">{rotulo}</span></div>'
        for i, (rotulo, valor, texto) in enumerate(dados)
    )
    return f'<div class="grafico-colunas">{itens}</div>'


def barras_pares(linhas):
    """Barras horizontais lado a lado: linhas = [(rótulo, valor_baixo, valor_alto)] em %."""
    corpo = ''.join(
        f'<div class="par"><div class="par-rotulo">{rotulo}</div>'
        f'<div class="par-barras">'
        f'<div class="barra-h baixa"><span style="width:{baixo}%"></span><b>{baixo}%</b></div>'
        f'<div class="barra-h alta"><span style="width:{alto}%"></span><b>{alto}%</b></div>'
        f'</div></div>'
        for rotulo, baixo, alto in linhas
    )
    return (f'<div class="grafico-pares">{corpo}<div class="legenda-pares">'
            f'<span><i class="amostra baixa"></i>Menor conectividade</span>'
            f'<span><i class="amostra alta"></i>Maior conectividade</span></div></div>')


def cartao_numero(numero, texto, cor=''):
    return f'<div class="numero-grande {cor}"><strong>{numero}</strong><span>{texto}</span></div>'


def cartao_ataque(icone, titulo, golpe, defesa):
    return (f'<div class="ataque"><div class="ataque-titulo"><span class="icone">{icone}</span>{titulo}</div>'
            f'<p class="golpe">{golpe}</p><p class="defesa"><b>Defesa:</b> {defesa}</p></div>')


SLIDES = [
    {
        'classe': 'capa',
        'titulo': 'Capa',
        'html': f'''
            <div class="capa-esquerda">
                <div class="selos-ods"><span class="ods ods-10">ODS 10</span><span class="ods ods-16">ODS 16</span></div>
                {_macro("{{ titulo_medieval() }}")}
                <p class="capa-subtitulo">Um quiz virtual para promover o conhecimento sobre
                   segurança da informação e LGPD</p>
                <div class="capa-dados"><strong>{AUTOR}</strong><br>{CURSO}<br>{DISCIPLINA}</div>
            </div>
            <div class="capa-direita">{_macro("{{ guardiao_svg('orgulhoso') }}")}</div>''',
        'fonte': '',
        'fala': f'Olá a todos. Meu nome é {AUTOR}, sou aluno do curso de Redes de Computadores da UNINTER, e vou '
                'apresentar o projeto de extensão "O Guardião dos Dados": um quiz virtual para promover o conhecimento '
                'sobre segurança da informação e LGPD, ligado aos Objetivos de Desenvolvimento Sustentável 10 e 16.',
        'tempo': 30,
    },
    {
        'titulo': 'Um Brasil cada vez mais digital',
        'rotulo': 'Contexto',
        'html': f'''
            <div class="grade-3">
                {cartao_numero('159 mi', 'de usuários de internet no Brasil — 84% da população com 10 anos ou mais')}
                {cartao_numero('82%', 'das transações bancárias feitas por canais digitais; <b>75%</b> pelo celular')}
                {cartao_numero('2,26 mi', 'de estelionatos (golpes) registrados no país em 2025', 'alerta')}
            </div>
            <p class="mensagem">Quanto mais a vida acontece no celular, mais os golpes nos alcançam.</p>''',
        'fonte': 'Fontes: Cetic.br, TIC Domicílios 2024 · Febraban, Pesquisa de Tecnologia Bancária 2025 (ano-base 2024) · '
                 'Fórum Brasileiro de Segurança Pública (FBSP), Anuário 2026.',
        'fala': 'Antes de falar do projeto, um retrato rápido. Segundo a pesquisa TIC Domicílios 2024, do Cetic.br, o '
                'Brasil tem 159 milhões de usuários de internet, 84% da população com 10 anos ou mais. Segundo a '
                'Febraban, 82% das transações bancárias já são feitas por canais digitais, três em cada quatro pelo '
                'celular. A vida financeira passou para a palma da mão. E o crime acompanhou esse movimento: em 2025 '
                'foram registrados mais de 2,2 milhões de estelionatos no país.',
        'tempo': 45,
    },
    {
        'titulo': 'O que é segurança da informação?',
        'rotulo': 'Conceito',
        'html': '''
            <p class="definicao">É o conjunto de <b>práticas, tecnologias e comportamentos</b> que protegem a
               informação contra acesso, alteração ou perda indevidos. Ela se apoia em três pilares:</p>
            <div class="grade-3 pilares">
                <div class="pilar"><span class="icone">🔒</span><h3>Confidencialidade</h3>
                    <p>Só quem tem autorização consegue acessar a informação.</p></div>
                <div class="pilar"><span class="icone">🧩</span><h3>Integridade</h3>
                    <p>A informação não é alterada sem autorização.</p></div>
                <div class="pilar"><span class="icone">⏱️</span><h3>Disponibilidade</h3>
                    <p>A informação está acessível quando precisamos dela.</p></div>
            </div>
            <p class="mensagem">Muitos golpes não invadem sistemas: eles <b>enganam pessoas</b>.
               É a engenharia social — e a primeira linha de defesa somos nós.</p>''',
        'fonte': 'Base conceitual: tríade CID (confidencialidade, integridade e disponibilidade) da norma ABNT NBR ISO/IEC 27001.',
        'fala': 'Mas, afinal, o que é segurança da informação? É o conjunto de práticas, tecnologias e, principalmente, '
                'comportamentos que protegem a informação. Ela se apoia em três pilares: confidencialidade, ou seja, só '
                'quem deve ter acesso consegue ver; integridade, a informação não é alterada sem autorização; e '
                'disponibilidade, ela está acessível quando precisamos. Muita gente pensa que isso é assunto só de '
                'empresas e técnicos, mas boa parte dos golpes do dia a dia não quebra nenhum sistema: engana pessoas. '
                'É o que chamamos de engenharia social. Por isso, a primeira linha de defesa somos nós.',
        'tempo': 60,
    },
    {
        'titulo': 'Por que isso importa: os golpes explodiram',
        'rotulo': 'Dados',
        'html': f'''
            <div class="dados-lado">
                <div class="painel grafico">
                    <h3>Estelionatos registrados no Brasil</h3>
                    {colunas([('2018', 427, '≈ 427 mil'), ('2024', 2167, '2,17 mi'), ('2025', 2261, '2,26 mi')], destaque=2)}
                </div>
                <div class="destaques">
                    {cartao_numero('+429,8%', 'de crescimento entre 2018 e 2025', 'alerta')}
                    {cartao_numero('4 por minuto', 'golpes registrados, em média, em 2024')}
                    <p class="nota-slide">E esses são apenas os casos que viraram boletim de ocorrência.</p>
                </div>
            </div>''',
        'fonte': 'Fonte: FBSP — Anuário Brasileiro de Segurança Pública 2025 (19ª ed., dado de 2024: 2.166.552) e 2026 '
                 '(20ª ed., dado de 2025: 2.261.055). 2018 calculado a partir da variação de +429,8% divulgada pelo FBSP.',
        'fala': 'E por que isso importa tanto? Este gráfico usa dados do Anuário Brasileiro de Segurança Pública. Em 2018 '
                'eram cerca de 427 mil estelionatos registrados. Em 2024, 2,17 milhões, uma média de quatro golpes por '
                'minuto. Em 2025, 2,26 milhões. É um crescimento de quase 430% em sete anos. E esses são apenas os '
                'casos que viraram boletim de ocorrência.',
        'tempo': 50,
    },
    {
        'titulo': 'O tamanho do problema',
        'rotulo': 'Dados',
        'html': f'''
            <div class="dados-lado">
                <div class="destaques grade-2x2">
                    {cartao_numero('26,3 mi', 'de brasileiros (15,8% com 16 anos ou mais) caíram em algum golpe no último ano', 'alerta')}
                    {cartao_numero('83,2%', 'têm medo de ser vítimas de fraude pela internet ou pelo celular')}
                    {cartao_numero('+ de 97%', 'dos estelionatos registrados não chegam ao Judiciário')}
                    {cartao_numero('4.819', 'pessoas presas por estelionato em 2025, para 2,26 milhões de registros')}
                </div>
                <div class="painel grafico estreito">
                    <h3>Estelionato por meio eletrônico</h3>
                    {colunas([('2023', 222.7, '222,7 mil'), ('2024', 281.2, '281,2 mil')], destaque=1)}
                </div>
            </div>
            <p class="mensagem">Depois do golpe, reverter é difícil: <b>prevenir é a melhor defesa</b>.</p>''',
        'fonte': 'Fontes: FBSP — "O avanço do estelionato em um Brasil cada vez mais digital" (Anuário 2026); Anuário 2025, '
                 'via Agência Lupa (estelionato eletrônico; alguns estados não separam o meio eletrônico, então o número é subestimado).',
        'fala': 'As pesquisas de vitimização mostram que o problema é ainda maior: 15,8% dos brasileiros com mais de 16 '
                'anos, cerca de 26 milhões de pessoas, caíram em algum golpe no último ano, e 83% têm medo de ser '
                'vítimas de fraude pela internet ou pelo celular. Só o estelionato por meio eletrônico passou de 223 mil '
                'para 281 mil registros entre 2023 e 2024. E mais de 97% dos casos nem chegam ao Judiciário. Ou seja: '
                'depois que o golpe acontece, é muito difícil reverter. A melhor defesa é a prevenção.',
        'tempo': 50,
    },
    {
        'titulo': 'ODS 16 · Paz, Justiça e Instituições Eficazes',
        'rotulo': 'Objetivo de Desenvolvimento Sustentável',
        'classe': 'ods16',
        'html': '''
            <div class="ods-layout">
                <div class="ods-bloco ods-16"><span class="ods-numero">16</span><span>Paz, Justiça e<br>Instituições Eficazes</span></div>
                <div class="ods-texto">
                    <div class="citacao"><b>Meta 16.10:</b> “Assegurar o acesso público à informação e proteger as
                        liberdades fundamentais, em conformidade com a legislação nacional e os acordos internacionais.”</div>
                    <ul class="lista">
                        <li><b>Privacidade é uma liberdade fundamental:</b> desde 2022 a proteção de dados pessoais é direito
                            fundamental na Constituição (art. 5º, LXXIX).</li>
                        <li><b>A LGPD</b> (Lei 13.709/2018) garante direitos ao titular e criou a <b>ANPD</b> para fiscalizar.</li>
                        <li><b>Golpes e vazamentos minam a confiança</b> nas instituições; informar a população fortalece essa confiança.</li>
                    </ul>
                </div>
            </div>''',
        'fonte': 'Fontes: ONU Brasil — ODS 16 (brasil.un.org/pt-br/sdgs/16) · Emenda Constitucional nº 115/2022 · Lei nº 13.709/2018 (LGPD).',
        'fala': 'É aqui que entram os Objetivos de Desenvolvimento Sustentável da ONU. O ODS 16, Paz, Justiça e '
                'Instituições Eficazes, tem uma meta, a 16.10, que fala em garantir acesso à informação e proteger as '
                'liberdades fundamentais. A privacidade é uma dessas liberdades: tanto que, desde 2022, a proteção de '
                'dados pessoais é um direito fundamental na Constituição, e a LGPD define regras e criou a ANPD para '
                'fiscalizar. Golpes e vazamentos minam a confiança nas instituições; informar a população fortalece essa confiança.',
        'tempo': 50,
    },
    {
        'titulo': 'ODS 10 · Redução das Desigualdades',
        'rotulo': 'Objetivo de Desenvolvimento Sustentável',
        'html': f'''
            <div class="ods-layout">
                <div class="ods-bloco ods-10"><span class="ods-numero">10</span><span>Redução das<br>Desigualdades</span></div>
                <div class="painel grafico largo">
                    <h3>Usuários de internet que já… (por nível de conectividade, 2024)</h3>
                    {barras_pares([
                        ('Adotaram medidas de segurança<br><small>(senhas fortes, verificação em duas etapas)</small>', 23, 79),
                        ('Verificaram se uma informação<br>era verdadeira', 27, 81),
                        ('Mudaram configurações<br>de privacidade', 20, 60),
                    ])}
                </div>
            </div>
            <p class="mensagem"><b>34%</b> da população está no nível mais baixo de conectividade.
               Quem tem menos acesso tem <b>menos ferramentas para se proteger</b>.</p>''',
        'fonte': 'Fonte: Cetic.br — TIC Domicílios 2024, Resumo Executivo, Gráfico 2 (níveis de conectividade significativa: 0–2 e 7–9 pontos).',
        'fala': 'O segundo objetivo é o ODS 10, Redução das Desigualdades. A segurança digital não está distribuída de '
                'forma igual. A TIC Domicílios 2024 mostra que, entre as pessoas com o nível mais alto de conectividade, '
                '79% já adotaram medidas de segurança, como senhas fortes ou verificação em duas etapas. Entre as de '
                'nível mais baixo, só 23%. A diferença se repete em checar se uma informação é verdadeira e em '
                'configurar a privacidade. E 34% da população está nesse nível mais baixo. Quem tem menos acesso tem '
                'menos ferramentas para se proteger, e é para esse público que o projeto foi pensado.',
        'tempo': 55,
    },
    {
        'titulo': 'Os golpes mais comuns do dia a dia',
        'rotulo': 'Prevenção · 1/2',
        'html': f'''
            <div class="grade-2x2 ataques">
                {cartao_ataque('🎣', 'Phishing e SMS falso', '“Sua conta será bloqueada”, “pague a taxa da encomenda” — com um link e muita urgência.',
                               'não clique; entre pelo aplicativo ou digitando o site oficial.')}
                {cartao_ataque('💬', 'WhatsApp clonado', 'Alguém pede “o código de 6 dígitos que chegou por SMS” para “confirmar um cadastro”.',
                               'nunca compartilhe códigos; ative a confirmação em duas etapas.')}
                {cartao_ataque('👪', 'Falso parente', '“Oi, mãe! Troquei de número. Me faz um Pix urgente?”',
                               'ligue para o número antigo ou confirme por outro meio antes de pagar.')}
                {cartao_ataque('📞', 'Falsa central do banco', 'Ligação sobre “compra suspeita” que pede senha ou transferência para uma “conta segura”.',
                               'banco não pede isso; desligue e ligue para o número do cartão.')}
            </div>''',
        'fonte': 'Golpes recorrentes descritos pelo FBSP, Febraban e Banco Central; todos abordados nas perguntas do quiz.',
        'fala': 'Vamos ao que mais acontece no dia a dia. Primeiro, o phishing: e-mail ou SMS com urgência, como "sua '
                'conta será bloqueada" ou "pague a taxa da encomenda", e um link. Regra: não clique; entre pelo '
                'aplicativo ou site oficial. Segundo, o golpe do WhatsApp: alguém pede o código de seis dígitos que '
                'chegou por SMS. Esse código é a chave da sua conta; nunca compartilhe e ative a confirmação em duas '
                'etapas. Terceiro, o falso parente: "troquei de número, me faz um Pix?". Ligue para o número antigo '
                'antes de pagar. E a falsa central do banco, que pede senha ou transferência para uma "conta segura": '
                'banco nenhum faz isso. Desligue e ligue você mesmo para o número do cartão.',
        'tempo': 60,
    },
    {
        'titulo': 'Outros riscos que passam despercebidos',
        'rotulo': 'Prevenção · 2/2',
        'html': f'''
            <div class="grade-2x2 ataques">
                {cartao_ataque('🔑', 'Senha repetida', 'Um site vaza senhas e os criminosos testam a mesma senha no seu e-mail e no seu banco.',
                               'uma senha diferente por serviço (um gerenciador ajuda) + verificação em duas etapas.')}
                {cartao_ataque('📶', 'Wi-Fi público aberto', 'Redes sem senha podem ser falsas ou monitoradas por outras pessoas conectadas.',
                               'para banco e compras, use os dados móveis ou uma rede confiável.')}
                {cartao_ataque('🦠', 'Anexos e ransomware', 'Um arquivo ou link malicioso instala um programa que rouba dados ou “sequestra” arquivos.',
                               'atualizações em dia e cópias de segurança (backup) fora do aparelho.')}
                {cartao_ataque('📸', 'Exposição nas redes', 'Fotos de documentos, cartão de embarque e localização em tempo real entregam informações.',
                               'poste depois, sem documentos à vista e sem dizer onde você está agora.')}
            </div>''',
        'fonte': 'Boas práticas da Cartilha de Segurança para Internet do CERT.br (cartilha.cert.br).',
        'fala': 'Outros riscos comuns: senhas repetidas. Quando um site vaza, os criminosos testam a mesma senha no seu '
                'e-mail e no seu banco; use uma senha diferente por serviço. Wi-Fi público aberto: para banco, prefira os '
                'dados móveis. Anexos e programas maliciosos, como o ransomware, que sequestra arquivos: mantenha tudo '
                'atualizado e tenha backup. E a exposição nas redes: foto de documento, cartão de embarque ou localização '
                'em tempo real entregam informações para golpistas.',
        'tempo': 50,
    },
    {
        'titulo': 'As regras de ouro do Guardião',
        'rotulo': 'Prevenção',
        'html': '''
            <ol class="regras">
                <li><span><b>Desconfie da urgência.</b> Pressa é a principal arma do golpista.</span></li>
                <li><span><b>Nunca compartilhe</b> senhas, códigos de verificação ou dados do cartão.</span></li>
                <li><span><b>Ative a verificação em duas etapas</b> no WhatsApp, e-mail e redes sociais.</span></li>
                <li><span><b>Confirme por outro canal</b> antes de pagar ou transferir.</span></li>
                <li><span><b>Mantenha tudo atualizado</b> e faça backup do que é importante.</span></li>
                <li><span><b>Foi vítima?</b> Avise o banco na hora, peça a devolução pelo <b>MED do Pix</b> e registre boletim de ocorrência.</span></li>
            </ol>''',
        'fonte': 'MED: Mecanismo Especial de Devolução do Pix, regulamentado pelo Banco Central (bcb.gov.br/estabilidadefinanceira/pix).',
        'fala': 'Resumindo em seis regras de ouro: desconfie de toda urgência; nunca compartilhe senhas e códigos; ative '
                'a verificação em duas etapas; confirme sempre por outro canal; mantenha os aparelhos atualizados e faça '
                'backup; e, se for vítima, avise o banco imediatamente, peça a devolução pelo MED do Pix e registre '
                'boletim de ocorrência.',
        'tempo': 45,
    },
    {
        'titulo': 'O projeto: O Guardião dos Dados',
        'rotulo': 'Solução',
        'html': f'''
            <div class="projeto">
                <ul class="lista">
                    <li><b>Quiz web</b> com tema medieval: funciona em qualquer celular, sem instalar nada.</li>
                    <li><b>5 provações sorteadas</b> de um banco de 25 perguntas sobre golpes, LGPD e o ODS 16.</li>
                    <li>Depois de cada resposta, <b>o Guardião explica o porquê</b>.</li>
                    <li>No final: título conquistado e o quadro <b>“Por que isso importa?”</b> (ODS 10 e 16).</li>
                    <li><b>Participação anônima</b> (“Jogador 1, 2, 3…”): o quiz pratica a LGPD que ensina.</li>
                </ul>
                <div class="telas">
                    <img src="{_imagem('tela-menu.jpg')}" alt="Menu do quiz">
                    <img src="{_imagem('tela-pergunta.jpg')}" alt="Pergunta com explicação">
                    <img src="{_imagem('tela-resultado.jpg')}" alt="Resultado da jornada">
                </div>
            </div>''',
        'fonte': '',
        'fala': 'Foi para levar esse conhecimento de forma simples que criei O Guardião dos Dados. É um quiz web, com '
                'tema medieval, que funciona em qualquer celular, sem instalar nada. A cada jornada, o participante '
                'enfrenta cinco provações sorteadas de um banco de 25 perguntas sobre golpes, LGPD e o ODS 16. Depois de '
                'cada resposta, o Guardião explica o porquê. No final, a pessoa recebe um título e vê o quadro "Por que '
                'isso importa?". E a participação é anônima: o próprio quiz pratica o que ensina sobre a LGPD.',
        'tempo': 50,
    },
    {
        'titulo': 'Validação e coleta de dados',
        'rotulo': 'Metodologia',
        'html': '''
            <div class="grade-3">
                <div class="pilar"><span class="icone">📝</span><h3>Avaliação do participante</h3>
                    <p>Notas de 1 a 10 para <b>dificuldade</b>, <b>facilidade de uso</b> e <b>relevância</b> das
                       informações, mais um campo de sugestões.</p></div>
                <div class="pilar"><span class="icone">📊</span><h3>Painel administrativo</h3>
                    <p>Acertos por pergunta, jornadas e avaliações em <b>gráficos</b> e <b>relatórios em PDF</b> para o
                       relatório final.</p></div>
                <div class="pilar"><span class="icone">⚙️</span><h3>Tecnologias</h3>
                    <p>Python + Flask, PostgreSQL (Neon), hospedagem no <b>Vercel</b> e versionamento no <b>GitHub</b>.</p></div>
            </div>
            <p class="mensagem">Aplicação com o público de <b>Campo Grande (RJ)</b>: os dados mostram o que a população já
               sabe — e onde a informação precisa chegar.</p>''',
        'fonte': '',
        'fala': 'Para validar o projeto, ao final cada participante avalia de 1 a 10 a dificuldade das perguntas, a '
                'facilidade de uso e a relevância das informações, e pode deixar sugestões. Um painel administrativo '
                'reúne os acertos por pergunta, as jornadas e as avaliações em gráficos e relatórios em PDF, que vão '
                'compor o relatório final da aplicação em Nova Iguaçu. O sistema foi desenvolvido em Python com Flask e '
                'banco PostgreSQL, está hospedado no Vercel e tem o código no GitHub.',
        'tempo': 40,
    },
    {
        'titulo': 'Referências',
        'rotulo': 'Fontes pesquisáveis',
        'classe': 'referencias',
        'html': '''
            <ul class="refs">
                <li>FÓRUM BRASILEIRO DE SEGURANÇA PÚBLICA. <b>Anuário Brasileiro de Segurança Pública 2025</b> (19ª ed.).
                    forumseguranca.org.br/wp-content/uploads/2025/07/anuario-2025.pdf</li>
                <li>FBSP. <b>19ª edição do Anuário revela 2,2 milhões de casos de estelionato em 2024</b>. Fonte Segura, 25/07/2025.
                    fontesegura.forumseguranca.org.br</li>
                <li>BUENO, S.; LIMA, R. S.; SOBRAL, I. <b>O avanço do estelionato em um Brasil cada vez mais digital</b>
                    (Anuário 2026, 20ª ed.). Fonte Segura, 19/08/2026. fontesegura.forumseguranca.org.br</li>
                <li>AGÊNCIA LUPA. <b>Golpes nas redes: Brasil registrou 281 mil casos de estelionato digital em 2024</b>. 24/07/2025.
                    agencialupa.org</li>
                <li>CETIC.BR / NIC.BR. <b>Pesquisa TIC Domicílios 2024 — Resumo Executivo</b>. cetic.br/pt/pesquisa/domicilios</li>
                <li>FEBRABAN; DELOITTE. <b>Pesquisa Febraban de Tecnologia Bancária 2025</b> (ano-base 2024). febraban.org.br</li>
                <li>NAÇÕES UNIDAS BRASIL. <b>ODS 10</b> e <b>ODS 16</b>. brasil.un.org/pt-br/sdgs/10 · brasil.un.org/pt-br/sdgs/16</li>
                <li>BRASIL. <b>Lei nº 13.709/2018 (LGPD)</b> e <b>Emenda Constitucional nº 115/2022</b>. planalto.gov.br</li>
                <li>CERT.BR. <b>Cartilha de Segurança para Internet</b>. cartilha.cert.br</li>
                <li>BANCO CENTRAL DO BRASIL. <b>Pix — Mecanismo Especial de Devolução (MED)</b>. bcb.gov.br/estabilidadefinanceira/pix</li>
            </ul>''',
        'fonte': '',
        'fala': 'Todos os dados apresentados vêm de fontes públicas e podem ser consultados: o Fórum Brasileiro de '
                'Segurança Pública, o Cetic.br, a Febraban, a ONU e a legislação brasileira.',
        'tempo': 15,
    },
    {
        'classe': 'final',
        'titulo': 'Aceite o desafio do Guardião!',
        'html': f'''
            <div class="final-esquerda">
                {_macro("{{ guardiao_svg('orgulhoso') }}")}
            </div>
            <div class="final-centro">
                <p class="final-chamada">Aceite o desafio do Guardião!</p>
                <p class="final-texto">5 provações · cerca de 5 minutos · anônimo · direto no celular</p>
                <a class="final-link" href="{LINK_APP}">{LINK_APP.replace('https://', '').rstrip('/')}</a>
                <p class="final-obrigado">Obrigado!</p>
                <p class="final-autor">{AUTOR} · {CURSO}</p>
            </div>
            <div class="final-qr">{{QR}}<span>Aponte a câmera do celular</span></div>''',
        'fonte': '',
        'fala': 'Para encerrar, deixo o convite: apontem a câmera do celular para o QR Code e aceitem o desafio do '
                'Guardião. Leva cerca de cinco minutos e, no final, a avaliação de vocês ajuda a melhorar o projeto. '
                'Muito obrigado!',
        'tempo': 30,
    },
]


CSS = """
@page { size: 1280px 720px; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #091722; }
body { font-family: "Segoe UI", system-ui, Arial, sans-serif; color: var(--texto);
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.slide { width: 1280px; height: 720px; position: relative; overflow: hidden; break-after: page;
         padding: 44px 64px 74px; color: #e2e8f0; display: flex; flex-direction: column;
         background: radial-gradient(circle at 50% -10%, #1d435b 0%, #102636 55%, #091722 100%); }
.slide::before { content: ""; position: absolute; inset: 14px; border: 1.5px solid rgba(213, 180, 108, 0.45);
                 border-radius: 18px; pointer-events: none; }
.rotulo-slide { display: inline-block; padding: 4px 14px; border-radius: 999px; background: var(--ouro-claro);
                color: #5c3d04; font-size: 13px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;
                border: 1px solid var(--borda-ouro); }
.corpo-slide { flex: 1; display: flex; flex-direction: column; justify-content: center; min-height: 0; }
.slide h2 { margin: 12px 0 10px; font-family: "Cinzel", Georgia, serif; font-size: 38px; font-weight: 800;
            color: #fde68a; letter-spacing: 0.02em; text-shadow: 0 2px 10px rgba(0,0,0,0.35); }
.rodape { position: absolute; left: 64px; right: 64px; bottom: 26px; display: flex; justify-content: space-between;
          align-items: flex-end; gap: 30px; font-size: 12px; color: #94a3b8; }
.rodape .fonte { flex: 1; min-width: 0; line-height: 1.35; }
.rodape .marca-slide { flex: none; white-space: nowrap; font-family: "Cinzel", serif; font-weight: 700; color: #d5b46c; }

.painel, .numero-grande, .pilar, .ataque, .citacao { background: var(--superficie); color: var(--texto);
        border: 2px solid var(--borda-ouro); border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.35); }
.grade-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }
.grade-2x2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.numero-grande { padding: 28px 28px; display: flex; flex-direction: column; gap: 10px; }
.numero-grande strong { font-family: "Cinzel", serif; font-size: 62px; line-height: 1; color: var(--primaria); }
.numero-grande.alerta strong { color: var(--erro); }
.numero-grande span { font-size: 21px; line-height: 1.38; }
.mensagem { margin: 28px 0 0; padding: 18px 24px; border-radius: 14px; background: rgba(253, 230, 138, 0.12);
            border-left: 5px solid var(--ouro); font-size: 24px; color: #f8fafc; }
.mensagem b { color: #fde68a; }
.nota-slide { margin: 6px 0 0; font-size: 16px; color: #cbd5e1; font-style: italic; }

.definicao { font-size: 26px; line-height: 1.45; margin: 0 0 26px; color: #f1f5f9; }
.pilar { padding: 26px 28px; }
.pilar .icone { font-size: 40px; }
.pilar h3 { margin: 10px 0 8px; font-family: "Cinzel", serif; color: var(--primaria-escura); font-size: 25px; }
.pilar p { margin: 0; font-size: 20.5px; line-height: 1.42; }

.dados-lado { display: grid; grid-template-columns: 1.25fr 1fr; gap: 26px; align-items: stretch; }
.painel.grafico { padding: 20px 24px; }
.painel h3 { margin: 0 0 12px; font-family: "Cinzel", serif; color: var(--primaria-escura); font-size: 20px; }
.destaques { display: flex; flex-direction: column; gap: 16px; }
.destaques.grade-2x2 { display: grid; }
.destaques.grade-2x2 .numero-grande { padding: 22px 24px; }
.destaques.grade-2x2 .numero-grande strong { font-size: 46px; }
.destaques.grade-2x2 .numero-grande span { font-size: 17.5px; }
.painel.estreito .grafico-colunas { height: 300px; }
.grafico-colunas { display: flex; align-items: flex-end; justify-content: space-around; gap: 26px; height: 360px;
                   border-bottom: 3px solid var(--borda); padding: 0 10px; }
.coluna { flex: 1; max-width: 150px; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; position: relative; }
.coluna .barra-col { width: 100%; border-radius: 10px 10px 0 0; background: linear-gradient(180deg, #2e6f8e, #173d52); }
.coluna.destaque .barra-col { background: linear-gradient(180deg, #d9534a, #9b2c22); }
.coluna .valor { font-family: "Cinzel", serif; font-weight: 800; font-size: 22px; color: var(--primaria-escura); margin-bottom: 6px; white-space: nowrap; }
.coluna .rotulo { position: absolute; bottom: -34px; font-weight: 700; font-size: 18px; color: var(--texto-suave); }
.painel.grafico .grafico-colunas { margin-bottom: 38px; }

.ods-layout { display: grid; grid-template-columns: 230px 1fr; gap: 28px; align-items: start; }
.ods-bloco { height: 230px; border-radius: 16px; color: #fff; padding: 20px; display: flex; flex-direction: column;
             justify-content: space-between; font-weight: 800; font-size: 19px; line-height: 1.2; text-transform: uppercase;
             box-shadow: 0 10px 30px rgba(0,0,0,0.35); }
.ods-bloco .ods-numero { font-size: 92px; line-height: 0.9; font-family: "Segoe UI", Arial, sans-serif; }
.ods-16 { background: #00689d; } .ods-10 { background: #dd1367; }
.citacao { padding: 20px 24px; font-size: 22px; line-height: 1.45; margin-bottom: 18px; }
.lista { margin: 0; padding-left: 28px; font-size: 22.5px; line-height: 1.45; color: #f1f5f9; }
.lista li { margin-bottom: 14px; } .lista b { color: #fde68a; }
.painel.largo { padding: 22px 26px; }
.grafico-pares { display: flex; flex-direction: column; gap: 16px; }
.par { display: grid; grid-template-columns: 290px 1fr; gap: 18px; align-items: center; }
.par-rotulo { font-weight: 700; font-size: 19px; line-height: 1.3; color: var(--primaria-escura); }
.par-rotulo small { font-weight: 400; color: var(--texto-suave); font-size: 13px; }
.par-barras { display: flex; flex-direction: column; gap: 6px; }
.barra-h { display: flex; align-items: center; gap: 10px; height: 30px; }
.barra-h span { height: 100%; border-radius: 0 6px 6px 0; }
.barra-h.baixa span { background: #dd1367; } .barra-h.alta span { background: #2e6f8e; }
.barra-h b { font-size: 19px; color: var(--texto); }
.legenda-pares { display: flex; gap: 26px; justify-content: flex-end; font-size: 15px; color: var(--texto-suave); }
.amostra { display: inline-block; width: 14px; height: 14px; border-radius: 3px; margin-right: 6px; vertical-align: -2px; }
.amostra.baixa { background: #dd1367; } .amostra.alta { background: #2e6f8e; }

.ataques { gap: 18px; }
.ataque { padding: 20px 24px; }
.ataque-titulo { display: flex; align-items: center; gap: 10px; font-family: "Cinzel", serif; font-weight: 800;
                 font-size: 24px; color: var(--primaria-escura); }
.ataque .icone { font-size: 32px; }
.ataque p { margin: 10px 0 0; font-size: 19px; line-height: 1.4; }
.ataque .golpe { color: var(--texto-suave); font-style: italic; }
.ataque .defesa { padding: 8px 12px; border-radius: 10px; background: var(--sucesso-claro); color: #14532d; }
.ataque .defesa b { color: var(--sucesso); }

.regras { margin: 0; padding: 0; list-style: none; counter-reset: regra; display: grid; grid-template-columns: 1fr 1fr; gap: 16px 22px; }
.regras li { counter-increment: regra; position: relative; padding: 18px 22px 18px 86px; min-height: 120px; display: flex; align-items: center;
             background: var(--superficie); color: var(--texto); border: 2px solid var(--borda-ouro); border-radius: 16px;
             font-size: 21px; line-height: 1.4; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
.regras li::before { content: counter(regra); position: absolute; left: 18px; top: 50%; transform: translateY(-50%);
                     width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
                     background: linear-gradient(180deg, #f9db78, #c89223); color: #422c03; font-family: "Cinzel", serif;
                     font-weight: 800; font-size: 24px; border: 2px solid #9e6d10; }
.regras b { color: var(--primaria-escura); }

.projeto { display: grid; grid-template-columns: 1fr 640px; gap: 30px; align-items: center; }
.telas { display: flex; gap: 14px; justify-content: flex-end; }
.telas img { width: 205px; border-radius: 18px; border: 3px solid var(--borda-ouro); box-shadow: 0 12px 30px rgba(0,0,0,0.45); }
.telas img:nth-child(2) { transform: translateY(-14px); }

.referencias h2 { margin-bottom: 14px; }
.refs { margin: 0; padding: 18px 26px 18px 44px; background: var(--superficie); color: var(--texto); border: 2px solid var(--borda-ouro);
        border-radius: 16px; font-size: 17px; line-height: 1.45; columns: 2; column-gap: 38px; }
.refs li { margin-bottom: 13px; break-inside: avoid; }

.capa, .final { display: grid; align-items: center; padding: 50px 70px; }
.capa { grid-template-columns: 1.35fr 1fr; gap: 30px; }
.capa .emblema-titulo-medieval { width: 640px; margin: 18px 0 8px; max-width: none; }
.capa .svg-titulo-medieval { width: 100%; height: auto; }
.capa-subtitulo { font-size: 25px; line-height: 1.4; color: #f1f5f9; margin: 8px 0 24px; max-width: 620px; }
.capa-dados { font-size: 17px; line-height: 1.6; color: #cbd5e1; padding: 14px 20px; border-left: 4px solid var(--ouro);
              background: rgba(255, 255, 255, 0.04); border-radius: 0 12px 12px 0; }
.capa-dados strong { color: #fde68a; font-size: 20px; }
.selos-ods { display: flex; gap: 10px; }
.ods { padding: 6px 14px; border-radius: 8px; color: #fff; font-weight: 800; letter-spacing: 0.06em; font-size: 15px; }
.capa-direita .guardiao-retrato, .final-esquerda .guardiao-retrato { width: 400px; height: 400px; margin: 0 auto; }
.capa-direita svg, .final-esquerda svg { width: 100%; height: 100%; }
.final { grid-template-columns: 300px 1fr 300px; gap: 30px; text-align: center; }
.final-esquerda .guardiao-retrato { width: 280px; height: 280px; }
.final-chamada { margin: 0; font-family: "Cinzel", serif; font-weight: 800; font-size: 44px; color: #fde68a; line-height: 1.15; }
.final-texto { margin: 14px 0 26px; font-size: 20px; color: #cbd5e1; }
.final-link { display: inline-block; padding: 16px 28px; border-radius: 999px; font-size: 22px; white-space: nowrap; font-weight: 800; color: #fff;
              text-decoration: none; background: linear-gradient(180deg, #2e6f8e, #173d52); border: 2px solid var(--borda-ouro);
              box-shadow: 0 10px 30px rgba(0,0,0,0.45); }
.final-obrigado { margin: 34px 0 6px; font-family: "Cinzel Decorative", "Cinzel", serif; font-size: 40px; font-weight: 900; color: #fde68a; }
.final-autor { margin: 0; font-size: 16px; color: #94a3b8; }
.final-qr { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.final-qr svg { width: 260px; height: 260px; border-radius: 16px; border: 4px solid var(--borda-ouro); background: #fff; }
.final-qr span { font-size: 16px; color: #cbd5e1; }
"""


def html_slides():
    qr = _qr_code()
    total = len(SLIDES)
    paginas = []
    for numero, s in enumerate(SLIDES, 1):
        conteudo = s['html'].replace('{QR}', qr)
        if s.get('classe') in ('capa', 'final'):
            corpo = conteudo
        else:
            corpo = (f'<div class="topo-slide"><span class="rotulo-slide">{s["rotulo"]}</span><h2>{s["titulo"]}</h2></div>'
                     f'<div class="corpo-slide">{conteudo}</div>'
                     f'<div class="rodape"><span class="fonte">{escape(s["fonte"])}</span>'
                     f'<span class="marca-slide">O Guardião dos Dados · {numero}/{total}</span></div>')
        paginas.append(f'<section class="slide {s.get("classe", "")}">{corpo}</section>')
    return _documento('Apresentação — O Guardião dos Dados', CSS, ''.join(paginas))


CSS_ROTEIRO = """
@page { size: A4; margin: 16mm 16mm 18mm;
        @bottom-right { content: "Página " counter(page); font: 8pt "Segoe UI", Arial, sans-serif; color: #5a6770; } }
body { margin: 0; font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.55; color: var(--texto);
       -webkit-print-color-adjust: exact; print-color-adjust: exact; background: #fff; }
.cabecalho { padding: 9mm 10mm; border-radius: 4mm; color: #e2e8f0; margin-bottom: 7mm;
             background: radial-gradient(circle at 50% 0%, #1d435b 0%, #102636 60%, #091722 100%); }
.cabecalho h1 { margin: 0 0 2mm; font-family: "Cinzel", serif; color: #fde68a; font-size: 20pt; }
.cabecalho p { margin: 0; }
.dicas { margin: 0 0 6mm; padding: 4mm 6mm; border-left: 4px solid var(--ouro); background: var(--ouro-claro); border-radius: 0 3mm 3mm 0; }
.item { break-inside: avoid; margin: 0 0 4.5mm; padding: 4mm 5mm; border: 1.5px solid var(--borda-ouro); border-radius: 3mm; background: var(--superficie); }
.item h2 { display: flex; justify-content: space-between; gap: 6mm; margin: 0 0 1.5mm; font-family: "Cinzel", serif; font-size: 12.5pt; color: var(--primaria-escura); }
.item h2 span { font-family: "Segoe UI", Arial, sans-serif; font-size: 9.5pt; color: #5c3d04; background: var(--ouro-claro);
                border: 1px solid var(--borda-ouro); border-radius: 99px; padding: 0.5mm 3mm; white-space: nowrap; align-self: center; }
.item p { margin: 0; }
"""


def html_roteiro():
    total = sum(s['tempo'] for s in SLIDES)
    palavras = sum(len(s['fala'].split()) for s in SLIDES)
    acumulado, itens = 0, []
    for numero, s in enumerate(SLIDES, 1):
        acumulado += s['tempo']
        itens.append(
            f'<div class="item"><h2>{numero}. {escape(s["titulo"])}'
            f'<span>{s["tempo"]} s · até {acumulado // 60}:{acumulado % 60:02d}</span></h2>'
            f'<p>{escape(s["fala"])}</p></div>'
        )
    corpo = (f'<div class="cabecalho"><h1>Roteiro da apresentação</h1>'
             f'<p>O Guardião dos Dados · {AUTOR} · {len(SLIDES)} slides · cerca de {total // 60} min {total % 60:02d} s '
             f'({palavras} palavras: cerca de {round(palavras / 130)} min de fala, mais as pausas para o público ler os '
             f'gráficos e para as transições)</p></div>'
             f'<div class="dicas"><b>Dicas:</b> fale olhando para o público e use os números dos slides como apoio — não é '
             f'preciso ler tudo. Se o tempo apertar, resuma os slides 9 e 12. No final, deixe o QR Code na tela enquanto '
             f'responde às perguntas.</div>' + ''.join(itens))
    return _documento('Roteiro — O Guardião dos Dados', CSS_ROTEIRO, corpo)


def _documento(titulo, css, corpo):
    css_site = (RAIZ / 'View' / 'Estilo' / 'style.css').as_uri()
    return f"""<!DOCTYPE html><html lang="pt-br"><head><meta charset="utf-8"><title>{titulo}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700;900&family=Cinzel:wght@600;700;800&display=block" rel="stylesheet">
<link rel="stylesheet" href="{css_site}">
<style>html, body {{ min-height: 0 !important; }} {css}</style></head><body>{corpo}</body></html>"""


def imprimir(html, destino_final, pasta):
    pagina = Path(pasta) / (destino_final.stem.replace(' ', '_') + '.html')
    pagina.write_text(html, encoding='utf-8')
    destino = Path(pasta) / 'saida.pdf'
    imprimir_pdf(pagina, destino, pasta)
    shutil.copyfile(destino, destino_final)
    destino.unlink()
    print(f'PDF gerado: {destino_final}')


def main():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as pasta:
        imprimir(html_slides(), SAIDA_SLIDES, pasta)
        imprimir(html_roteiro(), SAIDA_ROTEIRO, pasta)


if __name__ == '__main__':
    main()
