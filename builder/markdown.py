import re
from typing import List
from .utils import render_youtube_player

class MarkdownParser:
    """Parses lightweight GitHub Flavored Markdown and media embeds into clean HTML."""

    @classmethod
    def to_html(cls, md_text: str) -> str:
        """Converts markdown text to semantic HTML."""
        lines = md_text.split('\n')
        html_lines: List[str] = []
        in_code_block = False
        in_list = False

        for line in lines:
            stripped = line.strip()

            # Code block toggle
            if stripped.startswith('```'):
                if in_code_block:
                    html_lines.append('</code></pre>')
                    in_code_block = False
                else:
                    lang = stripped[3:].strip()
                    html_lines.append(f'<pre><code class="language-{lang}">' if lang else '<pre><code>')
                    in_code_block = True
                continue

            if in_code_block:
                line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_lines.append(line_escaped)
                continue

            # Close list if line is not a bullet
            if in_list and not stripped.startswith('- ') and not stripped.startswith('* '):
                html_lines.append('</ul>')
                in_list = False

            if not stripped:
                continue

            # Check for YouTube embeds:
            # 1. Format: ![youtube](url) or ![youtube:Caption](url) or ![video](url)
            yt_md_match = re.match(r'^!\[(?:youtube|video)(?::\s*(.*?))?\]\((.*?)\)$', stripped, re.IGNORECASE)
            if yt_md_match:
                caption = (yt_md_match.group(1) or '').strip()
                url = yt_md_match.group(2).strip()
                html_lines.append(render_youtube_player(url, caption))
                continue

            # 2. Format: {% youtube URL_OR_ID [optional caption] %}
            yt_tag_match = re.match(r'^\{%\s*youtube\s+([^\s%]+)(?:\s+(.*?))?\s*%\}$', stripped, re.IGNORECASE)
            if yt_tag_match:
                url_or_id = yt_tag_match.group(1).strip()
                caption = (yt_tag_match.group(2) or '').strip().strip('"\'')
                html_lines.append(render_youtube_player(url_or_id, caption))
                continue

            # 3. Format: Standalone YouTube URL on its own line
            if re.match(r'^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}(?:[^\s]*)?$', stripped):
                html_lines.append(render_youtube_player(stripped))
                continue

            # Horizontal rules
            if stripped in ('---', '***', '___'):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append('<hr>')
                continue

            # Headings
            if stripped.startswith('##### '):
                html_lines.append(f'<h5>{cls.inline_format(stripped[6:])}</h5>')
            elif stripped.startswith('#### '):
                html_lines.append(f'<h4>{cls.inline_format(stripped[5:])}</h4>')
            elif stripped.startswith('### '):
                html_lines.append(f'<h3>{cls.inline_format(stripped[4:])}</h3>')
            elif stripped.startswith('## '):
                html_lines.append(f'<h2>{cls.inline_format(stripped[3:])}</h2>')
            elif stripped.startswith('# '):
                html_lines.append(f'<h1>{cls.inline_format(stripped[2:])}</h1>')
            elif stripped.startswith('> '):
                html_lines.append(f'<blockquote><p>{cls.inline_format(stripped[2:])}</p></blockquote>')
            elif stripped.startswith('- ') or stripped.startswith('* '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{cls.inline_format(stripped[2:])}</li>')
            elif (
                stripped.startswith('<div') or stripped.startswith('</div') or
                stripped.startswith('<iframe') or stripped.startswith('<section') or
                stripped.startswith('</section') or stripped.startswith('<hr')
            ):
                html_lines.append(stripped)
            else:
                html_lines.append(f'<p>{cls.inline_format(stripped)}</p>')

        if in_list:
            html_lines.append('</ul>')
        if in_code_block:
            html_lines.append('</code></pre>')

        return '\n'.join(html_lines)

    @staticmethod
    def inline_format(text: str) -> str:
        """Parses inline formatting (images, bold, italic, code, links)."""
        # Images
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" class="content-img" loading="lazy" />', text)
        # Bold & Italic
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        # Inline code
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        return text
