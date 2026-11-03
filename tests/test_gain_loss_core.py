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
    ranking_pista_gl_volta1,
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


def test_exclui_numerais_e_usa_nomes():
    if not PASTA.is_dir():
        return
    regs = carregar_gain_loss_2026(PASTA, mapa_numeral_piloto={})
    df = dataframe_registros(regs)
    assert not df["Numeral"].isin([54, 72]).any()
    assert not df["Piloto"].astype(str).str.startswith("#").any()
    # Aliases pedidos
    por_num = df.drop_duplicates("Numeral").set_index("Numeral")["Piloto"]
    if 111 in por_num.index:
        assert por_num.loc[111] == "Rubens Barrichello"
    if 33 in por_num.index:
        assert por_num.loc[33] == "Nelson Piquet Jr"
    if 51 in por_num.index:
        assert por_num.loc[51] == "Atila Abreu"


def test_dnf_nao_entra_gl_corrida():
    """NC conhecidos (ex.: Cesar #30 na Principal Cuiabá) sem G/L de corrida."""
    if not PASTA.is_dir():
        return
    regs = carregar_gain_loss_2026(PASTA, mapa_numeral_piloto={30: "Cesar Ramos"})
    df = dataframe_registros(regs)
    row = df[(df["Etapa"] == 5) & (df["Tipo"] == "Principal") & (df["Numeral"] == 30)]
    assert not row.empty
    assert row["G/L Corrida"].isna().all()


def test_pista_usa_apenas_gl_positivo():
    if not PASTA.is_dir():
        return
    df = dataframe_registros(carregar_gain_loss_2026(PASTA, {}))
    ranking = ranking_pista_gl_volta1(df)
    assert "Média posições ganhas" in ranking.columns
    assert "Total posições ganhas" in ranking.columns
    assert (ranking["Média posições ganhas"] >= 0).all()
    assert (ranking["Total posições ganhas"] >= 0).all()
