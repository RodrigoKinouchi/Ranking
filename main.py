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
df = df.drop(index=0)

# Passo 1: Substituir "NC" por 0 nas colunas de pontuação (corridas 1 a 22)
df.iloc[:, 5:27] = df.iloc[:, 5:27].replace("NC", 0)

# Passo 2: Converter as colunas de pontuação para numérico, forçando erros para NaN
df.iloc[:, 5:27] = df.iloc[:, 5:27].apply(pd.to_numeric, errors='coerce')

# Passo 3: Substituir "DSC" por NaN para que essas corridas não sejam consideradas no cálculo do descarte
df.iloc[:, 5:27] = df.iloc[:, 5:27].replace("DSC", pd.NA)

# Passo 4: Remover casas decimais (forçando as colunas de pontuação para inteiros)
df.iloc[:, 5:27] = df.iloc[:, 5:27].fillna(0).round(0).astype(int)

# Passo 5: Calcular o "Descarte" (menor pontuação válida, ignorando "DSC")
df['Descarte'] = df.iloc[:, 5:27].min(axis=1, skipna=True)


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

# Criando abas de visualização
tabs = st.tabs(['Pilotos', 'Equipes', 'Wins', 'Análise de consistência'])

with tabs[0]:

    coluna_soma = 'Soma'

    # Cria uma lista com as colunas do DataFrame, colocando "Soma" na posição desejada
    novas_colunas = ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma'] + \
        [col for col in df.columns if col not in [
            'Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma']]

    # Reorganiza o DataFrame com a nova ordem de colunas
    df = df[novas_colunas]

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
    colunas_pontuacao = df.columns[5:28].tolist() + df.columns[29:31].tolist()

    # Verificar se todas as colunas de pontuação são numéricas antes de realizar a soma
    df[colunas_pontuacao] = df[colunas_pontuacao].apply(
        pd.to_numeric, errors='coerce')

    # Agrupar por equipe e somar as pontuações de cada corrida
    df_equipes = df.groupby('Equipe')[colunas_pontuacao].sum()

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

with tabs[2]:

    # Passo 1: Contar vitórias em cada tipo de corrida (Sprint e Principal)
    vitorias_sprint = {}
    vitorias_principal = {}
    vitorias_gerais = {}

    # Loop pelas linhas do DataFrame para contar as vitórias de cada piloto nas corridas Sprint e Principal
    for _, row in df.iterrows():
        piloto = row['Piloto']

        # Contando vitórias nas corridas Sprint (ímpares) - valores 55
        vitorias_sprint_count = (row.iloc[6:27:2] == 55).sum()

        # Contando vitórias nas corridas Principal (pares) - valores 80
        vitorias_principal_count = (row.iloc[7:27:2] == 80).sum()

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

    # Passo 2: Criar gráfico de pizza para vitórias gerais
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
        st.plotly_chart(fig_gerais)

    # Passo 3: Criar gráfico de pizza para vitórias nas corridas Sprint
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

        # Exibindo o gráfico de vitórias Sprint
        st.plotly_chart(fig_sprint)

    # Passo 4: Criar gráfico de pizza para vitórias nas corridas Principal
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

    else:
        st.write("Nenhum piloto com vitórias foi encontrado.")

with tabs[3]:
    st.write("### Análise de Consistência")
    # Contar o número total de corridas (colunas de pontuação)
    # Assumindo que as colunas de pontuação começam na posição 5 até a penúltima
    df = df.drop(columns=['Descarte'])
    total_corridas = 20

    # Calcular o número de corridas participadas (onde a pontuação é diferente de zero)
    df['Corridas Participadas'] = df.iloc[:, 7:-
                                          1].apply(lambda x: (x != 0).sum(), axis=1)

    # Calcular o número de abandonos (total de corridas - corridas participadas)
    df['Abandonos'] = total_corridas - df['Corridas Participadas']

    # Exibir número de abandonos por piloto
    st.write("#### Número de Abandonos por Piloto")
    st.dataframe(df[['Piloto', 'Abandonos']])

    # Média de Pontuação por Corrida (Ordenada)
    df['Média por Corrida'] = df.iloc[:, 6:26].apply(
        pd.to_numeric, errors='coerce').mean(axis=1)
    df_sorted_by_media = df.sort_values('Média por Corrida', ascending=False)
    st.write("#### Ranking de Pilotos por Média de Pontuação por Corrida")
    st.dataframe(
        df_sorted_by_media[['Piloto', 'Média por Corrida']])

    # Desvio Padrão da Pontuação (Ordenado do Menor para o Maior)
    df['Desvio Padrão'] = df.iloc[:, 6:26].apply(
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
