"""Gráficos de pizza (acertos x erros) desenhados como SVG no servidor, sem biblioteca JavaScript."""
from math import cos, pi, sin

from markupsafe import Markup

from Model.repositorio import percentual_acerto

PROPRIEDADES_PERCENTUAIS = {'width', 'height', 'left'}


def estilo_percentual(propriedade, valor):
    """Atributo style com uma medida em %, ex.: estilo_percentual('width', 80) -> style="width: 80.0%".

    Usado nas barras dos gráficos e na barra de progresso. Gerar o atributo inteiro (em vez de escrever
    style="width: {{ valor }}%" no template) evita os falsos erros do verificador de CSS do VS Code e garante que
    só um número entre no CSS.
    """
    if propriedade not in PROPRIEDADES_PERCENTUAIS:
        raise ValueError(f'Propriedade não permitida: {propriedade}')
    percentual = min(max(float(valor or 0), 0.0), 100.0)
    return Markup(f'style="{propriedade}: {percentual:.1f}%"')


def fatias_pizza(acertos, erros):
    """Fatias de uma pizza de raio 1 centrada em (0, 0), começando no topo e seguindo no sentido horário.

    Retorna uma lista de {'rotulo', 'classe', 'valor', 'percentual', 'd'} ('d' é o caminho SVG da fatia),
    ou lista vazia quando não há respostas. Fatias com valor zero não são desenhadas.
    """
    total = acertos + erros
    if not total:
        return []
    percentual_acertos = percentual_acerto(acertos, total)
    partes = [
        ('Acertos', 'fatia-acertos', acertos, percentual_acertos),
        ('Erros', 'fatia-erros', erros, 100 - percentual_acertos),
    ]

    fatias = []
    inicio = -pi / 2
    for rotulo, classe, valor, percentual in partes:
        if not valor:
            continue
        fracao = valor / total
        if fracao == 1:
            d = 'M 0 -1 A 1 1 0 1 1 0 1 A 1 1 0 1 1 0 -1 Z'
        else:
            fim = inicio + fracao * 2 * pi
            arco_grande = 1 if fracao > 0.5 else 0
            d = (f'M 0 0 L {cos(inicio):.4f} {sin(inicio):.4f} '
                 f'A 1 1 0 {arco_grande} 1 {cos(fim):.4f} {sin(fim):.4f} Z')
            inicio = fim
        fatias.append({'rotulo': rotulo, 'classe': classe, 'valor': valor, 'percentual': percentual, 'd': d})
    return fatias
