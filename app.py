from flask import Flask, render_template, request, send_file
import requests
import json
import pandas as pd
from io import BytesIO
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# URL do endpoint do TJPE no Datajud
url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search"

# Chave de autenticação
headers = {
    "Authorization": "APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==",
    "Content-Type": "application/json"
}

# Códigos de movimentações que indicam arquivamento ou estados que devem ser excluídos
codigos_exclusao = [246, 12430, 865, 870, 866, 867, 12029, 977, 917]

# Termos de movimentações que indicam arquivamento ou estados que devem ser excluídos
descricoes_exclusao = [
    "arquivamento definitivo",
    "arquivamento",
    "processo arquivado",
    "arquivo definitivo",
    "remetido ao arquivo geral",
    "arquivado",
    "remetido ao arquivo",
    "remessa ao arquivo"
]


# Função para buscar o nome do movimento baseado no código
def buscar_nome_movimento(codigo):
    movimentos_dict = {
        92: "Publicado #{ato_publicado} em #{data}.",
        928: "Republicado #{ato_publicado} em #{data}.",
        14982: "Levantada a Causa Suspensiva ou de Sobrestamento - Suspensão / Sobrestamento.",
        14738: "Classe retificada de #{classe_anterior} para #{classe_nova}.",
        14739: "Evoluída a classe de #{classe_anterior} para #{classe_nova}.",
        12260: "Autos restaurados em #{data}.",
        1051: "Decorrido prazo de #{nome_da_parte} em #{data}.",
        1061: "Disponibilizado no DJ Eletrônico em #{data}.",
        1062: "Redisponibilizado no DJe em #{data}.",
        190: "Reformada decisão anterior #{tipo_da_decisao_anterior} datada de #{data}.",
        945: "Revogada decisão anterior #{tipo_da_decisao_anterior} datada de #{data}.",
        848: "Transitado em Julgado em #{data}.",
        15049: "Audiência Concentrada Protetiva conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        970: "Audiência #{tipo_de_audiencia} conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12739: "Audiência admonitória conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        15050: "Audiência Concentrada infracional conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12741: "Audiência de acolhimento conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        15045: "Audiência de apresentação de adolescente conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12740: "Audiência de conciliação conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12742: "Audiência de custódia conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        15188: "Audiência de depoimento especial conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12749: "Audiência de instrução conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12750: "Audiência de instrução e julgamento conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12743: "Audiência de interrogatório conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12751: "Audiência de julgamento conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12744: "Audiência de justificação conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12752: "Audiência de mediação conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12745: "Audiência do art. 16 da Lei 11.340 conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12624: "Audiência do art. 334 CPC conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12746: "Audiência em execução conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12747: "Audiência inicial conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        12753: "Audiência preliminar conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        14096: "Audiência pública dirigida por #{dirigida_por} em #{local}, em #{data_horal}.",
        417: "Incluído em pauta para #{data_hora}, #{local}.",
        311: "Leilão ou Praça em/para #{data_hora}, #{local}.",
        12759: "Realizado o Procedimento restaurativo em #{data_hora}, #{local}.",
        313: "Sessão do Tribunal do Júri em/para #{data_hora}, #{local}.",
        15102: "Sessão Restaurativa conduzida por #{dirigida_por} em/para #{data_hora}, #{local}.",
        391: "Recebida a denúncia contra #{nome_da_parte}.",
        263: "Processo Suspenso por Réu revel citado por edital #{nome_da_parte}.",
        493: "Autos entregues em carga ao #{destinatario}.",
        12214: "Processo Encaminhado a #{destinatario}.",
        11424: "Concedida em parte medida protetiva de #{tipo_de_medida_protetiva} para #{destinatario_de_medida_protetiva}.",
        11423: "Concedida medida protetiva de #{tipo_de_medida_protetiva} para #{destinatario_de_medida_protetiva}.",
        14681: "Descumprida a Medida Protetiva de #{tipo_de_medida_protetiva} destinada a #{destinatario_de_medida_protetiva}.",
        12476: "Homologada medida protetiva determinada por autoridade policial.",
        12479: "Não homologada medida protetiva de #{tipo_de_medida_protetiva} para #{destinatario_de_medida_protetiva}.",
        14733: "Prorrogada a medida protetiva de #{tipo_de_medida_protetiva} a #{destinatario_da_medida_protetiva}.",
        11426: "Revogada medida protetiva de #{tipo_de_medida_protetiva} para #{destinatario_de_medida_protetiva}.",
        106: "Mandado devolvido #{resultado}.",
        112: "Ofício Devolvido #{resultado}.",
        1061: "Disponibilizado no DJ Eletrônico em #{data}.",
        1062: "Redisponibilizado no DJe em #{data}.",
        12736: "Unificado o Processo de Execução ao processo #{numero_do_processo}.",
        391: "Recebida a denúncia contra #{nome_da_parte}.",
        393: "Recebida a queixa contra #{nome_da_parte}.",
        12035: "Recebida a representação contra #{nome_da_parte}.",
        388: "Recebido aditamento à denúncia contra #{nome_da_parte}.",
        389: "Recebido aditamento à queixa contra #{nome_da_parte}.",
        12734: "Revogado o acordo de não persecução penal de #{nome_da_parte}.",
        15064: "Não acolhida a impugnação aos cálculos de liquidação apresentada por #{nome_da_parte}.",
        15065: "Não admitida a impugnação aos cálculos de liquidação apresentada por #{nome_da_parte}.",
        12456: "Não admitido o Recurso ordinário de #{nome_da_parte}.",
        12475: "Não conhecido o Habeas Corpus de #{nome_da_parte}.",
        12736: "Unificado o Processo de Execução ao processo #{numero_do_processo}.",
        263: "Processo Suspenso por Réu revel citado por edital #{nome_da_parte}.",
    }
    
    # Se o código não estiver no dicionário, retorna "Movimento Desconhecido"
    return movimentos_dict.get(codigo, "Movimento Desconhecido")

