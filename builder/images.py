"""
RenderPhoenix Image Pipeline Utilities
Handles image path resolution (WebP/SVG/PNG), intrinsic dimensions caching, and optimization hooks.
Dependency-free: Uses only Python standard library.
"""

import os
import struct
import hashlib
import urllib.parse
from typing import Optional, Tuple
from .config import Config

try:
    from PIL import Image  # Optional: enables build-time thumbnails
except ImportError:  # pragma: no cover
    Image = None

_DIMENSION_CACHE = {}

def get_webp_url(img_url: str) -> str:
    """
    Given an image URL or relative path (e.g., '/assets/images/projects/.../thumb.png'),
    returns the WebP version if it exists in the codebase or falls back to original.
    Ensures URLs are safely percent-encoded.
    """
    if not img_url:
        return img_url
    
    # Strip query params or hash if any
    parts = img_url.split('?', 1)
    base_url = parts[0]
    query_str = f"?{parts[1]}" if len(parts) > 1 else ""
    
    unquoted_base = urllib.parse.unquote(base_url)
    base_name, ext = os.path.splitext(unquoted_base)
    
    if ext.lower() in ['.png', '.jpg', '.jpeg']:
        webp_candidate = f"{base_name}.webp"
        if os.path.exists(os.path.join(Config.ROOT_DIR, webp_candidate.lstrip('/'))):
            encoded_path = urllib.parse.quote(webp_candidate, safe='/:?#&=%')
            return f"{encoded_path}{query_str}"
            
    encoded_base = urllib.parse.quote(unquoted_base, safe='/:?#&=%')
    return f"{encoded_base}{query_str}"

def _parse_image_dimensions_raw(fpath: str) -> Optional[Tuple[int, int]]:
    """
    Parses image dimensions from file headers using standard library struct.
    Supports PNG, WebP, GIF, and JPEG with zero external dependencies.
    """
    try:
        with open(fpath, 'rb') as f:
            data = f.read(512)
            if len(data) < 24:
                return None
                
            # 1. PNG
            if data.startswith(b'\x89PNG\r\n\x1a\n'):
                w, h = struct.unpack('>II', data[16:24])
                return (w, h)
                
            # 2. GIF
            if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
                w, h = struct.unpack('<HH', data[6:10])
                return (w, h)
                
            # 3. WebP
            if data.startswith(b'RIFF') and data[8:12] == b'WEBP':
                vp8 = data[12:16]
                if vp8 == b'VP8X':
                    w = 1 + int.from_bytes(data[24:27], 'little')
                    h = 1 + int.from_bytes(data[27:30], 'little')
                    return (w, h)
                elif vp8 == b'VP8 ':
                    w, h = struct.unpack('<HH', data[26:30])
                    return (w & 0x3FFF, h & 0x3FFF)
                elif vp8 == b'VP8L':
                    b1, b2, b3, b4 = data[21:25]
                    w = 1 + (((b2 & 0x3F) << 8) | b1)
                    h = 1 + (((b4 & 0x0F) << 10) | (b3 << 2) | ((b2 & 0xC0) >> 6))
                    return (w, h)
                    
            # 4. JPEG
            if data.startswith(b'\xff\xd8'):
                f.seek(2)
                while True:
                    marker_bytes = f.read(2)
                    if len(marker_bytes) < 2 or marker_bytes[0] != 0xFF:
                        break
                    marker = marker_bytes[1]
                    if marker in [0xD9, 0xDA]: # EOI or SOS
                        break
                    length_bytes = f.read(2)
                    if len(length_bytes) < 2:
                        break
                    length = struct.unpack('>H', length_bytes)[0]
                    if marker in [0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF]:
                        sof_data = f.read(5)
                        if len(sof_data) == 5:
                            h, w = struct.unpack('>HH', sof_data[1:5])
                            return (w, h)
                        break
                    else:
                        f.seek(length - 2, 1)
    except Exception:
        return None
    return None

def get_image_dimensions(img_path: str) -> Optional[Tuple[int, int]]:
    """
    Retrieves intrinsic (width, height) of an image with caching to avoid repeated I/O.
    """
    if not img_path:
        return None
        
    clean_path = urllib.parse.unquote(img_path.split('?')[0].split('#')[0]).lstrip('/')
    
    if clean_path in _DIMENSION_CACHE:
        return _DIMENSION_CACHE[clean_path]
        
    # Attempt resolving file location
    candidates = [os.path.join(Config.ROOT_DIR, clean_path)]
    
    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            dims = _parse_image_dimensions_raw(cand)
            if dims:
                _DIMENSION_CACHE[clean_path] = dims
                return dims
                
    return None


def get_thumbnail_url(img_url: str, width: int = Config.THUMB_WIDTH, ratio: Optional[float] = None) -> str:
    """
    Returns a URL to a WebP copy of `img_url` resized to `width` px (or the source width if
    smaller), generated into _site/assets/thumbs/. The original aspect ratio is kept unless a
    `ratio` is given, in which case the image is centre-cropped to it.
    Falls back to the full-size URL when Pillow is missing or the source is not a raster image.
    """
    full_url = get_webp_url(img_url)
    if not img_url or Image is None:
        return full_url

    src_rel = urllib.parse.unquote(full_url.split('?')[0]).lstrip('/')
    src_path = os.path.join(Config.ROOT_DIR, src_rel)
    if not os.path.isfile(src_path) or not src_rel.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        return full_url

    dims = get_image_dimensions(full_url)
    if not dims:
        return full_url
    out_w = min(width, dims[0])
    out_h = round(out_w / ratio) if ratio else round(dims[1] * out_w / dims[0])

    digest = hashlib.sha1(f'{src_rel}:{os.path.getmtime(src_path)}:{out_w}:{ratio or "orig"}'.encode()).hexdigest()[:12]
    out_name = f'{digest}-{out_w}.webp'
    out_path = os.path.join(Config.SITE_DIR, 'assets', 'thumbs', out_name)
    if not os.path.exists(out_path):
        try:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with Image.open(src_path) as im:
                im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
                src_ratio = im.width / im.height
                if not ratio:
                    pass
                elif src_ratio > ratio:   # too wide: trim the sides
                    crop_w = round(im.height * ratio)
                    left = (im.width - crop_w) // 2
                    im = im.crop((left, 0, left + crop_w, im.height))
                elif src_ratio < ratio:  # too tall: trim top and bottom
                    crop_h = round(im.width / ratio)
                    top = (im.height - crop_h) // 2
                    im = im.crop((0, top, im.width, top + crop_h))
                im.resize((out_w, out_h), Image.LANCZOS).save(out_path, 'WEBP', quality=78, method=6)
        except Exception as exc:
            print(f"  Warning: thumbnail failed for {src_rel}: {exc}")
            return full_url
    _DIMENSION_CACHE[f'assets/thumbs/{out_name}'] = (out_w, out_h)
    return f'/assets/thumbs/{out_name}'
