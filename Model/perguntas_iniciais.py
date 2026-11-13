"""Banco de perguntas padrão. A cada jornada são sorteadas PERGUNTAS_POR_JORNADA delas (Model/config.py).

São gravadas na criação do banco. Num banco que já existe, perguntas novas acrescentadas aqui entram pelo botão
"Adicionar provações padrão que faltam" da área administrativa (compara pelo enunciado, não duplica).

Campos: enunciado, alternativas (5), correta (índice 0-4), comentario (texto informativo exibido após responder).
Escreva as alternativas erradas com tamanho parecido com o da correta, para o tamanho não entregar a resposta.
"""

PERGUNTAS_INICIAIS = [
    {
        'enunciado': (
            'Um mensageiro misterioso envia um pergaminho urgente dizendo que sua conta será bloqueada '
            'em 10 minutos caso você não clique em um link e informe sua senha. Que ameaça é essa e como agir?'
        ),
        'alternativas': [
            'É um aviso legítimo de segurança; clique no link e troque a senha antes do prazo.',
            'É Phishing (engenharia social); não clique e confirme pelo canal oficial do serviço.',
            'É spam comum; basta responder pedindo para ser removido da lista de envios.',
            'É um vírus já instalado; formate o computador antes de abrir outros e-mails.',
            'É um erro do sistema; informe a senha só se a mensagem tiver o logotipo da empresa.',
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
            'Nome completo, CPF e endereço residencial de um cliente cadastrado.',
            'Número do cartão de crédito, senha do banco e saldo da conta corrente.',
            'Dados de saúde, biometria, origem racial ou convicção religiosa.',
            'E-mail, telefone celular e perfis em redes sociais da pessoa.',
            'Cargo, salário e histórico profissional informados no currículo.',
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
            'Trocar a mesma senha curta todo mês, mudando apenas o número final.',
            'Usar uma única senha bem complexa em todos os serviços, sem anotá-la.',
            'Criar senhas com nome e data de nascimento, fáceis de lembrar.',
            'Usar senhas longas e únicas junto com a verificação em duas etapas (2FA).',
            'Guardar todas as senhas num arquivo "senhas.txt" na área de trabalho.',
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
            'Princípio da Necessidade: a coleta deve se limitar ao mínimo essencial.',
            'Princípio do Livre Acesso: o titular deve consultar seus dados de graça.',
            'Princípio da Transparência: as regras do sorteio devem estar publicadas.',
            'Princípio da Qualidade dos Dados: as informações devem estar atualizadas.',
            'Nenhum, pois o participante pode simplesmente desistir do sorteio.',
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
            'O Controlador dos Dados.',
            'O Titular dos Dados.',
            'O Operador dos Dados.',
            'O Encarregado (DPO).',
            'A Autoridade Nacional (ANPD).',
        ],
        'correta': 1,
        'comentario': (
            'O Titular (Art. 5º, V e Art. 18 da LGPD) é a pessoa física dona dos dados. A lei garante ao '
            'titular direitos como confirmação da existência de tratamento, acesso aos dados, correção de '
            'dados incompletos e revogação do consentimento.'
        ),
    },

    {
        'enunciado': (
            'Toda organização que trata dados pessoais deve indicar um "Encarregado" (também chamado de DPO). '
            'Qual é o papel dessa pessoa segundo a LGPD?'
        ),
        'alternativas': [
            'Decidir quais dados a organização coleta e para quais finalidades.',
            'Aplicar multas às empresas que descumprem as regras de proteção de dados.',
            'Executar o tratamento dos dados em nome da organização que o contratou.',
            'Impedir que a organização colete qualquer dado pessoal, em qualquer caso.',
            'Ser o canal de comunicação entre a organização, os titulares e a ANPD.',
        ],
        'correta': 4,
        'comentario': (
            'Pelo Art. 5º, VIII e Art. 41 da LGPD, o Encarregado é a pessoa indicada para atuar como canal de '
            'comunicação entre o controlador, os titulares e a ANPD: recebe reclamações, presta esclarecimentos '
            'e orienta a equipe sobre as boas práticas de proteção de dados.'
        ),
    },
    {
        'enunciado': (
            'Uma empresa descumpriu a LGPD e foi punida. Qual é o limite da multa simples que a lei permite '
            'aplicar por infração?'
        ),
        'alternativas': [
            'Até 10% do faturamento mundial da empresa, sem limite de valor.',
            'Um valor fixo de R$ 5 mil por infração, para empresas de qualquer porte.',
            'Até 2% do faturamento no Brasil, limitada a R$ 50 milhões por infração.',
            'Até 20% do lucro anual, dividido entre os titulares que foram afetados.',
            'Não há multa: a LGPD prevê apenas advertências e orientações.',
        ],
        'correta': 2,
        'comentario': (
            'O Art. 52 da LGPD prevê sanções como advertência, multa simples de até 2% do faturamento '
            '(limitada a R$ 50 milhões por infração), multa diária, publicização da infração, bloqueio e '
            'eliminação dos dados. A punição também atinge a reputação da organização.'
        ),
    },
    {
        'enunciado': (
            'Você descobriu que uma empresa usa seus dados de forma irregular e não resolveu sua reclamação. '
            'Qual órgão é responsável por fiscalizar o cumprimento da LGPD no Brasil?'
        ),
        'alternativas': [
            'A ANPD — Autoridade Nacional de Proteção de Dados.',
            'A ANATEL — Agência Nacional de Telecomunicações.',
            'O CGI.br — Comitê Gestor da Internet no Brasil.',
            'A Polícia Federal, pela delegacia de crimes cibernéticos.',
            'O Banco Central, que regula as empresas que guardam dados.',
        ],
        'correta': 0,
        'comentario': (
            'A ANPD (Art. 55-A e seguintes da LGPD) zela pela proteção de dados, fiscaliza, aplica sanções e '
            'recebe petições dos titulares contra quem trata seus dados. O Procon e o Judiciário também podem '
            'ser acionados.'
        ),
    },
    {
        'enunciado': (
            'Uma clínica contrata uma empresa de software para armazenar os prontuários dos pacientes. É a '
            'clínica quem decide quais dados são coletados e para quê. Pela LGPD, qual é o papel de cada uma?'
        ),
        'alternativas': [
            'A empresa de software é a controladora; a clínica é a operadora.',
            'A clínica é a encarregada; a empresa de software é a controladora.',
            'As duas são controladoras, pois ambas têm acesso aos prontuários.',
            'A clínica é a controladora; a empresa de software é a operadora.',
            'A clínica é a titular dos dados; a empresa de software é a operadora.',
        ],
        'correta': 3,
        'comentario': (
            'Controlador é quem toma as decisões sobre o tratamento (Art. 5º, VI); operador é quem trata os '
            'dados em nome do controlador (Art. 5º, VII). Os dois têm deveres de segurança e podem responder '
            'por danos causados aos titulares.'
        ),
    },
    {
        'enunciado': (
            'Uma loja virtual sofreu um vazamento que expôs nomes, endereços e números de cartão de milhares de '
            'clientes. O que a LGPD exige da loja?'
        ),
        'alternativas': [
            'Corrigir a falha em silêncio e avisar os clientes só se alguém reclamar.',
            'Comunicar o incidente à ANPD e aos titulares afetados, com riscos e medidas.',
            'Avisar apenas a polícia, já que o vazamento foi causado por criminosos.',
            'Publicar a lista dos dados vazados para cada cliente conferir se foi afetado.',
            'Comunicar apenas aos sócios, pois o incidente afeta o valor da empresa.',
        ],
        'correta': 1,
        'comentario': (
            'O Art. 48 da LGPD obriga o controlador a comunicar à ANPD e aos titulares incidentes de segurança '
            'que possam causar risco ou dano relevante, descrevendo os dados afetados, os riscos e as medidas '
            'adotadas. Esconder o vazamento agrava a situação.'
        ),
    },
    {
        'enunciado': (
            'Você aceitou receber ofertas de uma loja por e-mail, mas se arrependeu. O que a LGPD diz sobre '
            'esse consentimento?'
        ),
        'alternativas': [
            'Só pode ser revogado ao fim do prazo informado no termo que você aceitou.',
            'Pode ser revogado, mas a loja pode cobrar uma taxa pelo cancelamento.',
            'Não pode ser revogado, mas você pode pedir para receber menos e-mails.',
            'Só pode ser revogado por escrito, com firma reconhecida em cartório.',
            'Pode ser revogado a qualquer momento, de forma gratuita e facilitada.',
        ],
        'correta': 4,
        'comentario': (
            'O consentimento deve ser livre, informado e para uma finalidade determinada (Art. 5º, XII), e pode '
            'ser revogado a qualquer momento por procedimento gratuito e facilitado (Art. 8º, § 5º). Procure '
            'o link de descadastro ou o canal do Encarregado.'
        ),
    },
    {
        'enunciado': (
            'Um aplicativo de jogos infantil quer coletar dados pessoais de crianças. O que a LGPD exige nesse caso?'
        ),
        'alternativas': [
            'Consentimento específico e em destaque de um dos pais ou responsável.',
            'Consentimento da própria criança, desde que ela saiba ler os termos de uso.',
            'Autorização da escola onde a criança estuda, renovada a cada ano letivo.',
            'Nenhuma regra especial: valem as mesmas condições aplicadas aos adultos.',
            'Autorização judicial prévia para cada dado coletado pelo aplicativo.',
        ],
        'correta': 0,
        'comentario': (
            'O Art. 14 da LGPD determina que o tratamento de dados de crianças seja feito no seu melhor '
            'interesse e com consentimento específico e em destaque de pelo menos um dos pais ou responsável '
            'legal. Os pais devem acompanhar quais aplicativos os filhos usam.'
        ),
    },
    {
        'enunciado': (
            'Uma pesquisa transforma os dados dos participantes de modo que ninguém consiga mais descobrir a '
            'quem eles pertencem, nem com esforço razoável. Como a LGPD trata esses dados anonimizados?'
        ),
        'alternativas': [
            'Continuam sendo dados pessoais e exigem o consentimento de cada participante.',
            'Passam a ser dados sensíveis, por terem sido modificados pela pesquisa.',
            'Deixam de ser dados pessoais, se a anonimização não puder ser revertida.',
            'Devem ser apagados em até 30 dias, pois não podem ser usados em estatísticas.',
            'Passam a pertencer à ANPD, que decide quem pode usá-los em outras pesquisas.',
        ],
        'correta': 2,
        'comentario': (
            'Pelo Art. 12 da LGPD, dados anonimizados não são considerados dados pessoais, salvo quando o '
            'processo de anonimização puder ser revertido. Por isso pesquisas e estatísticas preferem dados '
            'anônimos: geram conhecimento sem expor ninguém.'
        ),
    },

    {
        'enunciado': (
            'O Objetivo de Desenvolvimento Sustentável 16 da ONU ("Paz, Justiça e Instituições Eficazes") tem '
            'uma meta ligada à informação e às liberdades das pessoas. Qual é ela?'
        ),
        'alternativas': [
            'Garantir internet gratuita de alta velocidade em todos os municípios.',
            'Proibir a coleta de dados pessoais por empresas privadas em todos os países.',
            'Criar uma única lei mundial de proteção de dados, igual para todos os países.',
            'Assegurar o acesso público à informação e proteger as liberdades fundamentais.',
            'Ampliar o número de computadores nas escolas públicas de ensino fundamental.',
        ],
        'correta': 3,
        'comentario': (
            'A meta 16.10 do ODS 16 busca assegurar o acesso público à informação e proteger as liberdades '
            'fundamentais. Proteger dados pessoais faz parte disso: sem privacidade, as pessoas ficam expostas '
            'a fraudes, discriminação e abusos, e as instituições perdem a confiança da sociedade.'
        ),
    },
    {
        'enunciado': (
            'Desde 2022, como a Constituição Federal brasileira trata a proteção dos dados pessoais?'
        ),
        'alternativas': [
            'Como uma obrigação só das empresas privadas, sem valer para o poder público.',
            'Como um direito fundamental de todos, inclusive nos meios digitais.',
            'Como um tema exclusivo da LGPD, sem nenhuma menção na Constituição.',
            'Como um direito apenas de quem tem conta em banco ou em redes sociais.',
            'Como um dever do cidadão, que responde sozinho pela segurança dos dados.',
        ],
        'correta': 1,
        'comentario': (
            'A Emenda Constitucional nº 115/2022 incluiu no Art. 5º, LXXIX, o direito à proteção dos dados '
            'pessoais, inclusive nos meios digitais. Esse direito vale para todos, sem distinção, o que reforça '
            'a ideia do ODS 16 de instituições justas e inclusivas.'
        ),
    },

    {
        'enunciado': (
            'Chega um SMS: "Sua encomenda está retida. Pague a taxa de R$ 4,90 para liberar a entrega: '
            '[link]". Você não estava esperando nenhuma compra. O que fazer?'
        ),
        'alternativas': [
            'Pagar a taxa, pois o valor é baixo e evita que a encomenda seja devolvida.',
            'Clicar no link só para conferir os dados, sem digitar nenhuma informação.',
            'Não clicar no link e, na dúvida, consultar o rastreio no site oficial.',
            'Responder ao SMS pedindo o código de rastreio antes de fazer o pagamento.',
            'Pagar a taxa com cartão de crédito, que é mais seguro do que PIX ou boleto.',
        ],
        'correta': 2,
        'comentario': (
            'Isso é smishing: phishing por SMS. A taxa baixa serve para você não desconfiar, e o objetivo é '
            'roubar dados do cartão ou instalar programas maliciosos. Consulte sempre pelo site ou aplicativo '
            'oficial, nunca pelo link recebido.'
        ),
    },
    {
        'enunciado': (
            'Alguém se passando por atendente de uma loja diz que enviou um código de 6 dígitos por SMS para '
            '"confirmar seu cadastro" e pede que você o informe. O que esse pedido indica?'
        ),
        'alternativas': [
            'Uma tentativa de clonar sua conta: nunca informe códigos de verificação.',
            'Um procedimento normal: lojas usam esse código para confirmar cadastros.',
            'Um risco pequeno: o código expira em minutos e não dá acesso a nenhuma conta.',
            'Um pedido seguro, desde que a ligação venha de um número da sua cidade.',
            'Um pedido aceitável, desde que você informe só os três primeiros dígitos.',
        ],
        'correta': 0,
        'comentario': (
            'Códigos de verificação são a chave para ativar sua conta em outro aparelho. Com ele, o golpista '
            'assume seu WhatsApp e pede dinheiro aos seus contatos. Nunca compartilhe esses códigos e ative a '
            'confirmação em duas etapas do aplicativo.'
        ),
    },
    {
        'enunciado': (
            'Você recebe uma ligação de alguém que diz ser da "central de segurança do seu banco": houve uma '
            'compra suspeita e, para cancelá-la, você deve informar sua senha e transferir o saldo para uma '
            '"conta segura". O que fazer?'
        ),
        'alternativas': [
            'Seguir as instruções, pois o atendente já sabia seu nome e os dados do cartão.',
            'Informar a senha, mas recusar a transferência para a conta indicada por ele.',
            'Fazer a transferência só se o atendente informar um número de protocolo.',
            'Pedir que ele envie um SMS com o link do banco para confirmar a operação.',
            'Desligar e ligar você mesmo para o número oficial do verso do cartão.',
        ],
        'correta': 4,
        'comentario': (
            'Bancos nunca pedem senha nem transferências para "conta segura". É o golpe da falsa central, uma '
            'forma de engenharia social que usa urgência e medo. Desligue e ligue pelo número oficial, de '
            'preferência de outro aparelho.'
        ),
    },
    {
        'enunciado': (
            'Você está numa praça com Wi-Fi público e aberto (sem senha) e precisa consultar sua conta bancária. '
            'Qual é a atitude mais segura?'
        ),
        'alternativas': [
            'Conectar à rede aberta com o nome mais parecido com o do estabelecimento.',
            'Usar a rede aberta, mas abrir o banco na aba anônima do navegador.',
            'Usar a rede aberta e desativar o antivírus para a conexão ficar estável.',
            'Usar os dados móveis do celular ou deixar para acessar numa rede confiável.',
            'Usar a rede aberta e salvar a senha do banco no navegador para digitar menos.',
        ],
        'correta': 3,
        'comentario': (
            'Em redes abertas, outras pessoas conectadas podem tentar interceptar o tráfego ou criar redes '
            'falsas com nomes parecidos. Para serviços sensíveis, use os dados móveis ou uma rede de confiança, '
            'e mantenha o celular atualizado.'
        ),
    },
    {
        'enunciado': (
            'O computador de um pequeno comércio foi atacado por um ransomware: todos os arquivos foram '
            'criptografados e os criminosos exigem pagamento. Qual medida, tomada antes, mais ajudaria agora?'
        ),
        'alternativas': [
            'Ter guardado as senhas do sistema num arquivo dentro do próprio computador.',
            'Ter backups recentes, guardados fora do computador que foi atacado.',
            'Ter desativado as atualizações automáticas para evitar mudanças inesperadas.',
            'Ter uma cópia dos arquivos em outra pasta do mesmo disco do computador.',
            'Ter reservado dinheiro para pagar o resgate e recuperar os arquivos.',
        ],
        'correta': 1,
        'comentario': (
            'Backups regulares, guardados separados do computador (na nuvem ou num disco desconectado), '
            'permitem recuperar os arquivos sem negociar com criminosos. Atualizações em dia e cuidado com '
            'anexos e links ajudam a evitar a infecção.'
        ),
    },
    {
        'enunciado': (
            'Um site mostra o cadeado e o endereço começa com "https://". O que isso garante?'
        ),
        'alternativas': [
            'Que o site foi verificado pelo governo e está autorizado a vender produtos.',
            'Que o site é o oficial da empresa cujo nome aparece no endereço da página.',
            'Que o site não contém vírus e é seguro para baixar arquivos.',
            'Que seus dados não serão compartilhados pelo site com outras empresas.',
            'Que a conexão é criptografada, mas não que o site seja legítimo.',
        ],
        'correta': 4,
        'comentario': (
            'O HTTPS protege os dados no caminho entre você e o site, mas qualquer um pode obter um certificado, '
            'inclusive golpistas. Confira o endereço com atenção (letras trocadas, domínios estranhos) e '
            'desconfie de preços bons demais.'
        ),
    },
    {
        'enunciado': (
            'Você encontra um pendrive no estacionamento do trabalho com a etiqueta "Salários 2025". '
            'Qual é a atitude correta?'
        ),
        'alternativas': [
            'Conectar no seu computador, com o antivírus ligado, para achar o dono.',
            'Conectar num computador antigo, que não tenha nenhum dado importante.',
            'Não conectar em nenhum computador e entregar à equipe de TI ou segurança.',
            'Abrir só as planilhas, que não conseguem instalar programas no computador.',
            'Levar para casa e verificar no computador pessoal, fora da rede da empresa.',
        ],
        'correta': 2,
        'comentario': (
            'Deixar dispositivos "esquecidos" com rótulos curiosos é uma técnica de engenharia social chamada '
            'baiting (isca). Ao conectar o pendrive, um programa malicioso pode infectar o computador e a rede. '
            'A curiosidade é a arma do atacante.'
        ),
    },
    {
        'enunciado': (
            'Feliz com a viagem, você quer postar nas redes sociais uma foto do seu cartão de embarque, com o '
            'código de barras visível, marcando sua localização em tempo real. Qual é o risco?'
        ),
        'alternativas': [
            'O código pode dar acesso à reserva, e a localização mostra a casa vazia.',
            'Nenhum, pois o cartão de embarque perde a validade assim que o voo decola.',
            'Nenhum, desde que o perfil esteja configurado para mostrar posts só a amigos.',
            'Só a companhia aérea consegue ler o código, então apenas o nome fica exposto.',
            'O único risco é a rede social usar a foto em anúncios de agências de viagem.',
        ],
        'correta': 0,
        'comentario': (
            'O código do cartão de embarque traz seu nome e o código da reserva, que permitem alterar ou '
            'cancelar o voo. A localização em tempo real avisa que você não está em casa. Prefira postar '
            'depois e sem documentos à vista: é o cuidado contra a exposição excessiva (oversharing).'
        ),
    },
    {
        'enunciado': (
            'Um site de receitas onde você tinha cadastro sofreu um vazamento de senhas. Por que isso pode '
            'colocar em risco também o seu e-mail e o seu banco?'
        ),
        'alternativas': [
            'Porque os sites compartilham entre si os cadastros dos seus clientes.',
            'Não há risco, pois senhas vazadas ficam criptografadas e não podem ser usadas.',
            'Porque o vazamento instala um vírus em todos os aparelhos usados no cadastro.',
            'Se você repetiu a senha, os criminosos vão testá-la nos outros serviços.',
            'Porque o site de receitas tinha acesso aos seus e-mails e às suas transações.',
        ],
        'correta': 3,
        'comentario': (
            'Criminosos testam as senhas vazadas em vários serviços, um ataque chamado credential stuffing. '
            'Use uma senha diferente para cada serviço (um gerenciador de senhas ajuda), ative a verificação '
            'em duas etapas e troque a senha sempre que souber de um vazamento.'
        ),
    },
    {
        'enunciado': (
            'Você recebe uma mensagem: "Oi, mãe/pai! Troquei de número, salva esse. Preciso pagar uma conta '
            'urgente, me faz um PIX?". O que fazer?'
        ),
        'alternativas': [
            'Fazer o PIX se a foto do perfil e o jeito de escrever forem iguais aos da pessoa.',
            'Ligar para o número antigo do familiar ou confirmar por outro meio antes.',
            'Fazer primeiro um PIX de valor pequeno, para testar se o número é verdadeiro.',
            'Pedir que a pessoa mande um áudio e, se a voz parecer a dela, fazer o PIX.',
            'Fazer o PIX para a conta indicada, desde que seja de um banco conhecido.',
        ],
        'correta': 1,
        'comentario': (
            'É o golpe do falso parente: o criminoso usa a foto da pessoa (copiada das redes sociais) e cria '
            'urgência. Confirme sempre por ligação para o número conhecido ou com uma pergunta que só a pessoa '
            'saberia responder. O PIX é instantâneo e difícil de reverter.'
        ),
    },
]