# Função que busca os processos de acordo com os filtros (incluindo a exclusão de arquivados)
def buscar_processos(filtros, page, per_page):
    data = {
        "query": {
            "bool": {
                "must": [
                    # Processos da 1ª Vara de São Bento do Una
                    {"match_phrase": {"orgaoJulgador.nome": "1ª Vara da Comarca de São Bento do Una"}}
                ],
                "must_not": [
                    # Excluir processos com os códigos indesejados
                    {"terms": {"movimentos.codigo": codigos_exclusao}},
                    # Excluir processos com descrições de arquivamento ou exclusão (usando filtro "wildcard" para palavras-chave)
                    {"wildcard": {"movimentos.descricao.keyword": "*arquiv*"}},
                    {"wildcard": {"movimentos.descricao.keyword": "*remetido ao arquivo*"}},
                    {"terms": {"movimentos.descricao.keyword": descricoes_exclusao}}
                ]
            }
        },
        "_source": [
            "classe.nome",
            "numeroProcesso",
            "movimentos.dataHora",
            "movimentos.codigo",
            "movimentos.descricao",
            "assuntos.nome",
            "orgaoJulgador.nome"
        ],
        "from": (page - 1) * per_page,
        "size": per_page
    }

    # Aplica o filtro de número de processo, se existir
    if filtros.get('numero_processo'):
        data["query"]["bool"]["must"].append({"match": {"numeroProcesso": filtros['numero_processo']}})
    
    # Aplica o filtro de assunto, se existir
    if filtros.get('assunto'):
        data["query"]["bool"]["must"].append({"match_phrase": {"assuntos.nome": filtros['assunto']}})
    
    # Aplica o filtro de classe, se existir
    if filtros.get('classe'):
        data["query"]["bool"]["must"].append({"match_phrase": {"classe.nome": filtros['classe']}})
    
    # Aplica o filtro de movimento, se existir
    if filtros.get('movimento'):
        data["query"]["bool"]["must"].append({"match_phrase": {"movimentos.descricao": filtros['movimento']}})

    # Faz a requisição para a API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        resultados = response.json()
        processos_filtrados = []
        contagem_classes = defaultdict(int)
        contagem_assuntos = defaultdict(int)

        for hit in sorted(resultados['hits']['hits'], key=lambda x: x['_source']['classe']['nome']):
            processo = hit['_source'].get('numeroProcesso', 'N/A')
            classe = hit['_source'].get('classe', {}).get('nome', 'N/A')
            assuntos = [assunto['nome'] for assunto in hit['_source'].get('assuntos', [])]
            orgao_julgador = hit['_source'].get('orgaoJulgador', {}).get('nome', 'N/A')

            movimentos = hit['_source'].get('movimentos', [])

            # Verifica se o processo tem qualquer movimentação com códigos ou descrições indesejados
            arquivado = False
            for movimento in movimentos:
                if (movimento.get('codigo') in codigos_exclusao or
                        any(desc in movimento.get('descricao', '').lower() for desc in descricoes_exclusao)):
                    arquivado = True
                    break

            if arquivado:
                continue  # Ignora processos arquivados ou com os códigos ou descrições indesejados

            contagem_classes[classe] += 1
            for assunto in assuntos:
                contagem_assuntos[assunto] += 1

            lista_movimentos = []
            for movimento in movimentos:
                nome_movimento = buscar_nome_movimento(movimento.get('codigo', 'N/A'))
                lista_movimentos.append({
                    "codigo": movimento.get('codigo', 'N/A'),
                    "descricao": nome_movimento,
                    "data": datetime.strptime(movimento['dataHora'], '%Y-%m-%dT%H:%M:%S.%fZ')
                })

            lista_movimentos.sort(key=lambda x: x['data'], reverse=True)

            processos_filtrados.append({
                "Número do Processo": processo,
                "Classe": classe,
                "Órgão Julgador": orgao_julgador,
                "Assuntos": ', '.join(assuntos),
                "Movimentos": lista_movimentos
            })

        total_resultados = resultados['hits']['total']['value']
        return processos_filtrados, total_resultados, contagem_classes, contagem_assuntos
    else:
        return [], 0, {}, {}


