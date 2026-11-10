"""Gráficos de pizza (acertos x erros) desenhados como SVG no servidor, sem biblioteca JavaScript."""
from math import cos, pi, sin

from Model.repositorio import percentual_acerto


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
    inicio = -pi / 2  # topo do círculo
    for rotulo, classe, valor, percentual in partes:
        if not valor:
            continue
        fracao = valor / total
        if fracao == 1:
            # Um arco SVG não fecha um círculo inteiro: usa dois semicírculos.
            d = 'M 0 -1 A 1 1 0 1 1 0 1 A 1 1 0 1 1 0 -1 Z'
        else:
            fim = inicio + fracao * 2 * pi
            arco_grande = 1 if fracao > 0.5 else 0
            d = (f'M 0 0 L {cos(inicio):.4f} {sin(inicio):.4f} '
                 f'A 1 1 0 {arco_grande} 1 {cos(fim):.4f} {sin(fim):.4f} Z')
            inicio = fim
        fatias.append({'rotulo': rotulo, 'classe': classe, 'valor': valor, 'percentual': percentual, 'd': d})
    return fatias
