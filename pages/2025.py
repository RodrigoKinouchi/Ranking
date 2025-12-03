import pdfplumber
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import os
import re


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
with pdfplumber.open("tabela2025.pdf") as pdf:
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
                  "16", "17", "18", "19", "20", "21", "Descarte", "22", "23", "Soma"
                  ]
df.columns = novo_cabecalho

# Cria uma lista com as colunas do DataFrame, colocando "Soma" na posição desejada
novas_colunas = ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma', "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                 "16", "17", "18", "19", "20", "21", "22", "23", "Descarte"] + \
    [col for col in df.columns if col not in ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma', "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                                              "16", "17", "18", "19", "20", "21", "22", "23", "Descarte"]]

df = df[novas_colunas]
df = df.drop(index=0)
df["Piloto"] = df["Piloto"].str.title()
df["Equipe"] = df["Equipe"].str.title()

modelo_map = {
    'Q': 'Mitsubishi',
    'A': 'Crevrolet',
    'S': 'Toyota'
}

# Substitui os códigos pela montadora
df['Modelo'] = df['Modelo'].map(modelo_map)


# Input do usuário para a última corrida
ultima_corrida = st.number_input(
    "Informe o número da última corrida realizada", min_value=1, max_value=24, value=21, step=1)

# Substitui "." (etapas futuras) por NaN
df.iloc[:, 6:ultima_corrida+5] = df.iloc[:, 6:ultima_corrida+5].replace(".", pd.NA)

# Criar o DataFrame para contabilizar os motivos de abandono
df_abandonos = pd.DataFrame(columns=["Piloto", "NC", "EXC", "DSC", "NP"])
abandonos_data = []
df_cortez = df

for _, row in df.iterrows():
    piloto = row['Piloto']
    
    # Inicializa contadores
    nc_count = 0
    exc_count = 0
    dsc_count = 0
    np_count = 0

    for score in row[6:ultima_corrida+6]:
        if score == "NC":
            nc_count += 1
        elif score == "EXC":
            exc_count += 1
        elif score == "DSC":
            dsc_count += 1
        elif pd.isna(score) or score in ["", "NP", "."]:
            np_count += 1

    abandonos_data.append({
        "Piloto": piloto,
        "NC": nc_count,
        "EXC": exc_count,
        "DSC": dsc_count,
        "NP": np_count
    })

df_abandonos = pd.DataFrame(abandonos_data)
df_original_para_descartes = df.copy()

# Substituições para facilitar os cálculos
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:, 6:ultima_corrida+6].replace({
    "NC": 0,         # NC conta como zero ponto
    "DSC": pd.NA,    # DSC desconsidera da pontuação
    "EXC": pd.NA     # EXC também
})

# Converte os valores para numérico (forçando NaN onde necessário)
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:, 6:ultima_corrida+6].apply(
    pd.to_numeric, errors='coerce'
)

# Calcula o descarte das duas menores pontuações válidas
#def calcular_descarte(row):
    #pontuacoes_validas = row[6:ultima_corrida+6].dropna()
    #if len(pontuacoes_validas) > 1:
        #return pontuacoes_validas.nsmallest(2).sum()
    #return 0

#df['Descarte'] = df.apply(calcular_descarte, axis=1).round(0).astype(int)

# Substitui NaN restantes por 0 para soma
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:, 6:ultima_corrida+6].fillna(0)

# Soma de todas as pontuações
df['Soma'] = df.iloc[:, 6:ultima_corrida+6].sum(axis=1).round(0).astype(int)

# Subtrai o descarte da soma total
#df['Soma'] = (df['Soma'] - df['Descarte']).round(0).astype(int)

# Garante que o tipo é numérico inteiro (evita erros em plotagens e análises futuras)
df.iloc[:, 6:ultima_corrida+6] = df.iloc[:, 6:ultima_corrida+6].astype(int)


mapa_corridas = {
    1: {'tipo': 'Sprint', 'pontuacao': {i: 16 - i for i in range(1, 16)}},  # Corrida especial
    2: {'tipo': 'Sprint'},
    3: {'tipo': 'Principal'},
    4: {'tipo': 'Sprint'},
    5: {'tipo': 'Principal'},
    6: {'tipo': 'Sprint'},
    7: {'tipo': 'Principal'},
    8: {'tipo': 'Sprint'},
    9: {'tipo': 'Principal'},
    10: {'tipo': 'Sprint'},
    11: {'tipo': 'Principal'},
    12: {'tipo': 'Sprint'},
    13: {'tipo': 'Principal'},
    14: {'tipo': 'Sprint'},
    15: {'tipo': 'Principal'},
    16: {'tipo': 'Sprint'},
    17: {'tipo': 'Principal'},
    18: {'tipo': 'Sprint'},
    19: {'tipo': 'Principal'},
    20: {'tipo': 'Sprint'},
    21: {'tipo': 'Principal'},
    22: {'tipo': 'Sprint'},
    23: {'tipo': 'Principal'},
}

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

