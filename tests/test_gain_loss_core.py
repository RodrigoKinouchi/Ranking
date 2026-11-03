from pathlib import Path

from gain_loss_core import (
    ETAPAS_GAIN_LOSS_2026,
    _resolve_grid_path,
    _resolve_lap_path,
    carregar_gain_loss_2026,
    dataframe_registros,
    extrair_grid_pdf,
    extrair_lap_chart_csv,
    ranking_medio_gl_volta1,
)


PASTA = Path("gainlossfirstlap")


def test_etapas_excluem_endurance():
    assert 9 not in ETAPAS_GAIN_LOSS_2026


def test_grid_pole_bate_com_lap1_na_maioria():
    if not PASTA.is_dir():
        return
    ok = 0
    total = 0
    for etapa in ETAPAS_GAIN_LOSS_2026:
        for prova, sprint in ((1, True), (2, False)):
            gp = _resolve_grid_path(PASTA, etapa, prova)
            lp = _resolve_lap_path(PASTA, etapa, sprint)
            if not gp or not lp:
                continue
            total += 1
            pole = next(
                (n for n, p in extrair_grid_pdf(gp).items() if p == 1), None
            )
            leader = next(
                (n for n, p in extrair_lap_chart_csv(lp).get(1, {}).items() if p == 1),
                None,
            )
            if pole == leader:
                ok += 1
    # ET6 Principal: pole #38, líder V1 #121 (real) — permite 1 divergência
    assert total >= 16
    assert ok >= total - 1


def test_carregar_gera_gl_volta1():
    if not PASTA.is_dir():
        return
    regs = carregar_gain_loss_2026(PASTA, mapa_numeral_piloto={30: "Cesar Ramos"})
    assert regs
    df = dataframe_registros(regs)
    assert "G/L Volta 1" in df.columns
    assert df["Etapa"].isin(ETAPAS_GAIN_LOSS_2026).all()
    assert not (df["Etapa"] == 9).any()
    ranking = ranking_medio_gl_volta1(df)
    assert not ranking.empty
