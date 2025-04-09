import pdfplumber
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import os


# Configurando o título da página URL
st.set_page_config(
    page_title="Classificação",
    layout="wide",
    initial_sidebar_state="expanded")


# Carregando uma imagem
image = Image.open('images/capa.png')

# Inserindo a imagem na página utilizando os comandos do stremalit
st.image(image, use_container_width=True)
st.write("<div align='center'><h2><i>Classificação by:Amattheis</i></h2></div>",
         unsafe_allow_html=True)
st.write("")


# Abre o PDF
with pdfplumber.open("tabela.pdf") as pdf:
    # Acessa a primeira página
    pagina = pdf.pages[0]

    # Extrai tabelas da página (retorna uma lista de tabelas)
    tabelas = pagina.extract_tables()

    if tabelas:
        # Converte a primeira tabela para DataFrame
        df = pd.DataFrame(tabelas[0][1:], columns=tabelas[0][0])
        print(df)
    else:
        print("Nenhuma tabela encontrada na primeira página.")

novo_cabecalho = ["Posição", "Numeral", "Piloto", "Equipe", "Modelo",
                  "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                  "16", "17", "18", "19", "20", "21", "22", "Descarte", "23", "24", "Soma"
                  ]
df.columns = novo_cabecalho

# Cria uma lista com as colunas do DataFrame, colocando "Soma" na posição desejada
novas_colunas = ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma', "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                 "16", "17", "18", "19", "20", "21", "22", "23", "24", "Descarte"] + \
    [col for col in df.columns if col not in ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma', "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                                              "16", "17", "18", "19", "20", "21", "22", "23", "24", "Descarte"]]

df = df[novas_colunas]
df = df.drop(index=0)

# Input do usuário para a última corrida
ultima_corrida = st.number_input(
    "Informe o número da última corrida realizada", min_value=1, max_value=24, value=24, step=1)

# Criar o DataFrame df_abandonos para contabilizar os motivos de abandonos e mostrar na tab analise de consistencia
df_abandonos = pd.DataFrame(columns=["Piloto", "NC", "EXC", "DSC", "NP"])

# Loop pelas linhas do DataFrame para contar as razões
for _, row in df.iterrows():
    piloto = row['Piloto']
    
    # Inicializa contadores
    nc_count = 0
    exc_count = 0
    dsc_count = 0
    np_count = 0
    
    # Verifica as colunas de pontuação
    for score in row[6:ultima_corrida + 6]:
        if score == "NC":
            nc_count += 1
        elif score == "EXC":
            exc_count += 1
        elif score == "DSC":
            dsc_count += 1
        elif pd.isna(score) or score == "":  # Considera NaN ou string vazia como não participação
            np_count += 1
    
    # Adiciona os resultados ao DataFrame df_abandonos usando pd.concat
    new_row = pd.DataFrame({
        "Piloto": [piloto],
        "NC": [nc_count],
        "EXC": [exc_count],
        "DSC": [dsc_count],
        "NP": [np_count]
    })
    
    df_abandonos = pd.concat([df_abandonos, new_row], ignore_index=True)

# Passo 1: Substituir "NC" por 0 nas colunas de pontuação (corridas 1 até a última corrida informada)
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:,
                                         6:ultima_corrida+6].replace("NC", 0)

# Passo 2: Substituir "DSC" por NaN para que essas corridas não sejam consideradas no cálculo do descarte
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:,
                                         6:ultima_corrida+6].replace("DSC", pd.NA)

# Passo 3: Substituir "EXC" por NaN para que essa corrida não seja considerada para descarte e soma
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:,
                                         6:ultima_corrida+6].replace("EXC", pd.NA)

# Passo 4: Converter as colunas de pontuação para numérico, forçando erros para NaN
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:,
                                         6:ultima_corrida+6].apply(pd.to_numeric, errors='coerce')

# Passo 5: Calcular o "Descarte"
# O "Descarte" deve ser a soma das 2 menores pontuações válidas (ignorando "DSC", "EXC" e "NaN")


def calcular_descarte(row):
    # Filtra as pontuações válidas (não considera NaN, DSC, nem EXC)
    # Droppa qualquer NaN (ou "DSC" ou "EXC")
    valid_scores = row[6:ultima_corrida+6].dropna()

    # Se houver mais de 1 valor válido, calcula o descarte
    if len(valid_scores) > 1:
        # Ordena as pontuações e pega as 2 menores
        valid_scores_sorted = valid_scores.sort_values()
        # Descartar as duas menores pontuações
        # Soma das 2 menores pontuações
        descarte = valid_scores_sorted.iloc[:2].sum()
        return descarte
    else:
        # Caso o piloto tenha apenas uma corrida válida (não deve acontecer normalmente)
        return 0


# Aplicando a função de descarte
df['Descarte'] = df.apply(calcular_descarte, axis=1)
df['Descarte'] = df['Descarte'].round(0).astype(int)

# Passo 6: Substituir NaN por 0 nas pontuações válidas (apenas para a soma)
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:,
                                         6:ultima_corrida+6].fillna(0)

# Passo 7: Calcular a "Soma" (somatório das pontuações sem considerar o "Descarte")
df['Soma'] = df.iloc[:, 6:ultima_corrida+6].sum(axis=1)

# Passo 8: Atualizar a "Soma" após subtrair o "Descarte"
df['Soma'] = df['Soma'] - df['Descarte']
df['Soma'] = df['Soma'].round(0).astype(int)

# Para garantir que as pontuações não sejam mais alteradas e "DSC", "EXC" ou "NC" não interfira nos cálculos
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:,
                                         6:ultima_corrida+6].astype(int)


pontuacao_sprint = {
    1: 55, 2: 50, 3: 46, 4: 42, 5: 38, 6: 36, 7: 34, 8: 32, 9: 30, 10: 28,
    11: 26, 12: 24, 13: 22, 14: 20, 15: 18, 16: 16, 17: 14, 18: 13, 19: 12, 20: 11,
    21: 10, 22: 9, 23: 8, 24: 7, 25: 6, 26: 5, 27: 4, 28: 3, 29: 2, 30: 1,
    31: 0, 32: 0, 33: 0, 34: 0
}

pontuacao_principal = {
    1: 80, 2: 74, 3: 69, 4: 64, 5: 59, 6: 55, 7: 51, 8: 47, 9: 43, 10: 40,
    11: 37, 12: 34, 13: 31, 14: 28, 15: 25, 16: 22, 17: 19, 18: 17, 19: 15, 20: 13,
    21: 12, 22: 11, 23: 10, 24: 9, 25: 8, 26: 7, 27: 6, 28: 5, 29: 4, 30: 3,
    31: 0, 32: 0, 33: 0, 34: 0
}

# Separar as corridas Sprint (ímpares) e Principal (pares)
corridas_sprint = [col for idx, col in enumerate(
    df.columns[6:29]) if (idx + 1) % 2 != 0]  # Ímpares
corridas_principal = [col for idx, col in enumerate(
    df.columns[6:29]) if (idx + 1) % 2 == 0]  # Pares

# Função para calcular a soma das pontuações por tipo de corrida (Sprint ou Principal)


