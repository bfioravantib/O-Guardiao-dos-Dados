"""Perguntas de exemplo carregadas na criação do banco (ou ao restaurar pela área administrativa).

Campos: enunciado, alternativas (5), correta (índice 0-4), comentario (texto informativo exibido após responder).
"""

PERGUNTAS_INICIAIS = [
    {
        'enunciado': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quis nostrud exercitation ullamco laboris?',
        'alternativas': [
            'Lorem ipsum dolor sit amet.',
            'Consectetur adipiscing elit sed do.',
            'Eiusmod tempor incididunt ut labore.',
            'Et dolore magna aliqua ut enim.',
            'Ad minim veniam quis nostrud.',
        ],
        'correta': 1,
        'comentario': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation.',
    },
    {
        'enunciado': 'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur?',
        'alternativas': [
            'Excepteur sint occaecat cupidatat.',
            'Non proident sunt in culpa.',
            'Qui officia deserunt mollit anim.',
            'Id est laborum sed ut perspiciatis.',
            'Unde omnis iste natus error.',
        ],
        'correta': 3,
        'comentario': 'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt.',
    },
    {
        'enunciado': 'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium?',
        'alternativas': [
            'Totam rem aperiam eaque ipsa.',
            'Quae ab illo inventore veritatis.',
            'Et quasi architecto beatae vitae.',
            'Dicta sunt explicabo nemo enim.',
            'Ipsam voluptatem quia voluptas.',
        ],
        'correta': 0,
        'comentario': 'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto.',
    },
    {
        'enunciado': 'Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur?',
        'alternativas': [
            'Magni dolores eos qui ratione.',
            'Voluptatem sequi nesciunt neque.',
            'Porro quisquam est qui dolorem.',
            'Ipsum quia dolor sit amet.',
            'Consectetur adipisci velit sed quia.',
        ],
        'correta': 4,
        'comentario': 'Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.',
    },
    {
        'enunciado': 'At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum?',
        'alternativas': [
            'Deleniti atque corrupti quos dolores.',
            'Et quas molestias excepturi sint.',
            'Occaecati cupiditate non provident.',
            'Similique sunt in culpa qui officia.',
            'Deserunt mollitia animi id est.',
        ],
        'correta': 2,
        'comentario': 'At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati.',
    },
]
