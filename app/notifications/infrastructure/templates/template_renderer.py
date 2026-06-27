# notifications/infrastructure/template_renderer.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateRenderer:

    def __init__(self, templates_dir: str | Path) -> None:
        self._env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html"]),
        )

    def render(self, template_name: str, **context) -> str:
        template = self._env.get_template(template_name)
        return template.render(**context)


template_renderer = TemplateRenderer(
    templates_dir=Path(__file__).parent / "templates"
)