def calcular_ranking(tipo_corrida, colunas_corridas):
    # Copiar o DataFrame original com as colunas necessárias
    df_rank = df[['Piloto', 'Equipe'] + colunas_corridas].copy()

    # Converter os valores das colunas de corridas para numérico, forçando erros para NaN
    df_rank[colunas_corridas] = df_rank[colunas_corridas].apply(
        pd.to_numeric, errors='coerce')

    # Calcular a soma das pontuações por piloto
    df_rank['Soma'] = df_rank[colunas_corridas].sum(axis=1)

    # Ordenar pelo total da soma de forma decrescente
    df_rank = df_rank.sort_values(by='Soma', ascending=False)

    # Recalcular a posição (ranking) com base na soma
    df_rank['Posição'] = df_rank['Soma'].rank(
        ascending=False, method='min').astype(int)

    # Selecionar as colunas desejadas para exibir
    df_rank = df_rank[['Posição', 'Piloto', 'Equipe', 'Soma']]

    # Exibir o ranking calculado
    return df_rank


# Corridas Sprint (ímpares)
corridas_sprint = [col for idx, col in enumerate(
    df.columns[6:29]) if (idx + 1) % 2 != 0]
# Corridas Principal (pares)
corridas_principal = [col for idx, col in enumerate(
    df.columns[6:29]) if (idx + 1) % 2 == 0]

# Passo 1: Contar vitórias em cada tipo de corrida (Sprint e Principal)
vitorias_sprint = {}
vitorias_principal = {}
vitorias_gerais = {}

# Loop pelas linhas do DataFrame para contar as vitórias de cada piloto nas corridas Sprint e Principal
for _, row in df.iterrows():
    piloto = row['Piloto']

    # Contando vitórias nas corridas Sprint (ímpares) - valores 55
    vitorias_sprint_count = (row.iloc[6:30:2] == 55).sum()

    # Contando vitórias nas corridas Principal (pares) - valores 80
    vitorias_principal_count = (row.iloc[7:30:2] == 80).sum()

    # Somando vitórias gerais (Sprint + Principal)
    vitorias_geral_count = vitorias_sprint_count + vitorias_principal_count

    # Armazenando o total de vitórias Sprint, Principal e Geral por piloto
    vitorias_sprint[piloto] = vitorias_sprint_count
    vitorias_principal[piloto] = vitorias_principal_count
    vitorias_gerais[piloto] = vitorias_geral_count

# Filtrando apenas pilotos que venceram ao menos uma corrida em cada tipo
vitorias_sprint_filtradas = {
    piloto: vitoria for piloto, vitoria in vitorias_sprint.items() if vitoria > 0}
vitorias_principal_filtradas = {
    piloto: vitoria for piloto, vitoria in vitorias_principal.items() if vitoria > 0}
vitorias_gerais_filtradas = {
    piloto: vitoria for piloto, vitoria in vitorias_gerais.items() if vitoria > 0}

# Utilizando mesma lógica mas agora para equipes
# Inicializando os dicionários para contar as vitórias das equipes nas corridas Sprint e Principal
vitorias_sprint_equipes = {}
vitorias_principal_equipes = {}

# Loop pelas linhas do DataFrame para contar as vitórias de cada piloto nas corridas Sprint e Principal
for _, row in df.iterrows():
    piloto = row['Piloto']

    # Identificando a equipe do piloto (supondo que a coluna 'Equipe' exista)
    equipe = row['Equipe']

    # Contando as vitórias nas corridas Sprint (ímpares) - valores 55
    vitorias_sprint_count = (row[corridas_sprint] == 55).sum()

    # Contando as vitórias nas corridas Principal (pares) - valores 80
    vitorias_principal_count = (row[corridas_principal] == 80).sum()

    # Atualizando a contagem de vitórias para cada equipe
    if vitorias_sprint_count > 0:
        if equipe not in vitorias_sprint_equipes:
            vitorias_sprint_equipes[equipe] = 0
        vitorias_sprint_equipes[equipe] += vitorias_sprint_count

    if vitorias_principal_count > 0:
        if equipe not in vitorias_principal_equipes:
            vitorias_principal_equipes[equipe] = 0
        vitorias_principal_equipes[equipe] += vitorias_principal_count

# Convertendo as vitórias para DataFrames
vitorias_sprint_df = pd.DataFrame(
    list(vitorias_sprint_equipes.items()), columns=['Equipe', 'Vitórias Sprint'])
vitorias_principal_df = pd.DataFrame(list(
    vitorias_principal_equipes.items()), columns=['Equipe', 'Vitórias Principal'])

# Unindo os DataFrames de vitórias Sprint e Principal
vitorias_df = pd.merge(
    vitorias_sprint_df, vitorias_principal_df, on='Equipe', how='outer').fillna(0)

# Somando as vitórias gerais (Sprint + Principal) por equipe
vitorias_df['Vitórias Totais'] = vitorias_df['Vitórias Sprint'] + \
    vitorias_df['Vitórias Principal']

# Ordenando as equipes pelo número total de vitórias
vitorias_df = vitorias_df.sort_values(by='Vitórias Totais', ascending=False)

# Gerando o gráfico de vitórias das equipes nas corridas Sprint
fig_sprint_equipes = px.pie(vitorias_df,
                            names='Equipe',
                            values='Vitórias Sprint',
                            title='Distribuição de Vitórias por Equipe - Corridas Sprint',
                            color='Equipe',
                            color_discrete_sequence=px.colors.qualitative.Set3)


# Gerando o gráfico de vitórias das equipes nas corridas Principais
fig_principal_equipes = px.pie(vitorias_df,
                               names='Equipe',
                               values='Vitórias Principal',
                               title='Distribuição de Vitórias por Equipe - Corridas Principal',
                               color='Equipe',
                               color_discrete_sequence=px.colors.qualitative.Set1)

# Gerando o gráfico de vitórias totais por equipe
fig_total_equipes = px.pie(vitorias_df,
                           names='Equipe',
                           values='Vitórias Totais',
                           title='Distribuição de Vitórias Totais por Equipe',
                           color='Equipe',
                           color_discrete_sequence=px.colors.qualitative.Pastel)


def plotar_grafico_evolucao(df, corridas_sprint, corridas_principal, tipo_corrida):
    """
    Gera um gráfico de linha mostrando a evolução de cada piloto ao longo das corridas.

    Parâmetros:
    - df: DataFrame com os dados de corridas.
    - corridas_sprint: Lista com as colunas das corridas Sprint.
    - corridas_principal: Lista com as colunas das corridas Principal.
    - tipo_corrida: Tipo de corrida ('Sprint' ou 'Principal').

    Retorna:
    - gráfico de linha
    """
    if tipo_corrida == 'Sprint':
        colunas_corridas = corridas_sprint
    else:
        colunas_corridas = corridas_principal

    # Criar um gráfico de linhas
    fig = go.Figure()

    # Adicionar uma linha para cada piloto
    for piloto in df['Piloto'].unique():
        # Filtrar os dados do piloto
        dados_piloto = df[df['Piloto'] == piloto]

        # Selecionar as pontuações nas corridas específicas
        pontuacoes = dados_piloto[colunas_corridas].values.flatten()

        # Adicionar a linha no gráfico
        fig.add_trace(go.Scatter(
            x=list(range(1, len(colunas_corridas) + 1)),  # Número da corrida
            y=pontuacoes,
            mode='lines+markers',
            name=piloto
        ))

    # Adicionar detalhes ao gráfico
    fig.update_layout(
        title=f'Evolução dos Pilotos nas Corridas {tipo_corrida}',
        xaxis_title='Corridas',
        yaxis_title='Pontuação',
        showlegend=True
    )

    # Exibir o gráfico
    return fig


