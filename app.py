from flask import Flask, render_template, request, send_file
import requests
import json
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# URL do endpoint do TJPE no Datajud
url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search"

# Chave de autenticação
headers = {
    "Authorization": "APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==",
    "Content-Type": "application/json"
}

# Função que faz a busca e retorna os resultados filtrados
def buscar_processos(filtros):
    data = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"orgaoJulgador.nome": "1ª Vara da Comarca de São Bento do Una"}}
                ]
            }
        },
        "_source": [
            "classe.nome", "numeroProcesso", "dataAutuacao", "segredoDeJustica", 
            "movimentos.dataHora", "movimentos.codigo", "movimentos.descricao", 
            "assuntos.nome", "orgaoJulgador.nome"
        ],
        "size": 5000
    }

    # Filtros adicionais
    if filtros.get('assunto'):
        data["query"]["bool"]["must"].append({
            "match_phrase": {"assuntos.nome": filtros['assunto']}
        })
    if filtros.get('classe'):
        data["query"]["bool"]["must"].append({
            "match_phrase": {"classe.nome": filtros['classe']}
        })
    if filtros.get('numero_processo'):
        data["query"]["bool"]["must"].append({
            "match": {"numeroProcesso": filtros['numero_processo']}
        })
    if filtros.get('movimento'):
        movimento_filtro = filtros['movimento']
        # Verifica se o filtro de movimento é um número (código) ou uma descrição
        if movimento_filtro.isdigit():
            data["query"]["bool"]["must"].append({
                "terms": {"movimentos.codigo": [int(movimento_filtro)]}
            })
        else:
            data["query"]["bool"]["must"].append({
                "match_phrase": {"movimentos.descricao": movimento_filtro}
            })

    # Fazendo a requisição para a API
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        resultados = response.json()
        if resultados['hits']['total']['value'] == 0:
            return []
        
        dados_processos = []
        for hit in resultados['hits']['hits']:
            processo = hit['_source'].get('numeroProcesso', 'N/A')
            classe = hit['_source'].get('classe', {}).get('nome', 'N/A')
            assuntos = [assunto['nome'] for assunto in hit['_source'].get('assuntos', [])]
            autuacao = datetime.strptime(hit['_source'].get('dataAutuacao', 'N/A'), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y') if hit['_source'].get('dataAutuacao') else 'N/A'
            segredo_justica = 'Sim' if hit['_source'].get('segredoDeJustica', False) else 'Não'

            movimentos = []
            for movimento in hit['_source'].get('movimentos', []):
                movimentos.append({
                    "codigo": movimento.get('codigo', 'N/A'),
                    "descricao": movimento.get('descricao', 'N/A'),
                    "data": datetime.strptime(movimento['dataHora'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y')
                })

            dados_processos.append({
                "Número do Processo": processo,
                "Classe": classe,
                "Assuntos": ', '.join(assuntos),
                "Autuação": autuacao,
                "Segredo de Justiça": segredo_justica,
                "Movimentos": movimentos
            })
        return dados_processos
    else:
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        numero_processo = request.form.get('numero_processo')
        classe = request.form.get('classe')
        assunto = request.form.get('assunto')
        movimento = request.form.get('movimento')

        filtros = {}
        if numero_processo:
            filtros['numero_processo'] = numero_processo
        if assunto:
            filtros['assunto'] = assunto
        if classe:
            filtros['classe'] = classe
        if movimento:
            filtros['movimento'] = movimento

        # Buscar processos com os filtros fornecidos
        processos = buscar_processos(filtros)

        # Se o botão "Exportar para Excel" for pressionado
        if 'exportar' in request.form:
            df = pd.DataFrame(processos)
            df.to_excel("processos_filtrados.xlsx", index=False)
            return send_file("processos_filtrados.xlsx", as_attachment=True)

        return render_template('index.html', processos=processos)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)





