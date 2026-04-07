from pathlib import Path


TEMPLATE_MARKER = "# === TEMPLATE START ==="


def _customizar_source_2026(source: str) -> str:
    source = source.replace(
        'st.number_input(\n    "Informe o número da última corrida realizada", min_value=1, max_value=24, value=23, step=1)',
        'st.number_input(\n    "Informe o número da última corrida realizada", min_value=1, max_value=24, value=4, step=1)'
    )

    ancora = 'df["Equipe"] = df["Equipe"].str.title()'
    injecao = """

# Ajuste exclusivo 2026:
# remover colunas de pole position (1a e 4a colunas de corrida apos "Modelo").
colunas_numericas_ordenadas = sorted(
    [c for c in df.columns if str(c).isdigit()],
    key=lambda x: int(x)
)
if len(colunas_numericas_ordenadas) >= 4:
    colunas_pole = [colunas_numericas_ordenadas[0], colunas_numericas_ordenadas[3]]
    df = df.drop(columns=colunas_pole, errors="ignore")

# Reindexa colunas de corrida para manter sequencia continua.
colunas_numericas_restantes = sorted(
    [c for c in df.columns if str(c).isdigit()],
    key=lambda x: int(x)
)
renomeio_corridas_2026 = {
    col: str(i + 1) for i, col in enumerate(colunas_numericas_restantes)
}
df = df.rename(columns=renomeio_corridas_2026)
"""

    return source.replace(ancora, ancora + injecao, 1)


def render_temporada(ano: int, template_page: str = "2025.py") -> None:
    """
    Renderiza uma temporada reaproveitando uma página-template.
    Troca apenas as fontes de dados da temporada (tabela e pasta de qualifying).
    """
    pages_dir = Path(__file__).parent
    template_path = pages_dir / template_page

    source = template_path.read_text(encoding="utf-8")
    if TEMPLATE_MARKER in source:
        source = source.split(TEMPLATE_MARKER, maxsplit=1)[1]

    source = (
        source.replace("tabela2025.pdf", f"tabela{ano}.pdf")
        .replace("qualifying2025/", f"qualifying{ano}/")
        .replace("qualifying2025\\", f"qualifying{ano}\\")
    )

    if ano == 2026:
        source = _customizar_source_2026(source)

    exec(compile(source, str(template_path), "exec"), globals())
