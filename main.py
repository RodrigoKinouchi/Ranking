import streamlit as st

# Configurações da página
st.set_page_config(
    page_title="AMM Statistics",  # Título da aba do navegador
    page_icon="📊",  # Ícone da aba (opcional)
    layout="wide"  # Layout da página (opcional)
)

# Adicionando CSS para definir a imagem de fundo
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1547190027-9156686aa2f0?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
    background-size: cover;  /* Ajusta a imagem para cobrir toda a área */
    background-position: center;  /* Centraliza a imagem */
    background-repeat: no-repeat;
    background-attachment: fixed;  /* Mantém a imagem fixa ao rolar */
}

.stApp {
    background-color: rgba(255, 255, 255, 0.9);  /* Fundo do conteúdo com transparência */
    border-radius: 10px;  /* Bordas arredondadas */
    padding: 20px;  /* Espaçamento interno */
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# Título e descrição
st.title("AMM Statistics")
st.subheader("Selecione uma das opções no menu localizado ao lado esquerdo para começar")


# Mensagem de boas-vindas
st.markdown("""
    Este aplicativo traz uma visualização das estatísticas do campeonato 2024 e 2025 da Stock Car Brasil. Navegue nas informações através das abas e insira o numero da última corrida para atualizar os cálculos.
""")

# Adicionando a versão em itálico
st.markdown("_v1.0_")