import re
import html
from typing import List, Tuple, Dict
from .utils import render_youtube_player
from .images import get_webp_url, get_image_dimensions

_BLOCK_HTML = re.compile(r'^</?(div|section|article|aside|figure|figcaption|table|thead|tbody|tr|td|th|iframe|details|'
                         r'summary|p|hr|br|img|video|picture|nav|ul|ol|li|blockquote|h[1-6])\b|^<!--', re.I)
_HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')
_ORDERED = re.compile(r'^(\d+)[.)]\s+')
_BULLET = re.compile(r'^[-*+]\s+')
_IMAGE_LINE = re.compile(r'^!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+"([^"]*)")?\s*\)$')
_YT_MD = re.compile(r'^!\[(?:youtube|video)(?::\s*(.*?))?\]\((.*?)\)$', re.I)
_YT_TAG = re.compile(r'^\{%\s*youtube\s+([^\s%]+)(?:\s+(.*?))?\s*%\}$', re.I)
_YT_URL = re.compile(r'^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}\S*$')

# Languages that get syntax colouring; anything else (text, yaml, ...) is shown as plain escaped text.
_CODE_LANGS = {'c', 'cpp', 'c++', 'cs', 'csharp', 'c#', 'java', 'js', 'javascript', 'ts', 'typescript', 'json',
               'py', 'python', 'glsl', 'hlsl', 'shader', 'gdscript', 'lua', 'go', 'rust', 'php', 'sh', 'bash'}
_HASH_COMMENT_LANGS = {'py', 'python', 'sh', 'bash', 'gdscript'}
_KEYWORDS = ('public|private|protected|internal|static|class|struct|interface|enum|void|int|float|double|string|bool|'
             'var|let|const|function|def|return|if|elif|else|for|foreach|in|while|new|using|import|from|export|'
             'async|await|override|virtual|null|None|true|false|True|False|this|self|uniform|out|vec2|vec3|vec4')


def _escape(text: str) -> str:
    return html.escape(text, quote=True)


def slugify(text: str) -> str:
    """Heading text -> URL fragment id."""
    text = html.unescape(re.sub(r'<[^>]+>', '', text)).lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-') or 'section'


