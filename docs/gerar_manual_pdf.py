"""Gera "docs/Manual - O Guardião dos Dados.pdf" a partir do MANUAL.md, com o visual do projeto.

Uso (na raiz do projeto ou de qualquer pasta):
    python -m pip install markdown      # só na primeira vez
    python docs/gerar_manual_pdf.py

Como funciona: o Markdown vira uma página HTML que usa as cores, as fontes (Cinzel) e o desenho do Guardião do
próprio site (View/Estilo/style.css e as macros de View/Página/_guardiao.html); o Microsoft Edge ou o Google Chrome,
em modo invisível, "imprime" essa página em PDF. Precisa de internet para carregar as fontes do Google.
Este script não faz parte do app: o servidor (local ou Vercel) não o utiliza.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit('Falta a biblioteca "markdown". Instale com:  python -m pip install markdown')
from jinja2 import Environment, FileSystemLoader

RAIZ = Path(__file__).resolve().parent.parent
MANUAL = RAIZ / 'MANUAL.md'
SAIDA = RAIZ / 'docs' / 'Manual - O Guardião dos Dados.pdf'

NAVEGADORES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
]


def navegadores_instalados():
    """Edge e Chrome encontrados no computador, na ordem de preferência."""
    encontrados = [c for c in NAVEGADORES if os.path.exists(c)]
    for nome in ('msedge', 'microsoft-edge', 'google-chrome', 'chromium', 'chromium-browser', 'chrome'):
        caminho = shutil.which(nome)
        if caminho and caminho not in encontrados:
            encontrados.append(caminho)
    return encontrados


def imprimir_pdf(pagina, destino, pasta):
    """Imprime a página HTML em PDF com o primeiro navegador que funcionar.

    Tenta o próximo navegador quando um deles não gera o arquivo (acontece, por exemplo, quando o Edge está no meio
    de uma atualização automática e fecha na hora sem imprimir).
    """
    navegadores = navegadores_instalados()
    if not navegadores:
        sys.exit('Nenhum navegador Edge/Chrome encontrado para gerar o PDF.')
    for i, navegador in enumerate(navegadores):
        if destino.exists():
            destino.unlink()
        subprocess.run([
            navegador, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
            '--allow-file-access-from-files', '--virtual-time-budget=15000',
            f'--user-data-dir={Path(pasta) / f"perfil{i}"}', f'--print-to-pdf={destino}', Path(pagina).as_uri(),
        ], capture_output=True, timeout=180)
        if destino.exists() and destino.stat().st_size:
            return
        print(f'Aviso: {Path(navegador).name} não gerou o PDF; tentando outro navegador.')
    sys.exit('Nenhum navegador conseguiu gerar o PDF.')


def ancora_github(texto, _separador='-'):
    """Mesmo formato de âncora do GitHub ("6. Páginas e endereços (rotas)" -> "6-páginas-e-endereços-rotas"),
    para os links do sumário do MANUAL.md funcionarem também no PDF."""
    texto = re.sub(r'<[^>]+>', '', texto).strip().lower()
    return re.sub(r'[^\w\- ]', '', texto).replace(' ', '-')


def corpo_do_manual():
    texto = MANUAL.read_text(encoding='utf-8')
    linhas = texto.splitlines()
    linhas = [l for l in linhas if not l.startswith('# ') and not l.startswith('**Autor:**')
              and 'Também disponível em PDF' not in l and 'veja como atualizá-lo na' not in l]
    html = markdown.markdown(
        '\n'.join(linhas),
        extensions=['tables', 'fenced_code', 'sane_lists', 'toc'],
        extension_configs={'toc': {'slugify': ancora_github}},
    )
    html = re.sub(r'<a href="(?!#|https?:)[^"]*">(.*?)</a>', r'<span class="ref-codigo">\1</span>', html)
    html = re.sub(r'(?<!<pre>)<code>(.*?)</code>',
                  lambda m: '<code>' + re.sub(r'([/_.\-])', r'\1<wbr>', m.group(1)) + '</code>', html)
    html = html.replace('<h2 id="sumário">Sumário</h2>\n<ol>', '<h2 id="sumário">Sumário</h2>\n<ol class="sumario">', 1)
    return html


def capa():
    ambiente = Environment(loader=FileSystemLoader(str(RAIZ / 'View' / 'Página')))
    modelo = ambiente.from_string(
        "{% from '_guardiao.html' import guardiao_svg, titulo_medieval %}"
        "{{ titulo_medieval() }}<div class='capa-retrato'>{{ guardiao_svg('orgulhoso') }}</div>"
    )
    return modelo.render()


CSS_IMPRESSAO = """
@page { size: A4; margin: 18mm 16mm 20mm;
        @bottom-left { content: "O Guardião dos Dados · Manual técnico"; font: 8pt "Segoe UI", Arial, sans-serif; color: #5a6770; }
        @bottom-right { content: "Página " counter(page); font: 8pt "Segoe UI", Arial, sans-serif; color: #5a6770; } }
@page capa { margin: 0; @bottom-left { content: none; } @bottom-right { content: none; } }
html, body { background: #fff !important; }
body { margin: 0; min-height: 0; font-size: 10pt; line-height: 1.5; color: var(--texto);
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }

.capa { page: capa; break-after: page; height: 297mm; display: flex; flex-direction: column; align-items: center;
        justify-content: center; gap: 8mm; text-align: center; color: #fef3c7;
        background: radial-gradient(circle at 50% 30%, #1d435b 0%, #102636 55%, #091722 100%); }
.capa .emblema-titulo-medieval { width: 150mm; max-width: none; margin: 0; }
.capa .svg-titulo-medieval { width: 100%; height: auto; }
.capa-retrato .guardiao-retrato { width: 62mm; height: 62mm; margin: 0 auto; }
.capa-retrato svg { width: 100%; height: 100%; }
.capa-subtitulo { font-family: var(--fonte-epica); font-size: 22pt; font-weight: 700; letter-spacing: 0.08em; color: #fde68a; margin: 0; }
.capa-descricao { max-width: 140mm; margin: 0; font-size: 11pt; color: #e2e8f0; }
.capa-dados { margin-top: 6mm; padding: 4mm 8mm; border: 1px solid rgba(213, 180, 108, 0.6); border-radius: 4mm;
              font-size: 10pt; color: #e2e8f0; line-height: 1.7; }
.capa-dados strong { color: #fde68a; }

.manual h2 { break-before: page; margin: 0 0 5mm; padding-bottom: 2.5mm; font-family: var(--fonte-epica);
             font-size: 19pt; color: var(--primaria-escura); border-bottom: 2.5px solid var(--ouro); }
.manual h2#sumário { break-before: avoid; }
.manual h3 { margin: 6mm 0 2.5mm; font-family: var(--fonte-epica); font-size: 13pt; color: var(--primaria); break-after: avoid; }
.manual p, .manual li { orphans: 3; widows: 3; }
.manual > p:first-child { font-size: 11pt; }
.manual blockquote { margin: 4mm 0; padding: 3mm 5mm; border-left: 4px solid var(--ouro); background: var(--ouro-claro);
                     border-radius: 0 3mm 3mm 0; break-inside: avoid; }
.manual blockquote p { margin: 0; }
.manual hr { display: none; }
.manual code { font-family: Consolas, "Cascadia Mono", monospace; font-size: 8.6pt; padding: 0.2mm 1.2mm;
               border-radius: 1.2mm; background: var(--fundo-card-interno); border: 1px solid var(--borda);
               color: #7c2d12; overflow-wrap: normal; word-break: normal; }
.manual pre { margin: 3mm 0 4mm; padding: 4mm 5mm; border-radius: 3mm; background: #102e3f; border: 2px solid var(--borda-ouro);
              break-inside: avoid; white-space: pre; overflow: hidden; }
.manual pre code { background: none; border: 0; padding: 0; color: #e2e8f0; font-size: 7.6pt; line-height: 1.45; }
.ref-codigo { font-weight: 600; color: var(--primaria); }
.manual table { width: 100%; border-collapse: collapse; margin: 3mm 0 5mm; font-size: 8.8pt; line-height: 1.4; }
.manual thead { display: table-header-group; }
.manual th { background: var(--primaria-escura); color: #fde68a; text-align: left; font-weight: 700; padding: 2mm 2.5mm;
             font-size: 8.4pt; letter-spacing: 0.02em; }
.manual td { padding: 1.8mm 2.5mm; border-bottom: 1px solid var(--borda); vertical-align: top; }
.manual tbody tr:nth-child(even) td { background: var(--superficie); }
.manual tr { break-inside: avoid; }
.manual td:first-child { overflow-wrap: anywhere; }

.manual ol.sumario { columns: 2; column-gap: 10mm; margin: 0 0 6mm; padding: 5mm 6mm 5mm 12mm; border: 2px solid var(--borda-ouro);
                     border-radius: 4mm; background: var(--superficie); font-family: var(--fonte-epica); font-weight: 700; }
.manual ol.sumario li { margin: 1mm 0; break-inside: avoid; }
.manual a { color: var(--primaria); text-decoration: none; }
"""


def montar_html():
    css_site = (RAIZ / 'View' / 'Estilo' / 'style.css').as_uri()
    return f"""<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="utf-8">
<title>Manual técnico — O Guardião dos Dados</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700;900&family=Cinzel:wght@600;700;800&display=block" rel="stylesheet">
<link rel="stylesheet" href="{css_site}">
<style>{CSS_IMPRESSAO}</style>
</head><body>
<section class="capa">
    {capa()}
    <p class="capa-subtitulo">MANUAL TÉCNICO</p>
    <p class="capa-descricao">Quiz web sobre segurança da informação e LGPD: funcionamento, tecnologias,
       funções, páginas, variáveis e onde alterar cada coisa.</p>
    <div class="capa-dados">
        <div><strong>Autor:</strong> Bruno Fioravanti</div>
        <div><strong>Projeto:</strong> Atividade Extensionista II — Tecnologia Aplicada à Inclusão Digital</div>
        <div><strong>Gerado em:</strong> {date.today():%d/%m/%Y}</div>
    </div>
</section>
<main class="manual">
{corpo_do_manual()}
</main>
</body></html>"""


def main():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as pasta:
        pagina = Path(pasta) / 'manual.html'
        pagina.write_text(montar_html(), encoding='utf-8')
        destino = Path(pasta) / 'manual.pdf'
        imprimir_pdf(pagina, destino, pasta)
        SAIDA.parent.mkdir(exist_ok=True)
        shutil.copyfile(destino, SAIDA)
    print(f'PDF gerado: {SAIDA}')


if __name__ == '__main__':
    main()
