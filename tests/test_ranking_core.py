import pandas as pd

from ranking_core import detectar_ultima_corrida, normalizar_pdf_stockcar_2026


def test_detectar_ultima_corrida():
    df = pd.DataFrame({
        "1": [80, 0, "."],
        "2": [55, 0, "."],
        "3": [pd.NA, pd.NA, "."],
    })
    assert detectar_ultima_corrida(df, fallback=1) == 2


def test_normalizar_pdf_colunas_corridas():
    raw = pd.DataFrame([[1, 2, 3, 4, 5, ".", 80, 55, "", 200]])
    raw.columns = list(range(10))
    out = normalizar_pdf_stockcar_2026(raw)
    assert "pole_1" in out.columns
    assert "1" in out.columns
