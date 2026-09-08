from __future__ import annotations

from dataclasses import dataclass, field


# Cores por equipe (nome CSS); chave em UPPERCASE.
EQUIPES_COR_2026: dict[str, str] = {
    "MERCADO LIVRE RACING TEAM": "yellow",
    "MERCADO LIVRE RACING": "yellow",
    "EUROFARMA RC": "greenyellow",
    "VALDA-CAVALEIRO SPORTS": "limegreen",
    "FULL TIME GAZOO RACING": "crimson",
    "CAR RACING": "orange",
    "TEAM RC": "red",
    "VOGEL MOTORSPORT": "grey",
    "TMG RACING": "darkgreen",
    "RTR SG28 TEAM": "navy",
    "SCUDERIA CHIARELLI": "seashell",
    "RTR SG28": "crimson",
    "BLAU MOTORSPORT": "blue",
    "CROWN RACING": "cyan",
    "STERLING RACING": "white",
    "SCUDERIA BANDEIRAS SPORTS": "silver",
    "SCUDERIA BANDEIRAS": "lightblue",
    "AMATTHEIS": "navy",
}

# Nomes do PDF / title-case → chave do mapa de cores.
EQUIPES_COR_ALIASES_2026: dict[str, str] = {
    "TIME LUBRAX TMG": "TMG RACING",
    "AMATTHEIS/TMG": "AMATTHEIS",
    "AMATTHEIS TMG": "AMATTHEIS",
    "SG28 POWERED RTR": "RTR SG28",
    "SG28 BY RTR": "RTR SG28",
    "SG28 POWERED BY RTR": "RTR SG28",
    "FULL TIME SPORTS": "FULL TIME GAZOO RACING",
    "ML RACING (TC + CR)": "MERCADO LIVRE RACING",
}


def cor_equipe_2026(nome_equipe: str) -> str:
    """Resolve a cor CSS da equipe, tolerando variações de nome do PDF."""
    if not nome_equipe:
        return "lightgray"
    key = " ".join(str(nome_equipe).strip().upper().replace("/", " / ").split())
    key_compact = key.replace(" / ", "/")

    for cand in (key, key_compact):
        if cand in EQUIPES_COR_2026:
            return EQUIPES_COR_2026[cand]
        alias = EQUIPES_COR_ALIASES_2026.get(cand)
        if alias and alias in EQUIPES_COR_2026:
            return EQUIPES_COR_2026[alias]

    # Heurísticas quando o nome não bate exatamente.
    if "MERCADO LIVRE" in key:
        return EQUIPES_COR_2026["MERCADO LIVRE RACING"]
    if "EUROFARMA" in key:
        return EQUIPES_COR_2026["EUROFARMA RC"]
    if "VALDA" in key or "CAVALEIRO" in key:
        return EQUIPES_COR_2026["VALDA-CAVALEIRO SPORTS"]
    if "FULL TIME" in key:
        return EQUIPES_COR_2026["FULL TIME GAZOO RACING"]
    if "CAR RACING" in key:
        return EQUIPES_COR_2026["CAR RACING"]
    if key == "TEAM RC" or key.endswith(" TEAM RC"):
        return EQUIPES_COR_2026["TEAM RC"]
    if "VOGEL" in key:
        return EQUIPES_COR_2026["VOGEL MOTORSPORT"]
    if "AMATTHEIS" in key:
        return EQUIPES_COR_2026["AMATTHEIS"]
    if "LUBRAX" in key or ("TMG" in key and "AMATTHEIS" not in key):
        return EQUIPES_COR_2026["TMG RACING"]
    if "SG28" in key or "RTR" in key:
        return EQUIPES_COR_2026["RTR SG28"]
    if "CHIARELLI" in key:
        return EQUIPES_COR_2026["SCUDERIA CHIARELLI"]
    if "BLAU" in key:
        return EQUIPES_COR_2026["BLAU MOTORSPORT"]
    if "CROWN" in key:
        return EQUIPES_COR_2026["CROWN RACING"]
    if "STERLING" in key:
        return EQUIPES_COR_2026["STERLING RACING"]
    if "BANDEIRAS SPORTS" in key:
        return EQUIPES_COR_2026["SCUDERIA BANDEIRAS SPORTS"]
    if "BANDEIRAS" in key:
        return EQUIPES_COR_2026["SCUDERIA BANDEIRAS"]

    return "lightgray"


@dataclass(frozen=True)
class SeasonConfig:
    year: int
    tabela_pdf: str
    qualifying_dir: str
    modo_colunas_2026: bool = False
    formato_pdf_novo: bool = False
    default_ultima_corrida: int = 23
    ultima_corrida_label: str = "Informe o número da última corrida realizada"
    montadora_pontos_bonus: dict[str, int] = field(default_factory=dict)
    montadora_soma_ajuste: dict[str, int] = field(default_factory=dict)
    qualifying_excecoes: dict[str, list[int]] = field(default_factory=dict)
    n_descartes: int = 5
    endurance_etapas: list[int] = field(default_factory=list)
    proteger_ultimas_concluidas: bool = True
    total_corridas_ano: int | None = None
    # {nome_equipe_virtual: [pilotos]} — soma pontos dos pilotos e entra na aba Equipes.
    equipes_virtuais: dict[str, list[str]] = field(default_factory=dict)
    equipes_cor: dict[str, str] = field(default_factory=dict)


def get_season_config(year: int) -> SeasonConfig:
    configs: dict[int, SeasonConfig] = {
        2025: SeasonConfig(
            year=2025,
            tabela_pdf="tabela2025.pdf",
            qualifying_dir="qualifying2025/",
            default_ultima_corrida=23,
            qualifying_excecoes={"Cesar Ramos": [8]},
            n_descartes=5,
            proteger_ultimas_concluidas=True,
        ),
        2026: SeasonConfig(
            year=2026,
            tabela_pdf="tabela2026.pdf",
            qualifying_dir="qualifying2026/",
            modo_colunas_2026=True,
            default_ultima_corrida=8,
            ultima_corrida_label=(
                "Última corrida disputada (1ª, 2ª, … — não é o nº da coluna do PDF)"
            ),
            montadora_pontos_bonus={"Chevrolet": 2},
            montadora_soma_ajuste={"Mitsubishi": 4},
            n_descartes=2,
            endurance_etapas=[9],
            proteger_ultimas_concluidas=False,
            total_corridas_ano=24,
            equipes_virtuais={
                "ML Racing (TC + CR)": ["Thiago Camilo", "Cesar Ramos"],
            },
            equipes_cor=EQUIPES_COR_2026,
        ),
    }
    if year not in configs:
        raise ValueError(f"Temporada não configurada: {year}")
    return configs[year]
