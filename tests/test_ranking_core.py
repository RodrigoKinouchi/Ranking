import pandas as pd

from ranking_core import (
    colunas_protegidas_descarte,
    corridas_logicas_da_etapa,
    detectar_ultima_corrida,
    normalizar_pdf_stockcar_2026,
)


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


def test_etapa_9_sao_corridas_17_e_18():
    assert corridas_logicas_da_etapa(9) == (17, 18)


def test_descarte_2026_protege_endurance_quando_ja_correu():
    cols = colunas_protegidas_descarte(
        endurance_etapas=[9],
        proteger_ultimas_concluidas=False,
        ultima_corrida=18,
        total_corridas_ano=24,
        coluna_fn=str,
    )
    assert "17" in cols
    assert "18" in cols
    assert "16" not in cols
    assert "23" not in cols


def test_descarte_2026_ainda_sem_endurance():
    cols = colunas_protegidas_descarte(
        endurance_etapas=[9],
        proteger_ultimas_concluidas=False,
        ultima_corrida=14,
        total_corridas_ano=24,
        coluna_fn=str,
    )
    assert cols == set()
