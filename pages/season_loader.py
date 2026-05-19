from pages.ranking_page import render_season_page
from season_config import get_season_config


def render_temporada(ano: int) -> None:
    """Renderiza uma temporada usando configuração centralizada (sem exec)."""
    render_season_page(get_season_config(ano))
