import os
import shutil
import re
from typing import List, Dict, Any
from .config import Config
from .models import Project, Post, Service, TeamMember, PageInfo
from .loaders import ContentLoader
from .markdown import MarkdownParser
from .components import ComponentRenderer
from .template import TemplateEngine
from .seo import SitemapBuilder
from .search import SearchIndexer
from .llm import LLMGenerator
from .utils import format_full_date, get_youtube_embed_url, clean_conditional

class SiteBuilder:
    """Orchestrates the static site generation lifecycle for RenderPhoenix."""

    def __init__(self, root_dir: str = Config.ROOT_DIR, site_dir: str = Config.SITE_DIR):
        self.root_dir = root_dir
        self.site_dir = site_dir
        self.template_engine = TemplateEngine()

    def clean(self) -> None:
        """Removes the old build directory."""
        if os.path.exists(self.site_dir):
            shutil.rmtree(self.site_dir, ignore_errors=True)
            print("Cleaned old _site directory")

    def copy_assets(self) -> None:
        """Copies static assets and mirrors the brand kit directory."""
        os.makedirs(self.site_dir, exist_ok=True)
        if os.path.exists(Config.ASSETS_DIR):
            dest_assets = os.path.join(self.site_dir, 'assets')
            if os.path.exists(dest_assets):
                shutil.rmtree(dest_assets)
            shutil.copytree(Config.ASSETS_DIR, dest_assets)
            print("Copied assets to _site/assets")

            # Mirror brand directory to _site/images/brand for direct URL access (/images/brand/)
            brand_src = os.path.join(Config.ASSETS_DIR, 'images', 'brand')
            if os.path.exists(brand_src):
                images_brand_dest = os.path.join(self.site_dir, 'images', 'brand')
                os.makedirs(os.path.dirname(images_brand_dest), exist_ok=True)
                if os.path.exists(images_brand_dest):
                    shutil.rmtree(images_brand_dest)
                shutil.copytree(brand_src, images_brand_dest)
                print("Mirrored brand assets -> _site/images/brand/")

    def build_projects(self, projects: List[Project]) -> None:
        """Compiles project portfolio detail pages and raw markdown endpoints."""
        def_layout = self.template_engine.get_layout('default')
        proj_layout = self.template_engine.get_layout('project')

        for proj in projects:
            slug = proj.slug
            proj.markdown_url = f"/work/{slug}.md"
            p_html_body = MarkdownParser.to_html(proj.body)

            # Assemble layout
            p_content = proj_layout.replace('{{ content }}', p_html_body)
            p_content = p_content.replace('{{ page.title }}', proj.title)
            p_content = p_content.replace('{{ page.description }}', proj.description)
            p_content = p_content.replace('{{ page.category }}', proj.category)
            proj_date_formatted = format_full_date(proj.date)
            p_content = p_content.replace('{{ page.date | date: "%d %b %Y" }}', proj_date_formatted)
            p_content = p_content.replace('{{ page.date }}', proj_date_formatted)
            p_content = p_content.replace('{{ page.year }}', proj_date_formatted)

            p_content = clean_conditional(p_content, 'page.downloads', bool(proj.downloads), {'{{ page.downloads }}': str(proj.downloads)})
            p_content = clean_conditional(p_content, 'page.description', bool(proj.description), {'{{ page.description }}': proj.description})
            p_content = clean_conditional(p_content, 'page.award', bool(proj.award), {'{{ page.award }}': proj.award})
            p_content = clean_conditional(p_content, 'page.developer', bool(proj.developer), {'{{ page.developer }}': proj.developer})

            # Render dynamic specs and sidebar action buttons
            specs_html = ComponentRenderer.render_project_specs(proj)
            actions_html = ComponentRenderer.render_project_sidebar_actions(proj)
            p_content = p_content.replace('{{ project_specs }}', specs_html)
            p_content = p_content.replace('{{ project_sidebar_actions }}', actions_html)

            yt_url = proj.youtube_url
            yt_embed = get_youtube_embed_url(yt_url)
            yt_author = proj.youtube_author

            p_content = p_content.replace('{{ page.youtube_url }}', yt_url)
            p_content = p_content.replace('{{ page.youtube_embed_url }}', yt_embed)
            p_content = p_content.replace('{{ page.youtube_author }}', yt_author)

            p_content = clean_conditional(p_content, 'page.youtube_author', bool(yt_author))
            p_content = clean_conditional(p_content, 'page.youtube_url', bool(yt_url))

            cover_img = proj.cover_image or '/assets/images/image-not-found.svg'
            p_content = re.sub(r'\{%\s*assign\s+cover_img\s*=[\s\S]*?%\}', '', p_content)
            p_content = p_content.replace('{{ cover_img | relative_url }}', cover_img)
            p_content = p_content.replace('{{ page.cover_image | relative_url }}', cover_img)

            full_html = def_layout.replace('{{ content }}', p_content)
            full_html = self.template_engine.clean_liquid_tags(full_html, proj.meta, page_type='project', slug=slug)

            out_dir = os.path.join(self.site_dir, 'work', slug)
            os.makedirs(out_dir, exist_ok=True)

            # 1. Output HTML
            with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(full_html)

            # 2. Output raw Markdown in directory and at /work/<slug>.md
            raw_md = proj.raw_content
            with open(os.path.join(out_dir, 'index.md'), 'w', encoding='utf-8') as f:
                f.write(raw_md)
            with open(os.path.join(self.site_dir, 'work', f"{slug}.md"), 'w', encoding='utf-8') as f:
                f.write(raw_md)

            print(f"Built project page -> _site/work/{slug}/ (index.html, index.md, {slug}.md)")

    def build_posts(self, posts: List[Post]) -> None:
        """Compiles blog post / devlog detail pages and raw markdown endpoints."""
        def_layout = self.template_engine.get_layout('default')
        post_layout = self.template_engine.get_layout('post')

        for i, post in enumerate(posts):
            slug = post.slug
            post.markdown_url = f"/blog/{slug}.md"
            p_html_body = MarkdownParser.to_html(post.body)

            # Build article tags
            tags = post.meta.get('tags', [])
            if tags:
                tag_chips = ''.join([f'<span class="tag-chip">#{t}</span>' for t in tags])
                tags_html = f'<div class="article-tags"><span class="tags-label">Tags:</span>{tag_chips}</div>'
            else:
                tags_html = ''

            # Build prev/next post navigation
            prev_post = posts[i + 1] if i + 1 < len(posts) else None
            next_post = posts[i - 1] if i > 0 else None
            nav_links = []
            if prev_post:
                nav_links.append(f'<a href="/blog/{prev_post.slug}/" class="post-nav-link prev-post"><span class="nav-dir">&larr; Previous</span><span class="nav-title">{prev_post.title}</span></a>')
            if next_post:
                nav_links.append(f'<a href="/blog/{next_post.slug}/" class="post-nav-link next-post"><span class="nav-dir">Next &rarr;</span><span class="nav-title">{next_post.title}</span></a>')
            nav_html = f'<div class="post-navigation">{"".join(nav_links)}</div>' if nav_links else ''

            p_content = post_layout.replace('{{ content }}', p_html_body)
            p_content = p_content.replace('{{ page.title }}', post.title)
            p_content = p_content.replace('{{ page.description }}', post.description)
            p_content = p_content.replace('{{ page.author | default: site.author.name }}', post.author or 'RenderPhoenix')
            p_content = p_content.replace('{{ article_tags }}', tags_html)
            p_content = p_content.replace('{{ post_navigation }}', nav_html)
            post_date_formatted = format_full_date(post.date)
            p_content = p_content.replace('{{ page.date | date: "%d %b %Y" }}', post_date_formatted)
            p_content = p_content.replace('{{ page.date | date: "%B %d, %Y" }}', post_date_formatted)
            p_content = p_content.replace('{{ page.date }}', post_date_formatted)
            p_content = re.sub(r'\{%\s*if\s+page\.categories\s*%\}.*?\{%\s*endif\s*%\}', 'Devlog', p_content)

            if post.image:
                p_content = p_content.replace('{% if page.image %}', '').replace('{% endif %}', '').replace('{{ page.image | relative_url }}', post.image)

            full_html = def_layout.replace('{{ content }}', p_content)
            full_html = self.template_engine.clean_liquid_tags(full_html, post.meta, page_type='post', slug=slug)

            out_dir = os.path.join(self.site_dir, 'blog', slug)
            os.makedirs(out_dir, exist_ok=True)

            # 1. Output HTML
            with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(full_html)

            # 2. Output raw Markdown in directory and at /blog/<slug>.md
            raw_md = post.raw_content
            with open(os.path.join(out_dir, 'index.md'), 'w', encoding='utf-8') as f:
                f.write(raw_md)
            with open(os.path.join(self.site_dir, 'blog', f"{slug}.md"), 'w', encoding='utf-8') as f:
                f.write(raw_md)

            print(f"Built post page -> _site/blog/{slug}/ (index.html, index.md, {slug}.md)")

    def build_pages(
        self,
        projects: List[Project],
        posts: List[Post],
        services: List[Service],
        team: List[TeamMember]
    ) -> List[Dict[str, Any]]:
        """Compiles main static pages, legal documents, error page, and injects dynamic loops."""
        def_layout = self.template_engine.get_layout('default')
        page_layout = self.template_engine.get_layout('page')

        featured_projects_cards = ''.join([ComponentRenderer.render_project_card(p) for p in projects[:3]])
        all_projects_cards = ''.join([ComponentRenderer.render_project_card(p) for p in projects])

        featured_post = posts[0] if posts else None
        featured_post_card = ComponentRenderer.render_post_card(featured_post, featured=True) if featured_post else ''
        latest_posts_cards = ''.join([ComponentRenderer.render_post_card(p) for p in posts[:2]])
        all_posts_cards = ''.join([ComponentRenderer.render_post_card(p) for p in posts])

        sidebar_items_cards = ''.join([ComponentRenderer.render_sidebar_item(p) for p in projects[:4]])
        merged_publications_cards = (
            (ComponentRenderer.render_post_card(posts[1], card_class="card-horizontal") if len(posts) > 1 else '') +
            (ComponentRenderer.render_project_card(projects[0]) if len(projects) > 0 else '') +
            ''.join([ComponentRenderer.render_post_card(p) for p in posts[2:]]) +
            ''.join([ComponentRenderer.render_project_card(p) for p in projects[1:]])
        )

        featured_services_cards = ''.join([ComponentRenderer.render_service_card(s) for s in services[:3]])
        all_services_cards = ''.join([ComponentRenderer.render_service_card(s) for s in services])
        all_team_cards = ''.join([ComponentRenderer.render_team_card(m) for m in team])

        compiled_pages_info: List[Dict[str, Any]] = []

        for pcfg in Config.PAGES_CONFIG:
            slug = pcfg['slug']
            src_dir = pcfg.get('dir', '')
            src_file = pcfg.get('file', '')

            src_path = None
            is_markdown = False

            if src_file:
                cand = os.path.join(self.root_dir, src_file)
                if os.path.exists(cand):
                    src_path = cand
                    is_markdown = cand.endswith('.md')
            elif src_dir:
                cand_html = os.path.join(self.root_dir, src_dir, 'index.html')
                cand_md = os.path.join(self.root_dir, src_dir, 'index.md')
                if os.path.exists(cand_html):
                    src_path = cand_html
                    is_markdown = False
                elif os.path.exists(cand_md):
                    src_path = cand_md
                    is_markdown = True

            if not src_path or not os.path.exists(src_path):
                continue

            meta, raw_body = ContentLoader.load_frontmatter_and_content(src_path)
            p_title = meta.get('title', pcfg.get('title', ''))
            p_desc = meta.get('description', '')
            header_img = meta.get('header_image', '')
            layout_type = meta.get('layout', 'default')

            # Convert body
            if is_markdown:
                body_html = MarkdownParser.to_html(raw_body)
            else:
                body_html = raw_body

            body_html = self.template_engine.render_includes(body_html)

            # Replace dynamic project & post loops
            body_html = re.sub(r'\{%\s*assign\s+featured_projects\s*=[\s\S]*?\{%\s*endfor\s*%\}', featured_projects_cards, body_html)
            body_html = re.sub(r'\{%\s*assign\s+sorted_projects\s*=[\s\S]*?\{%\s*endfor\s*%\}', all_projects_cards, body_html)
            body_html = re.sub(r'\{%\s*assign\s+featured_post\s*=[\s\S]*?\{%\s*include\s+post-card\.html[\s\S]*?\{%\s*endif\s*%\}', featured_post_card, body_html)
            body_html = re.sub(r'\{%\s*for\s+post\s+in\s+site\.posts\s+limit:2\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', latest_posts_cards, body_html)
            body_html = re.sub(r'\{%\s*assign\s+top_post\s*=[\s\S]*?\{%\s*endif\s*%\}', featured_post_card, body_html)
            body_html = re.sub(r'\{%\s*for\s+proj\s+in\s+site\.projects\s+limit:4\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', sidebar_items_cards, body_html)
            body_html = re.sub(r'\{%\s*for\s+post\s+in\s+site\.posts\s*%\}[\s\S]*?\{%\s*endfor\s*%\}[\s\S]*?\{%\s*for\s+proj\s+in\s+site\.projects\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', merged_publications_cards, body_html)
            body_html = re.sub(r'\{%\s*for\s+post\s+in\s+site\.posts\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', all_posts_cards, body_html)

            # Replace dynamic service & team loops
            body_html = re.sub(r'\{%\s*for\s+service\s+in\s+site\.data\.services\s+limit:3\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', featured_services_cards, body_html)
            body_html = re.sub(r'\{%\s*for\s+service\s+in\s+site\.data\.services\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', all_services_cards, body_html)
            body_html = re.sub(r'\{%\s*for\s+member\s+in\s+site\.data\.team\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', all_team_cards, body_html)

            # Layout Wrapping
            if layout_type == 'page':
                content_html = page_layout
                if header_img:
                    content_html = content_html.replace('{% if page.header_image %}page-header-hero{% endif %}', 'page-header-hero')
                    content_html = re.sub(r'\{%\s*if\s+page\.header_image\s*%\}style="background-image:\s*url\(\'\{\{\s*page\.header_image\s*\}\}\'\);"\s*\{%\s*endif\s*%\}', f'style="background-image: url(\'{header_img}\');"', content_html)
                else:
                    content_html = content_html.replace('{% if page.header_image %}page-header-hero{% endif %}', '')
                    content_html = re.sub(r'\{%\s*if\s+page\.header_image\s*%\}[\s\S]*?\{%\s*endif\s*%\}', '', content_html)

                content_html = content_html.replace('{{ page.title }}', p_title)
                if p_desc:
                    content_html = content_html.replace('{% if page.description %}', '').replace('{% endif %}', '').replace('{{ page.description }}', p_desc)
                else:
                    content_html = re.sub(r'\{% if page\.description %\}[\s\S]*?\{% endif %\}', '', content_html)

                if pcfg.get('type') == 'legal':
                    body_wrapped = f'<div class="page-body container">\n{body_html}\n</div>'
                else:
                    body_wrapped = body_html
                content_html = content_html.replace('{{ content }}', body_wrapped)
            else:
                content_html = body_html

            page_title_meta = f"{p_title} — {Config.SITE_NAME}" if p_title and slug != '' else (p_title or f"{Config.SITE_NAME} — {Config.SITE_TAGLINE}")
            page_meta = {
                'title': page_title_meta,
                'description': p_desc or Config.DEFAULT_DESCRIPTION,
                'header_image': header_img,
                'markdown_url': f"/{slug}.md" if slug and slug != '404' else '',
                'canonical_url': f"{Config.SITE_URL}/{slug}/" if slug and slug != '404' else f"{Config.SITE_URL}/"
            }

            final_html = def_layout.replace('{{ content }}', content_html)
            final_html = self.template_engine.clean_liquid_tags(final_html, page_meta, page_type='website', slug=slug)

            # Write Output HTML
            if slug == '':
                out_file = os.path.join(self.site_dir, 'index.html')
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(final_html)
                print("Built root page -> _site/index.html")
            elif slug == '404':
                out_file = os.path.join(self.site_dir, '404.html')
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(final_html)
                print("Built error page -> _site/404.html")
            else:
                out_dir = os.path.join(self.site_dir, slug)
                os.makedirs(out_dir, exist_ok=True)
                with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(final_html)
                with open(os.path.join(self.site_dir, f"{slug}.html"), 'w', encoding='utf-8') as f:
                    f.write(final_html)
                print(f"Built page -> _site/{slug}/index.html & _site/{slug}.html")

            # Write Raw Markdown Endpoints
            if slug and slug != '404':
                md_cand = os.path.join(self.root_dir, src_dir, 'index.md') if src_dir else ''
                if md_cand and os.path.exists(md_cand):
                    with open(md_cand, 'r', encoding='utf-8') as mf:
                        raw_md = mf.read()
                elif is_markdown:
                    with open(src_path, 'r', encoding='utf-8') as mf:
                        raw_md = mf.read()
                else:
                    clean_text = re.sub(r'<[^>]+>', '', raw_body).strip()
                    raw_md = f"---\ntitle: \"{p_title}\"\ndescription: \"{p_desc}\"\n---\n\n# {p_title}\n\n{p_desc}\n\n{clean_text}\n"

                out_dir = os.path.join(self.site_dir, slug)
                os.makedirs(out_dir, exist_ok=True)
                with open(os.path.join(out_dir, 'index.md'), 'w', encoding='utf-8') as f:
                    f.write(raw_md)
                with open(os.path.join(self.site_dir, f"{slug}.md"), 'w', encoding='utf-8') as f:
                    f.write(raw_md)

            compiled_pages_info.append({
                'slug': slug,
                'title': p_title,
                'desc': p_desc,
                'content_snippet': re.sub(r'<[^>]+>', '', body_html),
                'type': pcfg.get('type', 'page'),
                'priority': pcfg.get('priority', 0.8),
                'freq': pcfg.get('freq', 'monthly')
            })

        return compiled_pages_info

    def copy_static_root_files(self) -> None:
        """Copies static root files like robots.txt, CNAME, site.webmanifest to _site/."""
        for s_file in Config.STATIC_ROOT_FILES:
            s_src = os.path.join(self.root_dir, s_file)
            if os.path.exists(s_src):
                shutil.copy2(s_src, os.path.join(self.site_dir, s_file))
                print(f"Copied {s_file} -> _site/{s_file}")

    def build(self) -> None:
        """Runs the complete static site build pipeline."""
        # 1. Clean & Assets
        self.clean()
        self.copy_assets()

        # 2. Load Content Collections
        projects = ContentLoader.load_projects()
        posts = ContentLoader.load_posts()
        services = ContentLoader.load_services()
        team = ContentLoader.load_team()

        # 3. Build Project Pages
        self.build_projects(projects)

        # 4. Build Blog Post Pages
        self.build_posts(posts)

        # 5. Build Main Content Pages
        compiled_pages_info = self.build_pages(projects, posts, services, team)

        # 6. Search Indexing
        SearchIndexer.build_indexes(projects, posts, compiled_pages_info)

        # 7. Sitemap XML Generation
        page_models = [
            PageInfo(
                slug=p['slug'],
                title=p['title'],
                desc=p['desc'],
                type=p['type'],
                priority=p['priority'],
                freq=p['freq']
            ) for p in compiled_pages_info
        ]
        sitemap_xml = SitemapBuilder.build_sitemap(page_models, projects, posts)
        with open(os.path.join(self.site_dir, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        with open(os.path.join(self.root_dir, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        print("Built sitemap.xml -> _site/sitemap.xml & workspace root")

        # 8. AI / LLM Context Generation
        LLMGenerator.build_indexes(projects, posts, compiled_pages_info)

        # 9. Static Root Files
        self.copy_static_root_files()
