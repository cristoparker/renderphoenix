import re
import json
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Any, List
from .config import Config
from .utils import resolve_meta_image, xml_escape, iso_date, parse_date, html_escape as esc
from .images import get_image_dimensions
from .loaders import ContentLoader
from .models import Post, Project, PageInfo


def _as_list(value: Any) -> List[str]:
    if not value:
        return []
    return [str(v) for v in value] if isinstance(value, list) else [str(value)]


class SEOGenerator:
    """Generates the <head> metadata: title, description, canonical, Open Graph, Twitter Card
    and a Schema.org JSON-LD graph (Organization, WebSite, page entity, BreadcrumbList)."""

    _social: List[str] = []

    @classmethod
    def social_profiles(cls) -> List[str]:
        """Official profile URLs from _data/navigation.yml (footer.social), cached."""
        if not cls._social:
            nav = ContentLoader.load_yaml('navigation', {}) or {}
            cls._social = [i['url'] for i in (nav.get('footer', {}).get('social') or []) if i.get('url')]
            cls._social.append("https://mcpedl.com/user/renderphoenix/")
        return cls._social

    @staticmethod
    def page_path(page_type: str, slug: str) -> str:
        if slug == '':
            return '/'
        if page_type == 'project':
            return f'/work/{slug}/'
        if page_type == 'post':
            return f'/blog/{slug}/'
        return f'/{slug.strip("/")}/'

    @staticmethod
    def clean_description(text: Any) -> str:
        desc = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', str(text or ''))).strip()
        if len(desc) > 160:
            desc = desc[:157].rsplit(' ', 1)[0].rstrip(',.;:—-') + '…'
        return desc

    @classmethod
    def generate_meta_tags(cls, meta: Dict[str, Any], page_type: str = "website", slug: str = "") -> str:
        site_url, site_name = Config.SITE_URL, Config.SITE_NAME
        is_404 = slug == '404'

        title_raw = str(meta.get('title', '')).strip()
        if not title_raw or slug == '':
            full_title = f"{site_name} — {Config.SITE_TAGLINE} | Games & 3D Worlds"
        elif site_name.lower() in title_raw.lower():
            full_title = title_raw
        else:
            full_title = f"{title_raw} — {site_name}"

        desc = cls.clean_description(meta.get('description') or Config.DEFAULT_DESCRIPTION)
        path = cls.page_path(page_type, slug)
        canonical = '' if is_404 else f"{site_url}{path}"

        img_path = resolve_meta_image(meta.get('image') or meta.get('cover_image') or meta.get('header_image'))
        img_url = f"{site_url}{img_path}"
        img_dims = get_image_dimensions(img_path)
        author = meta.get('author') or meta.get('developer') or site_name
        published = iso_date(meta.get('date'))
        modified = iso_date(meta.get('last_modified_at')) or published
        is_article = page_type in ('post', 'project')

        # ---------------------------------------------------------- JSON-LD
        org_id, site_id = f"{site_url}/#organization", f"{site_url}/#website"
        graph: List[Dict[str, Any]] = [
            {
                "@type": "Organization",
                "@id": org_id,
                "name": site_name,
                "alternateName": "Minehutt",
                "url": f"{site_url}/",
                "logo": {"@type": "ImageObject", "url": f"{site_url}{Config.LOGO_IMAGE}", "width": 512, "height": 512},
                "foundingDate": "2019",
                "founder": {"@type": "Person", "name": Config.FOUNDER},
                "sameAs": cls.social_profiles(),
                "description": Config.DEFAULT_DESCRIPTION,
            },
            {"@type": "WebSite", "@id": site_id, "url": f"{site_url}/", "name": site_name,
             "publisher": {"@id": org_id}, "inLanguage": "en"},
        ]
        if canonical:
            page_entity: Dict[str, Any] = {
                "@id": f"{canonical}#main",
                "url": canonical,
                "name": title_raw or full_title,
                "headline": title_raw or full_title,
                "description": desc,
                "image": img_url,
                "isPartOf": {"@id": site_id},
                "inLanguage": "en",
            }
            if page_type == 'post':
                page_entity.update({"@type": "BlogPosting", "author": {"@type": "Person", "name": author},
                                    "publisher": {"@id": org_id}, "mainEntityOfPage": canonical,
                                    "keywords": _as_list(meta.get('tags'))})
            elif page_type == 'project':
                page_entity.update({"@type": "CreativeWork", "creator": {"@id": org_id},
                                    "genre": meta.get('category', ''),
                                    "keywords": _as_list(meta.get('tags')) + _as_list(meta.get('technologies'))})
                if meta.get('award'):
                    page_entity["award"] = meta['award']
            else:
                page_entity["@type"] = "WebPage"
                page_entity.pop("headline")
            if published:
                page_entity["datePublished"] = published
                page_entity["dateModified"] = modified
            graph.append(page_entity)

            crumbs = [("Home", f"{site_url}/")]
            if page_type == 'project':
                crumbs.append(("Work", f"{site_url}/work/"))
            elif page_type == 'post':
                crumbs.append(("Blog", f"{site_url}/blog/"))
            if slug:
                crumbs.append((title_raw or full_title, canonical))
            if len(crumbs) > 1:
                graph.append({"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
                    for i, (name, url) in enumerate(crumbs)]})

        # "</" must not appear raw inside <script>
        schema = json.dumps({"@context": "https://schema.org", "@graph": graph},
                            ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

        # ------------------------------------------------------------- tags
        t, d, im = esc(full_title), esc(desc), esc(img_url)
        tags = [
            f'<title>{t}</title>',
            f'<meta name="description" content="{d}">',
        ]
        if canonical:
            tags.append(f'<link rel="canonical" href="{esc(canonical)}">')
        if meta.get('markdown_url'):
            tags.append(f'<link rel="alternate" type="text/markdown" href="{esc(meta["markdown_url"])}" title="Markdown version">')
        tags += [
            f'<link rel="alternate" type="application/rss+xml" href="/feed.xml" title="{esc(site_name)} blog">',
            f'<meta name="theme-color" content="{Config.THEME_COLOR_LIGHT}">',
            '<meta name="robots" content="noindex, follow">' if is_404 else
            '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
            f'<meta name="author" content="{esc(author)}">',
            f'<meta property="og:type" content="{"article" if is_article else "website"}">',
            f'<meta property="og:site_name" content="{esc(site_name)}">',
            '<meta property="og:locale" content="en_US">',
            f'<meta property="og:title" content="{t}">',
            f'<meta property="og:description" content="{d}">',
            f'<meta property="og:image" content="{im}">',
        ]
        if canonical:
            tags.append(f'<meta property="og:url" content="{esc(canonical)}">')
        if img_dims:
            tags += [f'<meta property="og:image:width" content="{img_dims[0]}">',
                     f'<meta property="og:image:height" content="{img_dims[1]}">']
        tags.append(f'<meta property="og:image:alt" content="{esc(title_raw or full_title)}">')
        if is_article and published:
            tags += [f'<meta property="article:published_time" content="{published}">',
                     f'<meta property="article:modified_time" content="{modified}">']
            if meta.get('category'):
                tags.append(f'<meta property="article:section" content="{esc(meta["category"])}">')
        tags += [
            '<meta name="twitter:card" content="summary_large_image">',
            '<meta name="twitter:site" content="@renderphoenix">',
            f'<meta name="twitter:title" content="{t}">',
            f'<meta name="twitter:description" content="{d}">',
            f'<meta name="twitter:image" content="{im}">',
            f'<script type="application/ld+json">{schema}</script>',
        ]
        return '\n  '.join(tags)


class FeedBuilder:
    """Builds an RSS 2.0 feed of blog posts (/feed.xml)."""

    @staticmethod
    def build_feed(posts: List[Post]) -> str:
        site_url = Config.SITE_URL

        def rfc822(value: Any) -> str:
            dt = parse_date(value) or datetime(1970, 1, 1)
            return dt.replace(tzinfo=dt.tzinfo or timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')

        items = []
        for post in posts:
            url = f"{site_url}/blog/{post.slug}/"
            enclosure = ''
            if post.image:
                img = site_url + urllib.parse.quote(urllib.parse.unquote(post.image), safe='/')
                enclosure = f'\n      <enclosure url="{xml_escape(img)}" type="image/{post.image.rsplit(".", 1)[-1].lower().replace("jpg", "jpeg")}" length="0"/>'
            cats = ''.join(f'\n      <category>{xml_escape(c)}</category>' for c in post.categories)
            items.append(f"""    <item>
      <title>{xml_escape(post.title)}</title>
      <link>{xml_escape(url)}</link>
      <guid isPermaLink="true">{xml_escape(url)}</guid>
      <pubDate>{rfc822(post.date)}</pubDate>
      <dc:creator>{xml_escape(post.author or Config.SITE_NAME)}</dc:creator>
      <description>{xml_escape(post.description)}</description>{cats}{enclosure}
    </item>""")
        last = rfc822(posts[0].date) if posts else rfc822(None)
        feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>{xml_escape(Config.SITE_NAME)} Blog</title>
    <link>{site_url}/blog/</link>
    <atom:link href="{site_url}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Devlogs, studio news and behind-the-scenes stories from {xml_escape(Config.SITE_NAME)}.</description>
    <language>en</language>
    <lastBuildDate>{last}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
        ET.fromstring(feed)  # validate
        return feed


class SitemapBuilder:
    """Constructs and validates the sitemap.xml with Google Image Extension tags."""

    @staticmethod
    def build_sitemap(pages: List[PageInfo], projects: List[Project], posts: List[Post]) -> str:
        site_url = Config.SITE_URL

        def lastmod(item) -> str:
            d = iso_date(item.meta.get('last_modified_at') or item.date)
            return f"\n    <lastmod>{d}</lastmod>" if d else ''

        brand_images_xml = f"""    <image:image>
      <image:loc>{site_url}/assets/images/brand/Renderphoenix-Logo-512x512.png</image:loc>
      <image:title>RenderPhoenix Official Square Studio Logo Mark (PNG 512x512)</image:title>
    </image:image>
    <image:image>
      <image:loc>{site_url}/assets/images/favicon-512x512.png</image:loc>
      <image:title>RenderPhoenix Official Square Favicon Mark (PNG 512x512)</image:title>
    </image:image>
    <image:image>
      <image:loc>{site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.svg</image:loc>
      <image:title>RenderPhoenix Official Colored Logo Mark (SVG)</image:title>
    </image:image>
    <image:image>
      <image:loc>{site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.png</image:loc>
      <image:title>RenderPhoenix Official Colored Logo Mark (PNG)</image:title>
    </image:image>
    <image:image>
      <image:loc>{site_url}/assets/images/brand/Renderphoenix%20Text%20Colored%20Horizontal.svg</image:loc>
      <image:title>RenderPhoenix Official Horizontal Colored Wordmark</image:title>
    </image:image>
    <image:image>
      <image:loc>{site_url}/assets/images/brand/Renderphoenix%20White%20Logo.svg</image:loc>
      <image:title>RenderPhoenix Official White Logo Mark</image:title>
    </image:image>
    <image:image>
      <image:loc>{site_url}/assets/images/brand/Renderphoenix%20White%20Logo.png</image:loc>
      <image:title>RenderPhoenix Official White Logo PNG</image:title>
    </image:image>"""

        sitemap_entries: List[str] = [
            f"""  <url>
    <loc>{site_url}/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
{brand_images_xml}
  </url>"""
        ]

        for pinfo in pages:
            slug = pinfo.slug
            if slug == '404' or slug == '':
                continue
            img_xml = ""
            if slug == 'about':
                img_xml = f"""
    <image:image>
      <image:loc>{site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.png</image:loc>
      <image:title>RenderPhoenix Studio Logo</image:title>
    </image:image>"""
            sitemap_entries.append(f"""  <url>
    <loc>{site_url}/{slug}/</loc>
    <changefreq>{pinfo.freq}</changefreq>
    <priority>{pinfo.priority}</priority>{img_xml}
  </url>""")

        sitemap_entries.append(f"""  <url>
    <loc>{site_url}/images/brand/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
{brand_images_xml}
  </url>""")

        for post in posts:
            post_slug = post.slug
            post_img = post.image or ''
            img_xml = ""
            if post_img:
                img_xml = f"""
    <image:image>
      <image:loc>{xml_escape(site_url + post_img)}</image:loc>
      <image:title>{xml_escape(post.title)}</image:title>
    </image:image>"""
            sitemap_entries.append(f"""  <url>
    <loc>{xml_escape(site_url + '/blog/' + post_slug + '/')}</loc>{lastmod(post)}
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>{img_xml}
  </url>""")

        for proj in projects:
            proj_slug = proj.slug
            proj_img = proj.cover_image or ''
            img_xml = ""
            if proj_img and not proj_img.endswith('image-not-found.svg'):
                img_xml = f"""
    <image:image>
      <image:loc>{xml_escape(site_url + proj_img)}</image:loc>
      <image:title>{xml_escape(proj.title)}</image:title>
    </image:image>"""
            sitemap_entries.append(f"""  <url>
    <loc>{xml_escape(site_url + '/work/' + proj_slug + '/')}</loc>{lastmod(proj)}
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>{img_xml}
  </url>""")

        sitemap_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' +
            '\n'.join(sitemap_entries) +
            '\n</urlset>\n'
        )

        # Validate syntax
        ET.fromstring(sitemap_xml)
        return sitemap_xml
