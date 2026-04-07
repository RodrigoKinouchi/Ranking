from pathlib import Path


TEMPLATE_MARKER = "# === TEMPLATE START ==="


def _customizar_source_2026(source: str) -> str:
    bloco_original = """novo_cabecalho = ["Posição", "Numeral", "Piloto", "Equipe", "Modelo",
                  "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                  "16", "17", "18", "19", "20", "21", "Descarte", "22", "23", "Soma"
                  ]
# Ajusta o cabeçalho ao tamanho real da tabela extraída (evita quebra quando o PDF muda layout).
if len(df.columns) <= len(novo_cabecalho):
    df.columns = novo_cabecalho[:len(df.columns)]
else:
    extras = [f"extra_{i}" for i in range(1, len(df.columns) - len(novo_cabecalho) + 1)]
    df.columns = novo_cabecalho + extras

# Cria uma lista com as colunas do DataFrame, colocando "Soma" na posição desejada
novas_colunas = ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma', "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                 "16", "17", "18", "19", "20", "21", "22", "23", "Descarte"] + \\
    [col for col in df.columns if col not in ['Posição', 'Numeral', 'Piloto', 'Equipe', 'Modelo', 'Soma', "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                                              "16", "17", "18", "19", "20", "21", "22", "23", "Descarte"]]

colunas_existentes_na_ordem = [col for col in novas_colunas if col in df.columns]
df = df[colunas_existentes_na_ordem]
df = df.drop(index=0)
df["Piloto"] = df["Piloto"].str.title()
df["Equipe"] = df["Equipe"].str.title()
"""

    bloco_2026 = """# Tratamento exclusivo 2026:
# a organização adicionou colunas de bônus de pole ('.' para todos e '2' para o pole),
# então removemos essas colunas antes de normalizar as corridas.
def _eh_coluna_pole(serie):
    valores = serie.astype(str).str.strip().replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}).dropna()
    if valores.empty:
        return False
    # Coluna de pole costuma ter somente '.' e eventualmente '2'.
    return valores.isin([".", "2"]).all()

colunas_fixas = ["Posição", "Numeral", "Piloto", "Equipe", "Modelo"]

if len(df.columns) >= 5:
    df.columns = colunas_fixas + [f"_c{i}" for i in range(1, len(df.columns) - 4)]
else:
    raise ValueError("Layout inesperado no PDF 2026: menos de 5 colunas.")

colunas_pos_modelo = [c for c in df.columns if c not in colunas_fixas]
colunas_sem_pole = [c for c in colunas_pos_modelo if not _eh_coluna_pole(df[c])]

renomeio_corridas = {col: str(i + 1) for i, col in enumerate(colunas_sem_pole)}
df = df[colunas_fixas + colunas_sem_pole].rename(columns=renomeio_corridas)

df = df.drop(index=0)
df["Piloto"] = df["Piloto"].str.title()
df["Equipe"] = df["Equipe"].str.title()
"""

    return source.replace(bloco_original, bloco_2026)


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
