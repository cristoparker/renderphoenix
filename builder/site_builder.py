import os
import re
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from .config import Config
from .models import Project, Post, Service, TeamMember, PageInfo
from .loaders import ContentLoader
from .markdown import MarkdownParser
from .components import ComponentRenderer as C
from .template import TemplateEngine
from .seo import SEOGenerator, SitemapBuilder, FeedBuilder
from .search import SearchIndexer
from .llm import LLMGenerator
from .utils import format_full_date, iso_date, parse_date, html_escape as esc


class SiteBuilder:
    """Orchestrates the static site generation lifecycle for RenderPhoenix."""

    def __init__(self, root_dir: str = Config.ROOT_DIR, site_dir: str = Config.SITE_DIR):
        self.root_dir = root_dir
        self.site_dir = site_dir
        self.engine = TemplateEngine()
        self.inline_css = ''
        self.navigation: Dict[str, Any] = {}

    # ------------------------------------------------------------ helpers
    def _write(self, rel_path: str, content: str) -> None:
        path = os.path.join(self.site_dir, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def minify_css(css: str) -> str:
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        css = re.sub(r'\s+', ' ', css)
        # Spaces before "(" are kept, so `@media (...) and (...)` and `:not(...)` both survive.
        css = re.sub(r'\s*([{};,>])\s*', r'\1', css)
        css = re.sub(r':\s+', ':', css)  # only after ':' — a space before it is a descendant selector
        return css.replace(';}', '}').strip()

    @staticmethod
    def minify_js(js: str) -> str:
        """Conservative minification: drops block comments, whole-line // comments,
        indentation and blank lines. Code itself is never rewritten."""
        js = re.sub(r'/\*.*?\*/', '', js, flags=re.S)
        lines = (line.strip() for line in js.splitlines())
        return '\n'.join(l for l in lines if l and not l.startswith('//')) + '\n'

    def _base_context(self, meta: Dict[str, Any], page_type: str, slug: str, current_path: str) -> Dict[str, Any]:
        """Values used by the default layout, header and footer on every page."""
        footer = self.navigation.get('footer', {})
        return {
            'seo': SEOGenerator.generate_meta_tags(meta, page_type=page_type, slug=slug),
            'css': self.inline_css,
            'preload': meta.get('preload', ''),
            'nav': C.nav_links(self.navigation.get('header', []), current_path),
            'footer_nav': C.link_list(footer.get('navigation', [])),
            'footer_resources': C.link_list(footer.get('resources', [])),
            'footer_social': C.social_links(footer.get('social', [])),
            'year': str(datetime.now().year),
        }

    def _write_markdown(self, section: str, slug: str, raw_md: str) -> None:
        """Raw Markdown endpoints for AI/LLM consumers: /<section>/<slug>.md and /<section>/<slug>/index.md."""
        prefix = f'{section}/' if section else ''
        self._write(f'{prefix}{slug}.md', raw_md)
        self._write(f'{prefix}{slug}/index.md', raw_md)

    # ------------------------------------------------------------- assets
    def clean(self) -> None:
        if os.path.exists(self.site_dir):
            shutil.rmtree(self.site_dir, ignore_errors=True)
            print("Cleaned old _site directory")

    def copy_assets(self) -> None:
        """Copies static assets, mirrors the brand kit and prepares the inlined stylesheet."""
        os.makedirs(self.site_dir, exist_ok=True)
        dest_assets = os.path.join(self.site_dir, 'assets')
        shutil.copytree(Config.ASSETS_DIR, dest_assets, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('*.css'))
        for name in os.listdir(os.path.join(dest_assets, 'js')):
            if name.endswith('.js'):
                path = os.path.join(dest_assets, 'js', name)
                with open(path, 'r', encoding='utf-8') as f:
                    js = f.read()
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.minify_js(js))
        print("Copied assets to _site/assets")

        brand_src = os.path.join(Config.ASSETS_DIR, 'images', 'brand')
        if os.path.exists(brand_src):
            shutil.copytree(brand_src, os.path.join(self.site_dir, 'images', 'brand'), dirs_exist_ok=True)
            print("Mirrored brand assets -> _site/images/brand/")

        parts = []
        for name in Config.CSS_FILES:
            path = os.path.join(Config.ASSETS_DIR, 'css', name)
            if not os.path.exists(path):
                raise FileNotFoundError(f'Missing stylesheet: {path}')
            with open(path, 'r', encoding='utf-8') as f:
                parts.append(f.read())
        self.inline_css = self.minify_css('\n'.join(parts))
        print(f"Inlined CSS ({len(self.inline_css.encode('utf-8')) / 1024:.1f} KB)")

    # ----------------------------------------------------------- projects
    def build_projects(self, projects: List[Project]) -> None:
        for proj in projects:
            slug = proj.slug
            proj.markdown_url = f"/work/{slug}.md"
            cover = proj.cover_image or Config.FALLBACK_IMAGE
            meta = {**proj.meta, 'markdown_url': proj.markdown_url,
                    'preload': C.preload(cover, Config.COVER_WIDTHS, Config.COVER_SIZES)}

            meta_bits = [esc(proj.category), f'<time datetime="{iso_date(proj.date)}">{format_full_date(proj.date)}</time>']
            if proj.downloads:
                meta_bits.append(f'{esc(proj.downloads)} downloads')

            context = {
                **self._base_context(meta, 'project', slug, f'/work/{slug}/'),
                'page': {'title': esc(proj.title), 'description': esc(proj.description)},
                'meta_line': ' · '.join(meta_bits),
                'award': C.award_banner(proj),
                'cover': C.image(cover, f'{proj.title} cover', eager=True,
                                 widths=Config.COVER_WIDTHS, sizes=Config.COVER_SIZES),
                'specs': C.project_specs(proj),
                'actions': C.project_actions(proj),
            }
            html = self.engine.render_page('project', MarkdownParser.to_html(proj.body), context)
            self._write(f'work/{slug}/index.html', html)
            self._write_markdown('work', slug, proj.raw_content)
            print(f"Built project -> /work/{slug}/")

    # -------------------------------------------------------------- posts
    def build_posts(self, posts: List[Post]) -> None:
        for i, post in enumerate(posts):
            slug = post.slug
            post.markdown_url = f"/blog/{slug}.md"
            meta = {**post.meta, 'markdown_url': post.markdown_url}
            cover = ''
            if post.image:
                meta['preload'] = C.preload(post.image, Config.COVER_WIDTHS, Config.ARTICLE_COVER_SIZES)
                img = C.image(post.image, post.title, eager=True,
                              widths=Config.COVER_WIDTHS, sizes=Config.ARTICLE_COVER_SIZES)
                cover = f'<figure class="article-cover">{img}</figure>'

            prev_post = posts[i + 1] if i + 1 < len(posts) else None
            next_post = posts[i - 1] if i > 0 else None
            context = {
                **self._base_context(meta, 'post', slug, f'/blog/{slug}/'),
                'page': {
                    'title': esc(post.title),
                    'description': esc(post.description),
                    'category': esc(C.post_category(post)),
                    'date': format_full_date(post.date),
                    'date_iso': iso_date(post.date),
                    'author': esc(post.author or Config.SITE_NAME),
                },
                'cover': cover,
                'tags': C.tags(post.tags),
                'pager': C.post_nav(prev_post, next_post),
            }
            html = self.engine.render_page('post', MarkdownParser.to_html(post.body), context)
            self._write(f'blog/{slug}/index.html', html)
            self._write_markdown('blog', slug, post.raw_content)
            print(f"Built post -> /blog/{slug}/")

    # -------------------------------------------------------------- pages
    def _blocks(self, projects: List[Project], posts: List[Post], services: List[Service],
                team: List[TeamMember]) -> Dict[str, str]:
        """Pre-rendered blocks that page sources can place with `{{ name }}`."""
        site = ContentLoader.load_yaml('site', {}) or {}
        featured = [p for p in projects if p.featured] or projects
        tokens = {'project_count': len(projects)}
        return {
            'showcase': C.showcase(projects),
            'showcase_preload': C.showcase_preload(projects),
            'services_bento': C.services_bento(services, projects),
            'journal': ''.join(C.post_card(p) for p in posts[:Config.HOME_LATEST_POSTS]),
            'featured_projects': ''.join(C.project_card(p) for p in featured[:Config.HOME_FEATURED_PROJECTS]),
            'project_grid': ''.join(C.project_card(p, heading='h2') for p in projects),
            'project_filters': C.filter_chips(projects),
            'latest_posts': ''.join(C.post_row(p) for p in posts[:Config.HOME_LATEST_POSTS]),
            'post_grid': ''.join(C.post_card(p, eager=(i == 0)) for i, p in enumerate(posts)),
            'services_list': ''.join(C.service_item(s, i + 1) for i, s in enumerate(services)),
            'services_detailed': ''.join(C.service_item(s, i + 1, detailed=True, heading='h2')
                                         for i, s in enumerate(services)),
            'team_grid': ''.join(C.team_card(m) for m in team),
            'stats': C.stats(site.get('stats', []), tokens),
            'timeline': C.timeline(site.get('timeline', [])),
            'project_count': str(len(projects)),
            'post_count': str(len(posts)),
        }

    @staticmethod
    def _demote_headings(html: str, title: str) -> str:
        """The page layout already renders the title as <h1>, so Markdown `#` headings become
        <h2>, and a leading heading that just repeats the title is dropped."""
        html = re.sub(r'^\s*<h1[^>]*>\s*' + re.escape(esc(title)) + r'\s*</h1>', '', html, count=1, flags=re.I)
        return re.sub(r'<(/?)h1(\b[^>]*)>', r'<\1h2\2>', html)

    def _resolve_page_source(self, pcfg: Dict[str, Any]) -> Optional[str]:
        if pcfg.get('file'):
            cand = os.path.join(self.root_dir, pcfg['file'])
            return cand if os.path.exists(cand) else None
        for name in ('index.html', 'index.md'):
            cand = os.path.join(self.root_dir, pcfg.get('dir', ''), name)
            if os.path.exists(cand):
                return cand
        return None

    def build_pages(self, projects: List[Project], posts: List[Post], services: List[Service],
                    team: List[TeamMember]) -> List[Dict[str, Any]]:
        blocks = self._blocks(projects, posts, services, team)
        compiled: List[Dict[str, Any]] = []

        for pcfg in Config.PAGES_CONFIG:
            slug = pcfg['slug']
            src_path = self._resolve_page_source(pcfg)
            if not src_path:
                print(f"  Warning: no source for page '{slug or '/'}'")
                continue

            meta, raw_body = ContentLoader.load_frontmatter_and_content(src_path)
            title = meta.get('title', pcfg.get('title', ''))
            desc = meta.get('description', '')
            layout = meta.get('layout', 'default')

            if src_path.endswith('.md'):
                body = f'<div class="container prose">{self._demote_headings(MarkdownParser.to_html(raw_body), title)}</div>'
            else:
                body = self.engine.render(self.engine.render_includes(raw_body), blocks)

            is_page = slug not in ('', '404')
            page_meta = {
                'preload': blocks['showcase_preload'] if slug == '' else '',
                'title': title,
                'description': desc or Config.DEFAULT_DESCRIPTION,
                'image': meta.get('image', ''),
                'markdown_url': f"/{slug}.md" if is_page else '',
            }
            context = {
                **self._base_context(page_meta, 'website', slug, f'/{slug}/' if slug else '/'),
                **blocks,
                'page': {'title': esc(title), 'description': esc(desc)},
            }
            html = self.engine.render_page(layout, body, context)

            if slug == '':
                self._write('index.html', html)
            elif slug == '404':
                self._write('404.html', html)
            else:
                self._write(f'{slug}/index.html', html)
            print(f"Built page -> /{slug + '/' if slug else ''}")

            if is_page:
                md_path = os.path.join(self.root_dir, pcfg.get('dir', ''), 'index.md')
                if os.path.exists(md_path):
                    with open(md_path, 'r', encoding='utf-8') as f:
                        raw_md = f.read()
                else:
                    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body)).strip()
                    raw_md = f'---\ntitle: "{title}"\ndescription: "{desc}"\n---\n\n# {title}\n\n{desc}\n\n{text}\n'
                self._write(f'{slug}.md', raw_md)
                self._write(f'{slug}/index.md', raw_md)

            compiled.append({
                'slug': slug,
                'title': title,
                'desc': desc,
                'content_snippet': re.sub(r'<[^>]+>', ' ', body),
                'type': pcfg.get('type', 'page'),
                'priority': pcfg.get('priority', 0.8),
                'freq': pcfg.get('freq', 'monthly'),
            })
        return compiled

    # --------------------------------------------------------- root files
    def copy_static_root_files(self) -> None:
        for name in Config.STATIC_ROOT_FILES:
            src = os.path.join(self.root_dir, name)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(self.site_dir, name))
        print("Copied static root files")

    def build_redirects(self, redirects: List[Dict[str, str]]) -> None:
        """Instant HTML redirect pages plus a _redirects file for configured short URLs."""
        rules = []
        for r in redirects:
            slug = r.get('from', '').strip().strip('/')
            target = r.get('to', '').strip()
            if not slug or not target:
                continue
            canonical = f"{Config.SITE_URL}{target}" if target.startswith('/') else target
            self._write(f'{slug}/index.html', f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Redirecting…</title>
  <meta http-equiv="refresh" content="0; url={esc(target)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta name="robots" content="noindex, follow">
  <script>location.replace({json.dumps(target)});</script>
</head>
<body style="font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0;background:{Config.THEME_COLOR_LIGHT};color:#1F1C18">
  <p>Redirecting… <a href="{esc(target)}" style="color:inherit">Continue</a></p>
</body>
</html>
""")
            rules.append(f"/{slug} {target} 302")
        if rules:
            self._write('_redirects', '\n'.join(rules) + '\n')
            print(f"Built {len(rules)} redirects")

    # --------------------------------------------------------- validation
    def validate_content(self, projects: List[Project], posts: List[Post]) -> None:
        """Fails the build on content errors that would ship broken pages; warns on softer issues."""
        errors: List[str] = []
        warnings: List[str] = []

        def asset_exists(url: str) -> bool:
            if not url or url.startswith(('http://', 'https://')):
                return True
            from urllib.parse import unquote
            return os.path.isfile(os.path.join(self.root_dir, unquote(url.split('?')[0]).lstrip('/')))

        for kind, items in (('project', projects), ('post', posts)):
            seen: Dict[str, int] = {}
            for item in items:
                seen[item.slug] = seen.get(item.slug, 0) + 1
                if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', item.slug):
                    warnings.append(f"{kind} '{item.slug}': slug should be lowercase-hyphenated")
                if not item.description:
                    warnings.append(f"{kind} '{item.slug}': missing description (used for SEO)")
                if not parse_date(item.date):
                    errors.append(f"{kind} '{item.slug}': missing or unreadable date '{item.date}'")
                image = item.cover_image if kind == 'project' else item.image
                if image and not asset_exists(image):
                    errors.append(f"{kind} '{item.slug}': image not found: {image}")
            errors += [f"duplicate {kind} slug '{s}'" for s, count in seen.items() if count > 1]

        for w in warnings:
            print(f"  Warning: {w}")
        if errors:
            raise ValueError('Content validation failed:\n  - ' + '\n  - '.join(errors))

    # -------------------------------------------------------------- build
    def build(self) -> None:
        self.clean()
        self.copy_assets()
        self.navigation = ContentLoader.load_yaml('navigation', {}) or {}

        projects = ContentLoader.load_projects()
        posts = ContentLoader.load_posts()
        services = ContentLoader.load_services()
        team = ContentLoader.load_team()
        self.validate_content(projects, posts)

        self.build_projects(projects)
        self.build_posts(posts)
        compiled = self.build_pages(projects, posts, services, team)

        SearchIndexer.build_indexes(projects, posts, compiled)

        page_models = [PageInfo(slug=p['slug'], title=p['title'], desc=p['desc'], type=p['type'],
                                priority=p['priority'], freq=p['freq']) for p in compiled]
        sitemap_xml = SitemapBuilder.build_sitemap(page_models, projects, posts)
        self._write('sitemap.xml', sitemap_xml)
        with open(os.path.join(self.root_dir, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        print("Built sitemap.xml")

        self._write('feed.xml', FeedBuilder.build_feed(posts))
        print("Built feed.xml")

        LLMGenerator.build_indexes(projects, posts, compiled)
        self.copy_static_root_files()
        self.build_redirects(ContentLoader.load_redirects())
        print(f"Build complete: {len(projects)} projects, {len(posts)} posts, {len(compiled)} pages")