# Criando abas de visualização
tabs = st.tabs(['Pilotos', 'Equipes', 'Sprint',
               'Principal', 'Análise de consistência', 'Manual', 'Montadora', 'Pódios',
                'Resultados qualifyings', 'Estatisticas de qualifying', 'Comparação'])

with tabs[0]:

    # Função para aplicar estilos ao DataFrame
    def colorir_piloto(row):
        # Dicionário de cores
        color_map = {
            'Gabriel Casagrande': 'background-color: purple; color: white;',
            'Lucas Foresti': 'background-color: gray; color: white;',
            'Cesar Ramos': 'background-color: yellow; color: black;',
            'Thiago Camilo': 'background-color: red; color: white;',
            'Allam Khodair': 'background-color: green; color: white;',
            'Felipe Fraga': 'background-color: blue; color: white;',
        }

        # Aplica a cor se o nome do piloto corresponder
        color = color_map.get(row['Piloto'], '')

        # Retorna o estilo para cada célula da linha
        return [color] * len(row) if color else [''] * len(row)

    df = df.set_index('Posição')
    # Aplicando o estilo no DataFrame
    df_styled = df.style.apply(colorir_piloto, axis=1)

    # Passo 3: Exibir a tabela de forma interativa
    st.write("### Tabela de Pontuação do Campeonato")

    # Exibir a tabela com rolagem apenas vertical
    # A tabela ocupa toda a largura disponível
    st.dataframe(df_styled, use_container_width=True)

with tabs[1]:
    # Passo 6: Agrupar por equipe e somar as pontuações
    colunas_pontuacao = df.columns[6:30].tolist()

    # Verificar se todas as colunas de pontuação são numéricas antes de realizar a soma
    df[colunas_pontuacao] = df[colunas_pontuacao].apply(
        pd.to_numeric, errors='coerce')

    # Agrupar por equipe e somar as pontuações de cada corrida
    df_equipes = df.groupby('Equipe')[colunas_pontuacao].sum()

    # Criar a coluna "Soma" com a soma das pontuações de cada equipe
    df_equipes['Soma'] = df_equipes[colunas_pontuacao].sum(axis=1)

    # Resetar o índice para trazer 'Equipe' de volta como uma coluna normal
    df_equipes_sorted = df_equipes.reset_index()

    # Ordenar a tabela pela pontuação total em ordem decrescente
    df_equipes_sorted = df_equipes_sorted.sort_values(
        by='Soma', ascending=False)

    # Remover as casas decimais da coluna "Soma"
    df_equipes_sorted['Soma'] = df_equipes_sorted['Soma'].round(0).astype(int)

    # Adicionar a coluna "Posição" com base na ordenação da coluna "Soma"
    df_equipes_sorted['Posição'] = df_equipes_sorted['Soma'].rank(
        ascending=False, method='min').astype(int)

    # Reordenar as colunas para que "Posição" seja a primeira
    colunas = ['Posição'] + \
        [col for col in df_equipes_sorted.columns if col != 'Posição']
    df_equipes_sorted = df_equipes_sorted[colunas]

    # Função para aplicar estilos ao DataFrame (com base nas equipes)
    def colorir_equipe(row):
        # Dicionário de cores para as equipes
        color_map_equipes = {
            'Ipiranga Racing': 'background-color: yellow; color: black;',
            'A Mattheis Vogel': 'background-color: orange; color: black;',
            'Blau Motorsport': 'background-color: blue; color: white;',
        }

        # Aplica a cor se o nome da equipe corresponder
        color = color_map_equipes.get(row['Equipe'], '')

        # Retorna o estilo para cada célula da linha
        return [color] * len(row) if color else [''] * len(row)

    # **Remover a coluna de índice** antes de aplicar o estilo
    df_equipes_sorted = df_equipes_sorted.set_index('Posição')

    # Aplicando o estilo no DataFrame de equipes
    df_equipes_styled = df_equipes_sorted.style.apply(colorir_equipe, axis=1)

    # Exibir a tabela com pontuação por equipe, sem o índice
    st.write("### Tabela de Pontuação por Equipe")
    st.dataframe(df_equipes_styled.hide(
        axis="index"), use_container_width=True)

    # Exibe o gráfico de vitórias totais
    st.subheader("Vitórias Totais por Equipe")
    st.plotly_chart(fig_total_equipes)

with tabs[2]:
    # Criar gráfico de pizza para vitórias gerais
    if vitorias_gerais_filtradas:
        data_gerais = {
            "Piloto": list(vitorias_gerais_filtradas.keys()),
            "Vitórias": list(vitorias_gerais_filtradas.values())
        }

        fig_gerais = px.pie(data_gerais,
                            names="Piloto",
                            values="Vitórias",
                            title="Vitórias por Piloto",
                            hole=0.3,  # Tornar o gráfico de pizza "donut"
                            color="Piloto"  # Cor diferente para cada piloto
                            )

        # Atualizando o layout para melhorar a apresentação
        fig_gerais.update_layout(
            title_x=0.4,  # Centralizando o título
            title_y=0.95,  # Ajustando a posição do título
            showlegend=True,
            legend_title="Pilotos com vitórias",
            margin=dict(t=60, b=100, l=40, r=40)  # Ajuste das margens
        )

        # Exibindo o gráfico de vitórias gerais
        # st.plotly_chart(fig_gerais)

    # Criar gráfico de pizza para vitórias nas corridas Sprint
    if vitorias_sprint_filtradas:
        data_sprint = {
            "Piloto": list(vitorias_sprint_filtradas.keys()),
            "Vitórias Sprint": list(vitorias_sprint_filtradas.values())
        }

        fig_sprint = px.pie(data_sprint,
                            names="Piloto",
                            values="Vitórias Sprint",
                            title="Vitórias nas Corridas Sprint",
                            hole=0.3,  # Tornar o gráfico de pizza "donut"
                            color="Vitórias Sprint"  # Cores baseadas nas vitórias
                            )

        fig_sprint.update_layout(
            title_x=0.42,  # Centralizando o título
            title_y=0.95,  # Ajustando a posição do título
            showlegend=True,
            legend_title="Pilotos",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=12),
            ),
            margin=dict(t=60, b=100, l=40, r=40)
        )

        # Exibindo o gráfico de vitórias Sprint
        st.plotly_chart(fig_sprint)

        # Identificar os pilotos com mais vitórias
        max_vitorias_sprint = max(vitorias_sprint_filtradas.values())
        pilotos_com_max_vitorias_sprint = [
            piloto for piloto, vitorias in vitorias_sprint_filtradas.items() if vitorias == max_vitorias_sprint]

        # Exibir as fotos dos pilotos com mais vitórias
        st.subheader("Pilotos com mais vitórias")
        num_pilotos_sprint = len(pilotos_com_max_vitorias_sprint)
        # Criar colunas dinamicamente com base no número de pilotos empatados
        cols = st.columns(num_pilotos_sprint)

        for i, piloto in enumerate(pilotos_com_max_vitorias_sprint):
            with cols[i]:
                st.image(f'images/{piloto}.png', caption=piloto, width=150)

        fig_sprint = plotar_grafico_evolucao(
            df, corridas_sprint, corridas_principal, tipo_corrida='Sprint')
        st.plotly_chart(fig_sprint)

    else:
        st.write("Nenhum piloto com vitórias foi encontrado.")

    st.write("## Ranking de Pilotos - Corridas Sprint")

    # Calcular o ranking para as corridas Sprint
    df_ranking_sprint = calcular_ranking('Corridas Sprint', corridas_sprint)

    # Corrigir a coluna "Soma" para não ter casas decimais
    df_ranking_sprint['Soma'] = df_ranking_sprint['Soma'].round(0).astype(int)

    # Aplicar a estilização no DataFrame
    df_ranking_sprint_styled = df_ranking_sprint.style.apply(
        colorir_piloto, axis=1)

    # Exibir a tabela do ranking Sprint
    st.dataframe(df_ranking_sprint_styled)

    # Exibe o gráfico de vitórias Sprint
    st.subheader("Vitórias nas Corridas Sprint")
    st.plotly_chart(fig_sprint_equipes)

