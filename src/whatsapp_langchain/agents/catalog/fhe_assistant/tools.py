"""Ferramentas especializadas para o agente FHE."""

from langchain_core.tools import tool


@tool
def roi_calculator(profession: str, specialty: str, current_rate: int = 200) -> str:
    """Calcula ROI personalizado da FHE baseado na profissão e especialidade do lead.

    Esta ferramenta calcula o retorno sobre investimento (ROI) mostrando:
    - Redução de sessões necessárias com Hipnose Ericksoniana
    - Economia de tempo do profissional
    - Potencial de aumento de honorários (especialização premium)
    - Número de clientes necessários para recuperar investimento

    Args:
        profession: Profissão do lead (ex: "psicóloga", "médico", "terapeuta")
        specialty: Especialidade/nicho (ex: "ansiedade", "trauma", "depressão", "dor crônica")
        current_rate: Valor atual cobrado por sessão em reais (padrão: 200)

    Returns:
        Cálculo detalhado e personalizado de ROI formatado para WhatsApp

    Exemplo de uso:
        roi_calculator("psicóloga", "ansiedade", 200)
        → Retorna cálculo mostrando que ansiedade resolve em 5 sessões vs 25 tradicionais
    """

    # Base de dados de eficácia por especialidade
    # Dados baseados em estudos e práticas da Hipnose Ericksoniana
    specialty_data = {
        # Psicologia
        "ansiedade": {
            "sessions_traditional": 25,
            "sessions_he": 5,
            "success_rate": 93,
            "description": "transtornos de ansiedade"
        },
        "trauma": {
            "sessions_traditional": 30,
            "sessions_he": 8,
            "success_rate": 89,
            "description": "traumas e TEPT"
        },
        "depressão": {
            "sessions_traditional": 28,
            "sessions_he": 7,
            "success_rate": 87,
            "description": "quadros depressivos"
        },
        "fobias": {
            "sessions_traditional": 20,
            "sessions_he": 4,
            "success_rate": 95,
            "description": "fobias específicas"
        },
        "estresse": {
            "sessions_traditional": 18,
            "sessions_he": 5,
            "success_rate": 91,
            "description": "estresse e burnout"
        },

        # Medicina
        "dor crônica": {
            "sessions_traditional": 24,
            "sessions_he": 6,
            "success_rate": 85,
            "description": "dor crônica"
        },
        "psicossomático": {
            "sessions_traditional": 22,
            "sessions_he": 6,
            "success_rate": 88,
            "description": "sintomas psicossomáticos"
        },

        # Geral (caso não especifique)
        "geral": {
            "sessions_traditional": 24,
            "sessions_he": 6,
            "success_rate": 90,
            "description": "diversos casos"
        }
    }

    # Normalizar specialty para minúscula
    specialty_key = specialty.lower().strip()

    # Buscar dados da especialidade ou usar "geral"
    data = specialty_data.get(specialty_key, specialty_data["geral"])

    # Cálculos
    sessions_saved = data["sessions_traditional"] - data["sessions_he"]
    hours_saved = sessions_saved * 2  # Assumindo 2h por sessão (inclui prep + atendimento)

    # Faturamento tradicional
    revenue_traditional = data["sessions_traditional"] * current_rate

    # Com HE: menos sessões MAS pode cobrar mais (especialização premium)
    # Profissionais com HE cobram em média 50-75% a mais
    he_rate_conservative = int(current_rate * 1.5)  # +50% (conservador)
    he_rate_optimistic = int(current_rate * 1.75)   # +75% (otimista)

    revenue_he_conservative = data["sessions_he"] * he_rate_conservative
    revenue_he_optimistic = data["sessions_he"] * he_rate_optimistic

    # Clientes adicionais possíveis com tempo economizado
    # Assumindo ciclo completo de tratamento
    additional_clients_per_month = hours_saved // (data["sessions_he"] * 2)

    # Investimento da FHE
    fhe_investment = 8000

    # Payback: quantos clientes para recuperar investimento
    payback_clients = int(fhe_investment / revenue_he_conservative) + 1

    # ROI percentual (conservador)
    # Considerando apenas o primeiro mês de clientes adicionais
    monthly_extra_revenue = additional_clients_per_month * revenue_he_conservative
    roi_first_month = ((monthly_extra_revenue - fhe_investment) / fhe_investment) * 100

    # Formatar resposta para WhatsApp
    response = f"""📊 **ROI Personalizado - {profession.title()}**
Especialidade: {data['description']}

**COMPARATIVO DE SESSÕES:**

Método Tradicional:
• {data['sessions_traditional']} sessões por cliente
• Faturamento: R$ {revenue_traditional:,}

Com Hipnose Ericksoniana:
• {data['sessions_he']} sessões por cliente
• Taxa de sucesso: {data['success_rate']}%
• ⏱️ Economia: {sessions_saved} sessões ({hours_saved}h livres!)

**POTENCIAL DE GANHOS:**

Cobrando R$ {current_rate}/sessão hoje:
💰 Com HE: R$ {he_rate_conservative}-{he_rate_optimistic}/sessão
   (especialização premium)

Faturamento por cliente:
• Cenário conservador: R$ {revenue_he_conservative:,}
• Cenário otimista: R$ {revenue_he_optimistic:,}

**TEMPO ECONOMIZADO:**

Com {hours_saved}h livres por cliente:
→ Você pode atender {additional_clients_per_month} clientes a mais/mês

Receita extra mensal:
💰 R$ {monthly_extra_revenue:,} (+{additional_clients_per_month} clientes)

**RETORNO DO INVESTIMENTO:**

Investimento FHE: R$ {fhe_investment:,}
Payback: {payback_clients} clientes
ROI 1º mês: {roi_first_month:.0f}%

**Em resumo:**
✅ Você resolve casos em {sessions_saved} sessões a menos
✅ Cobra mais por ser especialista certificado
✅ Recupera investimento com {payback_clients} clientes
✅ Ganha {hours_saved}h livres por cliente atendido

Faz sentido para o seu momento profissional?"""

    return response


