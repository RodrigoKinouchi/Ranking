from pathlib import Path


TEMPLATE_MARKER = "# === TEMPLATE START ==="


def render_temporada(ano: int, template_page: str = "2025.py") -> None:
    """
    Renderiza uma temporada reaproveitando uma página-template.
    Troca apenas as fontes de dados da temporada (tabela e pasta de qualifying).
    """
    pages_dir = Path(__file__).parent
    template_path = pages_dir / template_page

    source = template_path.read_text(encoding="utf-8")
    if TEMPLATE_MARKER in source:
        source = source.split(TEMPLATE_MARKER, maxsplit=1)[1]

    source = (
        source.replace("tabela2025.pdf", f"tabela{ano}.pdf")
        .replace("qualifying2025/", f"qualifying{ano}/")
        .replace("qualifying2025\\", f"qualifying{ano}\\")
    )

    exec(compile(source, str(template_path), "exec"), globals())
