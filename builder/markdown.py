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
        code_block_lines: List[str] = []
        code_block_lang = ""

        for line in lines:
            stripped = line.strip()

            # Code block toggle
            if stripped.startswith('```'):
                if in_code_block:
                    code_raw = '\n'.join(code_block_lines)
                    highlighted = cls.highlight_code(code_raw, code_block_lang)
                    display_lang = code_block_lang or 'code'
                    html_lines.append(f"""<div class="code-block-wrapper">
  <div class="code-block-header">
    <span class="code-lang-label">{display_lang}</span>
    <button type="button" class="code-copy-btn" aria-label="Copy code to clipboard">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
      <span>Copy</span>
    </button>
  </div>
  <pre><code class="language-{code_block_lang}">{highlighted}</code></pre>
</div>""")
                    in_code_block = False
                    code_block_lines = []
                    code_block_lang = ""
                else:
                    code_block_lang = stripped[3:].strip()
                    in_code_block = True
                    code_block_lines = []
                continue

            if in_code_block:
                code_block_lines.append(line)
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

    @classmethod
    def highlight_code(cls, code_text: str, lang: str = "") -> str:
        """Lightweight token syntax highlighter for C#, Python, JS, C++, GLSL, etc."""
        escaped = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        result_lines = []
        for line in escaped.split('\n'):
            comment_match = re.search(r'(//|#)(.*)$', line)
            if comment_match:
                code_part = line[:comment_match.start()]
                comment_part = line[comment_match.start():]
                code_highlighted = cls._highlight_line(code_part, lang)
                result_lines.append(f'{code_highlighted}<span class="token-comment">{comment_part}</span>')
            else:
                result_lines.append(cls._highlight_line(line, lang))
        return '\n'.join(result_lines)

    @staticmethod
    def _highlight_line(line: str, lang: str) -> str:
        # Strings
        line = re.sub(r'(".*?"|\'.*?\')', r'<span class="token-string">\1</span>', line)
        # Keywords
        keywords = r'\b(public|private|protected|internal|static|class|struct|interface|enum|void|int|float|double|string|bool|var|let|const|function|def|return|if|else|for|foreach|while|new|using|import|from|async|await|override|virtual|null|true|false)\b'
        line = re.sub(keywords, r'<span class="token-keyword">\1</span>', line)
        # Numbers
        line = re.sub(r'\b(\d+(\.\d+)?f?)\b', r'<span class="token-number">\1</span>', line)
        # Built-in Types & Classes
        types = r'\b([A-Z][a-zA-Z0-9_]+)\b'
        line = re.sub(types, r'<span class="token-type">\1</span>', line)
        return line
