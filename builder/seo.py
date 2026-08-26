import re
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from .config import Config
from .utils import resolve_meta_image, xml_escape
from .models import Post, Project, PageInfo

class SEOGenerator:
    """Generates Open Graph, Twitter Cards, and Schema.org JSON-LD structured data."""

    @classmethod
    def generate_meta_tags(cls, meta: Dict[str, Any], page_type: str = "website", slug: str = "") -> str:
        """Constructs complete HTML meta tags block for <head>."""
        site_url = Config.SITE_URL
        site_name = Config.SITE_NAME
        default_desc = Config.DEFAULT_DESCRIPTION

        title_raw = str(meta.get('title', '')).strip()
        if not title_raw or slug == '':
            full_title = f"{site_name} — Independent Interactive Creative Studio | Games & 3D Worlds"
        elif site_name.lower() in title_raw.lower():
            full_title = title_raw
        else:
            full_title = f"{title_raw} — {site_name}"

        desc_raw = meta.get('description') or meta.get('excerpt') or default_desc
        clean_desc = re.sub(r'<[^>]+>', '', str(desc_raw)).replace('\n', ' ').strip()
        clean_desc = re.sub(r'\s+', ' ', clean_desc)
        if len(clean_desc) > 160:
            clean_desc = clean_desc[:157] + "..."

        if slug == '':
            page_url = "/"
        elif slug == '404':
            page_url = "/404.html"
        elif page_type == 'project' or (slug and not slug.startswith('work/') and page_type == 'project'):
            clean_slug = slug.replace('work/', '')
            page_url = f"/work/{clean_slug}/"
        elif page_type == 'post' or (slug and not slug.startswith('blog/') and page_type == 'post'):
            clean_slug = slug.replace('blog/', '')
            page_url = f"/blog/{clean_slug}/"
        else:
            page_url = f"/{slug}/" if not slug.startswith('/') else slug
            if not page_url.endswith('/') and not page_url.endswith('.html'):
                page_url += '/'

        canonical_url = f"{site_url}{page_url}" if slug != '404' else ''

        img_candidate = meta.get('image') or meta.get('cover_image') or meta.get('header_image') or meta.get('og_image')
        meta_img_path = resolve_meta_image(img_candidate)
        absolute_img_url = f"{site_url}{meta_img_path}"

        og_type = "article" if page_type in ('post', 'project') else "website"
        author = meta.get('author') or meta.get('developer') or site_name

        published_time = ""
        if meta.get('date'):
            d = meta.get('date')
            if hasattr(d, 'isoformat'):
                published_time = d.isoformat()
            else:
                published_time = str(d)[:10]

        tags = meta.get('tags', [])
        techs = meta.get('technologies', [])
        cats = meta.get('categories', [])
        if isinstance(tags, str):
            tags = [tags]
        if isinstance(techs, str):
            techs = [techs]
        if isinstance(cats, str):
            cats = [cats]
        all_keywords = list(dict.fromkeys(["RenderPhoenix", "indie gamedev", "3D assets"] + tags + techs + cats))
        keywords_str = ", ".join(all_keywords)

        markdown_url = meta.get('markdown_url', '')
        md_link_tag = f'\n  <link rel="alternate" type="text/markdown" href="{markdown_url}" title="{full_title} Markdown">' if markdown_url else ''

        article_og_tags = ""
        if og_type == "article" and published_time:
            article_og_tags = f"""
  <meta property="article:published_time" content="{published_time}">
  <meta property="article:author" content="{author}">
  <meta property="article:section" content="{meta.get('category', 'Creative Work')}">"""

        schema_graph: List[Dict[str, Any]] = [
            {
                "@type": "Organization",
                "@id": f"{site_url}/#organization",
                "name": site_name,
                "url": f"{site_url}/",
                "logo": f"{site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.png",
                "sameAs": [
                    "https://mcpedl.com/user/renderphoenix/"
                ],
                "founder": {
                    "@type": "Person",
                    "name": "Tasrif Ibn Mizan"
                },
                "description": default_desc
            },
            {
                "@type": "WebSite",
                "@id": f"{site_url}/#website",
                "url": f"{site_url}/",
                "name": site_name,
                "description": default_desc,
                "publisher": {
                    "@id": f"{site_url}/#organization"
                }
            }
        ]

        if canonical_url:
            if page_type == 'post':
                schema_graph.append({
                    "@type": "BlogPosting",
                    "@id": f"{canonical_url}#article",
                    "isPartOf": {
                        "@id": f"{site_url}/#website"
                    },
                    "headline": title_raw or full_title,
                    "description": clean_desc,
                    "image": absolute_img_url,
                    "datePublished": published_time,
                    "author": {
                        "@type": "Person",
                        "name": author
                    },
                    "publisher": {
                        "@id": f"{site_url}/#organization"
                    },
                    "mainEntityOfPage": {
                        "@type": "WebPage",
                        "@id": canonical_url
                    }
                })
            elif page_type == 'project':
                schema_graph.append({
                    "@type": "CreativeWork",
                    "@id": f"{canonical_url}#project",
                    "isPartOf": {
                        "@id": f"{site_url}/#website"
                    },
                    "headline": title_raw or full_title,
                    "description": clean_desc,
                    "image": absolute_img_url,
                    "datePublished": published_time,
                    "author": {
                        "@type": "Person",
                        "name": author
                    },
                    "publisher": {
                        "@id": f"{site_url}/#organization"
                    },
                    "mainEntityOfPage": {
                        "@type": "WebPage",
                        "@id": canonical_url
                    }
                })
            else:
                schema_graph.append({
                    "@type": "WebPage",
                    "@id": canonical_url,
                    "url": canonical_url,
                    "name": full_title,
                    "description": clean_desc,
                    "image": absolute_img_url,
                    "isPartOf": {
                        "@id": f"{site_url}/#website"
                    }
                })

        schema_json = json.dumps({"@context": "https://schema.org", "@graph": schema_graph}, indent=2)

        return f"""<!-- Primary Meta Tags -->
  <title>{full_title}</title>
  <meta name="title" content="{full_title}">
  <meta name="description" content="{clean_desc}">
  <link rel="canonical" href="{canonical_url}">{md_link_tag}
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="{Config.THEME_COLOR}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="author" content="{author}">
  <meta name="keywords" content="{keywords_str}">

  <!-- Open Graph / Facebook / WhatsApp / Instagram / LinkedIn -->
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="{site_name}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:title" content="{full_title}">
  <meta property="og:description" content="{clean_desc}">
  <meta property="og:image" content="{absolute_img_url}">
  <meta property="og:image:secure_url" content="{absolute_img_url}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{title_raw or full_title}">
  <meta property="og:locale" content="en_US">{article_og_tags}

  <!-- Twitter / X -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@renderphoenix">
  <meta name="twitter:creator" content="@renderphoenix">
  <meta name="twitter:url" content="{canonical_url}">
  <meta name="twitter:title" content="{full_title}">
  <meta name="twitter:description" content="{clean_desc}">
  <meta name="twitter:image" content="{absolute_img_url}">
  <meta name="twitter:image:alt" content="{title_raw or full_title}">

  <!-- JSON-LD Structured Data -->
  <script type="application/ld+json">
{schema_json}
  </script>"""

class SitemapBuilder:
    """Constructs and validates the sitemap.xml with Google Image Extension tags."""

    @staticmethod
    def build_sitemap(pages: List[PageInfo], projects: List[Project], posts: List[Post]) -> str:
        site_url = Config.SITE_URL

        brand_images_xml = f"""    <image:image>
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
            if slug == '404':
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
    <loc>{xml_escape(site_url + '/blog/' + post_slug + '/')}</loc>
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
    <loc>{xml_escape(site_url + '/work/' + proj_slug + '/')}</loc>
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
