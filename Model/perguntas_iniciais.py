"""Perguntas de exemplo carregadas na criação do banco (ou ao restaurar pela área administrativa).

Campos: enunciado, alternativas (5), correta (índice 0-4), comentario (texto informativo exibido após responder).
"""

PERGUNTAS_INICIAIS = [
    {
        'enunciado': (
            'Um mensageiro misterioso envia um pergaminho urgente dizendo que sua conta será bloqueada '
            'em 10 minutos caso você não clique em um link e informe sua senha. Que ameaça é essa e como agir?'
        ),
        'alternativas': [
            'É um procedimento padrão de segurança; clique rápido para não perder o acesso.',
            'Trata-se de Phishing (engenharia social); não clique no link e verifique pelo canal oficial.',
            'Responda à mensagem enviando apenas metade da sua senha para confirmar a identidade.',
            'Encaminhe o link para todos os colegas de equipe testarem em seus computadores.',
            'Desative o antivírus temporariamente antes de abrir o link para evitar bloqueios.',
        ],
        'correta': 1,
        'comentario': (
            'O Phishing usa senso de urgência ou medo para enganar a vítima e capturar credenciais. '
            'Nunca clique em links suspeitos: acesse o serviço digitando o endereço oficial no navegador '
            'e comunique a equipe de Segurança da Informação.'
        ),
    },
    {
        'enunciado': (
            'Segundo a LGPD (Lei Geral de Proteção de Dados — Lei nº 13.709/2018), qual das opções abaixo '
            'é classificada como um Dado Pessoal Sensível, exigindo proteção ainda mais rigorosa?'
        ),
        'alternativas': [
            'O endereço comercial público de uma empresa.',
            'O número do CNPJ de um fornecedor.',
            'Dados sobre saúde, biometria, origem racial ou convicção religiosa de uma pessoa.',
            'O cargo profissional informado em um crachá corporativo.',
            'O nome de fantasia de uma loja virtual.',
        ],
        'correta': 2,
        'comentario': (
            'Pelo Art. 5º, II da LGPD, dados pessoais sensíveis incluem origem racial ou étnica, convicção '
            'religiosa, opinião política, filiação a sindicato, dados referentes à saúde, à vida sexual e '
            'dados genéticos ou biométricos, pois seu uso indevido pode gerar discriminação.'
        ),
    },
    {
        'enunciado': (
            'Para proteger os portões da Cidadela Digital, apenas uma senha simples não basta. '
            'Qual é a melhor prática para fortalecer o acesso às suas contas?'
        ),
        'alternativas': [
            'Usar a mesma senha em todos os sistemas para nunca esquecê-la.',
            'Anotar a senha em um adesivo colado na borda do monitor.',
            'Usar datas de aniversário ou sequências como "123456" para digitar mais rápido.',
            'Combinar senhas longas e únicas com a Autenticação em Múltiplos Fatores (MFA / 2FA).',
            'Compartilhar sua senha com um colega de confiança para emergências.',
        ],
        'correta': 3,
        'comentario': (
            'Senhas são individuais e intransferíveis. A combinação de senhas fortes e exclusivas (ou um '
            'gerenciador de senhas) com o segundo fator de autenticação (MFA/2FA) impede invasões mesmo '
            'que a senha seja descoberta.'
        ),
    },
    {
        'enunciado': (
            'Um cadastro para sorteio de brindes exige CPF, religião, tipo sanguíneo e histórico médico, '
            'embora precise apenas de nome e e-mail para contato. Qual princípio da LGPD está sendo violado?'
        ),
        'alternativas': [
            'Princípio da Necessidade (minimização de dados), que limita a coleta ao mínimo essencial.',
            'Princípio da Portabilidade Obrigatória Irrestrita.',
            'Princípio do Anonimato Total da Internet.',
            'Princípio da Publicidade Universal dos Dados.',
            'Nenhum princípio, pois coletar dados extras sempre melhora a segurança.',
        ],
        'correta': 0,
        'comentario': (
            'O Princípio da Necessidade (Art. 6º, III da LGPD) determina que o tratamento de dados deve se '
            'limitar ao mínimo necessário para a realização de suas finalidades, com abrangência dos dados '
            'pertinentes, proporcionais e não excessivos.'
        ),
    },
    {
        'enunciado': (
            'Pela LGPD, quem é a pessoa natural a quem se referem os dados pessoais que são objeto de '
            'tratamento e que possui o direito de solicitar acesso, correção ou eliminação desses dados?'
        ),
        'alternativas': [
            'O Operador de Firewall.',
            'O Titular dos Dados.',
            'O Invasor Externo.',
            'O Provedor de Internet.',
            'O Desenvolvedor do Navegador.',
        ],
        'correta': 1,
        'comentario': (
            'O Titular (Art. 5º, V e Art. 18 da LGPD) é a pessoa física dona dos dados. A lei garante ao '
            'titular direitos como confirmação da existência de tratamento, acesso aos dados, correção de '
            'dados incompletos e revogação do consentimento.'
        ),
    },
]
