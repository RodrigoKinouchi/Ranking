from __future__ import annotations

from dataclasses import dataclass, field


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


def get_season_config(year: int) -> SeasonConfig:
    configs: dict[int, SeasonConfig] = {
        2025: SeasonConfig(
            year=2025,
            tabela_pdf="tabela2025.pdf",
            qualifying_dir="qualifying2025/",
            default_ultima_corrida=23,
            qualifying_excecoes={"Cesar Ramos": [8]},
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
        ),
    }
    if year not in configs:
        raise ValueError(f"Temporada não configurada: {year}")
    return configs[year]