with tabs[3]:
    # Criar gráfico de pizza para vitórias nas corridas Principal
    if vitorias_principal_filtradas:
        data_principal = {
            "Piloto": list(vitorias_principal_filtradas.keys()),
            "Vitórias Principal": list(vitorias_principal_filtradas.values())
        }

        fig_principal = px.pie(data_principal,
                               names="Piloto",
                               values="Vitórias Principal",
                               title="Vitórias nas Corridas Principais",
                               hole=0.3,  # Tornar o gráfico de pizza "donut"
                               color="Vitórias Principal"  # Cores baseadas nas vitórias
                               )

        fig_principal.update_layout(
            title_x=0.45,  # Centralizando o título
            title_y=0.95,  # Ajustando a posição do título
            showlegend=True,
            legend_title="Pilotos",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=12),
            ),
            margin=dict(t=60, b=100, l=40, r=40)
        )

        # Exibindo o gráfico de vitórias Principal
        st.plotly_chart(fig_principal)

        # Identificar os pilotos com mais vitórias
        max_vitorias_principal = max(vitorias_principal_filtradas.values())
        pilotos_com_max_vitorias_principal = [
            piloto for piloto, vitorias in vitorias_principal_filtradas.items() if vitorias == max_vitorias_principal]

        # Exibir as fotos dos pilotos com mais vitórias
        st.subheader("Pilotos com mais vitórias")
        num_pilotos_principal = len(pilotos_com_max_vitorias_principal)
        # Criar colunas dinamicamente com base no número de pilotos empatados
        cols = st.columns(num_pilotos_principal)

        for i, piloto in enumerate(pilotos_com_max_vitorias_principal):
            with cols[i]:
                st.image(f'images/{piloto}.png', caption=piloto, width=150)

        st.write("## Ranking de Pilotos - Corridas Principal")

        # Calcular o ranking para as corridas Principal
        df_ranking_principal = calcular_ranking(
            'Corridas Principal', corridas_principal)

        # Corrigir a coluna "Soma" para não ter casas decimais
        df_ranking_principal['Soma'] = df_ranking_principal['Soma'].round(
            0).astype(int)

        # Aplicar a estilização no DataFrame
        df_ranking_principal_styled = df_ranking_principal.style.apply(
            colorir_piloto, axis=1)

        # Exibir a tabela do ranking Principal
        st.dataframe(df_ranking_principal_styled)

        st.subheader("Evolução dos Pilotos - Corridas Principal")
        fig_principal = plotar_grafico_evolucao(
            df, corridas_sprint, corridas_principal, tipo_corrida='Principal')
        st.plotly_chart(fig_principal)

        # Exibe o gráfico de vitórias Principal
        st.subheader("Vitórias nas Corridas Principais")
        st.plotly_chart(fig_principal_equipes)

with tabs[4]:
    # Contar o número total de corridas (colunas de pontuação)
    # Assumindo que as colunas de pontuação começam na posição 5 até a penúltima
    df = df.drop(columns=['Descarte'])
    total_corridas = ultima_corrida

    # Calcular o número de corridas participadas (onde a pontuação é diferente de zero)
    df['Corridas Participadas'] = df.iloc[:, 5:ultima_corrida +
                                          5].apply(lambda x: (x != 0).sum(), axis=1)

    # Calcular o número de abandonos (total de corridas - corridas participadas)
    df['Abandonos'] = total_corridas - df['Corridas Participadas']

    # Exibir número de abandonos por piloto
    st.write("#### Quantidade de corridas sem pontuar por Piloto")
    st.dataframe(df[['Piloto', 'Abandonos']])

    # Manipulando o df_abandonos
    # Criar a coluna "TOTAL"
    df_abandonos["TOTAL"] = df_abandonos["NC"] + df_abandonos["EXC"] + df_abandonos["DSC"] + df_abandonos["NP"]

    # Criar a coluna "%"
    df_abandonos["%"] = (df_abandonos["TOTAL"] / ultima_corrida) * 100
    # Garantir que a coluna "%" seja numérica antes de arredondar
    df_abandonos["%"] = pd.to_numeric(df_abandonos["%"], errors='coerce')
    # Arredondar a coluna "%" para 2 casas decimais
    df_abandonos["%"] = df_abandonos["%"].round(1)

    st.write("#### Quantidade de corridas sem pontuar por Piloto e Razão")
    st.dataframe(df_abandonos)

    # Média de Pontuação por Corrida (Ordenada)
    df['Média por Corrida'] = df['Soma'] / ultima_corrida
    df_sorted_by_media = df.sort_values('Média por Corrida', ascending=False)
    st.write("#### Ranking de Pilotos por Média de Pontuação por Corrida")
    st.dataframe(
        df_sorted_by_media[['Piloto', 'Média por Corrida']])

    # Desvio Padrão da Pontuação (Ordenado do Menor para o Maior)
    df['Desvio Padrão'] = df.iloc[:, 6:ultima_corrida+5].apply(
        pd.to_numeric, errors='coerce').std(axis=1)
    df_sorted_by_std = df.sort_values(
        'Desvio Padrão', ascending=True)  # Menor para maior desvio
    st.write("#### Ranking de Pilotos por Desvio Padrão de Pontuação")
    st.dataframe(
        df_sorted_by_std[['Piloto', 'Desvio Padrão']])

    fig = px.histogram(df, x="Soma", nbins=20,
                       title="Distribuição de Pontuação - Soma Total")
    fig.update_layout(
        xaxis_title="Pontuação",
        yaxis_title="Frequência",
        template="plotly_dark"
    )
    st.plotly_chart(fig)