colunas_corridas = df.columns[6:28]

corridas_sprint = []
corridas_principal = []
valores_vitoria_por_coluna = {}

for i, col in enumerate(colunas_corridas):
    corrida_num = i + 1
    corrida_info = mapa_corridas.get(corrida_num)
    if not corrida_info:
        continue
    tipo = corrida_info['tipo']
    pontuacao_personalizada = corrida_info.get('pontuacao')

    if tipo == 'Sprint':
        corridas_sprint.append(col)
        valores_vitoria_por_coluna[col] = max(pontuacao_personalizada.values()) if pontuacao_personalizada else max(pontuacao_sprint.values())
    elif tipo == 'Principal':
        corridas_principal.append(col)
        valores_vitoria_por_coluna[col] = max(pontuacao_principal.values())

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


# === Contar vitórias ===
vitorias_sprint = {}
vitorias_principal = {}
vitorias_gerais = {}

vitorias_sprint_equipes = {}
vitorias_principal_equipes = {}


for _, row in df.iterrows():
    piloto = row['Piloto']
    equipe = row['Equipe']

    sprint_vitorias = 0
    principal_vitorias = 0

    for col in corridas_sprint:
        if pd.to_numeric(row[col], errors='coerce') == valores_vitoria_por_coluna[col]:
            sprint_vitorias += 1

    for col in corridas_principal:
        if pd.to_numeric(row[col], errors='coerce') == valores_vitoria_por_coluna[col]:
            principal_vitorias += 1

    total_vitorias = sprint_vitorias + principal_vitorias

    vitorias_sprint[piloto] = sprint_vitorias
    vitorias_principal[piloto] = principal_vitorias
    vitorias_gerais[piloto] = total_vitorias

    vitorias_sprint_equipes[equipe] = vitorias_sprint_equipes.get(equipe, 0) + sprint_vitorias
    vitorias_principal_equipes[equipe] = vitorias_principal_equipes.get(equipe, 0) + principal_vitorias

# Pilotos com pelo menos uma vitória em cada tipo
vitorias_sprint_filtradas = {p: v for p, v in vitorias_sprint.items() if v > 0}
vitorias_principal_filtradas = {p: v for p, v in vitorias_principal.items() if v > 0}
vitorias_gerais_filtradas = {p: v for p, v in vitorias_gerais.items() if v > 0}

# === Converter para DataFrame de vitórias por equipe ===
vitorias_df = pd.DataFrame({
    'Equipe': list(set(vitorias_sprint_equipes.keys()) | set(vitorias_principal_equipes.keys()))
})
vitorias_df['Vitórias Sprint'] = vitorias_df['Equipe'].map(vitorias_sprint_equipes).fillna(0).astype(int)
vitorias_df['Vitórias Principal'] = vitorias_df['Equipe'].map(vitorias_principal_equipes).fillna(0).astype(int)
vitorias_df['Vitórias Totais'] = vitorias_df['Vitórias Sprint'] + vitorias_df['Vitórias Principal']
vitorias_df = vitorias_df.sort_values(by='Vitórias Totais', ascending=False)

# === Gráficos ===
fig_sprint_equipes = px.pie(vitorias_df,
                            names='Equipe',
                            values='Vitórias Sprint',
                            title='Vitórias por Equipe - Corridas Sprint',
                            color='Equipe',
                            color_discrete_sequence=px.colors.qualitative.Set3)

fig_principal_equipes = px.pie(vitorias_df,
                               names='Equipe',
                               values='Vitórias Principal',
                               title='Vitórias por Equipe - Corridas Principal',
                               color='Equipe',
                               color_discrete_sequence=px.colors.qualitative.Set1)

fig_total_equipes = px.pie(vitorias_df,
                           names='Equipe',
                           values='Vitórias Totais',
                           title='Vitórias Totais por Equipe',
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
               'Principal', 'Análise de consistência', 'Montadora', 'Pódios',
                'Resultados qualifyings', 'Estatisticas de qualifying', 'Comparação','Cortez'])

