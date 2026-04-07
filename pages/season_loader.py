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
    # Coluna de pole pode vir como "."/"2" ou "0"/"2" dependendo do parser do PDF.
    return valores.isin([".", "0", "2"]).all()

colunas_fixas = ["Posição", "Numeral", "Piloto", "Equipe", "Modelo"]

if len(df.columns) >= 5:
    df.columns = colunas_fixas + [f"_c{i}" for i in range(1, len(df.columns) - 4)]
else:
    raise ValueError("Layout inesperado no PDF 2026: menos de 5 colunas.")

colunas_pos_modelo = [c for c in df.columns if c not in colunas_fixas]
# Regra solicitada para 2026: as colunas 1 e 4 após "Modelo" são de pole e
# nunca devem aparecer nem entrar em estatísticas.
indices_fixos_pole = {0, 3}
colunas_sem_pole = [
    c for i, c in enumerate(colunas_pos_modelo)
    if i not in indices_fixos_pole
]

# Segurança adicional para mudanças futuras de layout da organização.
colunas_sem_pole = [c for c in colunas_sem_pole if not _eh_coluna_pole(df[c])]

renomeio_corridas = {col: str(i + 1) for i, col in enumerate(colunas_sem_pole)}
df = df[colunas_fixas + colunas_sem_pole].rename(columns=renomeio_corridas)

df = df.drop(index=0)
df["Piloto"] = df["Piloto"].str.title()
df["Equipe"] = df["Equipe"].str.title()

# Blindagem final: remove qualquer coluna de corrida que ainda tenha padrão de pole
# (somente ".", "2", vazio ou NaN), para não exibir nem usar em estatística.
colunas_corrida_renomeadas = [c for c in df.columns if c not in colunas_fixas]
for col in colunas_corrida_renomeadas:
    valores = df[col].astype(str).str.strip().replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}).dropna()
    if not valores.empty and valores.isin([".", "0", "2"]).all():
        df = df.drop(columns=[col])

# Reindexa corridas para manter sequência limpa (1, 2, 3, ...).
colunas_corrida_finais = [c for c in df.columns if c not in colunas_fixas]

# Regra fixa 2026: remover 1a e 4a colunas apos "Modelo"
# (colunas de pontos de pole position, nao sao corridas).
if len(colunas_corrida_finais) >= 4:
    colunas_pole_fixas = [colunas_corrida_finais[0], colunas_corrida_finais[3]]
    df = df.drop(columns=colunas_pole_fixas)
    colunas_corrida_finais = [c for c in df.columns if c not in colunas_fixas]

renomeio_final = {col: str(i + 1) for i, col in enumerate(colunas_corrida_finais)}
df = df.rename(columns=renomeio_final)
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