with tabs[5]:
    # Calculando a próxima corrida
    proxima_corrida = ultima_corrida + 1

    # Verifica se o número da próxima corrida está dentro do limite de corridas
    if proxima_corrida <= 24:
        # Exibe a tabela interativa para o usuário editar as pontuações da próxima corrida
        st.subheader(f"Insira as pontuações para a Corrida {proxima_corrida}")

        # Definindo o nome da coluna da próxima corrida a ser editada
        coluna_corrida = ultima_corrida+1
        proxima_corrida = str(proxima_corrida)

        # Criando uma cópia do DataFrame com apenas as colunas de interesse para a próxima corrida
        df_editavel = df[['Piloto', 'Equipe', proxima_corrida]]

        # Exibindo a tabela para edição interativa
        df_editavel = st.data_editor(df_editavel)

        # Atualiza as pontuações quando o botão for pressionado
        if st.button("Atualizar Pontuações"):
            # Atualiza as pontuações inseridas pelo usuário
            for i, row in df_editavel.iterrows():
                nova_pontuacao = row[proxima_corrida]
                if pd.notna(nova_pontuacao) and nova_pontuacao != 0:
                    df.at[i, proxima_corrida] = nova_pontuacao

            df[proxima_corrida] = df[proxima_corrida].fillna(
                0)
            df["Soma"] = df["Soma"] + df[proxima_corrida]
            df["Soma"] = df["Soma"].round(0).astype(int)
            df[proxima_corrida] = df[proxima_corrida].round(0).astype(int)

            # Ordenar o DataFrame do maior para o menor pela coluna "Soma"
            df = df.sort_values(by="Soma", ascending=False)

            # Atualizar a coluna "Posição" com base na nova ordem
            df["Posição"] = range(1, len(df) + 1)

            # Recalcular o Descarte após a atualização das pontuações
            def recalcular_descarte(row):
                # Filtra as pontuações válidas (não considera NaN nem "DSC")
                # Droppa qualquer NaN (ou "DSC" convertido)
                valid_scores = row[5:ultima_corrida+6].dropna()

                # Se houver mais de 1 valor válido, calcula o descarte
                if len(valid_scores) > 1:
                    valid_scores_sorted = valid_scores.sort_values()
                    # Soma das 2 menores pontuações
                    descarte = valid_scores_sorted.iloc[:2].sum()
                    return descarte
                else:
                    return 0

            # Aplicando a função de recalcular o descarte
            df['Descarte'] = df.apply(recalcular_descarte, axis=1)

            # Atualizar a "Soma" após subtrair o "Descarte"
            df["Soma"] = df["Soma"] - df["Descarte"]
            df["Soma"] = df["Soma"].round(0).astype(int)

            df_filtered = df.iloc[:, :ultima_corrida+7]
            df_filtered['Descarte'] = df['Descarte']

            # Aplicando o estilo no DataFrame
            df_styled = df_filtered.style.apply(colorir_piloto, axis=1)

            # Exibe o DataFrame atualizado
            st.success(f"Pontuações da Corrida {
                       proxima_corrida} atualizadas com sucesso!")
            st.dataframe(df_styled, use_container_width=True)
    else:
        st.warning("A próxima corrida ultrapassa o número máximo de 24 corridas.")

with tabs[6]:
    def campeonato_por_modelo(df, ultima_corrida):
        resultado_campeonato = {}
        logos = {
            'Corolla': 'images/toyota.png',
            'Cruze': 'images/chev.png'
        }

        # Filtra os modelos para considerar apenas "Corolla" e "Cruze"
        df_filtrado = df[df['Modelo'].isin(['Corolla', 'Cruze'])]

        for modelo in df_filtrado['Modelo'].unique():
            df_modelo = df_filtrado[df_filtrado['Modelo'] == modelo]
            pontuacao_total_por_modelo = []

            for corrida in range(1, ultima_corrida + 1):
                coluna_corrida = str(corrida)

                if coluna_corrida in df_modelo.columns:
                    df_pontuacao = df_modelo[['Piloto', coluna_corrida]].sort_values(
                        by=coluna_corrida, ascending=False)

                    top_2 = df_pontuacao.head(2)
                    pontuacao_total = top_2[coluna_corrida].apply(
                        pd.to_numeric, errors='coerce').sum()

                    pontuacao_total_por_modelo.append(pontuacao_total)
                else:
                    pontuacao_total_por_modelo.append(0)

            resultado_campeonato[modelo] = sum(pontuacao_total_por_modelo)

        # Cria o DataFrame
        df_campeonato = pd.DataFrame(list(resultado_campeonato.items()), columns=[
                                     'Modelo', 'Pontuação Atual'])

        # Adiciona logos ao DataFrame
        df_campeonato['Logo'] = df_campeonato['Modelo'].apply(
            lambda x: logos[x])

        return df_campeonato

    def exibir_tabela_com_logos(df_campeonato):
        # Usando st.columns para criar duas colunas: uma para Corolla e outra para Cruze
        col1, col2 = st.columns(2)

        with col1:
            # Informações do Corolla
            corolla_row = df_campeonato[df_campeonato['Modelo']
                                        == 'Corolla'].iloc[0]
            st.image(corolla_row['Logo'], width=200)  # Exibe o logo do Corolla
            # Exibe a pontuação do Corolla
            st.write(
                f"Pontuação: {corolla_row['Pontuação Atual']} pontos")

        with col2:
            # Informações do Cruze
            cruze_row = df_campeonato[df_campeonato['Modelo']
                                      == 'Cruze'].iloc[0]
            st.image(cruze_row['Logo'], width=270)  # Exibe o logo do Cruze
            st.write(
                f"Pontuação: {cruze_row['Pontuação Atual']} pontos")

    df_campeonato = campeonato_por_modelo(df, ultima_corrida)

    # Exibe a tabela com logos e pontuação
    exibir_tabela_com_logos(df_campeonato)

    def evolucao_pontuacao(df, ultima_corrida):
        # Inicializa um dicionário para armazenar as pontuações por corrida para cada modelo
        # A lista 'Modelo' será usada para armazenar os modelos
        evolucao = {'Modelo': []}

        # Adiciona as colunas das corridas ao dicionário
        for corrida in range(1, ultima_corrida + 1):
            evolucao[f'Corrida {corrida}'] = []

        # Filtra o DataFrame para considerar apenas "Corolla" e "Cruze"
        df_filtrado = df[df['Modelo'].isin(['Corolla', 'Cruze'])]

        # Itera sobre os modelos "Corolla" e "Cruze"
        for modelo in df_filtrado['Modelo'].unique():
            df_modelo = df_filtrado[df_filtrado['Modelo'] == modelo]

            # Adiciona o modelo à lista 'Modelo'
            evolucao['Modelo'].append(modelo)

            # Itera sobre as corridas (de 1 até a última corrida)
            for corrida in range(1, ultima_corrida + 1):
                coluna_corrida = str(corrida)

                if coluna_corrida in df_modelo.columns:
                    # Filtra os pilotos e suas pontuações para a corrida atual
                    df_pontuacao = df_modelo[['Piloto', coluna_corrida]].sort_values(
                        by=coluna_corrida, ascending=False)

                    # Obtém os dois maiores pontuadores dessa corrida
                    top_2 = df_pontuacao.head(2)

                    # Soma as duas maiores pontuações dessa corrida
                    pontuacao_total_corrida = top_2[coluna_corrida].apply(
                        pd.to_numeric, errors='coerce').sum()

                    # Adiciona essa soma ao acumulado da corrida
                    evolucao[f'Corrida {corrida}'].append(
                        pontuacao_total_corrida)
                else:
                    # Se não houver dados para a corrida, assume pontuação 0
                    evolucao[f'Corrida {corrida}'].append(0)

        # Converte o dicionário em um DataFrame
        df_evolucao = pd.DataFrame(evolucao)

        # Calcula a "Soma" total de cada modelo, somando todas as corridas
        # Soma as corridas (excluindo a coluna 'Modelo')
        df_evolucao['Soma'] = df_evolucao.iloc[:, 1:].sum(axis=1)

        # Reorganiza as colunas para garantir que "Soma" seja a última coluna
        df_evolucao = df_evolucao[[
            'Modelo'] + [f'Corrida {i}' for i in range(1, ultima_corrida + 1)] + ['Soma']]

        # Exibe o DataFrame resultante
        return df_evolucao

    df_evolucao = evolucao_pontuacao(df, ultima_corrida)

    # Exibe o DataFrame de evolução no Streamlit
    st.write("Evolução das Pontuações ao Longo das Corridas:")
    st.dataframe(df_evolucao)

    def calcular_pontuacao_acumulada(df_evolucao):
        # Calcular a pontuação acumulada para cada modelo
        df_acumulado = df_evolucao.copy()
        modelos = df_acumulado["Modelo"].unique()

        # Iterar sobre os modelos e calcular a pontuação acumulada para cada um
        for modelo in modelos:
            df_modelo = df_acumulado[df_acumulado["Modelo"] == modelo]
            # Calculando a pontuação acumulada
            df_modelo.iloc[:, 1:] = df_modelo.iloc[:, 1:].cumsum(axis=1)
            df_acumulado.loc[df_acumulado["Modelo"] == modelo,
                             df_modelo.columns[1:]] = df_modelo.iloc[:, 1:]

        return df_acumulado

    def plotar_evolucao_acumulada(df_evolucao):
        # Calculando a pontuação acumulada
        df_acumulado = calcular_pontuacao_acumulada(df_evolucao)

        # Excluindo a coluna "Soma" para o gráfico
        df_acumulado_sem_soma = df_acumulado.drop(columns=["Soma"])

        # Converte o DataFrame de "largura" para "longo" (melt)
        df_melted = df_acumulado_sem_soma.melt(
            id_vars=["Modelo"], var_name="Corrida", value_name="Pontuação Acumulada")

        # Definindo as cores personalizadas para os modelos
        color_map = {
            "Corolla": "red",  # Corolla em vermelho
            "Cruze": "orange"  # Cruze em laranja
        }

        # Cria o gráfico de linha interativo com Plotly
        fig = px.line(df_melted,
                      x="Corrida",
                      y="Pontuação Acumulada",
                      color="Modelo",
                      line_group="Modelo",
                      title="Evolução Acumulada das Pontuações ao Longo das Corridas",
                      labels={"Pontuação Acumulada": "Pontuação Acumulada",
                              "Corrida": "Corridas"},
                      markers=True,
                      color_discrete_map=color_map)

        # Exibe o gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)

    # Exemplo de como você pode chamar a função
    plotar_evolucao_acumulada(df_evolucao)

