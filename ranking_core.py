from __future__ import annotations

import os

import pandas as pd

DEFAULT_PILOTO_IMG = os.path.join("images", "Pilotodesc.png")

PILOTO_IMAGE_ALIASES: dict[str, str] = {
    "Helio Castroneves": "Helio Castroneves",
    "Hélio Castroneves": "Helio Castroneves",
}


def strip_cell_header(header) -> str:
    if header is None:
        return ""
    return str(header).strip()


def normalizar_pdf_stockcar_2026(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Layout típico do PDF Stock Car (pilotos): após Modelo repete-se pole («.») +
    corrida + corrida, e à direita (opcional) Descarte e Soma.
    """
    df = df_raw.copy()
    meta = ["Posição", "Numeral", "Piloto", "Equipe", "Modelo"]
    raw_cols = list(df.columns)
    n = len(raw_cols)
    if n <= 5:
        return df

    final = [None] * n
    for i in range(5):
        final[i] = meta[i]

    j = n - 1
    trailers = []
    while j >= 5:
        h_raw = strip_cell_header(raw_cols[j])
        h = h_raw.lower()
        if not h_raw:
            if j == n - 1:
                trailers.append((j, "Soma"))
                j -= 1
                continue
            break
        if "descarte" in h:
            trailers.append((j, "Descarte"))
            j -= 1
            continue
        if "soma" in h or h == "total":
            trailers.append((j, "Soma"))
            j -= 1
            continue
        break

    core_idxs = list(range(5, j + 1))
    pole_i = 1
    race_i = 1
    for offset, idx_col in enumerate(core_idxs):
        if offset % 3 == 0:
            final[idx_col] = f"pole_{pole_i}"
            pole_i += 1
        else:
            final[idx_col] = str(race_i)
            race_i += 1

    for idx_col, label in sorted(trailers, key=lambda t: t[0]):
        final[idx_col] = label

    for i in range(n):
        if final[i] is None:
            final[i] = f"extra_{i}"

    df.columns = final
    return df


def _coluna_tem_resultado(serie: pd.Series) -> bool:
    for valor in serie:
        if pd.isna(valor):
            continue
        texto = str(valor).strip().upper()
        if texto in {"", ".", "NP"}:
            continue
        return True
    return False


def detectar_ultima_corrida(df: pd.DataFrame, fallback: int = 1) -> int:
    """Infere a última corrida com dado no PDF (colunas numéricas 1, 2, 3…)."""
    corridas = sorted((int(c) for c in df.columns if str(c).isdigit()), reverse=True)
    for n in corridas:
        col = str(n)
        if col in df.columns and _coluna_tem_resultado(df[col]):
            return n
    return fallback


def caminho_imagem_piloto(nome_piloto: str) -> str:
    nome = PILOTO_IMAGE_ALIASES.get(nome_piloto, nome_piloto)
    path = os.path.join("images", f"{nome}.png")
    return path if os.path.isfile(path) else DEFAULT_PILOTO_IMG


def extrair_qualifying_pdf(arquivo_pdf: str) -> pd.DataFrame | None:
    """Extrai qualifying: tenta tabela estruturada; fallback para texto."""
    import pdfplumber

    dados: list[tuple[str, str, str]] = []
    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            pagina = pdf.pages[0]
            tabelas = pagina.extract_tables()
            if tabelas and tabelas[0]:
                for linha in tabelas[0]:
                    if not linha or not linha[0]:
                        continue
                    pos = str(linha[0]).strip()
                    if not pos.isdigit():
                        continue
                    no = str(linha[1]).strip() if len(linha) > 1 else ""
                    piloto = " ".join(
                        str(c).strip() for c in linha[2:] if c and str(c).strip()
                    )
                    if piloto:
                        dados.append((pos, no, piloto.title()))
                if dados:
                    return pd.DataFrame(dados, columns=["Posição", "Numeral", "Piloto"])

            texto = pagina.extract_text() or ""
            for linha in texto.split("\n"):
                colunas = linha.split()
                if colunas and colunas[0].isdigit() and len(colunas) >= 3:
                    pos, no = colunas[0], colunas[1]
                    name = " ".join(colunas[2:min(len(colunas), 5)])
                    dados.append((pos, no, name.title()))
    except OSError:
        return None

    if not dados:
        return None
    return pd.DataFrame(dados, columns=["Posição", "Numeral", "Piloto"])
