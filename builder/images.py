"""
RenderPhoenix Image Pipeline Utilities
Handles image path resolution (WebP/SVG/PNG), intrinsic dimensions caching, and optimization hooks.
Dependency-free: Uses only Python standard library.
"""

import os
import struct
import urllib.parse
from typing import Optional, Tuple

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
        local_path = webp_candidate.lstrip('/')
        if os.path.exists(local_path) or os.path.exists(os.path.join('assets', local_path)):
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
    candidates = [
        clean_path,
        os.path.join(os.getcwd(), clean_path),
        os.path.join(os.getcwd(), 'assets', clean_path)
    ]
    
    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            dims = _parse_image_dimensions_raw(cand)
            if dims:
                _DIMENSION_CACHE[clean_path] = dims
                return dims
                
    return None
