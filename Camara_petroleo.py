import datetime
import requests
import pandas as pd
import streamlit as st


st.set_page_config(layout = 'wide')
#inserindo o titulo
st.title('Monitoramento das Proposições Legislativas da Câmara dos Deputados')
st.title('Tema: **Petróleo, Gás e Biocombustíveis**')


st.text("São acompanhados os PLs, PLPs, PECs e Requerimentos")
st.text("que apresentaram alguma tramitação nos ultimos 7 dias")

st.text('Os temas em monitoramento são: "gás", "petróleo", "biocombust", "etanol", "biometano", "SAF", "diesel", "transição energética"')


# Definir a URL da API para o endpoint de projetos
url = "https://dadosabertos.camara.leg.br/api/v2/proposicoes"

# Definir os parâmetros da requisição
data_inicio = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
data_fim = datetime.datetime.now().strftime("%Y-%m-%d")
params = {
    "dataInicio": data_inicio,
    "dataFim": data_fim,
    "ordenarPor": "id",
    "itens": 100,  # Quantidade de itens por página
    "pagina": 1,   # Começar pela primeira página
    "siglaTipo": ["PL", "PLP", "PEC", "REQ"],
}

# Definir as palavras-chave que deseja filtrar na ementa dos projetos
palavras_chave = ["gás", "petróleo", "biocombust", "etanol", "biometano", "SAF", "diesel", "transição energética"]

# Fazer requisições para todas as páginas de resultados
projetos = []
while True:
    # Fazer a requisição para a API
    response = requests.get(url, params=params, headers={'Cache-Control': 'no-cache'})

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Acessar o conteúdo da resposta em formato JSON
        dados = response.json()["dados"]

        # Verificar se há projetos na página atual
        if len(dados) == 0:
            break

        # Filtrar os projetos que contêm pelo menos uma palavra-chave na ementa
        projetos.extend(
            [projeto for projeto in dados
             if any(palavra in projeto["ementa"].lower() for palavra in palavras_chave)]
        )

        # Avançar para a próxima página
        params["pagina"] += 1
    else:
        print("Erro ao fazer requisição para a API:", response.status_code)
        break

# Adicionar a situação de tramitação e data da última movimentação
token = "seu_token_de_acesso_aqui"  # Substituir pelo seu token de acesso válido
for proposicao in projetos:
    id_proposicao = proposicao['id']

    # Fazer uma chamada ao endpoint /proposicoes/{id}/tramitacoes para obter as tramitações da proposição
    url_tramitacoes = f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id_proposicao}/tramitacoes"
    response_tramitacoes = requests.get(url_tramitacoes, headers={"Authorization": f"Bearer {token}"})

    if response_tramitacoes.status_code == 200:
        tramitacoes = response_tramitacoes.json()['dados']

        # Obter a última tramitação da proposição
        if tramitacoes:
            ultima_tramitacao = tramitacoes[-1]
            proposicao['situacaoTramitacao'] = ultima_tramitacao['descricaoSituacao']
            proposicao['dataUltimaMovimentacao'] = ultima_tramitacao['dataHora']
        else:
            proposicao['situacaoTramitacao'] = "Sem tramitações registradas"
            proposicao['dataUltimaMovimentacao'] = None
    else:
        print(f"Erro ao obter as tramitações da proposição {id_proposicao}: {response_tramitacoes.status_code}")
        proposicao['situacaoTramitacao'] = "Erro ao obter dados"
        proposicao['dataUltimaMovimentacao'] = None

# Criar DataFrame com as informações relevantes
colunas = ['siglaTipo', 'numero', 'ano', 'ementa', 'situacaoTramitacao', 'dataUltimaMovimentacao']
df1 = pd.DataFrame(projetos, columns=colunas)

# Adicionar a coluna de links para as proposições
df1['link'] = df1.index.map(lambda i: f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={projetos[i]['id']}")

# Exibir a tabela final
st.write("Tabela com as proposições filtradas:")
st.dataframe(df1)
