import os
from typing import List, Dict, Any

class Config:
    """Core configuration for the RenderPhoenix website generator."""
    SITE_URL: str = "https://renderphoenix.com"
    SITE_NAME: str = "RenderPhoenix"
    SITE_TAGLINE: str = "Independent Interactive Creative Studio"
    DEFAULT_DESCRIPTION: str = (
        "RenderPhoenix is an independent interactive creative studio building games, "
        "3D worlds, game assets, and digital experiences."
    )
    THEME_COLOR: str = "#FAF8F5"

    # Base directory paths
    ROOT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SITE_DIR: str = os.path.join(ROOT_DIR, '_site')
    INCLUDES_DIR: str = os.path.join(ROOT_DIR, '_includes')
    LAYOUTS_DIR: str = os.path.join(ROOT_DIR, '_layouts')
    PROJECTS_DIR: str = os.path.join(ROOT_DIR, '_projects')
    POSTS_DIR: str = os.path.join(ROOT_DIR, '_posts')
    DATA_DIR: str = os.path.join(ROOT_DIR, '_data')
    ASSETS_DIR: str = os.path.join(ROOT_DIR, 'assets')

    # Static pages registry
    PAGES_CONFIG: List[Dict[str, Any]] = [
        {'dir': '', 'file': 'index.html', 'slug': '', 'type': 'home', 'priority': 1.0, 'freq': 'weekly'},
        {'dir': 'about', 'slug': 'about', 'title': 'About RenderPhoenix', 'type': 'page', 'priority': 0.8, 'freq': 'monthly'},
        {'dir': 'services', 'slug': 'services', 'title': 'Services & Capabilities', 'type': 'page', 'priority': 0.8, 'freq': 'monthly'},
        {'dir': 'work', 'slug': 'work', 'title': 'Work Portfolio', 'type': 'page', 'priority': 0.9, 'freq': 'weekly'},
        {'dir': 'blog', 'slug': 'blog', 'title': 'Blog', 'type': 'page', 'priority': 0.9, 'freq': 'daily'},
        {'dir': 'contact', 'slug': 'contact', 'title': 'Get in Touch', 'type': 'page', 'priority': 0.7, 'freq': 'monthly'},
        {'dir': 'privacy-policy', 'slug': 'privacy-policy', 'title': 'Privacy Policy', 'type': 'legal', 'priority': 0.6, 'freq': 'monthly'},
        {'dir': 'dmca', 'slug': 'dmca', 'title': 'DMCA & Copyright Policy', 'type': 'legal', 'priority': 0.6, 'freq': 'monthly'},
        {'dir': '', 'file': '404.html', 'slug': '404', 'title': 'Page Not Found', 'type': 'error'}
    ]

    STATIC_ROOT_FILES: List[str] = [
        'robots.txt',
        'CNAME',
        'site.webmanifest',
        'favicon.ico',
        'favicon.png',
        'apple-touch-icon.png'
    ]