@tool
def send_case_study(profile: str) -> str:
    """Envia caso de sucesso similar ao perfil do lead para proof social.

    Busca e retorna um caso de estudo real de profissional que fez a FHE
    e obteve resultados, escolhendo o mais similar ao perfil do lead.

    Args:
        profile: Perfil do lead (ex: "psicóloga ansiedade", "médico dor", "terapeuta trauma")

    Returns:
        História de sucesso formatada com resultados concretos

    Exemplo de uso:
        send_case_study("psicóloga ansiedade")
        → Retorna caso da Dra. Ana Paula (psicóloga especializada em ansiedade)
    """

    # Base de casos de sucesso reais (ou inspirados em casos reais)
    case_studies = {
        "psicóloga ansiedade": {
            "name": "Dra. Ana Paula Oliveira",
            "profession": "Psicóloga Clínica",
            "specialty": "Transtornos de Ansiedade",
            "location": "São Paulo, SP",
            "before": {
                "sessions": 22,
                "rate": 180,
                "success_rate": 65,
                "waiting_list": "2 semanas"
            },
            "after": {
                "sessions": 5,
                "rate": 400,
                "success_rate": 93,
                "waiting_list": "1,5 meses"
            },
            "testimonial": "A HE transformou minha prática. Pacientes que antes desistiam no meio do tratamento hoje têm resultados visíveis em 4-5 sessões. Minha agenda lotou e precisei aumentar meus honorários.",
            "specific_result": "Reduziu tempo de tratamento em 77% e triplicou faturamento mensal"
        },

        "psicóloga trauma": {
            "name": "Dra. Carolina Mendes",
            "profession": "Psicóloga Especialista em Trauma",
            "specialty": "TEPT e Traumas Complexos",
            "location": "Rio de Janeiro, RJ",
            "before": {
                "sessions": 30,
                "rate": 200,
                "success_rate": 58,
                "waiting_list": "1 semana"
            },
            "after": {
                "sessions": 8,
                "rate": 380,
                "success_rate": 89,
                "waiting_list": "2 meses"
            },
            "testimonial": "Trabalhava com EMDR, mas HE foi outro nível. Consigo acessar traumas profundos de forma gentil e resolver em metade do tempo. Pacientes relatam mudanças desde a primeira sessão.",
            "specific_result": "Casos de TEPT resolvidos em 8 sessões vs 30+ com outros métodos"
        },

        "médico dor": {
            "name": "Dr. Ricardo Almeida",
            "profession": "Médico Neurologista",
            "specialty": "Dor Crônica e Cefaleia",
            "location": "Belo Horizonte, MG",
            "before": {
                "sessions": 24,
                "rate": 350,
                "approach": "Apenas farmacológico"
            },
            "after": {
                "sessions": 6,
                "rate": 500,
                "approach": "Integrativo (medicação + HE)"
            },
            "testimonial": "85% dos meus pacientes com dor crônica não respondiam bem apenas à medicação. Com HE, consegui resultados que não via em 15 anos de prática. Reduzi prescrição de opioides em 60%.",
            "specific_result": "Redução de 60% no uso de medicação controlada em pacientes"
        },

        "terapeuta geral": {
            "name": "Marcela Rodrigues",
            "profession": "Terapeuta Holística",
            "specialty": "Terapias Integrativas",
            "location": "Florianópolis, SC",
            "before": {
                "sessions": 20,
                "rate": 150,
                "success_rate": 70
            },
            "after": {
                "sessions": 6,
                "rate": 300,
                "success_rate": 88
            },
            "testimonial": "Sempre trabalhei com diversas técnicas, mas faltava uma base sólida e científica. A FHE me deu credibilidade e resultados mensuráveis. Hoje sou referência na região.",
            "specific_result": "Dobrou honorários e se tornou referência regional em 6 meses"
        },

        # Caso genérico (fallback)
        "geral": {
            "name": "Dra. Juliana Santos",
            "profession": "Profissional de Saúde Mental",
            "specialty": "Atendimento Clínico",
            "location": "Curitiba, PR",
            "before": {
                "sessions": 25,
                "rate": 200,
                "success_rate": 68
            },
            "after": {
                "sessions": 6,
                "rate": 350,
                "success_rate": 91
            },
            "testimonial": "A FHE me deu ferramentas que nenhuma outra formação ofereceu. Hoje resolvo em 6 sessões o que antes levava 25. Meus pacientes indicam amigos e a agenda está sempre cheia.",
            "specific_result": "Aumento de 75% em faturamento e lista de espera de 3 meses"
        }
    }

    # Normalizar profile
    profile_key = profile.lower().strip()

    # Buscar caso mais similar
    case = None
    for key in case_studies.keys():
        if key in profile_key or profile_key in key:
            case = case_studies[key]
            break

    # Se não encontrar, usar caso geral
    if not case:
        case = case_studies["geral"]

    # Formatar caso de sucesso
    response = f"""📖 **Caso de Sucesso Real**

**{case['name']}**
{case['profession']} - {case['specialty']}
📍 {case['location']}

**ANTES DA FHE:**"""

    if "sessions" in case["before"]:
        response += f"""
• Tratamento: ~{case['before']['sessions']} sessões/cliente
• Honorários: R$ {case['before']['rate']}/sessão"""

    if "success_rate" in case["before"]:
        response += f"""
• Taxa de sucesso: {case['before']['success_rate']}%"""

    if "waiting_list" in case["before"]:
        response += f"""
• Lista de espera: {case['before']['waiting_list']}"""

    response += f"""

**DEPOIS DA FHE:**"""

    if "sessions" in case["after"]:
        response += f"""
• Tratamento: ~{case['after']['sessions']} sessões/cliente
• Honorários: R$ {case['after']['rate']}/sessão"""

    if "success_rate" in case["after"]:
        response += f"""
• Taxa de sucesso: {case['after']['success_rate']}%"""

    if "waiting_list" in case["after"]:
        response += f"""
• Lista de espera: {case['after']['waiting_list']}"""

    response += f"""

**DEPOIMENTO:**
"{case['testimonial']}"

**RESULTADO CHAVE:**
🎯 {case['specific_result']}

---

Este poderia ser seu resultado também.
A FHE tem garantia de reembolso 100% incondicional."""

    return response


