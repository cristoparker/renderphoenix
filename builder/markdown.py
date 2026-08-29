import re
from typing import List, Tuple, Optional
from .utils import render_youtube_player
from .images import get_webp_url, get_image_dimensions

class MarkdownParser:
    """Parses lightweight GitHub Flavored Markdown, media embeds, and tables into clean HTML."""

    @classmethod
    def to_html(cls, md_text: str) -> str:
        """Converts markdown text to semantic HTML."""
        lines = md_text.split('\n')
        html_lines: List[str] = []
        in_code_block = False
        code_block_lines: List[str] = []
        code_block_lang = ""
        current_list: Optional[str] = None  # 'ul' or 'ol'

        def close_list():
            nonlocal current_list
            if current_list == 'ul':
                html_lines.append('</ul>')
            elif current_list == 'ol':
                html_lines.append('</ol>')
            current_list = None

        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            stripped = line.strip()

            # Code block toggle
            if stripped.startswith('```'):
                close_list()
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
                i += 1
                continue

            if in_code_block:
                code_block_lines.append(line)
                i += 1
                continue

            # Empty lines
            if not stripped:
                i += 1
                continue

            # Check if this line starts a table!
            if '|' in stripped:
                # Look ahead for a delimiter row (ignoring empty lines)
                next_non_empty_idx = i + 1
                while next_non_empty_idx < n and not lines[next_non_empty_idx].strip():
                    next_non_empty_idx += 1
                
                if next_non_empty_idx < n and cls._is_table_delimiter(lines[next_non_empty_idx].strip()):
                    close_list()
                    table_html, next_i = cls._parse_table(lines, i, next_non_empty_idx)
                    html_lines.append(table_html)
                    i = next_i
                    continue

            # Check for YouTube embeds:
            # 1. Format: ![youtube](url) or ![youtube:Caption](url) or ![video](url)
            yt_md_match = re.match(r'^!\[(?:youtube|video)(?::\s*(.*?))?\]\((.*?)\)$', stripped, re.IGNORECASE)
            if yt_md_match:
                close_list()
                caption = (yt_md_match.group(1) or '').strip()
                url = yt_md_match.group(2).strip()
                html_lines.append(render_youtube_player(url, caption))
                i += 1
                continue

            # 2. Format: {% youtube URL_OR_ID [optional caption] %}
            yt_tag_match = re.match(r'^\{%\s*youtube\s+([^\s%]+)(?:\s+(.*?))?\s*%\}$', stripped, re.IGNORECASE)
            if yt_tag_match:
                close_list()
                url_or_id = yt_tag_match.group(1).strip()
                caption = (yt_tag_match.group(2) or '').strip().strip('"\'')
                html_lines.append(render_youtube_player(url_or_id, caption))
                i += 1
                continue

            # 3. Format: Standalone YouTube URL on its own line
            if re.match(r'^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}(?:[^\s]*)?$', stripped):
                close_list()
                html_lines.append(render_youtube_player(stripped))
                i += 1
                continue

            # Horizontal rules
            if stripped in ('---', '***', '___'):
                close_list()
                html_lines.append('<hr>')
                i += 1
                continue

            # Headings
            if stripped.startswith('##### '):
                close_list()
                html_lines.append(f'<h5>{cls.inline_format(stripped[6:])}</h5>')
            elif stripped.startswith('#### '):
                close_list()
                html_lines.append(f'<h4>{cls.inline_format(stripped[5:])}</h4>')
            elif stripped.startswith('### '):
                close_list()
                html_lines.append(f'<h3>{cls.inline_format(stripped[4:])}</h3>')
            elif stripped.startswith('## '):
                close_list()
                html_lines.append(f'<h2>{cls.inline_format(stripped[3:])}</h2>')
            elif stripped.startswith('# '):
                close_list()
                html_lines.append(f'<h1>{cls.inline_format(stripped[2:])}</h1>')
            elif stripped.startswith('> '):
                close_list()
                html_lines.append(f'<blockquote><p>{cls.inline_format(stripped[2:])}</p></blockquote>')
            # Unordered lists
            elif stripped.startswith('- ') or stripped.startswith('* '):
                if current_list != 'ul':
                    close_list()
                    html_lines.append('<ul>')
                    current_list = 'ul'
                item_content = stripped[2:].strip()
                if item_content.startswith('[ ] '):
                    html_lines.append(f'<li class="task-list-item"><input type="checkbox" disabled /> {cls.inline_format(item_content[4:])}</li>')
                elif item_content.startswith('[x] ') or item_content.startswith('[X] '):
                    html_lines.append(f'<li class="task-list-item"><input type="checkbox" checked disabled /> {cls.inline_format(item_content[4:])}</li>')
                else:
                    html_lines.append(f'<li>{cls.inline_format(item_content)}</li>')
            # Ordered lists (e.g. 1. Item)
            elif re.match(r'^\d+\.\s+', stripped):
                if current_list != 'ol':
                    close_list()
                    html_lines.append('<ol>')
                    current_list = 'ol'
                item_content = re.sub(r'^\d+\.\s+', '', stripped).strip()
                html_lines.append(f'<li>{cls.inline_format(item_content)}</li>')
            # HTML tags passthrough
            elif (
                stripped.startswith('<div') or stripped.startswith('</div') or
                stripped.startswith('<iframe') or stripped.startswith('<section') or
                stripped.startswith('</section') or stripped.startswith('<hr') or
                stripped.startswith('<table') or stripped.startswith('</table')
            ):
                close_list()
                html_lines.append(stripped)
            else:
                close_list()
                html_lines.append(f'<p>{cls.inline_format(stripped)}</p>')

            i += 1

        close_list()
        if in_code_block:
            html_lines.append('</code></pre>')

        return '\n'.join(html_lines)

    @classmethod
    def _is_table_delimiter(cls, line: str) -> bool:
        """Checks if a line is a markdown table delimiter row (e.g., '| :--- | :---: | ---: |')."""
        if not line or '|' not in line:
            return False
        cells = cls._split_table_row(line)
        if not cells:
            return False
        for cell in cells:
            if not re.match(r'^\s*:?-{1,}:?\s*$', cell):
                return False
        return True

    @staticmethod
    def _split_table_row(line: str) -> List[str]:
        r"""Splits a markdown table row into trimmed cell contents, respecting escaped pipes \|."""
        stripped = line.strip()
        if stripped.startswith('|'):
            stripped = stripped[1:]
        if stripped.endswith('|'):
            stripped = stripped[:-1]
        
        # Replace escaped pipes \| with placeholder
        placeholder = "\x00PIPE\x00"
        escaped = stripped.replace(r'\|', placeholder)
        raw_cells = escaped.split('|')
        return [c.replace(placeholder, '|').strip() for c in raw_cells]

    @classmethod
    def _parse_table(cls, lines: List[str], header_idx: int, delimiter_idx: int) -> Tuple[str, int]:
        """Parses a full markdown table starting from header_idx and returns (html, next_line_index)."""
        header_cells = cls._split_table_row(lines[header_idx])
        delimiter_cells = cls._split_table_row(lines[delimiter_idx])
        num_cols = max(len(header_cells), len(delimiter_cells))

        # Extract column alignments
        alignments: List[str] = []
        for d in delimiter_cells:
            d_clean = d.strip()
            if d_clean.startswith(':') and d_clean.endswith(':'):
                alignments.append('center')
            elif d_clean.endswith(':'):
                alignments.append('right')
            elif d_clean.startswith(':'):
                alignments.append('left')
            else:
                alignments.append('left')
        
        while len(alignments) < num_cols:
            alignments.append('left')

        while len(header_cells) < num_cols:
            header_cells.append('')

        # Build <thead>
        th_elements = []
        for col_idx, cell in enumerate(header_cells):
            align = alignments[col_idx]
            align_attr = f' style="text-align: {align};"' if align != 'left' else ''
            formatted = cls.inline_format(cell)
            th_elements.append(f'      <th{align_attr}>{formatted}</th>')
        
        thead_html = '  <thead>\n    <tr>\n' + '\n'.join(th_elements) + '\n    </tr>\n  </thead>'

        # Gather table body rows
        curr_idx = delimiter_idx + 1
        rows: List[List[str]] = []
        n = len(lines)

        while curr_idx < n:
            row_line = lines[curr_idx].strip()
            # If blank line, check if next non-empty line continues table
            if not row_line:
                peek = curr_idx + 1
                while peek < n and not lines[peek].strip():
                    peek += 1
                if peek < n and '|' in lines[peek] and not cls._is_table_delimiter(lines[peek].strip()):
                    curr_idx += 1
                    continue
                else:
                    break

            if '|' not in row_line:
                break
            
            if cls._is_table_delimiter(row_line) or row_line.startswith('```') or row_line.startswith('#'):
                break

            cells = cls._split_table_row(row_line)
            while len(cells) < num_cols:
                cells.append('')
            rows.append(cells[:num_cols])
            curr_idx += 1

        # Build <tbody>
        tbody_html = ''
        if rows:
            tr_elements = []
            for row in rows:
                td_elements = []
                for col_idx, cell in enumerate(row):
                    align = alignments[col_idx]
                    align_attr = f' style="text-align: {align};"' if align != 'left' else ''
                    formatted = cls.inline_format(cell)
                    td_elements.append(f'      <td{align_attr}>{formatted}</td>')
                tr_elements.append('    <tr>\n' + '\n'.join(td_elements) + '\n    </tr>')
            tbody_html = '\n  <tbody>\n' + '\n'.join(tr_elements) + '\n  </tbody>'

        table_markup = f"""<div class="table-responsive">
  <table class="content-table">
{thead_html}{tbody_html}
  </table>
</div>"""
        return table_markup, curr_idx

    @classmethod
    def inline_format(cls, text: str) -> str:
        """Parses inline formatting (code, images, links, bold, italic, strikethrough) with token protection."""
        if not text:
            return ""

        # 1. Protect inline code blocks
        code_tokens: List[str] = []
        def _save_code(match: re.Match) -> str:
            code_tokens.append(f'<code>{match.group(1)}</code>')
            return f'\x00CODE_{len(code_tokens) - 1}\x00'
        text = re.sub(r'`([^`]+)`', _save_code, text)

        # 2. Protect images
        img_tokens: List[str] = []
        def _save_img(match: re.Match) -> str:
            alt = match.group(1)
            src = match.group(2)
            webp_src = get_webp_url(src)
            dims = get_image_dimensions(webp_src)
            dim_attrs = f' width="{dims[0]}" height="{dims[1]}"' if dims else ''
            fallback_url = src if webp_src != src else '/assets/images/image-not-found.svg'
            img_tokens.append(f'<img src="{webp_src}" alt="{alt}" class="content-img" loading="lazy" decoding="async"{dim_attrs} onerror="this.onerror=null; this.src=\'{fallback_url}\';" />')
            return f'\x00IMG_{len(img_tokens) - 1}\x00'
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', _save_img, text)

        # 3. Protect links (recursively format label text)
        link_tokens: List[str] = []
        def _save_link(match: re.Match) -> str:
            label = match.group(1)
            href = match.group(2)
            formatted_label = cls.inline_format(label)
            link_tokens.append(f'<a href="{href}">{formatted_label}</a>')
            return f'\x00LINK_{len(link_tokens) - 1}\x00'
        text = re.sub(r'\[(.*?)\]\((.*?)\)', _save_link, text)

        # 4. Strikethrough
        text = re.sub(r'~~(.*?)~~', r'<del>\1</del>', text)

        # 5. Bold & Italic
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'___(.*?)___', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)', r'<em>\1</em>', text)

        # 6. Restore protected tokens
        for i, tok in enumerate(link_tokens):
            text = text.replace(f'\x00LINK_{i}\x00', tok)
        for i, tok in enumerate(img_tokens):
            text = text.replace(f'\x00IMG_{i}\x00', tok)
        for i, tok in enumerate(code_tokens):
            text = text.replace(f'\x00CODE_{i}\x00', tok)

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