class MarkdownParser:
    """Converts the GitHub-flavoured Markdown subset used on this site into semantic HTML:
    paragraphs, headings with anchor ids, lists and task lists, blockquotes, fenced code,
    tables, captioned figures, YouTube embeds and raw HTML blocks."""

    @classmethod
    def to_html(cls, md_text: str) -> str:
        lines = md_text.replace('\r\n', '\n').split('\n')
        out: List[str] = []
        para: List[str] = []
        used_ids: Dict[str, int] = {}
        i, n = 0, len(lines)

        def flush_para() -> None:
            if para:
                text = '\n'.join(para)
                text = re.sub(r'(?: {2,}|\\)\n', '<br>\n', text.rstrip())  # Markdown hard line breaks
                text = re.sub(r'[ \t]+\n', '\n', text)
                out.append(f'<p>{cls.inline_format(text)}</p>')
                para.clear()

        while i < n:
            line = lines[i]
            stripped = line.strip()

            # Fenced code block — an unclosed fence runs to the end of the document
            if stripped.startswith('```') or stripped.startswith('~~~'):
                flush_para()
                fence, lang = stripped[:3], stripped[3:].strip().lower()
                body: List[str] = []
                i += 1
                while i < n and not lines[i].strip().startswith(fence):
                    body.append(lines[i])
                    i += 1
                out.append(cls.code_block('\n'.join(body), lang))
                i += 1
                continue

            if not stripped:
                flush_para()
                i += 1
                continue

            # Tables
            if '|' in stripped:
                nxt = i + 1
                while nxt < n and not lines[nxt].strip():
                    nxt += 1
                if nxt < n and cls._is_table_delimiter(lines[nxt].strip()):
                    flush_para()
                    table_html, i = cls._parse_table(lines, i, nxt)
                    out.append(table_html)
                    continue

            # YouTube: ![youtube:Caption](url), {% youtube ID caption %}, or a bare URL line
            m = _YT_MD.match(stripped)
            if m:
                flush_para()
                out.append(render_youtube_player(m.group(2).strip(), (m.group(1) or '').strip()))
                i += 1
                continue
            m = _YT_TAG.match(stripped)
            if m:
                flush_para()
                out.append(render_youtube_player(m.group(1).strip(), (m.group(2) or '').strip().strip('"\'')))
                i += 1
                continue
            if _YT_URL.match(stripped):
                flush_para()
                out.append(render_youtube_player(stripped))
                i += 1
                continue

            # Image on its own line -> captioned <figure> (title, else alt text, is the caption)
            m = _IMAGE_LINE.match(stripped)
            if m:
                flush_para()
                alt, src, title = m.group(1), m.group(2), m.group(3)
                caption = title or alt
                cap_html = f'<figcaption>{cls.inline_format(caption)}</figcaption>' if caption else ''
                out.append(f'<figure>{cls.image_tag(src, alt)}{cap_html}</figure>')
                i += 1
                continue

            # Horizontal rule
            if re.fullmatch(r'(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,}', stripped):
                flush_para()
                out.append('<hr>')
                i += 1
                continue

            # Headings with unique anchor ids
            m = _HEADING.match(stripped)
            if m:
                flush_para()
                level = len(m.group(1))
                content = cls.inline_format(m.group(2))
                hid = slugify(content)
                used_ids[hid] = used_ids.get(hid, 0) + 1
                if used_ids[hid] > 1:
                    hid = f'{hid}-{used_ids[hid]}'
                out.append(f'<h{level} id="{hid}">{content}</h{level}>')
                i += 1
                continue

            # Blockquote: consecutive ">" lines, parsed recursively
            if stripped.startswith('>'):
                flush_para()
                quote: List[str] = []
                while i < n and lines[i].strip().startswith('>'):
                    quote.append(re.sub(r'^\s*>\s?', '', lines[i]))
                    i += 1
                out.append(f'<blockquote>{cls.to_html(chr(10).join(quote))}</blockquote>')
                continue

            # Lists; indented lines continue the previous item
            if _BULLET.match(stripped) or _ORDERED.match(stripped):
                flush_para()
                ordered = bool(_ORDERED.match(stripped))
                marker = _ORDERED if ordered else _BULLET
                start = int(_ORDERED.match(stripped).group(1)) if ordered else 1
                items: List[str] = []
                while i < n:
                    cur = lines[i].strip()
                    if marker.match(cur):
                        items.append(marker.sub('', cur, count=1))
                    elif cur and items and lines[i][:1] in (' ', '\t'):
                        items[-1] += ' ' + cur
                    else:
                        break
                    i += 1
                lis = []
                for item in items:
                    task = re.match(r'^\[([ xX])\]\s+', item)
                    if task:
                        checked = ' checked' if task.group(1).lower() == 'x' else ''
                        lis.append(f'<li class="task-list-item"><input type="checkbox" disabled{checked}> '
                                   f'{cls.inline_format(item[task.end():])}</li>')
                    else:
                        lis.append(f'<li>{cls.inline_format(item)}</li>')
                tag = 'ol' if ordered else 'ul'
                start_attr = f' start="{start}"' if ordered and start != 1 else ''
                out.append(f'<{tag}{start_attr}>' + ''.join(lis) + f'</{tag}>')
                continue

            # Raw HTML block lines pass through untouched
            if _BLOCK_HTML.match(stripped):
                flush_para()
                out.append(stripped)
                i += 1
                continue

            para.append(line.lstrip())  # keep trailing spaces: two of them mean a hard break
            i += 1

        flush_para()
        return '\n'.join(out)

    # ------------------------------------------------------------------ blocks
    @staticmethod
    def image_tag(src: str, alt: str) -> str:
        webp_src = get_webp_url(src)
        dims = get_image_dimensions(webp_src)
        dim_attrs = f' width="{dims[0]}" height="{dims[1]}"' if dims else ''
        return (f'<img src="{_escape(webp_src)}" alt="{_escape(alt)}" class="content-img"{dim_attrs} '
                f'loading="lazy" decoding="async">')

    @classmethod
    def code_block(cls, code: str, lang: str) -> str:
        body = cls.highlight_code(code, lang) if lang in _CODE_LANGS else _escape(code)
        lang_class = f' class="language-{_escape(lang)}"' if lang else ''
        return (f'<div class="code-block-wrapper"><div class="code-block-header">'
                f'<span class="code-lang-label">{_escape(lang or "code")}</span>'
                f'<button type="button" class="code-copy-btn" aria-label="Copy code to clipboard">'
                f'<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
                f'<rect x="9" y="9" width="13" height="13" rx="2"></rect>'
                f'<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
                f'<span>Copy</span></button></div><pre><code{lang_class}>{body}</code></pre></div>')

    # ------------------------------------------------------------------ tables
    @classmethod
    def _is_table_delimiter(cls, line: str) -> bool:
        """True for a delimiter row such as '| :--- | :---: | ---: |'."""
        if not line or '|' not in line:
            return False
        cells = cls._split_table_row(line)
        return bool(cells) and all(re.match(r'^\s*:?-+:?\s*$', c) for c in cells)

    @staticmethod
    def _split_table_row(line: str) -> List[str]:
        r"""Splits a table row into trimmed cells, respecting escaped pipes \|."""
        stripped = line.strip()
        if stripped.startswith('|'):
            stripped = stripped[1:]
        if stripped.endswith('|'):
            stripped = stripped[:-1]
        placeholder = '\x00PIPE\x00'
        return [c.replace(placeholder, '|').strip() for c in stripped.replace(r'\|', placeholder).split('|')]

    @classmethod
    def _parse_table(cls, lines: List[str], header_idx: int, delimiter_idx: int) -> Tuple[str, int]:
        """Parses a table starting at header_idx; returns (html, next_line_index)."""
        header = cls._split_table_row(lines[header_idx])
        delims = cls._split_table_row(lines[delimiter_idx])
        cols = max(len(header), len(delims))
        aligns = []
        for d in delims:
            d = d.strip()
            aligns.append('center' if d.startswith(':') and d.endswith(':') else 'right' if d.endswith(':') else 'left')
        aligns += ['left'] * (cols - len(aligns))
        header += [''] * (cols - len(header))

        def cell(tag: str, text: str, col: int) -> str:
            style = f' style="text-align:{aligns[col]}"' if aligns[col] != 'left' else ''
            return f'<{tag}{style}>{cls.inline_format(text)}</{tag}>'

        rows: List[List[str]] = []
        idx, n = delimiter_idx + 1, len(lines)
        while idx < n:
            row = lines[idx].strip()
            if not row or '|' not in row or cls._is_table_delimiter(row) or row.startswith(('```', '#')):
                break
            cells = cls._split_table_row(row)
            rows.append((cells + [''] * cols)[:cols])
            idx += 1

        thead = '<thead><tr>' + ''.join(cell('th', h, c) for c, h in enumerate(header)) + '</tr></thead>'
        tbody = ''.join('<tr>' + ''.join(cell('td', v, c) for c, v in enumerate(r)) + '</tr>' for r in rows)
        return (f'<div class="table-responsive"><table class="content-table">{thead}'
                f'{"<tbody>" + tbody + "</tbody>" if tbody else ""}</table></div>'), idx

    # ------------------------------------------------------------------ inline
    @classmethod
    def inline_format(cls, text: str) -> str:
        """Inline Markdown: code, images, links, bare URLs, bold/italic, strikethrough.
        Inline HTML written in the source is kept as-is."""
        if not text:
            return ''
        tokens: List[str] = []

        def protect(fragment: str) -> str:
            tokens.append(fragment)
            return f'\x00{len(tokens) - 1}\x00'

        text = re.sub(r'`([^`]+)`', lambda m: protect(f'<code>{_escape(m.group(1))}</code>'), text)
        text = re.sub(r'!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+"[^"]*")?\s*\)',
                      lambda m: protect(cls.image_tag(m.group(2), m.group(1))), text)

        def link(m: re.Match) -> str:
            href = m.group(2)
            ext = ' target="_blank" rel="noopener noreferrer"' if href.startswith(('http://', 'https://')) else ''
            return protect(f'<a href="{_escape(href)}"{ext}>{cls.inline_format(m.group(1))}</a>')
        text = re.sub(r'\[([^\]]+)\]\(\s*([^)\s]+)(?:\s+"[^"]*")?\s*\)', link, text)
        text = re.sub(r'(?<!["=\w])https?://[^\s<]*[^\s<.,;:!?)\]]', lambda m: protect(
            f'<a href="{_escape(m.group(0))}" target="_blank" rel="noopener noreferrer">{_escape(m.group(0))}</a>'), text)

        text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'(?<!\w)__(.+?)__(?!\w)', r'<strong>\1</strong>', text)
        text = re.sub(r'(?<![*\w])\*(?![\s*])(.+?)(?<![\s*])\*(?![*\w])', r'<em>\1</em>', text)
        text = re.sub(r'(?<!\w)_(?![\s_])(.+?)(?<![\s_])_(?!\w)', r'<em>\1</em>', text)

        # Restore protected fragments (links may contain other tokens, so repeat until stable)
        for _ in range(5):
            if '\x00' not in text:
                break
            text = re.sub(r'\x00(\d+)\x00', lambda m: tokens[int(m.group(1))], text)
        return text

    @classmethod
    def highlight_code(cls, code: str, lang: str = '') -> str:
        """Single-pass tokenizer: each fragment is escaped once and wrapped once, so highlighting
        can never re-match inside its own <span> markup."""
        line_comment = r'#[^\n]*|//[^\n]*' if lang in _HASH_COMMENT_LANGS else r'(?<!:)//[^\n]*'
        pattern = re.compile(
            rf'(?P<comment>/\*[\s\S]*?\*/|{line_comment})'
            r'|(?P<string>"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\')'
            rf'|(?P<keyword>\b(?:{_KEYWORDS})\b)'
            r'|(?P<number>\b\d+(?:\.\d+)?f?\b)'
            r'|(?P<type>\b[A-Z][A-Za-z0-9_]+\b)'
        )
        out, pos = [], 0
        for m in pattern.finditer(code):
            out.append(_escape(code[pos:m.start()]))
            out.append(f'<span class="token-{m.lastgroup}">{_escape(m.group(0))}</span>')
            pos = m.end()
        out.append(_escape(code[pos:]))
        return ''.join(out)
