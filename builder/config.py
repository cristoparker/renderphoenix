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
    THEME_COLOR_LIGHT: str = "#F6F3ED"
    FOUNDER: str = "Tasrif Ibn Mizan"
    LOGO_IMAGE: str = "/assets/images/brand/Renderphoenix-Logo-512x512.png"
    FALLBACK_IMAGE: str = "/assets/images/image-not-found.svg"

    # Base directory paths
    ROOT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SITE_DIR: str = os.path.join(ROOT_DIR, '_site')
    INCLUDES_DIR: str = os.path.join(ROOT_DIR, '_includes')
    LAYOUTS_DIR: str = os.path.join(ROOT_DIR, '_layouts')
    PROJECTS_DIR: str = os.path.join(ROOT_DIR, '_projects')
    POSTS_DIR: str = os.path.join(ROOT_DIR, '_posts')
    DATA_DIR: str = os.path.join(ROOT_DIR, '_data')
    ASSETS_DIR: str = os.path.join(ROOT_DIR, 'assets')

    # Stylesheets, in cascade order. They are minified and inlined into every page's
    # <head>, so the first paint never waits on a CSS request.
    CSS_FILES: List[str] = ['tokens.css', 'base.css', 'layout.css', 'components.css', 'content.css', 'pages.css']

    # Card thumbnails are generated at these widths (served via srcset) when Pillow is available.
    THUMB_WIDTH: int = 800
    THUMB_WIDTHS: List[int] = [320, 480, 640, 800]
    CARD_SIZES: str = '(min-width: 1024px) 380px, (min-width: 600px) 46vw, calc(100vw - 2rem)'
    HERO_MAIN_SIZES: str = '(min-width: 1240px) 512px, (min-width: 901px) 42vw, calc(100vw - 5rem)'
    HERO_TILE_SIZES: str = '(min-width: 1240px) 250px, (min-width: 901px) 21vw, calc(50vw - 3rem)'
    COVER_WIDTHS: List[int] = [480, 640, 960, 1280]
    SHOWCASE_WIDTHS: List[int] = [480, 640, 800, 1120]
    SHOWCASE_SIZES: str = '(min-width: 700px) 560px, 82vw'
    BENTO_SIZES: str = '(min-width: 1024px) 590px, calc(100vw - 2rem)'
    COVER_SIZES: str = '(min-width: 1264px) 1200px, calc(100vw - 2rem)'
    ARTICLE_COVER_SIZES: str = '(min-width: 1024px) 960px, calc(100vw - 2rem)'

    # Number of items in homepage sections
    HOME_FEATURED_PROJECTS: int = 3
    HOME_LATEST_POSTS: int = 2

    # Static pages registry
    PAGES_CONFIG: List[Dict[str, Any]] = [
        {'dir': '', 'file': 'index.html', 'slug': '', 'type': 'home', 'priority': 1.0, 'freq': 'weekly'},
        {'dir': 'about', 'slug': 'about', 'title': 'About RenderPhoenix', 'type': 'page', 'priority': 0.8, 'freq': 'monthly'},
        {'dir': 'services', 'slug': 'services', 'title': 'Services & Capabilities', 'type': 'page', 'priority': 0.8, 'freq': 'monthly'},
        {'dir': 'work', 'slug': 'work', 'title': 'Work', 'type': 'page', 'priority': 0.9, 'freq': 'weekly'},
        {'dir': 'blog', 'slug': 'blog', 'title': 'Blog', 'type': 'page', 'priority': 0.9, 'freq': 'weekly'},
        {'dir': 'contact', 'slug': 'contact', 'title': 'Get in Touch', 'type': 'page', 'priority': 0.7, 'freq': 'monthly'},
        {'dir': 'privacy-policy', 'slug': 'privacy-policy', 'title': 'Privacy Policy', 'type': 'legal', 'priority': 0.3, 'freq': 'yearly'},
        {'dir': 'dmca', 'slug': 'dmca', 'title': 'DMCA & Copyright Policy', 'type': 'legal', 'priority': 0.3, 'freq': 'yearly'},
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
