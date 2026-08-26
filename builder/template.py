import os
import re
from typing import Dict, Any, Optional
from .config import Config
from .utils import resolve_meta_image
from .seo import SEOGenerator

class TemplateEngine:
    """Handles layout wrapping, partial includes, and Liquid tag evaluation."""

    def __init__(self, layouts_dir: Optional[str] = None, includes_dir: Optional[str] = None):
        self.layouts_dir = layouts_dir or Config.LAYOUTS_DIR
        self.includes_dir = includes_dir or Config.INCLUDES_DIR
        self._layouts_cache: Dict[str, str] = {}

    def get_layout(self, layout_name: str) -> str:
        """Retrieves and caches layout template with includes resolved."""
        if layout_name not in self._layouts_cache:
            layout_path = os.path.join(self.layouts_dir, f"{layout_name}.html")
            if os.path.exists(layout_path):
                with open(layout_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Split off frontmatter if present
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        content = parts[2]
                self._layouts_cache[layout_name] = self.render_includes(content)
            else:
                self._layouts_cache[layout_name] = "{{ content }}"
        return self._layouts_cache[layout_name]

    def render_includes(self, html_str: str) -> str:
        """Recursively resolves {% include <filename.html> %} tags."""
        def replace_include(match):
            inc_file = match.group(1).strip()
            inc_path = os.path.join(self.includes_dir, inc_file)
            if os.path.exists(inc_path):
                with open(inc_path, 'r', encoding='utf-8') as f:
                    return self.render_includes(f.read())
            return ''
        return re.sub(r'\{%\s*include\s+([\w\.\-]+)\s*%\}', replace_include, html_str)

    def clean_liquid_tags(self, text: str, meta: Optional[Dict[str, Any]] = None, page_type: str = "website", slug: str = "") -> str:
        """Resolves template variables, SEO tags, navigation links, and removes remaining Liquid tags."""
        if meta is None:
            meta = {}

        header_nav_html = """
      <li class="nav-item"><a href="/" class="nav-link">Home</a></li>
      <li class="nav-item"><a href="/about/" class="nav-link">About</a></li>
      <li class="nav-item"><a href="/services/" class="nav-link">Services</a></li>
      <li class="nav-item"><a href="/work/" class="nav-link">Work</a></li>
      <li class="nav-item"><a href="/blog/" class="nav-link">Blog</a></li>
      <li class="nav-item"><a href="/contact/" class="nav-link">Contact</a></li>
    """
        text = re.sub(r'\{%\s*for\s+item\s+in\s+site\.data\.navigation\.header\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', header_nav_html, text)

        footer_nav_html = """
      <li><a href="/">Home</a></li>
      <li><a href="/about/">About</a></li>
      <li><a href="/services/">Services</a></li>
      <li><a href="/work/">Work Portfolio</a></li>
      <li><a href="/blog/">Blog</a></li>
      <li><a href="/contact/">Contact Us</a></li>
    """
        text = re.sub(r'\{%\s*for\s+link\s+in\s+site\.data\.navigation\.footer\.navigation\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', footer_nav_html, text)

        footer_res_html = """
      <li><a href="/privacy-policy/">Privacy Policy</a></li>
      <li><a href="/dmca/">DMCA Policy</a></li>
      <li><a href="https://mcpedl.com/user/renderphoenix/" target="_blank" rel="noopener noreferrer">MCPEDL Official Profile</a></li>
      <li><a href="/llms.txt">llms.txt (AI Metadata)</a></li>
      <li><a href="/llms-full.txt">llms-full.txt (Full AI Corpus)</a></li>
      <li><a href="/sitemap.xml">Sitemap XML</a></li>
    """
        text = re.sub(r'\{%\s*for\s+link\s+in\s+site\.data\.navigation\.footer\.resources\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', footer_res_html, text)

        seo_meta_html = SEOGenerator.generate_meta_tags(meta, page_type=page_type, slug=slug)
        text = text.replace('{{ seo_meta_tags }}', seo_meta_html)

        full_title = meta.get('title', f"{Config.SITE_NAME} — {Config.SITE_TAGLINE}")
        text = text.replace('{{ full_title }}', full_title)
        text = text.replace('{{ page_desc }}', meta.get('description', Config.DEFAULT_DESCRIPTION))
        text = text.replace('{{ canonical_url }}', f"{Config.SITE_URL}/{slug}/" if slug else f"{Config.SITE_URL}/")
        text = text.replace('{{ og_image }}', resolve_meta_image(meta.get('cover_image') or meta.get('image') or meta.get('header_image')))
        text = text.replace('{{ site.title }}', Config.SITE_NAME)
        text = text.replace('{{ site.description }}', Config.DEFAULT_DESCRIPTION)
        text = text.replace('{{ site.url }}', Config.SITE_URL)

        markdown_url = meta.get('markdown_url', '')
        if markdown_url:
            text = text.replace('{{ markdown_alternate_link }}', f'<link rel="alternate" type="text/markdown" href="{markdown_url}" title="{full_title} Markdown">')
        else:
            text = text.replace('{{ markdown_alternate_link }}', '')

        text = re.sub(r"\{\{\s*'([^']+)'\s*\|\s*relative_url\s*\}\}", r"\1", text)
        text = re.sub(r'\{\{\s*"([^"]+)"\s*\|\s*relative_url\s*\}\}', r"\1", text)

        # Remove leftover liquid tags and variables
        text = re.sub(r'\{%[\s\S]*?%\}', '', text)
        text = re.sub(r'\{\{[\s\S]*?\}\}', '', text)

        return text
