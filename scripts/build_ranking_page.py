from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "pages" / "2025.py").read_text(encoding="utf-8")
marker = "# === TEMPLATE START ==="
body = src.split(marker, 1)[1].lstrip("\n")

header = '''"""Renderização da página de classificação por temporada."""
from __future__ import annotations

import logging
import os
import re

import matplotlib.pyplot as plt
import pandas as pd
import pdfplumber
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
from PIL import Image

from ranking_core import (
    caminho_imagem_piloto,
    detectar_ultima_corrida,
    normalizar_pdf_stockcar_2026,
    strip_cell_header,
)
from season_config import SeasonConfig

logger = logging.getLogger(__name__)


def render_season_page(config: SeasonConfig) -> None:
'''

indented = "".join(
    ("    " + line if line.strip() else line) for line in body.splitlines(keepends=True)
)
(ROOT / "pages" / "ranking_page.py").write_text(header + indented, encoding="utf-8")
print(f"Wrote {len((header + indented).splitlines())} lines")
