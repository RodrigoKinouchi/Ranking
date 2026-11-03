"""Gain/Loss 1ª volta e corrida — parsing de grid, lap chart e resultado (2026)."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

# Etapas usadas no indicador (Endurance = 9 fora).
ETAPAS_GAIN_LOSS_2026 = [1, 2, 3, 4, 5, 6, 7, 8, 10]

PISTA_POR_ETAPA_2026 = {
    1: "Curvelo",
    2: "Cascavel",
    3: "Interlagos",
    4: "Goiânia",
    5: "Cuiabá",
    6: "Velocitta",
    7: "Santa Cruz do Sul",
    8: "Curvelo",
    10: "Cascavel",
}

# Numerais fora da amostragem (convidados / one-off).
NUMERAIS_EXCLUIDOS_GAIN_LOSS = {54, 72}

# Garante nome mesmo se a tabela do campeonato não tiver o numeral.
ALIASES_NUMERAL_PILOTO = {
    33: "Nelson Piquet Jr",
    51: "Atila Abreu",
    111: "Rubens Barrichello",
}

_TEMPO_RE = re.compile(r"^\d{1,2}:\d{2}")
_NUM_RE = re.compile(r"^\d{1,3}$")


def _title_nome_piloto(nome: str) -> str:
    t = " ".join(str(nome).strip().split())
    if not t:
        return t
    return t.title()


@dataclass(frozen=True)
class RaceGainLoss:
    etapa: int
    pista: str
    tipo: str  # "Sprint" | "Principal"
    numeral: int
    piloto: str
    largada: int
    fim_volta1: int | None
    chegada: int | None

    @property
    def gl_volta1(self) -> int | None:
        if self.fim_volta1 is None:
            return None
        return self.largada - self.fim_volta1

    @property
    def gl_corrida(self) -> int | None:
        if self.chegada is None:
            return None
        return self.largada - self.chegada


def _resolve_grid_path(pasta: Path, etapa: int, prova: int) -> Path | None:
    candidates = [
        pasta / f"SP26_{etapa}_P{prova}_GRID.pdf",
        pasta / f"SDP26_{etapa}_P{prova}_GRID.pdf",
        pasta / f"SP25_{etapa}_P{prova}_GRID.pdf",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def _resolve_lap_path(pasta: Path, etapa: int, sprint: bool) -> Path | None:
    suf = "S" if sprint else "M"
    exact = pasta / f"Lap Chart ET{etapa}_{suf}.csv"
    if exact.is_file():
        return exact
    # Principal incompleto (ex.: ET7)
    for p in sorted(pasta.glob(f"Lap Chart ET{etapa}_{suf}*.csv")):
        return p
    return None


def _resolve_resultado_path(pasta: Path, etapa: int, prova: int) -> Path | None:
    p = pasta / f"SP26_{etapa}_P{prova}_RESULTADO.pdf"
    return p if p.is_file() else None


def _parece_nome_piloto(token: str) -> bool:
    t = (token or "").strip()
    if len(t) < 3:
        return False
    if _TEMPO_RE.match(t):
        return False
    letras = sum(ch.isalpha() for ch in t)
    if letras < 3:
        return False
    # Nomes no grid vêm em CAIXA ALTA
    core = t.replace(".", "").replace("-", "")
    return core.isalpha() and core == core.upper()


def extrair_grid_pdf(arquivo: str | Path) -> dict[int, int]:
    """
    Retorna {numeral: posição_de_largada}.

    O PDF visual não extrai tabela limpa; a ordem das linhas
    ``NUMERAL NOME`` no texto (após POLE POSITION) reflete o grid.
    """
    grid, _nomes = _grid_from_texto(Path(arquivo))
    return grid


def extrair_grid_pdf_completo(
    arquivo: str | Path,
) -> tuple[dict[int, int], dict[int, str]]:
    """Retorna (posições, nomes Title Case extraídos do PDF)."""
    return _grid_from_texto(Path(arquivo))


def _grid_from_texto(path: Path) -> tuple[dict[int, int], dict[int, str]]:
    """Extrai grid página a página (o PDF tem 2 páginas; não cortar a 2ª)."""
    grid: dict[int, int] = {}
    nomes: dict[int, str] = {}
    pos = 1
    cut_markers = ("ASSINADO", "Comissário", "Diretor de Prova")

    with pdfplumber.open(path) as pdf:
        for page_i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            cut_at = len(text)
            for m in cut_markers:
                idx = text.find(m)
                if idx != -1:
                    cut_at = min(cut_at, idx)
            body = text[:cut_at]
            if page_i == 0:
                pole_idx = body.upper().find("POLE POSITION")
                if pole_idx != -1:
                    body = body[pole_idx:]

            for line in body.splitlines():
                line = line.strip()
                # Aceita nome truncado no fim da linha ("GUILHERME SALA", "FELIPE B")
                m = re.match(
                    r"^(\d{1,3})\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ .'\-]{1,})$",
                    line,
                )
                if not m:
                    continue
                n = int(m.group(1))
                nome = m.group(2).strip()
                if n >= 2000:
                    continue
                tokens = [t for t in nome.replace(".", " ").split() if t]
                if not tokens:
                    continue
                if not any(_parece_nome_piloto(tok) or (tok.isalpha() and tok == tok.upper() and len(tok) >= 2) for tok in tokens):
                    continue
                if n not in grid:
                    grid[n] = pos
                    pos += 1
                if n not in nomes and len(nome) >= 3:
                    nomes[n] = _title_nome_piloto(nome)
    return grid, nomes


def extrair_lap_chart_csv(arquivo: str | Path) -> dict[int, dict[int, int]]:
    """
    Retorna {volta: {numeral: posição}}.
    """
    path = Path(arquivo)
    out: dict[int, dict[int, int]] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))
    for row in rows:
        if not row:
            continue
        lap_s = str(row[0]).strip().strip('"')
        if not lap_s.isdigit():
            continue
        lap = int(lap_s)
        pos_map: dict[int, int] = {}
        pos = 1
        for cell in row[1:]:
            cell = (cell or "").strip()
            if not cell:
                continue
            if not cell.isdigit() and cell != "0":
                continue
            # numeral 0 é válido (Cacá Bueno)
            numeral = int(cell)
            if numeral not in pos_map:
                pos_map[numeral] = pos
                pos += 1
        if pos_map:
            out[lap] = pos_map
    return out


def extrair_resultado_pdf(arquivo: str | Path) -> dict[int, int]:
    """Retorna {numeral: posição_oficial} da classificação (com punições)."""
    posicoes, _nomes = extrair_resultado_pdf_completo(arquivo)
    return posicoes


def extrair_resultado_pdf_completo(
    arquivo: str | Path,
) -> tuple[dict[int, int], dict[int, str]]:
    """Retorna (posições, nomes) da classificação oficial."""
    path = Path(arquivo)
    order: list[tuple[int, str]] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for row in table:
                    if not row or not row[0]:
                        continue
                    pos_s = str(row[0]).strip()
                    if not pos_s.isdigit():
                        continue
                    if len(row) < 3:
                        continue
                    num_s = str(row[1]).strip()
                    if not (num_s.isdigit() or num_s == "0"):
                        continue
                    driver = str(row[2] or "")
                    if sum(ch.isalpha() for ch in driver) < 3:
                        continue
                    order.append((int(num_s), _title_nome_piloto(driver)))
    seen: set[int] = set()
    out: dict[int, int] = {}
    nomes: dict[int, str] = {}
    pos = 1
    for n, nome in order:
        if n in seen:
            continue
        seen.add(n)
        out[n] = pos
        if nome:
            nomes[n] = nome
        pos += 1
    return out, nomes


def _chegada_de_fontes(
    resultado: dict[int, int] | None,
    laps: dict[int, dict[int, int]],
) -> dict[int, int]:
    """Prefere resultado oficial; senão última volta 'cheia' do lap chart."""
    if resultado:
        return resultado
    if not laps:
        return {}
    # Evita voltas truncadas (ex.: só o líder)
    candidatas = sorted(
        ((lap, m) for lap, m in laps.items() if len(m) >= 8),
        key=lambda t: t[0],
    )
    if not candidatas:
        # fallback absoluto: maior volta mesmo truncada
        lap = max(laps)
        return dict(laps[lap])
    return dict(candidatas[-1][1])


def _resolver_nome_piloto(
    numeral: int,
    mapa: dict[int, str],
    *fontes_nomes: dict[int, str],
) -> str | None:
    if numeral in NUMERAIS_EXCLUIDOS_GAIN_LOSS:
        return None
    if numeral in ALIASES_NUMERAL_PILOTO:
        return ALIASES_NUMERAL_PILOTO[numeral]
    if numeral in mapa and mapa[numeral]:
        return str(mapa[numeral])
    for fonte in fontes_nomes:
        if numeral in fonte and fonte[numeral]:
            return fonte[numeral]
    return None


def carregar_gain_loss_2026(
    pasta: str | Path = "gainlossfirstlap",
    mapa_numeral_piloto: dict[int, str] | None = None,
) -> list[RaceGainLoss]:
    """Carrega todas as corridas das etapas configuradas."""
    pasta_p = Path(pasta)
    mapa = {int(k): str(v) for k, v in (mapa_numeral_piloto or {}).items()}
    registros: list[RaceGainLoss] = []

    for etapa in ETAPAS_GAIN_LOSS_2026:
        pista = PISTA_POR_ETAPA_2026.get(etapa, f"Etapa {etapa}")
        for prova, tipo, sprint in (
            (1, "Sprint", True),
            (2, "Principal", False),
        ):
            grid_path = _resolve_grid_path(pasta_p, etapa, prova)
            lap_path = _resolve_lap_path(pasta_p, etapa, sprint)
            if grid_path is None or lap_path is None:
                continue

            grid, nomes_grid = extrair_grid_pdf_completo(grid_path)
            laps = extrair_lap_chart_csv(lap_path)
            volta1 = laps.get(1, {})
            res_path = _resolve_resultado_path(pasta_p, etapa, prova)
            nomes_res: dict[int, str] = {}
            resultado = None
            if res_path:
                resultado, nomes_res = extrair_resultado_pdf_completo(res_path)
            chegada = _chegada_de_fontes(resultado, laps)

            for numeral, largada in grid.items():
                n = int(numeral)
                piloto = _resolver_nome_piloto(n, mapa, nomes_res, nomes_grid)
                if piloto is None:
                    continue
                registros.append(
                    RaceGainLoss(
                        etapa=etapa,
                        pista=pista,
                        tipo=tipo,
                        numeral=n,
                        piloto=piloto,
                        largada=int(largada),
                        fim_volta1=volta1.get(n),
                        chegada=chegada.get(n),
                    )
                )
    return registros


def dataframe_registros(registros: list[RaceGainLoss]):
    import pandas as pd

    rows = []
    for r in registros:
        rows.append(
            {
                "Etapa": r.etapa,
                "Pista": r.pista,
                "Tipo": r.tipo,
                "Numeral": r.numeral,
                "Piloto": r.piloto,
                "Largada": r.largada,
                "Fim Volta 1": r.fim_volta1,
                "Chegada": r.chegada,
                "G/L Volta 1": r.gl_volta1,
                "G/L Corrida": r.gl_corrida,
            }
        )
    return pd.DataFrame(rows)


def _media(series):
    s = series.dropna()
    if s.empty:
        return None
    return float(s.mean())


def metricas_piloto(df, piloto: str) -> dict:
    """Métricas resumidas para a visão Piloto."""
    import pandas as pd

    p = df[df["Piloto"] == piloto]
    sprint = p[p["Tipo"] == "Sprint"]
    principal = p[p["Tipo"] == "Principal"]
    return {
        "Média largada Sprint": _media(sprint["Largada"]),
        "Média G/L corrida Sprint": _media(sprint["G/L Corrida"]),
        "Média largada Principal": _media(principal["Largada"]),
        "Média G/L corrida Principal": _media(principal["G/L Corrida"]),
        "Média G/L 1ª volta": _media(p["G/L Volta 1"]),
    }


def tabela_piloto_por_etapa(df, piloto: str):
    """Uma linha por etapa com G/L da 1ª volta (Sprint e Principal)."""
    import pandas as pd

    p = df[df["Piloto"] == piloto].copy()
    rows = []
    for etapa, g in p.groupby("Etapa"):
        pista = g["Pista"].iloc[0]
        s = g[g["Tipo"] == "Sprint"]
        m = g[g["Tipo"] == "Principal"]
        rows.append(
            {
                "Etapa": int(etapa),
                "Pista": pista,
                "Largada Sprint": int(s["Largada"].iloc[0]) if not s.empty else None,
                "Fim V1 Sprint": int(s["Fim Volta 1"].iloc[0])
                if not s.empty and pd.notna(s["Fim Volta 1"].iloc[0])
                else None,
                "G/L V1 Sprint": int(s["G/L Volta 1"].iloc[0])
                if not s.empty and pd.notna(s["G/L Volta 1"].iloc[0])
                else None,
                "Largada Principal": int(m["Largada"].iloc[0]) if not m.empty else None,
                "Fim V1 Principal": int(m["Fim Volta 1"].iloc[0])
                if not m.empty and pd.notna(m["Fim Volta 1"].iloc[0])
                else None,
                "G/L V1 Principal": int(m["G/L Volta 1"].iloc[0])
                if not m.empty and pd.notna(m["G/L Volta 1"].iloc[0])
                else None,
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values("Etapa")
    return out


def ranking_medio_gl_corrida(df, tipo: str):
    """Ranking geral: média G/L de corrida (Sprint ou Principal)."""
    import pandas as pd

    sub = df[df["Tipo"] == tipo]
    g = (
        sub.groupby("Piloto", as_index=False)
        .agg(
            **{
                "Média G/L Corrida": ("G/L Corrida", "mean"),
                "Corridas": ("G/L Corrida", "count"),
                "Média Largada": ("Largada", "mean"),
            }
        )
    )
    g = g.dropna(subset=["Média G/L Corrida"])
    g["Média G/L Corrida"] = g["Média G/L Corrida"].round(1)
    g["Média Largada"] = g["Média Largada"].round(1)
    return g.sort_values("Média G/L Corrida", ascending=False).reset_index(drop=True)


def ranking_medio_gl_volta1(df):
    """Ranking geral: média G/L da 1ª volta (todas as corridas)."""
    import pandas as pd

    g = (
        df.groupby("Piloto", as_index=False)
        .agg(
            **{
                "Média G/L 1ª Volta": ("G/L Volta 1", "mean"),
                "Amostras": ("G/L Volta 1", "count"),
            }
        )
    )
    g = g.dropna(subset=["Média G/L 1ª Volta"])
    g["Média G/L 1ª Volta"] = g["Média G/L 1ª Volta"].round(1)
    return g.sort_values("Média G/L 1ª Volta", ascending=False).reset_index(drop=True)


def ranking_pista_gl_corrida(df, tipo: str):
    """Uma linha por pista: média G/L de corrida naquele traçado."""
    import pandas as pd

    sub = df[df["Tipo"] == tipo]
    g = (
        sub.groupby("Pista", as_index=False)
        .agg(
            **{
                "Média G/L Corrida": ("G/L Corrida", "mean"),
                "Amostras": ("G/L Corrida", "count"),
                "Etapas": ("Etapa", "nunique"),
            }
        )
    )
    g = g.dropna(subset=["Média G/L Corrida"])
    g["Média G/L Corrida"] = g["Média G/L Corrida"].round(1)
    return g.sort_values("Média G/L Corrida", ascending=False).reset_index(drop=True)


def ranking_pista_gl_volta1(df):
    """Uma linha por pista: média G/L da 1ª volta (Sprint + Principal)."""
    import pandas as pd

    g = (
        df.groupby("Pista", as_index=False)
        .agg(
            **{
                "Média G/L 1ª Volta": ("G/L Volta 1", "mean"),
                "Amostras": ("G/L Volta 1", "count"),
                "Etapas": ("Etapa", "nunique"),
            }
        )
    )
    g = g.dropna(subset=["Média G/L 1ª Volta"])
    g["Média G/L 1ª Volta"] = g["Média G/L 1ª Volta"].round(1)
    return g.sort_values("Média G/L 1ª Volta", ascending=False).reset_index(drop=True)