with tabs[7]:
    def calcular_podios(df, ultima_corrida):
        # Dicionário para armazenar os pódios
        podios = {}

        # Iterar sobre as corridas até a última corrida informada
        for corrida in range(1, ultima_corrida):
            # Verifica se a corrida é Sprint ou Principal
            if corrida % 2 != 0:  # Sprint
                pontuacao = pontuacao_sprint
            else:  # Principal
                pontuacao = pontuacao_principal

            # Obter a coluna da corrida
            coluna_corrida = df.iloc[:, 5 + corrida]

            # Obter os três primeiros pilotos
            top_3_indices = coluna_corrida.nlargest(3).index

            for idx in top_3_indices:
                piloto = df.at[idx, 'Piloto']
                if piloto not in podios:
                    podios[piloto] = 0
                podios[piloto] += 1  # Incrementa o contador de pódios

        # Converter o dicionário em DataFrame
        df_podios = pd.DataFrame(list(podios.items()),
                                 columns=['Piloto', 'Pódios'])
        return df_podios

    # Calcular os pódios
    df_podios = calcular_podios(df, ultima_corrida)

    # Obter todos os pilotos
    todos_pilotos = df[['Piloto']].drop_duplicates()

    # Criar DataFrame de pódios com 0 para pilotos sem pódios
    df_podios = df_podios.merge(
        todos_pilotos, on='Piloto', how='right').fillna(0)

    # Converter a coluna de pódios para inteiro
    df_podios['Pódios'] = df_podios['Pódios'].astype(int)

    # Ordenar o DataFrame pela quantidade de pódios em ordem decrescente
    df_podios = df_podios.sort_values(by='Pódios', ascending=False)

    # Adicionar a coluna de ranking
    df_podios['Ranking'] = range(1, len(df_podios) + 1)

    # Calcular os 3 primeiros colocados
    top_3 = df_podios.nsmallest(3, 'Ranking')

    # Criar colunas para o layout do pódio
    col1, col2, col3 = st.columns(3)
    image_width = 150

    # Exibir o 1º colocado no centro
    with col2:
        primeiro = top_3.iloc[0]
        st.image(f'images/{primeiro["Piloto"]}.png',
                 caption=primeiro["Piloto"], width=image_width)
        st.write(f"**{primeiro['Piloto']}**")
        st.write(f"Pódios: {primeiro['Pódios']}")

    # Exibir o 2º colocado à esquerda
    with col1:
        st.write("")
        st.write("")
        st.write("")
        segundo = top_3.iloc[1]
        st.image(f'images/{segundo["Piloto"]}.png',
                 caption=segundo["Piloto"], width=image_width)
        st.write(f"**{segundo['Piloto']}**")
        st.write(f"Pódios: {segundo['Pódios']}")

    # Exibir o 3º colocado à direita
    with col3:
        st.write("")
        st.write("")
        st.write("")
        terceiro = top_3.iloc[2]
        st.image(f'images/{terceiro["Piloto"]}.png',
                 caption=terceiro["Piloto"], width=image_width)
        st.write(f"**{terceiro['Piloto']}**")
        st.write(f"Pódios: {terceiro['Pódios']}")

    # Exibir o restante dos pilotos em forma de tabela
    st.write("### Demais Pilotos")
    st.dataframe(
        df_podios.iloc[3:][['Ranking', 'Piloto', 'Pódios']].set_index('Ranking'))

    def calcular_podios_por_equipe(df, ultima_corrida):
        # Dicionário para armazenar os pódios por equipe
        podios_por_equipe = {}

        # Iterar sobre as corridas até a última corrida informada
        for corrida in range(1, ultima_corrida + 1):
            # Verifica se a corrida é Sprint ou Principal
            if corrida % 2 != 0:  # Sprint
                pontuacao = pontuacao_sprint
            else:  # Principal
                pontuacao = pontuacao_principal

            # Obter a coluna da corrida
            coluna_corrida = df.iloc[:, 5 + corrida]

            # Obter os três primeiros pilotos
            top_3_indices = coluna_corrida.nlargest(3).index

            for idx in top_3_indices:
                piloto = df.at[idx, 'Piloto']
                equipe = df.at[idx, 'Equipe']
                if equipe not in podios_por_equipe:
                    podios_por_equipe[equipe] = 0
                # Incrementa o contador de pódios
                podios_por_equipe[equipe] += 1

        # Converter o dicionário em DataFrame
        df_podios_equipe = pd.DataFrame(
            list(podios_por_equipe.items()), columns=['Equipe', 'Pódios'])

        # Ordenar o DataFrame pela quantidade de pódios em ordem decrescente
        df_podios_equipe = df_podios_equipe.sort_values(
            by='Pódios', ascending=False)

        return df_podios_equipe

    # Calcular os pódios por equipe
    df_podios_equipe = calcular_podios_por_equipe(df, ultima_corrida)
    # Adicionar a coluna de ranking
    df_podios_equipe['Ranking'] = range(1, len(df_podios_equipe) + 1)

    # Definir a coluna 'Ranking' como índice
    df_podios_equipe.set_index('Ranking', inplace=True)

    # Aplicar a função de estilização
    styled_df_podios_equipe = df_podios_equipe.style.apply(
        colorir_equipe, axis=1)

    # Exibir a tabela de pódios por equipe com estilo
    st.write("### Estatísticas de Pódios por Equipe")
    st.dataframe(styled_df_podios_equipe)

