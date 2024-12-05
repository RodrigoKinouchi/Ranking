import pdfplumber
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import plotly.graph_objs as go
import matplotlib.pyplot as plt


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
    "Informe o número da última corrida realizada", min_value=1, max_value=24, value=22, step=1)

# Passo 1: Substituir "NC" por 0 nas colunas de pontuação (corridas 1 até a última corrida informada)
df.iloc[:, 5:ultima_corrida+6] = df.iloc[:,
                                         5:ultima_corrida+6].replace("NC", 0)

# Passo 2: Converter as colunas de pontuação para numérico, forçando erros para NaN
df.iloc[:, 5:ultima_corrida+6] = df.iloc[:,
                                         5:ultima_corrida+6].apply(pd.to_numeric, errors='coerce')

# Passo 3: Substituir "DSC" por NaN para que essas corridas não sejam consideradas no cálculo do descarte
df.iloc[:, 5:ultima_corrida+6] = df.iloc[:,
                                         5:ultima_corrida+6].replace("DSC", pd.NA)

# Passo 4: Remover casas decimais (forçando as colunas de pontuação para inteiros)
df.iloc[:, 5:ultima_corrida+6] = df.iloc[:,
                                         5:ultima_corrida+6].fillna(0).round(0).astype(int)

# Passo 5: Calcular o "Descarte" (menor pontuação válida, ignorando "DSC")
df['Descarte'] = df.iloc[:, 5:ultima_corrida+6].min(axis=1, skipna=True)


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
               'Principal', 'Análise de consistência', 'Manual'])

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
    df_equipes_sorted = df_equipes_sorted.reset_index(drop=True)

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

        st.subheader("Evolução dos Pilotos - Corridas Sprint")
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
    st.write("### Análise de Consistência")
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
    st.write("#### Número de Abandonos por Piloto")
    st.dataframe(df[['Piloto', 'Abandonos']])

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
            df_filtered = df.iloc[:, :ultima_corrida+7]

            # Aplicando o estilo no DataFrame
            df_styled = df_filtered.style.apply(colorir_piloto, axis=1)

            # Exibe o DataFrame atualizado
            st.success(f"Pontuações da Corrida {
                       proxima_corrida} atualizadas com sucesso!")
            st.dataframe(df_styled, use_container_width=True)
    else:
        st.warning("A próxima corrida ultrapassa o número máximo de 24 corridas.")
