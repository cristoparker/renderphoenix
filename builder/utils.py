import os
import re
import html
import email.utils
import xml.sax.saxutils
import urllib.parse
from datetime import datetime
from typing import Optional, Any
from .config import Config

def xml_escape(val: Any) -> str:
    """Escapes strings for safe inclusion in XML attributes and nodes."""
    if val is None:
        return ''
    return xml.sax.saxutils.escape(str(val), entities={'"': '&quot;', "'": '&apos;'})

def parse_date(date_val: Any) -> Optional[datetime]:
    """Parses frontmatter dates (date objects, ISO strings, or RFC 2822 strings)."""
    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val
    if hasattr(date_val, 'year') and hasattr(date_val, 'month'):
        return datetime(date_val.year, date_val.month, date_val.day)
    date_str = str(date_val).strip()
    try:
        return datetime.strptime(date_str[:10], '%Y-%m-%d')
    except ValueError:
        pass
    try:
        return email.utils.parsedate_to_datetime(date_str).replace(tzinfo=None)
    except (TypeError, ValueError):
        return None

def format_full_date(date_val: Any) -> str:
    """Formats dates consistently as 'DD Mon YYYY' (e.g., '25 Aug 2026')."""
    dt = parse_date(date_val)
    return dt.strftime('%d %b %Y') if dt else (str(date_val) if date_val else '')

def iso_date(date_val: Any) -> str:
    """Formats a date as YYYY-MM-DD for <time datetime>, sitemaps and schema."""
    dt = parse_date(date_val)
    return dt.strftime('%Y-%m-%d') if dt else ''

def html_escape(val: Any) -> str:
    """Escapes text for safe use in HTML content and attributes."""
    return html.escape(str(val or ''), quote=True)

def extract_youtube_id(url_or_id: str) -> str:
    """Extracts the 11-character YouTube video ID from various URL formats or raw ID."""
    if not url_or_id:
        return ''
    url_or_id = str(url_or_id).strip()
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    match = re.search(r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})', url_or_id)
    if match:
        return match.group(1)
    return ''

def render_youtube_player(url_or_id: str, caption: str = "") -> str:
    """Renders a lightweight YouTube facade: a thumbnail button that main.js swaps for a
    privacy-enhanced iframe on click, so the ~500 KB player only loads when wanted."""
    yt_id = extract_youtube_id(url_or_id)
    if not yt_id:
        return ''
    title = html.escape(caption or 'YouTube video', quote=True)
    caption_html = f'<figcaption class="video-caption">{html.escape(caption)}</figcaption>' if caption else ''
    return f"""<figure class="video-figure">
  <div class="video-responsive-wrapper">
    <button type="button" class="yt-facade" data-yt="{yt_id}" aria-label="Play video: {title}">
      <img src="https://i.ytimg.com/vi/{yt_id}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy" decoding="async">
      <span class="yt-play" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4v16l13-8z"/></svg></span>
    </button>
  </div>
  {caption_html}
</figure>"""

def get_youtube_embed_url(url: str) -> str:
    """Converts a standard YouTube URL to a nocookie embed URL, or returns original if not matched."""
    yt_id = extract_youtube_id(url)
    if yt_id:
        return f"https://www.youtube-nocookie.com/embed/{yt_id}"
    return url

def resolve_meta_image(img_candidate: Optional[str]) -> str:
    """
    Resolves an image candidate to a valid raster image path (.png, .jpg, .webp).
    If missing, empty, not found on disk, or SVG, returns /assets/images/og-default.png.
    """
    if img_candidate and not str(img_candidate).lower().endswith('.svg'):
        raw_path = str(img_candidate).strip()
        unquoted = urllib.parse.unquote(raw_path)
        rel_path = unquoted.lstrip('/')
        disk_path = os.path.join(Config.ROOT_DIR, rel_path)
        if os.path.isfile(disk_path):
            parts = [urllib.parse.quote(seg) for seg in rel_path.split('/')]
            return '/' + '/'.join(parts)

    return "/assets/images/og-default.png"
