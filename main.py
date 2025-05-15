import streamlit as st
import base64

# Função para converter a imagem em base64
def get_base64_from_file(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Caminho para o logo e imagem de fundo
logo_base64 = get_base64_from_file("images/capa.png")
bg_base64 = get_base64_from_file("images/background.png")

# Configurações da página
st.set_page_config(
    page_title="AMM Statistics",
    page_icon="📊",
    layout="wide"
)

# CSS com fundo e logo embutidos
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{bg_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

.stApp {{
    background-color: rgba(255, 255, 255, 0.92);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
}}

#logo-container {{
    position: absolute;
    top: 10px;
    right: 20px;
    margin-bottom: 0;
    z-index: 9999;
}}

#logo {{
    width: 500px;
}}
</style>

<div id="logo-container">
    <img id="logo" src="data:image/png;base64,{logo_base64}" />
</div>
"""

# Aplica o CSS e exibe o logo
st.markdown(page_bg_img, unsafe_allow_html=True)

# Conteúdo do app
st.title("AMM Statistics")
st.subheader("Selecione uma das opções no menu localizado ao lado esquerdo para começar")

st.markdown("""
Este aplicativo traz uma visualização das estatísticas do campeonato 2024 e 2025 da Stock Car Brasil. 
Navegue nas informações através das abas e insira o número da última corrida para atualizar os cálculos.
""")

st.markdown("_v1.0_")