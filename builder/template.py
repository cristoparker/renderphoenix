import os
import re
from typing import Dict, Any, Optional
from .config import Config

_INCLUDE_RE = re.compile(r'\{%\s*include\s+([\w.\-]+)\s*%\}')
_VAR_RE = re.compile(r'\{\{\s*([\w.]+)\s*\}\}')


class TemplateEngine:
    """Minimal template engine: `{% include file.html %}` and `{{ dotted.name }}` substitution.

    Logic lives in Python (components.py) — templates only place pre-rendered values.
    Substitution is single-pass, so inserted content (e.g. code blocks containing
    `{{ }}`) is never re-interpreted.
    """

    def __init__(self, layouts_dir: Optional[str] = None, includes_dir: Optional[str] = None):
        self.layouts_dir = layouts_dir or Config.LAYOUTS_DIR
        self.includes_dir = includes_dir or Config.INCLUDES_DIR
        self._cache: Dict[str, str] = {}

    @staticmethod
    def strip_frontmatter(content: str) -> str:
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].lstrip('\n')
        return content

    def get_layout(self, name: str) -> str:
        """Returns a layout's source with frontmatter removed and includes resolved."""
        if name not in self._cache:
            path = os.path.join(self.layouts_dir, f'{name}.html')
            if not os.path.exists(path):
                raise FileNotFoundError(f'Layout not found: {path}')
            with open(path, 'r', encoding='utf-8') as f:
                self._cache[name] = self.render_includes(self.strip_frontmatter(f.read()))
        return self._cache[name]

    def render_includes(self, html: str, depth: int = 0) -> str:
        """Recursively resolves `{% include name.html %}` tags."""
        if depth > 10:
            raise RecursionError('Include nesting too deep')

        def replace(match: re.Match) -> str:
            path = os.path.join(self.includes_dir, match.group(1))
            if not os.path.exists(path):
                raise FileNotFoundError(f'Include not found: {path}')
            with open(path, 'r', encoding='utf-8') as f:
                return self.render_includes(f.read(), depth + 1)

        return _INCLUDE_RE.sub(replace, html)

    @staticmethod
    def lookup(context: Dict[str, Any], dotted: str) -> Any:
        value: Any = context
        for key in dotted.split('.'):
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = getattr(value, key, None)
            if value is None:
                return ''
        return value

    @classmethod
    def render(cls, template: str, context: Dict[str, Any]) -> str:
        """Replaces every `{{ name }}` with its context value (missing → empty string)."""
        return _VAR_RE.sub(lambda m: str(cls.lookup(context, m.group(1))), template)

    def render_page(self, layout: str, content: str, context: Dict[str, Any]) -> str:
        """Renders `content` inside `layout`, then inside the `default` shell."""
        if layout and layout != 'default':
            content = self.render(self.get_layout(layout), {**context, 'content': content})
        return self.render(self.get_layout('default'), {**context, 'content': content})