with tabs[8]:
    def extrair_dados_pdf(arquivo_pdf):
        """Extrai dados de um PDF e retorna um DataFrame com informações dos pilotos."""
        dados = []
        try:
            with pdfplumber.open(arquivo_pdf) as pdf:
                # Acessa a primeira página
                pagina = pdf.pages[0]

                # Extrai o texto da página
                texto = pagina.extract_text()
                if not texto:
                    st.warning(
                        f"O PDF {arquivo_pdf} está vazio ou não contém texto.")
                    return None

                # Processa o texto para extrair a tabela
                linhas = texto.split('\n')

                for linha in linhas:
                    # Ignora linhas que não têm dados relevantes
                    if not linha.strip():  # Ignora linhas vazias
                        continue

                    # Divide a linha em colunas
                    colunas = linha.split()

                    # Verifica se a primeira coluna é um número (posição)
                    if colunas and colunas[0].isdigit():
                        try:
                            # Captura a posição, número, nome e equipe
                            pos = colunas[0]
                            no = colunas[1]

                            # Combina todos os nomes do piloto
                            # Junta todos os nomes do piloto
                            name = ' '.join(colunas[2:4])

                            # Adiciona os dados à lista
                            dados.append((pos, no, name))
                        except IndexError as e:
                            print(f"Erro ao processar a linha: '{
                                  linha}'. Detalhes: {e}")
                            continue  # Ignora a linha e continua com a próxima

        except Exception as e:
            st.error(f'Erro ao ler o arquivo {arquivo_pdf}: {e}')
            return None

        # Cria um DataFrame a partir dos dados extraídos
        if dados:
            # Definindo as colunas que queremos
            colunas = ['Posição', 'Numeral', 'Piloto']
            # Cria o DataFrame com as 3 colunas
            df_qualifying = pd.DataFrame(dados, columns=colunas)
            return df_qualifying
        else:
            st.warning('Nenhuma linha de dados encontrada.')
            return None

    def carregar_dados_qualifying():
        """Carrega dados de todas as etapas de qualifying e retorna um dicionário de DataFrames."""
        dados_qualifying = {}
        for i in range(1, 13):  # Para as 12 etapas
            # Ajuste o caminho conforme necessário
            pdf_path = f'qualifying/Q{i}.pdf'
            df_qualifying = extrair_dados_pdf(pdf_path)
            if df_qualifying is not None and not df_qualifying.empty:
                # Adiciona o DataFrame ao dicionário com a etapa como chave
                dados_qualifying[f'Etapa {i}'] = df_qualifying

        return dados_qualifying  # Retorna o dicionário de DataFrames

    # Carrega os dados de qualifying
    dados_qualifying = carregar_dados_qualifying()

    # Cria um selectbox para o usuário escolher a etapa
    etapas = list(dados_qualifying.keys())
    etapa_selecionada = st.selectbox(
        "Escolha a etapa para visualizar os dados de classificação:", etapas)

    # Exibe os dados da etapa selecionada
    if etapa_selecionada in dados_qualifying:
        df_etapa = dados_qualifying[etapa_selecionada]

        # Define a coluna 'Posição' como índice
        df_etapa.set_index('Posição', inplace=True)

        # Aplica a coloração aos pilotos
        styled_df_etapa = df_etapa.style.apply(colorir_piloto, axis=1)

        st.write(f"Resultado classificação {etapa_selecionada}:")
        # Exibe o DataFrame estilizado correspondente à etapa selecionada
        st.dataframe(styled_df_etapa)
    else:
        st.write("Etapa não encontrada.")

