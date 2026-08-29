from typing import Union, Dict, Any, List
from .models import Project, Post, Service, TeamMember
from .utils import format_full_date
from .images import get_webp_url, get_image_dimensions

class ComponentRenderer:
    """Renders reusable HTML UI components including project cards, blog post cards, specs, and action buttons."""

    @staticmethod
    def render_project_card(proj: Union[Project, Dict[str, Any]], card_class: str = "") -> str:
        """Renders standard portfolio project card."""
        cat = proj.get('category', '')
        cat_badge_html = f'<span class="badge cat-badge">{cat}</span>' if cat else ''
        award_html = (
            '<div class="card-badge award-badge">'
            '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
            '<circle cx="12" cy="8" r="7"></circle>'
            '<polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>'
            '</svg><span>Award Winner</span></div>'
        ) if proj.get('award') else ''
        
        raw_img = proj.get('cover_image') or '/assets/images/image-not-found.svg'
        img = get_webp_url(raw_img)
        img_html = f'<img src="{img}" alt="{proj.get("title")} preview" loading="lazy" decoding="async" width="520" height="245" onerror="this.onerror=null; this.src=\'/assets/images/image-not-found.svg\';">'
        slug = proj.get('slug', '')
        url = f'/work/{slug}/'
        date_formatted = format_full_date(proj.get('date'))
        downloads_count = proj.get('downloads')
        downloads_html = (
            f'<span class="meta-downloads" title="{downloads_count} downloads">'
            '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>'
            '<polyline points="7 10 12 15 17 10"></polyline>'
            '<line x1="12" y1="15" x2="12" y2="3"></line>'
            f'</svg><span>{downloads_count}</span></span>'
        ) if downloads_count else ''
        
        class_attr = f"project-card {card_class}".strip()

        return f"""
    <article class="{class_attr}" data-category="{str(cat).lower()}">
      <div class="card-media">
        <div class="media-aspect">
          {img_html}
        </div>
        {award_html}
      </div>

      <div class="card-body">
        <h3 class="card-title">
          <a href="{url}">{proj.get('title', '')}</a>
        </h3>

        <div class="card-meta">
          {cat_badge_html}
          <time class="meta-date">{date_formatted}</time>
          {downloads_html}
        </div>

        <p class="card-desc">{proj.get('description', '')}</p>
      </div>

      <div class="card-footer">
        <a href="{url}" class="card-link" aria-label="View {proj.get('title', '')} project details">
          <span>View Project</span>
          <svg class="arrow-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </a>
      </div>
    </article>
    """

    @staticmethod
    def render_post_card(post: Union[Post, Dict[str, Any]], featured: bool = False, card_class: str = "") -> str:
        """Renders blog post / devlog card (grid or featured magazine layout)."""
        feat_class = 'post-card-featured' if featured else card_class
        raw_img = post.get('image') or '/assets/images/image-not-found.svg'
        img = get_webp_url(raw_img)
        img_html = f'<div class="post-card-media"><img src="{img}" alt="{post.get("title")}" loading="lazy" decoding="async" width="520" height="245" onerror="this.onerror=null; this.src=\'/assets/images/image-not-found.svg\';"></div>'
        slug = post.get('slug', '')
        url = f'/blog/{slug}/'
        author = post.get('author', 'RenderPhoenix')
        date_formatted = format_full_date(post.get('date'))
        cats = post.get('categories', [])
        cat_name = cats[0].capitalize() if (cats and isinstance(cats, list)) else 'Devlog'

        return f"""
    <article class="post-card {feat_class}">
      {img_html}
      <div class="post-card-content">
        <h3 class="post-card-title">
          <a href="{url}">{post.get('title', '')}</a>
        </h3>

        <div class="post-card-meta">
          <span class="badge cat-badge">{cat_name}</span>
          <time class="post-date">{date_formatted}</time>
        </div>

        <p class="post-card-desc">
          {post.get('description', '')}
        </p>

        <div class="post-card-footer">
          <span class="post-author">By {author}</span>
          <a href="{url}" class="read-more-link" aria-label="Read story {post.get('title', '')}">
            Read Story
            <svg class="arrow-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </a>
        </div>
      </div>
    </article>
    """

    @staticmethod
    def render_sidebar_item(proj: Union[Project, Dict[str, Any]]) -> str:
        """Renders compact sidebar magazine story item."""
        cat = proj.get('category', 'Project')
        if cat in ['Interactive', 'Environment']:
            cat = 'Project'
        url = f"/work/{proj.get('slug')}/"
        raw_img = proj.get('cover_image') or '/assets/images/image-not-found.svg'
        img = get_webp_url(raw_img)
        dims = get_image_dimensions(img) or (70, 70)
        img_html = f'<div class="magazine-sidebar-thumb" style="width: 70px; height: 70px; flex-shrink: 0; background: var(--color-bg-alt); overflow: hidden; border-radius: var(--radius-md);"><img src="{img}" alt="{proj.get("title")}" loading="lazy" decoding="async" width="{dims[0]}" height="{dims[1]}" style="width: 100%; height: 100%; object-fit: cover; object-position: center; border-radius: var(--radius-md);" onerror="this.onerror=null; this.src=\'/assets/images/image-not-found.svg\';"></div>'
        date_formatted = format_full_date(proj.get('date'))

        return f"""
    <article class="magazine-sidebar-item" style="display: flex; gap: 0.85rem; align-items: center;">
      {img_html}
      <div style="flex: 1; min-width: 0;">
        <h4 class="magazine-sidebar-title">
          <a href="{url}">{proj.get('title', '')}</a>
        </h4>
        <div class="magazine-sidebar-meta">
          <span class="badge cat-badge">{cat}</span>
          <time class="sidebar-date">{date_formatted}</time>
        </div>
      </div>
    </article>
    """

    @staticmethod
    def render_service_card(serv: Union[Service, Dict[str, Any]]) -> str:
        """Renders capabilities / service offering card."""
        caps = ''.join([f'<li>{c}</li>' for c in serv.get('capabilities', [])])
        return f"""
        <div class="service-card" id="{serv.get('slug', '')}">
          <div class="service-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
          </div>
          <h3 class="service-title">{serv.get('title', '')}</h3>
          <p style="font-size: 0.9rem; color: var(--color-text-secondary);">{serv.get('short_description', serv.get('description', ''))}</p>
          <h4 style="font-size: 0.9rem; margin-top: var(--space-md); margin-bottom: 0.4rem; color: var(--c-1-electric-violet);">Key Capabilities:</h4>
          <ul class="service-caps">{caps}</ul>
        </div>
        """

    @staticmethod
    def render_team_card(mem: Union[TeamMember, Dict[str, Any]]) -> str:
        """Renders studio team member roster card."""
        raw_avatar = mem.get('avatar', '')
        avatar_url = get_webp_url(raw_avatar) if raw_avatar else ''
        name = mem.get('name', '')
        if avatar_url:
            dims = get_image_dimensions(avatar_url) or (80, 80)
            avatar_html = f'<img src="{avatar_url}" alt="{name}" class="team-avatar-img" width="{dims[0]}" height="{dims[1]}" loading="lazy" decoding="async" />'
        else:
            initial = name[0] if name else 'R'
            avatar_html = initial
        return f"""
        <div class="team-card">
          <div class="team-avatar">{avatar_html}</div>
          <h3 class="team-name">{name}</h3>
          <div class="team-role">{mem.get('role', '')}</div>
          <p class="team-bio">{mem.get('bio', '')}</p>
        </div>
        """

    @staticmethod
    def render_project_specs(proj: Union[Project, Dict[str, Any]]) -> str:
        """Renders project specifications list (<dl><dt>...<dd>...) for sidebar."""
        items = []

        dev = proj.get('developer')
        if dev:
            items.append(f'<dt>Developer</dt>\n<dd>{dev}</dd>')

        cat = proj.get('category')
        if cat:
            items.append(f'<dt>Category</dt>\n<dd>{cat}</dd>')

        ver = proj.get('version')
        if ver:
            items.append(f'<dt>Version</dt>\n<dd>{ver}</dd>')

        platform = proj.get('platform')
        platforms = proj.get('platforms')
        if platform:
            items.append(f'<dt>Platform</dt>\n<dd>{platform}</dd>')
        elif platforms:
            plat_str = ', '.join(platforms) if isinstance(platforms, list) else str(platforms)
            items.append(f'<dt>Platform</dt>\n<dd>{plat_str}</dd>')

        date_val = proj.get('date')
        if date_val:
            date_formatted = format_full_date(date_val)
            items.append(f'<dt>Release Date</dt>\n<dd>{date_formatted}</dd>')

        license_val = proj.get('license')
        if license_val:
            items.append(f'<dt>License</dt>\n<dd>{license_val}</dd>')

        dl_count = proj.get('downloads')
        if dl_count:
            dl_html = f'''<dt>Downloads</dt>
<dd class="spec-downloads">
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
  <span>{dl_count}</span>
</dd>'''
            items.append(dl_html)

        return '\n'.join(items)

    @staticmethod
    def render_project_sidebar_actions(proj: Union[Project, Dict[str, Any]]) -> str:
        """Renders modular action buttons (Demo, Downloads, GitHub repo, Docs, MCPEDL)."""
        buttons = []

        # 1. Live Demo link
        demo_url = proj.get('demo_url') or proj.get('live_demo_url')
        if demo_url:
            demo_label = proj.get('demo_label', 'Launch Live Demo')
            buttons.append(f'''<a href="{demo_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-block">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
  <span>{demo_label}</span>
</a>''')

        # 2. Modular Download Links
        dl_links = proj.get('download_links')
        if dl_links and isinstance(dl_links, list):
            for idx, dl in enumerate(dl_links):
                if isinstance(dl, dict):
                    url = dl.get('url', '')
                    label = dl.get('label') or f'Download #{idx+1}'
                    is_primary = dl.get('primary', idx == 0 and not demo_url)
                else:
                    url = str(dl)
                    label = f'Download #{idx+1}'
                    is_primary = idx == 0 and not demo_url

                btn_class = 'btn btn-primary btn-block' if is_primary else 'btn btn-secondary btn-block'
                buttons.append(f'''<a href="{url}" target="_blank" rel="noopener noreferrer" class="{btn_class}">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
  <span>{label}</span>
</a>''')
        elif proj.get('download_url'):
            dl_url = proj.get('download_url')
            dl_label = proj.get('download_label', 'Download Project')
            btn_class = 'btn btn-primary btn-block' if not demo_url else 'btn btn-secondary btn-block'
            buttons.append(f'''<a href="{dl_url}" target="_blank" rel="noopener noreferrer" class="{btn_class}">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
  <span>{dl_label}</span>
</a>''')
        elif proj.get('mcpedl_url'):
            mc_url = proj.get('mcpedl_url')
            btn_class = 'btn btn-primary btn-block' if not demo_url else 'btn btn-secondary btn-block'
            buttons.append(f'''<a href="{mc_url}" target="_blank" rel="noopener noreferrer" class="{btn_class}">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
  <span>View on MCPEDL</span>
</a>''')

        # 3. GitHub repository link
        gh_url = proj.get('github_url') or proj.get('github') or proj.get('repo_url')
        if gh_url:
            gh_label = proj.get('github_label', 'View on GitHub')
            buttons.append(f'''<a href="{gh_url}" target="_blank" rel="noopener noreferrer" class="btn btn-github btn-block">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
  <span>{gh_label}</span>
</a>''')

        # 4. Docs link
        docs_url = proj.get('docs_url')
        if docs_url:
            docs_label = proj.get('docs_label', 'Documentation')
            buttons.append(f'''<a href="{docs_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-block">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
  <span>{docs_label}</span>
</a>''')

        if not buttons:
            return ''

        return '<div class="sidebar-actions">\n' + '\n'.join(buttons) + '\n</div>'