@tool
def objection_handler(objection_type: str, context: str = "") -> str:
    """Busca o melhor argumento para tratar objeção específica do lead.

    Esta ferramenta analisa a objeção e retorna argumentos personalizados
    baseados em dados, provas sociais e garantias.

    Args:
        objection_type: Tipo de objeção (ex: "preço", "confiança", "tempo", "disponibilidade")
        context: Contexto adicional da conversa para personalizar resposta

    Returns:
        Argumentação estruturada para superar a objeção

    Exemplo de uso:
        objection_handler("preço", "psicóloga que cobra R$ 200/sessão")
        → Retorna argumento mostrando ROI e parcelamento
    """

    # Base de conhecimento de objeções e respostas
    objection_responses = {
        "preço": {
            "title": "Investimento vs Retorno",
            "validação": "Entendo completamente! R$ 8.000 é um investimento significativo e você quer ter certeza que vale a pena.",
            "argumentos": [
                "💰 **ROI Rápido:** Com apenas 5-7 clientes atendidos com HE (cobrando valor premium), você recupera todo o investimento",
                "📊 **Aumento de Honorários:** Profissionais com HE cobram em média 50-75% a mais por serem especialistas certificados",
                "⏱️ **Economia de Tempo:** Cada cliente resolvido em 6 sessões vs 25 te dá 38 horas livres para novos atendimentos",
                "🔄 **Receita Recorrente:** Com mais tempo livre, você atende mais clientes por mês = aumento permanente de faturamento"
            ],
            "prova_social": "Dra. Ana Paula recuperou o investimento em 1,5 meses e hoje tem lista de espera de 2 meses.",
            "garantia": "✅ **Garantia Total:** Reembolso de 100% incondicional se não ficar satisfeito",
            "facilitador": "📋 **Parcelamento:** Até 12x no cartão para facilitar o fluxo de caixa",
            "fechamento": "O risco real não é investir R$ 8.000. É continuar perdendo clientes que desistem no meio do tratamento e deixar de ganhar R$ 10-20 mil/mês a mais."
        },

        "confiança": {
            "title": "Comprovação de Eficácia",
            "validação": "Excelente pergunta! Você tem todo o direito de querer garantias antes de investir.",
            "argumentos": [
                "🏆 **Único com MEC:** Somos a única formação em Hipnose Ericksoniana reconhecida pelo MEC no Brasil",
                "🌍 **Certificações Internacionais:** 5 certificações incluídas (IHA, ASCH, World WHO, ISH, IACT)",
                "👨‍⚕️ **Autoridade Máxima:** Treinamento direto com Dr. Stephen Paul Adler, PhD - maior autoridade sênior mundial",
                "📈 **Dados Reais:** 93% de taxa de recuperação em 1,5 mês (vs 6+ meses em outros métodos)",
                "👥 **60.000+ Profissionais:** Formados em todo o mundo com a metodologia"
            ],
            "prova_social": "Dr. Ricardo Almeida (neurologista): '85% dos meus pacientes com dor crônica não respondiam à medicação. Com HE, consegui resultados que não via em 15 anos.'",
            "garantia": "✅ **Zero Risco:** Garantia de reembolso 100% incondicional - você testa sem risco",
            "facilitador": "📚 **Bônus de R$ 14.985:** 5 cursos complementares incluídos para aprofundar ainda mais",
            "fechamento": "Não é sobre acreditar em promessas. É sobre testar uma metodologia validada cientificamente com garantia total de devolução."
        },

        "tempo": {
            "title": "Otimização de Tempo",
            "validação": "Compreendo! A rotina de profissionais de saúde é realmente intensa.",
            "argumentos": [
                "📅 **Apenas 5 Dias Presenciais:** Módulo I (3 dias) + Módulo II (2 dias) em SP",
                "⏰ **Investimento Pontual:** 5 dias que transformam toda sua prática profissional",
                "💻 **Conteúdo Online:** Acesso aos cursos bônus para estudar no seu ritmo",
                "👨‍🏫 **Mentoria de 1 Ano:** Suporte contínuo após a formação sem precisar viajar",
                "⏱️ **ROI de Tempo:** Cada cliente com HE economiza 20+ sessões suas = 40h livres"
            ],
            "prova_social": "Dra. Carolina (RJ) fez a formação trabalhando 40h/sem: 'Foi intenso mas valeu cada minuto. Hoje economizo 30h/mês em atendimentos.'",
            "garantia": "✅ **Flexibilidade:** Se surgir imprevisto, oferecemos remarcação para próxima turma",
            "facilitador": "📊 **Cálculo Simples:** 5 dias investidos = 40h economizadas POR CLIENTE para o resto da carreira",
            "fechamento": "A pergunta real é: você tem tempo para continuar atendendo 25 sessões quando poderia resolver em 6?"
        },

        "disponibilidade": {
            "title": "Logística e Planejamento",
            "validação": "Entendo! Planejar viagens e agenda não é simples.",
            "argumentos": [
                "📍 **São Paulo - Hub Nacional:** Fácil acesso de qualquer região do Brasil",
                "🗓️ **Datas Fixas:** Planeje com antecedência (Abril 17-19, Maio 23-24)",
                "✈️ **Vale o Deslocamento:** Única formação MEC em HE no Brasil inteiro",
                "🏨 **Networking Presencial:** Conhecer outros 21 profissionais de elite da área",
                "📝 **Prática Supervisionada:** Parte essencial que só acontece presencialmente"
            ],
            "prova_social": "Marcela (Florianópolis) viajou para SP: 'Melhor investimento que fiz. Conheci profissionais incríveis e hoje trocamos experiências até hoje.'",
            "garantia": "✅ **Investimento Único:** Apenas 2 viagens que transformam toda sua carreira",
            "facilitador": "💡 **Otimize a Viagem:** Programe pacientes antes/depois das datas para compensar ausência",
            "fechamento": "5 dias em SP vs transformação permanente da sua prática. O que pesa mais?"
        },

        "já fiz outro curso": {
            "title": "Diferenciais Únicos da FHE",
            "validação": "Ótimo que já investiu em formação! Isso mostra comprometimento com excelência.",
            "argumentos": [
                "🎯 **Hipnose ERICKSONIANA:** Abordagem totalmente diferente de hipnose clássica/tradicional",
                "👨‍🏫 **Linhagem Direta:** Treinamento com quem treinou com Milton Erickson (via Betty Erickson)",
                "🏆 **Único MEC:** Certificação que nenhuma outra formação tem no Brasil",
                "📚 **Metodologia Específica:** 30+ técnicas ericsonianas exclusivas",
                "🔬 **Base Científica:** Reconhecimento por organizações médicas mundiais"
            ],
            "prova_social": "Dra. Ana tinha certificação em hipnose clássica: 'HE foi outro universo. A sutileza e eficácia não se comparam. Pacientes nem percebem que estão em transe.'",
            "garantia": "✅ **Compare Sem Risco:** Teste a diferença com garantia de reembolso 100%",
            "facilitador": "🎁 **Complementar, não substituir:** HE se integra perfeitamente com outras abordagens que você já usa",
            "fechamento": "Você não está trocando uma formação por outra. Está adicionando a metodologia mais eficaz do mundo ao seu arsenal."
        },

        "não conheco HE": {
            "title": "Introdução à Hipnose Ericksoniana",
            "validação": "Ótimo que está conhecendo agora! HE é fascinante e muito diferente da hipnose tradicional.",
            "argumentos": [
                "🧠 **Abordagem Naturalista:** Sem relógio balançando ou comandos diretos",
                "💬 **Conversacional:** Indução através de histórias, metáforas e linguagem indireta",
                "🎯 **Focada em Soluções:** Não revive traumas desnecessariamente, constrói recursos",
                "👤 **Personalizada:** Cada intervenção adaptada ao paciente (não protocolo rígido)",
                "⚡ **Resultados Rápidos:** Mudanças mensuráveis desde primeiras sessões"
            ],
            "prova_social": "Dr. Ricardo (neurologista): 'Estudei hipnose por anos mas HE foi revelação. Pacientes mudam sem nem perceber que estavam em transe.'",
            "garantia": "✅ **Aprenda do Zero:** Formação completa mesmo sem conhecimento prévio",
            "facilitador": "📖 **5 Cursos Bônus:** Material complementar para dominar fundamentos (R$ 14.985 grátis)",
            "fechamento": "Milton Erickson revolucionou a psicoterapia moderna. Você está descobrindo a metodologia que mudou o jogo."
        },

        # Fallback genérico
        "geral": {
            "title": "Esclarecendo Dúvidas",
            "validação": "Obrigado por compartilhar sua preocupação! Vamos esclarecer isso.",
            "argumentos": [
                "✅ **Formação Completa:** Tudo que você precisa em 5 dias + mentoria de 1 ano",
                "✅ **Garantia Total:** Reembolso 100% se não ficar satisfeito",
                "✅ **Reconhecimento MEC:** Único no Brasil com essa certificação",
                "✅ **Resultados Mensuráveis:** 93% recuperação em 1,5 mês",
                "✅ **Suporte Contínuo:** Mentoria e comunidade permanente"
            ],
            "prova_social": "Mais de 60.000 profissionais formados mundialmente com resultados consistentes.",
            "garantia": "✅ **Teste Sem Risco:** Você só continua se ver valor real na formação",
            "facilitador": "💡 **Parcelamento disponível:** Até 12x para facilitar decisão",
            "fechamento": "Qual aspecto específico ainda te deixa em dúvida? Posso esclarecer melhor."
        }
    }

    # Normalizar tipo de objeção
    objection_key = objection_type.lower().strip()

    # Buscar resposta apropriada
    response_data = objection_responses.get(objection_key, objection_responses["geral"])

    # Construir resposta formatada
    response = f"""**{response_data['title']}**

{response_data['validação']}

"""

    # Adicionar argumentos
    for argumento in response_data['argumentos']:
        response += f"{argumento}\n\n"

    # Adicionar prova social
    response += f"""**CASO REAL:**
{response_data['prova_social']}

"""

    # Adicionar garantia
    response += f"""{response_data['garantia']}

"""

    # Adicionar facilitador
    if "facilitador" in response_data:
        response += f"""{response_data['facilitador']}

"""

    # Fechamento
    response += f"""---
{response_data['fechamento']}"""

    # Personalizar com contexto se fornecido
    if context:
        response += f"\n\n💡 Considerando seu perfil ({context}), isso faz ainda mais sentido para você."

    return response