with tabs[9]:
    def contar_avancos(dados_qualifying):
        contagem_avanco_q2 = {}
        contagem_avanco_q3 = {}
        contagem_zona_inversao = {}

        for etapa, df in dados_qualifying.items():
            for index, row in df.iterrows():
                piloto = row['Piloto']
                posicao = int(row['Posição'])

                if posicao <= 20:  # Avançou para Q2
                    if piloto not in contagem_avanco_q2:
                        contagem_avanco_q2[piloto] = 0
                    contagem_avanco_q2[piloto] += 1

                if posicao <= 8:  # Avançou para Q3
                    if piloto not in contagem_avanco_q3:
                        contagem_avanco_q3[piloto] = 0
                    contagem_avanco_q3[piloto] += 1

                if posicao <= 12:  # Entrou na zona de inversão
                    if piloto not in contagem_zona_inversao:
                        contagem_zona_inversao[piloto] = 0
                    contagem_zona_inversao[piloto] += 1

        return contagem_avanco_q2, contagem_avanco_q3, contagem_zona_inversao

    def calcular_estatisticas(dados_qualifying, piloto_selecionado):
        posicoes = []
        for etapa, df in dados_qualifying.items():
            piloto_data = df[df['Piloto'] == piloto_selecionado]
            if not piloto_data.empty:
                posicao = int(piloto_data['Posição'].values[0])
                posicoes.append(posicao)

        if posicoes:
            posicao_media = sum(posicoes) / len(posicoes)
            melhor_posicao = min(posicoes)
        else:
            posicao_media = None
            melhor_posicao = None

        return posicoes, posicao_media, melhor_posicao

    # Carregue seus dados de qualifying
    dados_qualifying = carregar_dados_qualifying()

    # Contar avanços
    contagem_q2, contagem_q3, contagem_zona_inversao = contar_avancos(
        dados_qualifying)

    # Extrai todos os pilotos únicos que participaram da temporada
    pilotos_unicos = set()
    for df in dados_qualifying.values():
        pilotos_unicos.update(df['Piloto'].unique())

    # Cria um selectbox para o usuário escolher um piloto
    piloto_selecionado = st.selectbox(
        "Escolha um piloto para visualizar as estatísticas:", list(pilotos_unicos))

    # Calcular estatísticas do piloto selecionado
    posicoes, posicao_media, melhor_posicao = calcular_estatisticas(
        dados_qualifying, piloto_selecionado)

    # Gráfico de Performance Qualifying
    st.markdown("<h2 style='text-align: center;'>Performance de Qualifying</h2>",
                unsafe_allow_html=True)
    # Filtra as etapas e posições do piloto selecionado
    etapas = list(dados_qualifying.keys())
    posicoes = []

    for etapa in etapas:
        df_etapa = dados_qualifying[etapa]
        piloto_data = df_etapa[df_etapa['Piloto'] == piloto_selecionado]
        if not piloto_data.empty:
            posicao = int(piloto_data['Posição'].values[0])
            posicoes.append(posicao)
        else:
            # Adiciona None para etapas que o piloto não participou
            posicoes.append(None)

    # Criando o gráfico interativo com Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=etapas, y=posicoes, mode='lines+markers',
                             name=piloto_selecionado, line=dict(color='blue')))

    fig.update_layout(
        title=f'Posição de Qualifying de {piloto_selecionado} por Etapa',
        xaxis_title='Etapa',
        yaxis_title='Posição',
        template='plotly_white'
    )

    st.plotly_chart(fig)

    # Painéis de informações
    st.subheader(f"Estatísticas do Piloto {piloto_selecionado}")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Avanços para Q2", contagem_q2.get(piloto_selecionado, 0))

    with col2:
        st.metric("Avanços para Q3", contagem_q3.get(piloto_selecionado, 0))

    with col3:
        st.metric("Entradas na Zona de Inversão",
                  contagem_zona_inversao.get(piloto_selecionado, 0))

    with col4:
        st.metric("Posição Média de Largada", round(posicao_media, 2)
                  if posicao_media is not None else "N/A")

    with col5:
        st.metric("Melhor Posição de Largada",
                  melhor_posicao if melhor_posicao is not None else "N/A")

    # Adicionando interatividade com um gráfico de barras para a contagem de avanços
    etapas = list(dados_qualifying.keys())
    avancos_q2 = [contagem_q2.get(piloto, 0) for piloto in pilotos_unicos]
    avancos_q3 = [contagem_q3.get(piloto, 0) for piloto in pilotos_unicos]
    zona_inversao = [contagem_zona_inversao.get(
        piloto, 0) for piloto in pilotos_unicos]

    # Criando o gráfico de barras interativo com Plotly
    fig_barras = go.Figure()
    fig_barras.add_trace(go.Bar(x=list(pilotos_unicos),
                         y=avancos_q2, name='Avanços para Q2', offsetgroup=1))
    fig_barras.add_trace(go.Bar(x=list(pilotos_unicos),
                         y=avancos_q3, name='Avanços para Q3', offsetgroup=2))
    fig_barras.add_trace(go.Bar(x=list(pilotos_unicos),
                         y=zona_inversao, name='Zona de Inversão', offsetgroup=3))

    fig_barras.update_layout(
        title='Contagem de Avanços e Zona de Inversão por Piloto',
        xaxis_title='Pilotos',
        yaxis_title='Contagem',
        barmode='group',
        xaxis_tickangle=-45,
        template='plotly_white'
    )

    st.plotly_chart(fig_barras)

    # Criar um DataFrame para armazenar as estatísticas dos pilotos
    estatisticas_pilotos = []

    for piloto in pilotos_unicos:
        estatisticas_piloto = {
            "Piloto": piloto,
            "Avanços para Q2": contagem_q2.get(piloto, 0),
            "Avanços para Q3": contagem_q3.get(piloto, 0),
            "Entradas na Zona de Inversão": contagem_zona_inversao.get(piloto, 0),
            "Posição Média de Largada": round(calcular_estatisticas(dados_qualifying, piloto)[1], 2) if calcular_estatisticas(dados_qualifying, piloto)[1] is not None else "N/A"
        }
        estatisticas_pilotos.append(estatisticas_piloto)

    # Criar um DataFrame a partir da lista de dicionários
    df_estatisticas = pd.DataFrame(estatisticas_pilotos)

    # Aplicar a coloração ao DataFrame
    styled_df_estatisticas = df_estatisticas.style.apply(colorir_piloto, axis=1)

    # Formatar a coluna "Posição Média de Largada" para exibição
    styled_df_estatisticas = styled_df_estatisticas.format({
        "Posição Média de Largada": "{:.2f}"  # Formatar para duas casas decimais
    })
        
    st.markdown("<h2 style='text-align: center;'>Estatísticas dos Pilotos</h2>", unsafe_allow_html=True)
    st.dataframe(styled_df_estatisticas)

with tabs[10]:
    st.markdown("<h2 style='text-align: center;'>Comparação qualifying</h2>",
                unsafe_allow_html=True)

    # Cria um selectbox para o usuário escolher dois pilotos
    piloto1 = st.selectbox("Escolha o primeiro piloto:", list(pilotos_unicos))
    piloto2 = st.selectbox("Escolha o segundo piloto:", list(pilotos_unicos))

    # Função para calcular as estatísticas de um piloto
    def obter_estatisticas_comparacao(dados_qualifying, piloto):
        posicoes, posicao_media, melhor_posicao = calcular_estatisticas(
            dados_qualifying, piloto)
        contagem_q2, contagem_q3, contagem_zona_inversao = contar_avancos(
            dados_qualifying)

        return {
            "Melhor Posição": melhor_posicao,
            "Média de Posição": round(posicao_media,2),
            "Avanços para Q2": contagem_q2.get(piloto, 0),
            "Avanços para Q3": contagem_q3.get(piloto, 0),
        }

    # Obtém as estatísticas para os pilotos selecionados
    estatisticas_piloto1 = obter_estatisticas_comparacao(
        dados_qualifying, piloto1)
    estatisticas_piloto2 = obter_estatisticas_comparacao(
        dados_qualifying, piloto2)

    # Cria um DataFrame para as estatísticas
    comparacao_df = pd.DataFrame({
        "Métrica": list(estatisticas_piloto1.keys()),
        piloto1: list(estatisticas_piloto1.values()),
        piloto2: list(estatisticas_piloto2.values()),
    })

    # Gráfico de barras horizontal para comparação
    fig_comparacao = go.Figure()

    # Adiciona as barras do piloto 1 (crescendo para a esquerda)
    fig_comparacao.add_trace(go.Bar(
        y=comparacao_df['Métrica'],
        # Inverte o sinal para crescer para a esquerda
        x=-comparacao_df[piloto1],
        name=piloto1,
        orientation='h',
        marker=dict(color='blue')  # Cor para o piloto 1
    ))

    # Adiciona as barras do piloto 2 (crescendo para a direita)
    fig_comparacao.add_trace(go.Bar(
        y=comparacao_df['Métrica'],
        x=comparacao_df[piloto2],  # Mantém o sinal para crescer para a direita
        name=piloto2,
        orientation='h',
        marker=dict(color='orange')  # Cor para o piloto 2
    ))

    # Atualiza o layout do gráfico
    fig_comparacao.update_layout(
        title='Comparação de Pilotos',
        title_x=0.45,
        xaxis_title='Valores',
        yaxis_title='',
        xaxis=dict(showgrid=True, zeroline=True,
                   range=[-30, 30],
                   # Valores do eixo X
                   tickvals=[-30, -20, -10, 0, 10, 20, 30],
                   ticktext=['30', '20', '10', '0', '10',
                             '20', '30'],  # Rótulos do eixo X
                   zerolinecolor='black', zerolinewidth=5),
        yaxis=dict(showgrid=False),
        barmode='overlay',
        template='plotly_white'
    )

    # Exibe as imagens e dados dos pilotos em colunas
    col1, col2 = st.columns(2)

    # Função para exibir a imagem do piloto
    def exibir_imagem_piloto(piloto):
        image_path = f'images/{piloto}.png'
        if os.path.exists(image_path):
            st.image(image_path, caption=piloto, width=150)
        else:
            st.image('images/Pilotodesc.png', caption=piloto, width=150)

    with col1:
        exibir_imagem_piloto(piloto1)
        for metric, value in estatisticas_piloto1.items():
            st.metric(metric, value)

    with col2:
        exibir_imagem_piloto(piloto2)
        for metric, value in estatisticas_piloto2.items():
            st.metric(metric, value)

    # Exibe o gráfico de comparação
    st.plotly_chart(fig_comparacao)
