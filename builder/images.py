"""
RenderPhoenix Image Pipeline Utilities
Handles image path resolution (WebP/SVG/PNG), intrinsic dimensions caching, and optimization hooks.
"""

import os
import urllib.parse
from typing import Optional, Tuple
from PIL import Image

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
            try:
                with Image.open(cand) as img:
                    w, h = img.size
                    _DIMENSION_CACHE[clean_path] = (w, h)
                    return (w, h)
            except Exception:
                pass
                
    return None