# Função para exibir a página principal e realizar a busca com contagem de processos corretamente
@app.route('/', methods=['GET', 'POST'])
def index():
    processos = []
    total_resultados = 0
    contagem_classes = defaultdict(int)
    contagem_assuntos = defaultdict(int)

    # Filtros recebidos do formulário
    assunto = request.form.get('assunto')
    classe = request.form.get('classe')
    movimento = request.form.get('movimento')

    filtros = {}

    if assunto:
        filtros['assunto'] = assunto
    if classe:
        filtros['classe'] = classe
    if movimento:
        filtros['movimento'] = movimento

    # Buscar processos sem paginação para contar todos os resultados corretamente
    processos, total_resultados, contagem_classes, contagem_assuntos = buscar_processos(filtros, page=1, per_page=10000)

    return render_template(
        'index.html',
        processos=processos,
        total_resultados=total_resultados,
        contagem_classes=contagem_classes,
        contagem_assuntos=contagem_assuntos,
        filtros=filtros
    )


@app.route('/classe/<classe_nome>')
def processos_por_classe(classe_nome):
    # Buscar processos filtrados pela classe, excluindo os arquivados e com os códigos de exclusão
    filtros = {
        'classe': classe_nome
    }
    processos, total_resultados, _, _ = buscar_processos(filtros, page=1, per_page=5000)

    # Organizar os processos por assunto
    processos_por_assunto = defaultdict(list)
    for processo in processos:
        for assunto in processo.get('Assuntos', '').split(', '):
            processos_por_assunto[assunto].append(processo)

    # Renderiza a página com os processos organizados por assunto
    return render_template(
        'processos_por_classe.html', 
        classe_nome=classe_nome, 
        processos_por_assunto=processos_por_assunto, 
        total_resultados=total_resultados
    )


@app.route('/processo/<numero_processo>', methods=['GET', 'POST'])
def processo_detalhes(numero_processo):
    print(f"Buscando detalhes para o processo: {numero_processo}")
    
    # Filtra o processo pelo número específico fornecido na URL
    filtros = {
        'numero_processo': numero_processo
    }

    # Buscar o processo específico
    processos, _, _, _ = buscar_processos(filtros, page=1, per_page=1)

    if processos:
        processo = processos[0]  # Pega o primeiro (e único) processo da lista
        
        print(f"Processo encontrado: {processo['Número do Processo']}")

        # Verificar se foi submetido um filtro de movimento
        movimento_filtro = request.form.get('movimento_filtro')
        if movimento_filtro:
            processo['Movimentos'] = [mov for mov in processo['Movimentos'] if movimento_filtro.lower() in mov['descricao'].lower()]

        return render_template('processo_detalhes.html', processo=processo)
    else:
        print(f"Processo {numero_processo} não encontrado.")
        return "Processo não encontrado", 404


# Função para permitir o download dos resultados em Excel
@app.route('/download', methods=['POST'])
def download():
    numero_processo = request.form.get('numero_processo')
    classe = request.form.get('classe')
    assunto = request.form.get('assunto')

    filtros = {
        'numero_processo': numero_processo,
        'classe': classe,
        'assunto': assunto
    }

    processos, _, _, _ = buscar_processos(filtros, page=1, per_page=1000)
    excel_file = gerar_excel(processos)

    return send_file(excel_file, as_attachment=True, download_name="processos.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == '__main__':
    app.run(debug=True)



