import os
import re
import xml.sax.saxutils
import urllib.parse
from datetime import datetime
from typing import Optional, Any, Dict
from .config import Config

def xml_escape(val: Any) -> str:
    """Escapes strings for safe inclusion in XML attributes and nodes."""
    if val is None:
        return ''
    return xml.sax.saxutils.escape(str(val), entities={'"': '&quot;', "'": '&apos;'})

def format_full_date(date_val: Any) -> str:
    """Formats dates consistently as 'DD Mon YYYY' (e.g., '25 Aug 2026')."""
    if not date_val:
        return ''
    if isinstance(date_val, datetime):
        return date_val.strftime('%d %b %Y')
    if hasattr(date_val, 'strftime'):
        return date_val.strftime('%d %b %Y')
    date_str = str(date_val).strip()
    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S %z']:
        try:
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            return dt.strftime('%d %b %Y')
        except Exception:
            pass
    return date_str

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
    """Renders a responsive 16:9 privacy-enhanced YouTube iframe player inside a <figure>."""
    yt_id = extract_youtube_id(url_or_id)
    if not yt_id:
        return ''
    embed_url = f"https://www.youtube-nocookie.com/embed/{yt_id}"
    caption_html = f'<figcaption class="video-caption">{caption}</figcaption>' if caption else ''
    title_attr = caption if caption else 'YouTube video player'
    return f"""<figure class="video-figure">
  <div class="video-responsive-wrapper">
    <iframe src="{embed_url}" title="{title_attr}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>
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

def clean_conditional(text: str, condition_name: str, is_truthy: bool, replace_dict: Optional[Dict[str, Any]] = None) -> str:
    """Processes simple {% if condition_name %}...{% endif %} template blocks."""
    pattern = re.compile(rf'\{{%\s*if\s+{re.escape(condition_name)}\s*%\}}([\s\S]*?)\{{%\s*endif\s*%\}}')
    if is_truthy:
        def keep_content(m):
            content = m.group(1)
            if replace_dict:
                for k, v in replace_dict.items():
                    content = content.replace(k, str(v))
            return content
        return pattern.sub(keep_content, text)
    else:
        return pattern.sub('', text)
