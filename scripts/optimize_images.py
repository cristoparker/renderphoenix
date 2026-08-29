#!/usr/bin/env python3
"""
RenderPhoenix Image Optimization Engine
Batch converts raster images (PNG, JPG, JPEG) to ultra-fast WebP format (quality 82, method 6)
and losslessly/optimally compresses existing raster images as fallbacks.
"""

import os
import sys
import glob
import io
from PIL import Image

def optimize_image(src_path: str, quality: int = 82, method: int = 6) -> dict:
    """
    Optimizes a single image:
    1. Generates a .webp sibling file with optimal compression.
    2. Optimizes the original PNG/JPG file in-place if compressible.
    """
    stats = {
        'src': src_path,
        'orig_size': os.path.getsize(src_path),
        'webp_path': None,
        'webp_size': None,
        'opt_orig_size': None,
    }

    base, ext = os.path.splitext(src_path)
    ext_lower = ext.lower()

    if ext_lower not in ['.png', '.jpg', '.jpeg']:
        return stats

    webp_path = f"{base}.webp"
    stats['webp_path'] = webp_path

    try:
        with Image.open(src_path) as img:
            orig_mode = img.mode
            # 1. Generate WebP
            out_webp = io.BytesIO()
            if orig_mode in ('RGBA', 'LA'):
                # Check if alpha is actually used
                extrema = img.getextrema()
                if extrema and len(extrema) >= 4 and extrema[3][0] == 255:
                    # All opaque -> convert to RGB for smaller webp
                    img_rgb = img.convert('RGB')
                    img_rgb.save(out_webp, format='WEBP', quality=quality, method=method)
                else:
                    img.save(out_webp, format='WEBP', quality=quality, method=method)
            elif orig_mode == 'P':
                # Palette image
                if 'transparency' in img.info:
                    img_rgba = img.convert('RGBA')
                    img_rgba.save(out_webp, format='WEBP', quality=quality, method=method)
                else:
                    img_rgb = img.convert('RGB')
                    img_rgb.save(out_webp, format='WEBP', quality=quality, method=method)
            else:
                img_rgb = img.convert('RGB') if orig_mode != 'RGB' else img
                img_rgb.save(out_webp, format='WEBP', quality=quality, method=method)

            webp_bytes = out_webp.getvalue()
            with open(webp_path, 'wb') as f:
                f.write(webp_bytes)
            stats['webp_size'] = len(webp_bytes)

            # 2. In-place optimize original PNG / JPG
            out_opt = io.BytesIO()
            if ext_lower == '.png':
                img.save(out_opt, format='PNG', optimize=True, compress_level=9)
            elif ext_lower in ('.jpg', '.jpeg'):
                img_rgb = img.convert('RGB') if orig_mode != 'RGB' else img
                img_rgb.save(out_opt, format='JPEG', quality=85, optimize=True, progressive=True)

            opt_bytes = out_opt.getvalue()
            if len(opt_bytes) < stats['orig_size']:
                with open(src_path, 'wb') as f:
                    f.write(opt_bytes)
                stats['opt_orig_size'] = len(opt_bytes)
            else:
                stats['opt_orig_size'] = stats['orig_size']

    except Exception as e:
        print(f"Error optimizing {src_path}: {e}", file=sys.stderr)

    return stats

def run_batch_optimization(directory: str = 'assets/images'):
    """Finds all PNG, JPG, JPEG images and optimizes them."""
    pattern = os.path.join(directory, '**', '*')
    all_files = glob.glob(pattern, recursive=True)
    images = [f for f in all_files if os.path.isfile(f) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    print(f"==================================================")
    print(f" RenderPhoenix Image Optimization Engine")
    print(f" Found {len(images)} raster images to optimize in {directory}")
    print(f"==================================================")

    total_orig = 0
    total_webp = 0
    total_opt_orig = 0

    for idx, path in enumerate(images, 1):
        stats = optimize_image(path)
        orig_sz = stats['orig_size']
        webp_sz = stats['webp_size'] or orig_sz
        opt_sz = stats['opt_orig_size'] or orig_sz

        total_orig += orig_sz
        total_webp += webp_sz
        total_opt_orig += opt_sz

        savings_pct = (1.0 - (webp_sz / orig_sz)) * 100 if orig_sz > 0 else 0
        rel_path = os.path.relpath(path, directory)
        print(f"[{idx:02d}/{len(images):02d}] {rel_path[:45]:<45} | {orig_sz/1024:6.1f} KB -> WebP: {webp_sz/1024:5.1f} KB (-{savings_pct:4.1f}%)")

    print(f"==================================================")
    print(f" SUMMARY:")
    print(f" Original Payload:   {total_orig / (1024*1024):6.2f} MB")
    print(f" Optimized Fallback: {total_opt_orig / (1024*1024):6.2f} MB (-{(1 - total_opt_orig/total_orig)*100:.1f}%)")
    print(f" Modern WebP Total:  {total_webp / (1024*1024):6.2f} MB (-{(1 - total_webp/total_orig)*100:.1f}%)")
    print(f" Total Network Savings: {(total_orig - total_webp) / (1024*1024):.2f} MB saved!")
    print(f"==================================================")

if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else 'assets/images'
    run_batch_optimization(target_dir)