with tabs[0]:

    # Função para aplicar estilos ao DataFrame
    def colorir_piloto(row):
        # Dicionário de cores
        color_map = {
            'Gabriel Casagrande': 'background-color: purple; color: white;',
            'Lucas Foresti': 'background-color: gray; color: white;',
            'Cesar Ramos': 'background-color: yellow; color: black;',
            'Thiago Camilo': 'background-color: red; color: white;',
            'Helio Castroneves': 'background-color: green; color: white;'
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

    # ========== NOVA TABELA COM DESCARTES ==========
    st.write("---")
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #f7fafc; font-size: 28px; font-weight: 700; margin-bottom: 5px;'>
            🏁 Classificação com Descarte de Pontuações
        </h2>
        <p style='color: #a0aec0; font-size: 14px; margin-top: 5px;'>
            Classificação final após descartar as 5 menores pontuações de cada piloto
        </p>
    </div>
    """, unsafe_allow_html=True)

    df_com_descarte = df.reset_index()

    # Garante que a coluna 'Posição' exista
    if 'Posição' not in df_com_descarte.columns:
        df_com_descarte.insert(0, 'Posição', range(1, len(df_com_descarte) + 1))

    # Listar colunas de pontuação (corridas de 1 até ultima_corrida)
    colunas_pontuacao = [str(i) for i in range(1, ultima_corrida)]

    # Criar dicionário para identificar quais colunas eram "EXC" antes das transformações
    # Usar o DataFrame original para identificar EXC
    df_original_para_exc = df_original_para_descartes.copy()
    exc_por_piloto = {}  # piloto -> conjunto de colunas que eram EXC
    
    for idx, row in df_original_para_exc.iterrows():
        piloto = row['Piloto']
        colunas_exc = set()
        
        for col in colunas_pontuacao:
            if col in row.index:
                valor = row[col]
                # Verificar se era EXC (antes das transformações)
                if isinstance(valor, str) and valor.strip().upper() == "EXC":
                    colunas_exc.add(col)
                elif pd.isna(valor):
                    # Se era NaN, pode ter sido EXC ou DSC, mas vamos verificar
                    # Na verdade, vamos considerar apenas se for explicitamente "EXC"
                    pass
        
        exc_por_piloto[piloto] = colunas_exc

    def calcular_descartes(row):
        piloto = row['Piloto']
        colunas_exc = exc_por_piloto.get(piloto, set())
        pontuacoes_validas = []
        
        for col in colunas_pontuacao:
            if col in row.index:
                # Se esta coluna era EXC, não pode ser descartada
                if col in colunas_exc:
                    continue
                    
                try:
                    valor = row[col]
                    valor_numeric = pd.to_numeric(valor, errors='coerce')
                    # Valores > 0 podem ser descartados
                    # Valores 0 podem ser descartados SE não eram EXC (já filtrado acima)
                    # NaN não pode ser descartado (já que era DSC)
                    if pd.notna(valor_numeric) and valor_numeric >= 0:
                        # Incluir valores >= 0 (incluindo 0 que era NC ou NP)
                        pontuacoes_validas.append(valor_numeric)
                except:
                    pass

        # Se houver menos de 5, descarta todas
        if len(pontuacoes_validas) == 0:
            return 0
        elif len(pontuacoes_validas) <= 5:
            return sum(sorted(pontuacoes_validas)[:5])
        else:
            # Ordena e pega as 5 menores
            return sum(sorted(pontuacoes_validas)[:5])

    # --- Função para identificar quais colunas foram descartadas ---
    def identificar_colunas_descartadas(row):
        piloto = row['Piloto']
        colunas_exc = exc_por_piloto.get(piloto, set())
        pontuacoes_com_coluna = []
        
        for col in colunas_pontuacao:
            if col in row.index:
                # Se esta coluna era EXC, não pode ser descartada
                if col in colunas_exc:
                    continue
                    
                try:
                    valor = row[col]
                    valor_numeric = pd.to_numeric(valor, errors='coerce')
                    # Valores >= 0 podem ser descartados (incluindo 0 que era NC ou NP)
                    if pd.notna(valor_numeric) and valor_numeric >= 0:
                        pontuacoes_com_coluna.append((valor_numeric, col))
                except:
                    pass
        
        # Ordena por valor (crescente) - as menores primeiro
        pontuacoes_com_coluna = sorted(pontuacoes_com_coluna, key=lambda x: x[0])

        if len(pontuacoes_com_coluna) <= 5:
            return [col for _, col in pontuacoes_com_coluna]
        else:
            # Retorna as 5 menores
            return [col for _, col in pontuacoes_com_coluna[:5]]

    # Calcula descartes e colunas descartadas ANTES de criar a função de estilo
    df_com_descarte['Descarte'] = df_com_descarte.apply(calcular_descartes, axis=1).astype(int)
    
    # Criar dicionário piloto -> colunas descartadas ANTES de ordenar
    descartes_por_piloto = {}
    for idx, row in df_com_descarte.iterrows():
        piloto = row['Piloto']
        descartes_por_piloto[piloto] = identificar_colunas_descartadas(row)
    
    # Calcular soma com descarte
    df_com_descarte['Soma_Com_Descarte'] = (df_com_descarte['Soma'] - df_com_descarte['Descarte']).astype(int)
    
    # Renomear coluna para título mais apresentável ANTES de ordenar
    df_com_descarte = df_com_descarte.rename(columns={'Soma_Com_Descarte': 'Pontuação Final'})
    
    # Ordenar por Pontuação Final
    df_com_descarte = df_com_descarte.sort_values(by='Pontuação Final', ascending=False).reset_index(drop=True)
    
    # Recalcular posição baseada na nova ordenação
    df_com_descarte['Posição'] = range(1, len(df_com_descarte) + 1)
    
    # Reordenar colunas para manter a ordem original
    colunas_ordenadas = ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma', 'Pontuação Final', 'Descarte']
    colunas_restantes = [c for c in df_com_descarte.columns if c not in colunas_ordenadas + colunas_pontuacao]
    df_com_descarte = df_com_descarte[colunas_ordenadas + colunas_pontuacao + colunas_restantes]

    # --- Função de estilo corrigida - sem gradientes, destaque claro nos descartes ---
    def estilo_completo(row):
        # Cores profissionais para pilotos com fundo escuro
        color_map = {
            'Gabriel Casagrande': 'background-color: #7B68EE; color: white; font-weight: 700;',
            'Lucas Foresti': 'background-color: #778899; color: white; font-weight: 700;',
            'Cesar Ramos': 'background-color: #FFA500; color: #1a1a1a; font-weight: 700;',
            'Thiago Camilo': 'background-color: #DC143C; color: white; font-weight: 700;',
            'Helio Castroneves': 'background-color: #32CD32; color: white; font-weight: 700;'
        }
        # Fundo escuro padrão para linhas sem cor específica
        cor_base = color_map.get(row['Piloto'], 'background-color: #2d3748; color: #e2e8f0; font-weight: 500;')
        colunas_descartadas = descartes_por_piloto.get(row['Piloto'], [])

        styles = []
        
        # Aplicar estilo para cada coluna
        for i, col in enumerate(row.index):
            # Destaque especial para colunas de pontuação descartadas - SEMPRE vermelho brilhante
            if col in colunas_pontuacao and col in colunas_descartadas:
                # Estilo vermelho sólido e vibrante para descartes - sem gradiente
                style = 'background-color: #ff4444; color: white; font-weight: 900; border: 3px solid #ff0000; box-shadow: 0 0 10px rgba(255, 0, 0, 0.8); text-align: center;'
            
            # Destaque para colunas importantes (Soma, Pontuação Final, Descarte)
            elif col in ['Soma', 'Pontuação Final', 'Descarte']:
                if col == 'Pontuação Final':
                    style = 'background-color: #1e3a1e; color: #4CAF50; font-weight: 800; border-left: 5px solid #4CAF50; border-right: 5px solid #4CAF50; text-align: center; vertical-align: middle;'
                elif col == 'Descarte':
                    style = 'background-color: #3d2817; color: #ff9800; font-weight: 700; border-left: 5px solid #ff9800; text-align: center; vertical-align: middle;'
                else:
                    style = 'background-color: #1a1f3d; color: #2196F3; font-weight: 700; border-left: 5px solid #2196F3; text-align: center; vertical-align: middle;'
            
            # Colunas de informação e pontuação normais - usar cor base
            else:
                style = cor_base + ' text-align: center; vertical-align: middle;'
            
            styles.append(style)
        
        return styles
    
    # Aplicar estilo com formatação adicional e tema escuro
    df_com_descarte_styled = (df_com_descarte.set_index('Posição')
                              .style
                              .apply(estilo_completo, axis=1)
                              .format({
                                  'Soma': '{:,.0f}',
                                  'Pontuação Final': '{:,.0f}',
                                  'Descarte': '{:,.0f}'
                              }, na_rep='')
                              .set_properties(**{
                                  'text-align': 'center',
                                  'vertical-align': 'middle',
                                  'font-size': '13px',
                                  'padding': '10px 12px'
                              })
                              .set_properties(**{
                                  'text-align': 'center',
                                  'vertical-align': 'middle'
                              }, subset=['Pontuação Final', 'Soma', 'Descarte'])
                              .set_table_styles([
                                  {
                                      'selector': 'th',
                                      'props': [
                                          ('background-color', '#1a202c'),
                                          ('color', '#f7fafc'),
                                          ('font-weight', 'bold'),
                                          ('text-align', 'center'),
                                          ('vertical-align', 'middle'),
                                          ('padding', '14px'),
                                          ('font-size', '14px'),
                                          ('border', '2px solid #2d3748'),
                                          ('text-transform', 'uppercase'),
                                          ('letter-spacing', '0.5px')
                                      ]
                                  },
                                  {
                                      'selector': 'td',
                                      'props': [
                                          ('border', '1px solid #2d3748'),
                                          ('transition', 'all 0.2s ease'),
                                          ('text-align', 'center'),
                                          ('vertical-align', 'middle')
                                      ]
                                  },
                                  {
                                      'selector': 'tr:hover',
                                      'props': [
                                          ('background-color', '#2d3748'),
                                          ('cursor', 'pointer')
                                      ]
                                  },
                                  {
                                      'selector': 'table',
                                      'props': [
                                          ('background-color', '#1a202c'),
                                          ('border-collapse', 'collapse'),
                                          ('width', '100%')
                                      ]
                                  }
                              ]))
    # Adicionar uma explicação visual melhorada antes da tabela
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); border-left: 5px solid #ff4444; padding: 15px; margin-bottom: 20px; border-radius: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
        <strong style='color: #f7fafc; font-size: 16px;'>📊 Legenda:</strong> 
        <span style='color: #e2e8f0;'>Valores destacados em</span> 
        <span style='background-color: #ff4444; padding: 6px 12px; border-radius: 4px; border: 2px solid #ff0000; font-weight: bold; color: white; box-shadow: 0 0 10px rgba(255, 0, 0, 0.6);'>vermelho</span> 
        <span style='color: #e2e8f0;'>representam as <strong>5 menores pontuações descartadas</strong> de cada piloto.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(df_com_descarte_styled, use_container_width=True, height=600)


with tabs[1]:
    # Passo 6: Agrupar por equipe e somar as pontuações
    colunas_pontuacao = df.columns[5:29].tolist()

    # Garantir que as colunas sejam numéricas
    df[colunas_pontuacao] = df[colunas_pontuacao].apply(pd.to_numeric, errors='coerce')

    # Agrupar por equipe e somar as pontuações
    df_equipes = df.groupby('Equipe')[colunas_pontuacao].sum().reset_index()

    # Criar a coluna "Soma" com a soma das pontuações de cada equipe
    df_equipes['Soma'] = df_equipes[colunas_pontuacao].sum(axis=1)

    # Ordenar pela soma
    df_equipes_sorted = df_equipes.sort_values(by='Soma', ascending=False).reset_index(drop=True)

    # Arredondar e converter
    df_equipes_sorted['Soma'] = df_equipes_sorted['Soma'].round(0).astype(int)
    df_equipes_sorted['Descarte'] = df_equipes_sorted['Descarte'].round(0).astype(int)

    # Adicionar a coluna de posição
    df_equipes_sorted['Posição'] = df_equipes_sorted['Soma'].rank(ascending=False, method='min').astype(int)

    # Reordenar as colunas
    colunas = ['Posição'] + [col for col in df_equipes_sorted.columns if col != 'Posição']
    df_equipes_sorted = df_equipes_sorted[colunas]

    # Garantir índice único para estilização
    df_equipes_sorted = df_equipes_sorted.reset_index(drop=True)

    # Arredondar e converter todas as colunas numéricas (exceto 'Equipe') para int
    colunas_numericas = df_equipes_sorted.columns.difference(['Equipe'])

    df_equipes_sorted[colunas_numericas] = df_equipes_sorted[colunas_numericas].fillna(0).round(0).astype(int)

    # Função de estilo
    def colorir_equipe(row):
        color_map_equipes = {
            'IPIRANGA RACING': 'background-color: yellow; color: black;',
            'AMATTHEIS VOGEL': 'background-color: orange; color: black;',
            'AMATTHEIS RACING': 'background-color: green; color: black;'
        }
        equipe = row['Equipe'].strip().upper()
        color = color_map_equipes.get(equipe, '')
        return [color] * len(row) if color else [''] * len(row)
    
    # Substituir o índice por espaços únicos para evitar erro com Styler
    df_equipes_sorted.index = [' ' * (i + 1) for i in range(len(df_equipes_sorted))]
    # Aplicar o estilo no DataFrame final correto
    df_equipes_styled = df_equipes_sorted.style.apply(colorir_equipe, axis=1)


    # Exibir
    st.write("### Tabela de Pontuação por Equipe")
    st.dataframe(df_equipes_styled.hide(
        axis="index"), use_container_width=True, hide_index= True)

    # Gráfico de vitórias
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
    st.dataframe(df_ranking_sprint_styled, hide_index=True)

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
        st.dataframe(df_ranking_principal_styled, hide_index=True)

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
    #st.write("#### Quantidade de corridas sem pontuar por Piloto")
    #st.dataframe(df[['Piloto', 'Abandonos']])

    # Manipulando o df_abandonos
    # Criar a coluna "TOTAL"
    df_abandonos["TOTAL"] = df_abandonos["NC"] + df_abandonos["EXC"] + df_abandonos["DSC"] + df_abandonos["NP"]

    # Criar a coluna "%"
    df_abandonos["%"] = (df_abandonos["TOTAL"] / ultima_corrida) * 100
    # Garantir que a coluna "%" seja numérica antes de arredondar
    df_abandonos["%"] = pd.to_numeric(df_abandonos["%"], errors='coerce')
    # Arredondar a coluna "%" para 2 casas decimais
    df_abandonos["%"] = df_abandonos["%"].round(1)
    # Calcular a coluna "Eficiência" como 100 - %
    df_abandonos["Eficiência"] = 100 - df_abandonos["%"]
    df_abandonos.drop(columns=["%"], inplace=True)
    # Aplicar a coloração ao DataFrame df_abandonos
    styled_df_abandonos = df_abandonos.style.apply(colorir_piloto, axis=1).format({
    "Eficiência": "{:.1f}%"  # Formatar para 1 casa decimal e adicionar o símbolo de porcentagem
    })

    st.write("#### Confiabilidade")
    st.dataframe(styled_df_abandonos, hide_index=True)

    # Média de Pontuação por Corrida (Ordenada)
    df['Média por Corrida'] = (df['Soma'] / ultima_corrida).round(2)
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

        # Junta com o DataFrame principal para trazer a equipe de cada piloto
    df_eficiencia = df_abandonos.merge(df[['Piloto', 'Equipe']], on='Piloto', how='left')

    # Agrupa por equipe e calcula a média da eficiência dos pilotos
    df_eficiencia_equipes = df_eficiencia.groupby('Equipe', as_index=False)['Eficiência'].mean()

    # Arredonda para 1 casa decimal e ordena da maior para a menor eficiência
    df_eficiencia_equipes['Eficiência'] = df_eficiencia_equipes['Eficiência'].round(1)
    df_eficiencia_equipes = df_eficiencia_equipes.sort_values(by='Eficiência', ascending=False)

    df_eficiencia_equipes_styled = df_eficiencia_equipes.style.apply(colorir_equipe, axis=1).format({
    'Eficiência': '{:.1f}%'
    })

    st.write("#### Eficiência Média por Equipe")
    st.dataframe(df_eficiencia_equipes_styled, hide_index=True)

with tabs[5]:

    def campeonato_por_modelo(df, ultima_corrida):
        logos = {
            'Mitsubishi': 'images/mitsubishi.png',
            'Crevrolet': 'images/chev.png',
            'Toyota': 'images/toyota.png'
        }

        resultado_campeonato = {}

        for modelo in df['Modelo'].dropna().unique():
            df_modelo = df[df['Modelo'] == modelo]
            pontuacao_total_por_modelo = []

            for corrida in range(1, ultima_corrida + 1):
                coluna_corrida = str(corrida)
                if coluna_corrida in df_modelo.columns:
                    df_pontuacao = df_modelo[['Piloto', coluna_corrida]].sort_values(
                        by=coluna_corrida, ascending=False
                    )
                    top_2 = df_pontuacao.head(2)
                    pontuacao_total = top_2[coluna_corrida].apply(
                        pd.to_numeric, errors='coerce'
                    ).sum()
                    pontuacao_total_por_modelo.append(pontuacao_total)
                else:
                    pontuacao_total_por_modelo.append(0)

            resultado_campeonato[modelo] = sum(pontuacao_total_por_modelo)

        # Adiciona +2 pontos Chevrolet por conta do erro do Helinho ser GR na tabela
        if 'Crevolet' in resultado_campeonato:
            resultado_campeonato['Crevolet'] += 2

        df_campeonato = pd.DataFrame(list(resultado_campeonato.items()), columns=[
            'Modelo', 'Pontuação Atual'
        ])
        df_campeonato['Logo'] = df_campeonato['Modelo'].map(logos)

        return df_campeonato

    def exibir_tabela_com_logos(df_campeonato):
        tamanho_padrao = (250, 150)  # Largura x Altura padrão

        cols = st.columns(len(df_campeonato))

        for i, (_, row) in enumerate(df_campeonato.iterrows()):
            with cols[i]:
                imagem = Image.open(row['Logo']).resize(tamanho_padrao)
                st.image(imagem)
                st.markdown(f"### {row['Modelo']}")
                st.write(f"**Pontuação:** {row['Pontuação Atual']} pontos")

    df_campeonato = campeonato_por_modelo(df, ultima_corrida)
    exibir_tabela_com_logos(df_campeonato)

    def evolucao_pontuacao(df, ultima_corrida):
        df_filtrado = df[df['Modelo'].isin(['Mitsubishi', 'Crevrolet', 'Toyota'])]

        evolucao = {'Modelo': []}
        for corrida in range(1, ultima_corrida + 1):
            evolucao[f'Corrida {corrida}'] = []

        for modelo in df_filtrado['Modelo'].unique():
            df_modelo = df_filtrado[df_filtrado['Modelo'] == modelo]
            evolucao['Modelo'].append(modelo)

            for corrida in range(1, ultima_corrida + 1):
                coluna_corrida = str(corrida)

                if coluna_corrida in df_modelo.columns:
                    df_pontuacao = df_modelo[['Piloto', coluna_corrida]].sort_values(
                        by=coluna_corrida, ascending=False
                    )
                    top_2 = df_pontuacao.head(2)
                    pontuacao_total = top_2[coluna_corrida].apply(
                        pd.to_numeric, errors='coerce').sum()
                    evolucao[f'Corrida {corrida}'].append(pontuacao_total)
                else:
                    evolucao[f'Corrida {corrida}'].append(0)

        df_evolucao = pd.DataFrame(evolucao)
        df_evolucao['Soma'] = df_evolucao.iloc[:, 1:].sum(axis=1)
        #Pontos da Pole 2 Etapa
        df_evolucao.loc[df_evolucao['Modelo'] == 'Mitsubishi', 'Soma'] += 4
        df_evolucao = df_evolucao[['Modelo'] + [f'Corrida {i}' for i in range(1, ultima_corrida + 1)] + ['Soma']]

        return df_evolucao

    df_evolucao = evolucao_pontuacao(df, ultima_corrida)

    st.write("### Evolução das Pontuações ao Longo das Corridas")
    st.dataframe(df_evolucao, hide_index=True)

    def calcular_pontuacao_acumulada(df_evolucao):
        df_acumulado = df_evolucao.copy()
        modelos = df_acumulado["Modelo"].unique()

        for modelo in modelos:
            df_modelo = df_acumulado[df_acumulado["Modelo"] == modelo]
            df_modelo.iloc[:, 1:] = df_modelo.iloc[:, 1:].cumsum(axis=1)
            df_acumulado.loc[df_acumulado["Modelo"] == modelo,
                             df_modelo.columns[1:]] = df_modelo.iloc[:, 1:]

        return df_acumulado

    def plotar_evolucao_acumulada(df_evolucao):
        df_acumulado = calcular_pontuacao_acumulada(df_evolucao)
        df_acumulado_sem_soma = df_acumulado.drop(columns=["Soma"])

        df_melted = df_acumulado_sem_soma.melt(
            id_vars=["Modelo"],
            var_name="Corrida",
            value_name="Pontuação Acumulada"
        )

        color_map = {
            "Toyota": "red",
            "Crevrolet": "orange",
            "Mitsubishi": "blue"
        }

        fig = px.line(df_melted,
                      x="Corrida",
                      y="Pontuação Acumulada",
                      color="Modelo",
                      line_group="Modelo",
                      title="Evolução Acumulada das Pontuações ao Longo das Corridas",
                      labels={"Pontuação Acumulada": "Pontuação Acumulada", "Corrida": "Corridas"},
                      markers=True,
                      color_discrete_map=color_map)

        st.plotly_chart(fig, use_container_width=True)

    plotar_evolucao_acumulada(df_evolucao)
    
with tabs[6]:
    def calcular_podios(df, ultima_corrida):
        # Dicionário para armazenar os pódios
        podios = {}

        for corrida in range(1, ultima_corrida + 1):
            nome_coluna = str(corrida)  # Ex: "1", "2", etc.

            # Verifica se a coluna existe no DataFrame
            if nome_coluna not in df.columns:
                continue

            # Converte para numérico (ignora "DSC", "EXC", etc.)
            pontuacoes = pd.to_numeric(df[nome_coluna], errors='coerce')

            # Pega os 3 maiores valores válidos
            top_3 = pontuacoes.nlargest(3).dropna()

            for idx in top_3.index:
                piloto = df.at[idx, 'Piloto']
                podios[piloto] = podios.get(piloto, 0) + 1

        # Cria DataFrame com todos os pilotos (mesmo quem tem 0 pódios)
        df_podios = pd.DataFrame({'Piloto': df['Piloto'].unique()})
        df_podios['Pódios'] = df_podios['Piloto'].map(podios).fillna(0).astype(int)

        # Ranking
        df_podios = df_podios.sort_values(by='Pódios', ascending=False).reset_index(drop=True)
        df_podios['Ranking'] = df_podios['Pódios'].rank(method='min', ascending=False).astype(int)

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

with tabs[7]:
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
            df_qualifying['Piloto'] = df_qualifying['Piloto'].str.title()
            return df_qualifying
        else:
            st.warning('Nenhuma linha de dados encontrada.')
            return None
        

    def carregar_dados_qualifying():
        """Carrega automaticamente os dados de qualifying baseando-se nos arquivos da pasta."""
        dados_qualifying = {}
        pasta_qualifying = 'qualifying2025/'

        # Lista todos os arquivos que seguem o padrão Q*.pdf
        arquivos_pdf = [f for f in os.listdir(pasta_qualifying) if re.match(r'Q\d+\.pdf', f)]

        # Extrai os números das etapas, ordena e percorre
        etapas = sorted([int(re.findall(r'\d+', f)[0]) for f in arquivos_pdf])

        for etapa in etapas:
            pdf_path = os.path.join(pasta_qualifying, f'Q{etapa}.pdf')
            df_qualifying = extrair_dados_pdf(pdf_path)
            if df_qualifying is not None and not df_qualifying.empty:
                dados_qualifying[f'Etapa {etapa}'] = df_qualifying

        return dados_qualifying

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

with tabs[8]:

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

    # Dicionário de exceções — etapas que não devem contar para o cálculo médio
    excecoes = {
        "Cesar Ramos": [8]  # Ignorar etapa 8
    }

    def calcular_estatisticas(dados_qualifying, piloto_selecionado):
        posicoes = []
        etapas_excluidas = excecoes.get(piloto_selecionado, [])

        for etapa, df in dados_qualifying.items():
            # Extrai o número da etapa a partir da string da chave ("Etapa 8" → 8)
            match = re.search(r'\d+', etapa)
            etapa_num = int(match.group()) if match else etapa

            # Ignora a etapa se estiver nas exceções do piloto
            if etapa_num in etapas_excluidas:
                continue

            # Filtra os dados do piloto
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
        "Posição Média de Largada": "{:.1f}"  # Formatar para duas casas decimais
    })
        
    st.markdown("<h2 style='text-align: center;'>Estatísticas dos Pilotos</h2>", unsafe_allow_html=True)
    st.dataframe(styled_df_estatisticas, hide_index=True)

with tabs[9]:
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

    with tabs[10]:
        # Cria um formulário para agrupar os widgets
        with st.form(key='form_recorte'):
            # Opção para selecionar um intervalo de etapas
            intervalo = st.slider("Selecione um intervalo de etapas (caso não queira usar o slider, deixe fixo em 0)", 0, 24, (5, 15))

            # Opção para selecionar etapas específicas
            etapas_opcoes = [str(i) for i in range(1, ultima_corrida + 1)]  # Etapas de "1" a "24"
            etapas_selecionadas = st.multiselect("Selecione etapas específicas", etapas_opcoes)

            # Botão para aplicar o filtro
            submit_button = st.form_submit_button("Aplicar Filtro")

        if submit_button:
            if intervalo[1] > ultima_corrida:
                st.error(
                        f"Você selecionou um intervalo de corridas de {intervalo[0]} até {intervalo[1]}, "
                        f"mas apenas até a corrida {ultima_corrida} já aconteceu. "
                        "Ajuste o intervalo e tente novamente."
                    )
            else:
                # Combina as seleções
                if intervalo[0] == 0 and intervalo[1] == 0:
                    # Se o intervalo for 0, apenas use as etapas selecionadas
                    etapas_final = set(etapas_selecionadas)
                else:
                    # Caso contrário, combine o intervalo com as etapas selecionadas
                    etapas_final = set(etapas_opcoes[intervalo[0]-1:intervalo[1]]) | set(etapas_selecionadas)

                # Filtra o DataFrame
                def filter_dataframe(df, etapas_selecionadas):
                    # Mantém a ordem das colunas
                    colunas_filtradas = ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma'] + \
                                        [etapa for etapa in novas_colunas[5:30] if etapa in etapas_selecionadas] + \
                                        ['Descarte']
                    return df[colunas_filtradas]

                df_recorte = filter_dataframe(df_cortez, etapas_final)
                
                # Calcula a soma das pontuações das etapas filtradas
                df_recorte['Soma'] = df_recorte[[etapa for etapa in etapas_final if etapa in df_cortez.columns]].sum(axis=1)

                # Ordena o DataFrame pela coluna "Soma"
                df_recorte = df_recorte.sort_values(by='Soma', ascending=False).reset_index(drop=True)

                # Recalcula a coluna "Posição"
                df_recorte['Posição'] = range(1, len(df_recorte) + 1)

                # Remove a coluna 'Descarte' antes de aplicar o estilo
                df_recorte_sem_descarte = df_recorte.drop(columns=['Descarte'])

                # Aplica a coloração usando a função colorir_piloto
                styled_df_recorte = df_recorte_sem_descarte.style.apply(colorir_piloto, axis=1)

                # Exibe o DataFrame filtrado
                st.dataframe(styled_df_recorte, hide_index=True)
