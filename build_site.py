import os
import shutil
import re
import yaml
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(ROOT_DIR, '_site')

def extract_youtube_id(url_or_id):
    if not url_or_id:
        return ''
    url_or_id = url_or_id.strip()
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    match = re.search(r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})', url_or_id)
    if match:
        return match.group(1)
    return ''

def render_youtube_player(url_or_id, caption=""):
    yt_id = extract_youtube_id(url_or_id)
    if not yt_id:
        return ''
    embed_url = f"https://www.youtube-nocookie.com/embed/{yt_id}"
    caption_html = f'<figcaption class="video-caption">{caption}</figcaption>' if caption else ''
    title_attr = caption if caption else 'YouTube video player'
    return f"""<figure class="video-figure">
  <div class="video-responsive-wrapper">
    <iframe src="{embed_url}" title="{title_attr}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>
  </div>
  {caption_html}
</figure>"""

def get_youtube_embed_url(url):
    yt_id = extract_youtube_id(url)
    if yt_id:
        return f"https://www.youtube-nocookie.com/embed/{yt_id}"
    return url

def simple_markdown_to_html(md_text):
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    in_list = False

    for line in lines:
        stripped = line.strip()
        
        # Code block toggle
        if stripped.startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                lang = stripped[3:].strip()
                html_lines.append(f'<pre><code class="language-{lang}">' if lang else '<pre><code>')
                in_code_block = True
            continue
        
        if in_code_block:
            # Escape HTML inside code block
            line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_lines.append(line_escaped)
            continue

        # Close list if line is not bullet
        if in_list and not stripped.startswith('- ') and not stripped.startswith('* '):
            html_lines.append('</ul>')
            in_list = False

        if not stripped:
            continue

        # Check for YouTube embeds:
        # Format 1: ![youtube](url) or ![youtube:Caption](url) or ![video](url)
        yt_md_match = re.match(r'^!\[(?:youtube|video)(?::\s*(.*?))?\]\((.*?)\)$', stripped, re.IGNORECASE)
        if yt_md_match:
            caption = (yt_md_match.group(1) or '').strip()
            url = yt_md_match.group(2).strip()
            html_lines.append(render_youtube_player(url, caption))
            continue

        # Format 2: {% youtube URL_OR_ID [optional caption] %}
        yt_tag_match = re.match(r'^\{%\s*youtube\s+([^\s%]+)(?:\s+(.*?))?\s*%\}$', stripped, re.IGNORECASE)
        if yt_tag_match:
            url_or_id = yt_tag_match.group(1).strip()
            caption = (yt_tag_match.group(2) or '').strip().strip('"\'')
            html_lines.append(render_youtube_player(url_or_id, caption))
            continue

        # Format 3: Standalone YouTube URL on its own line: https://www.youtube.com/watch?v=... or https://youtu.be/...
        if re.match(r'^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}(?:[^\s]*)?$', stripped):
            html_lines.append(render_youtube_player(stripped))
            continue

        # Headings
        if stripped.startswith('### '):
            html_lines.append(f'<h3>{inline_format(stripped[4:])}</h3>')
        elif stripped.startswith('## '):
            html_lines.append(f'<h2>{inline_format(stripped[3:])}</h2>')
        elif stripped.startswith('# '):
            html_lines.append(f'<h1>{inline_format(stripped[2:])}</h1>')
        elif stripped.startswith('> '):
            html_lines.append(f'<blockquote><p>{inline_format(stripped[2:])}</p></blockquote>')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{inline_format(stripped[2:])}</li>')
        elif stripped.startswith('<div') or stripped.startswith('</div') or stripped.startswith('<iframe') or stripped.startswith('<section') or stripped.startswith('</section'):
            html_lines.append(stripped)
        else:
            html_lines.append(f'<p>{inline_format(stripped)}</p>')

    if in_list:
        html_lines.append('</ul>')
    if in_code_block:
        html_lines.append('</code></pre>')

    return '\n'.join(html_lines)

def inline_format(text):
    # Images
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" class="content-img" loading="lazy" />', text)
    # Bold & Italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    return text

def load_frontmatter_and_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2]
            meta['raw_content'] = content
            return meta, body
    return {'raw_content': content}, content

def render_includes(html_str):
    def replace_include(match):
        inc_file = match.group(1).strip()
        inc_path = os.path.join(ROOT_DIR, '_includes', inc_file)
        if os.path.exists(inc_path):
            with open(inc_path, 'r', encoding='utf-8') as f:
                return render_includes(f.read())
        return ''
    return re.sub(r'\{%\s*include\s+([\w\.\-]+)\s*%\}', replace_include, html_str)

def clean_liquid_tags(text, meta=None):
    if meta is None:
        meta = {}
    
    header_nav_html = """
      <li class="nav-item"><a href="/" class="nav-link">Home</a></li>
      <li class="nav-item"><a href="/about/" class="nav-link">About</a></li>
      <li class="nav-item"><a href="/services/" class="nav-link">Services</a></li>
      <li class="nav-item"><a href="/work/" class="nav-link">Work</a></li>
      <li class="nav-item"><a href="/blog/" class="nav-link">Blog</a></li>
      <li class="nav-item"><a href="/contact/" class="nav-link">Contact</a></li>
    """
    text = re.sub(r'\{%\s*for\s+item\s+in\s+site\.data\.navigation\.header\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', header_nav_html, text)

    footer_nav_html = """
      <li><a href="/">Home</a></li>
      <li><a href="/about/">About</a></li>
      <li><a href="/services/">Services</a></li>
      <li><a href="/work/">Work Portfolio</a></li>
      <li><a href="/blog/">Editorial & Devlogs</a></li>
      <li><a href="/contact/">Contact Us</a></li>
    """
    text = re.sub(r'\{%\s*for\s+link\s+in\s+site\.data\.navigation\.footer\.navigation\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', footer_nav_html, text)

    footer_res_html = """
      <li><a href="https://mcpedl.com/user/renderphoenix/" target="_blank" rel="noopener noreferrer">MCPEDL Official Profile</a></li>
      <li><a href="/llm.txt">llm.txt (AI Metadata)</a></li>
      <li><a href="/llms-full.txt">llms-full.txt (Full AI Corpus)</a></li>
      <li><a href="/sitemap.xml">Sitemap XML</a></li>
    """
    text = re.sub(r'\{%\s*for\s+link\s+in\s+site\.data\.navigation\.footer\.resources\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', footer_res_html, text)

    full_title = meta.get('title', 'RenderPhoenix — Independent Interactive Creative Studio')
    text = text.replace('{{ full_title }}', full_title)
    text = text.replace('{{ page_desc }}', meta.get('description', 'RenderPhoenix is an independent interactive creative studio.'))
    text = text.replace('{{ canonical_url }}', '')
    text = text.replace('{{ og_image }}', '/assets/images/og-default.svg')
    text = text.replace('{{ site.title }}', 'RenderPhoenix')
    text = text.replace('{{ site.description }}', 'RenderPhoenix is an independent interactive creative studio.')
    text = text.replace('{{ site.url }}', '')

    markdown_url = meta.get('markdown_url', '')
    if markdown_url:
        text = text.replace('{{ markdown_alternate_link }}', f'<link rel="alternate" type="text/markdown" href="{markdown_url}" title="{full_title} Markdown">')
    else:
        text = text.replace('{{ markdown_alternate_link }}', '')

    text = re.sub(r"\{\{\s*'([^']+)'\s*\|\s*relative_url\s*\}\}", r"\1", text)
    text = re.sub(r'\{\{\s*"([^"]+)"\s*\|\s*relative_url\s*\}\}', r"\1", text)

    text = re.sub(r'\{%[\s\S]*?%\}', '', text)
    text = re.sub(r'\{\{[\s\S]*?\}\}', '', text)

    return text

def format_full_date(date_val):
    if not date_val:
        return ''
    if isinstance(date_val, datetime):
        return date_val.strftime('%d %b %Y')
    if hasattr(date_val, 'strftime'):
        return date_val.strftime('%d %b %Y')
    date_str = str(date_val).strip()
    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S %z']:
        try:
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            return dt.strftime('%d %b %Y')
        except Exception:
            pass
    return date_str

def render_project_card(proj, card_class=""):
    cat = proj.get('category', '')
    cat_badge_html = f'<span class="badge cat-badge">{cat}</span>' if cat else ''
    award_html = f'<div class="card-badge award-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg><span>Award Winner</span></div>' if proj.get('award') else ''
    img = proj.get('cover_image') or '/assets/images/image-not-found.svg'
    img_html = f'<img src="{img}" alt="{proj.get("title")} preview" loading="lazy" width="520" height="245" onerror="this.onerror=null; this.src=\'/assets/images/image-not-found.svg\';">'
    slug = proj.get('slug', '')
    url = f'/work/{slug}/'
    date_formatted = format_full_date(proj.get('date'))
    downloads_count = proj.get('downloads')
    downloads_html = f'<span class="meta-downloads" title="{downloads_count} downloads"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg><span>{downloads_count}</span></span>' if downloads_count else ''

    return f"""
    <article class="project-card {card_class}" data-category="{cat.lower()}">
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

def render_post_card(post, featured=False, card_class=""):
    feat_class = 'post-card-featured' if featured else card_class
    img = post.get('image') or '/assets/images/image-not-found.svg'
    img_html = f'<div class="post-card-media"><img src="{img}" alt="{post.get("title")}" loading="lazy" width="600" height="340" onerror="this.onerror=null; this.src=\'/assets/images/image-not-found.svg\';"></div>'
    slug = post.get('slug', '')
    url = f'/blog/{slug}/'
    author = post.get('author', 'RenderPhoenix')
    date_formatted = format_full_date(post.get('date'))
    cats = post.get('categories', [])
    cat_name = cats[0].capitalize() if cats else 'Devlog'

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

def render_sidebar_item(proj):
    cat = proj.get('category', 'Project')
    if cat in ['Interactive', 'Environment']:
        cat = 'Project'
    url = f"/work/{proj['slug']}/"
    img = proj.get('cover_image') or '/assets/images/image-not-found.svg'
    img_html = f'<div class="magazine-sidebar-thumb" style="width: 70px; height: 70px; flex-shrink: 0; background: var(--color-bg-alt); overflow: hidden; border-radius: var(--radius-md);"><img src="{img}" alt="{proj.get("title")}" loading="lazy" style="width: 100%; height: 100%; object-fit: cover; object-position: center; border-radius: var(--radius-md);" onerror="this.onerror=null; this.src=\'/assets/images/image-not-found.svg\';"></div>'
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

def clean_conditional(text, condition_name, is_truthy, replace_dict=None):
    pattern = re.compile(rf'\{{%\s*if\s+{re.escape(condition_name)}\s*%\}}([\s\S]*?)\{{%\s*endif\s*%\}}')
    if is_truthy:
        def keep_content(m):
            content = m.group(1)
            if replace_dict:
                for k, v in replace_dict.items():
                    content = content.replace(k, str(v))
            return content
        return pattern.sub(keep_content, text)
    else:
        return pattern.sub('', text)

def render_project_specs(proj):
    items = []
    
    # Developer
    dev = proj.get('developer')
    if dev:
        items.append(f'<dt>Developer</dt>\n<dd>{dev}</dd>')
        
    # Category
    cat = proj.get('category')
    if cat:
        items.append(f'<dt>Category</dt>\n<dd>{cat}</dd>')
        
    # Version
    ver = proj.get('version')
    if ver:
        items.append(f'<dt>Version</dt>\n<dd>{ver}</dd>')
        
    # Platform / Platforms
    platform = proj.get('platform')
    platforms = proj.get('platforms')
    if platform:
        items.append(f'<dt>Platform</dt>\n<dd>{platform}</dd>')
    elif platforms:
        plat_str = ', '.join(platforms) if isinstance(platforms, list) else str(platforms)
        items.append(f'<dt>Platform</dt>\n<dd>{plat_str}</dd>')
        
    # Release Date
    date_val = proj.get('date')
    if date_val:
        date_formatted = format_full_date(date_val)
        items.append(f'<dt>Release Date</dt>\n<dd>{date_formatted}</dd>')
        
    # License
    license_val = proj.get('license')
    if license_val:
        items.append(f'<dt>License</dt>\n<dd>{license_val}</dd>')
        
    # Downloads count
    dl_count = proj.get('downloads')
    if dl_count:
        dl_html = f'''<dt>Downloads</dt>
<dd class="spec-downloads">
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
  <span>{dl_count}</span>
</dd>'''
        items.append(dl_html)
        
    return '\n'.join(items)

def render_project_sidebar_actions(proj):
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
        # Fallback for mcpedl_url if no other download links specified
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
        
    return f'<div class="sidebar-actions">\n' + '\n'.join(buttons) + '\n</div>'

def build():
    # 0. Clean previous build directory completely
    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR, ignore_errors=True)
        print("Cleaned old _site directory")

    # 1. Copy assets
    os.makedirs(SITE_DIR, exist_ok=True)
    if os.path.exists(os.path.join(ROOT_DIR, 'assets')):
        dest_assets = os.path.join(SITE_DIR, 'assets')
        if os.path.exists(dest_assets):
            shutil.rmtree(dest_assets)
        shutil.copytree(os.path.join(ROOT_DIR, 'assets'), dest_assets)
        print("Copied assets to _site/assets")

        # Mirror brand directory to _site/images/brand for direct URL access (/images/brand/)
        brand_src = os.path.join(ROOT_DIR, 'assets', 'images', 'brand')
        if os.path.exists(brand_src):
            images_brand_dest = os.path.join(SITE_DIR, 'images', 'brand')
            os.makedirs(os.path.dirname(images_brand_dest), exist_ok=True)
            if os.path.exists(images_brand_dest):
                shutil.rmtree(images_brand_dest)
            shutil.copytree(brand_src, images_brand_dest)
            print("Mirrored brand assets -> _site/images/brand/")

    # Read layout files
    _, def_layout_body = load_frontmatter_and_content(os.path.join(ROOT_DIR, '_layouts', 'default.html'))
    def_layout_html = render_includes(def_layout_body)

    _, page_layout_body = load_frontmatter_and_content(os.path.join(ROOT_DIR, '_layouts', 'page.html'))
    page_layout_body = render_includes(page_layout_body)

    _, proj_layout_body = load_frontmatter_and_content(os.path.join(ROOT_DIR, '_layouts', 'project.html'))
    proj_layout_body = render_includes(proj_layout_body)

    _, post_layout_body = load_frontmatter_and_content(os.path.join(ROOT_DIR, '_layouts', 'post.html'))
    post_layout_body = render_includes(post_layout_body)

    # 2. Load Projects
    projects = []
    proj_dir = os.path.join(ROOT_DIR, '_projects')
    if os.path.exists(proj_dir):
        for fname in os.listdir(proj_dir):
            if fname.endswith('.md'):
                fpath = os.path.join(proj_dir, fname)
                meta, body = load_frontmatter_and_content(fpath)
                slug = meta.get('slug', fname.replace('.md', ''))
                meta['slug'] = slug
                meta['body'] = body
                projects.append(meta)
    projects.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    # 3. Load Posts
    posts = []
    post_dir = os.path.join(ROOT_DIR, '_posts')
    if os.path.exists(post_dir):
        for fname in os.listdir(post_dir):
            if fname.endswith('.md'):
                fpath = os.path.join(post_dir, fname)
                meta, body = load_frontmatter_and_content(fpath)
                slug = fname[11:].replace('.md', '') if len(fname) > 11 and fname[10] == '-' else fname.replace('.md', '')
                meta['slug'] = slug
                meta['body'] = body
                posts.append(meta)
    posts.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    # Build Project detail pages & raw Markdown endpoints
    for proj in projects:
        slug = proj['slug']
        proj['markdown_url'] = f"/work/{slug}.md"
        p_html_body = simple_markdown_to_html(proj['body'])
        
        # Build layout
        p_content = proj_layout_body.replace('{{ content }}', p_html_body)
        p_content = p_content.replace('{{ page.title }}', proj.get('title', ''))
        p_content = p_content.replace('{{ page.description }}', proj.get('description', ''))
        p_content = p_content.replace('{{ page.category }}', proj.get('category', ''))
        proj_date_formatted = format_full_date(proj.get('date'))
        p_content = p_content.replace('{{ page.date | date: "%d %b %Y" }}', proj_date_formatted)
        p_content = p_content.replace('{{ page.date }}', proj_date_formatted)
        p_content = p_content.replace('{{ page.year }}', proj_date_formatted)
        
        p_content = clean_conditional(p_content, 'page.downloads', bool(proj.get('downloads')), {'{{ page.downloads }}': str(proj.get('downloads', ''))})
        p_content = clean_conditional(p_content, 'page.description', bool(proj.get('description')), {'{{ page.description }}': proj.get('description', '')})
        p_content = clean_conditional(p_content, 'page.award', bool(proj.get('award')), {'{{ page.award }}': proj.get('award', '')})
        p_content = clean_conditional(p_content, 'page.developer', bool(proj.get('developer')), {'{{ page.developer }}': proj.get('developer', '')})
        
        # Render dynamic specs and sidebar action buttons
        specs_html = render_project_specs(proj)
        actions_html = render_project_sidebar_actions(proj)
        p_content = p_content.replace('{{ project_specs }}', specs_html)
        p_content = p_content.replace('{{ project_sidebar_actions }}', actions_html)
        
        yt_url = proj.get('youtube_url', '')
        yt_embed = get_youtube_embed_url(yt_url)
        yt_author = proj.get('youtube_author', '')
        
        p_content = p_content.replace('{{ page.youtube_url }}', yt_url)
        p_content = p_content.replace('{{ page.youtube_embed_url }}', yt_embed)
        p_content = p_content.replace('{{ page.youtube_author }}', yt_author)
        
        p_content = clean_conditional(p_content, 'page.youtube_author', bool(yt_author))
        p_content = clean_conditional(p_content, 'page.youtube_url', bool(yt_url))
        
        cover_img = proj.get('cover_image', '/assets/images/image-not-found.svg')
        p_content = re.sub(r'\{%\s*assign\s+cover_img\s*=[\s\S]*?%\}', '', p_content)
        p_content = p_content.replace('{{ cover_img | relative_url }}', cover_img)
        p_content = p_content.replace('{{ page.cover_image | relative_url }}', cover_img)

        full_html = def_layout_html.replace('{{ content }}', p_content)
        full_html = clean_liquid_tags(full_html, proj)

        out_dir = os.path.join(SITE_DIR, 'work', slug)
        os.makedirs(out_dir, exist_ok=True)
        
        # 1. Output HTML
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(full_html)
            
        # 2. Output raw Markdown in same directory and at /work/<slug>.md
        raw_md = proj.get('raw_content', '')
        with open(os.path.join(out_dir, 'index.md'), 'w', encoding='utf-8') as f:
            f.write(raw_md)
        with open(os.path.join(SITE_DIR, 'work', f"{slug}.md"), 'w', encoding='utf-8') as f:
            f.write(raw_md)
            
        print(f"Built project page -> _site/work/{slug}/ (index.html, index.md, {slug}.md)")

    # Build Blog detail pages & raw Markdown endpoints
    for post in posts:
        slug = post['slug']
        post['markdown_url'] = f"/blog/{slug}.md"
        p_html_body = simple_markdown_to_html(post['body'])
        
        p_content = post_layout_body.replace('{{ content }}', p_html_body)
        p_content = p_content.replace('{{ page.title }}', post.get('title', ''))
        p_content = p_content.replace('{{ page.description }}', post.get('description', ''))
        p_content = p_content.replace('{{ page.author | default: site.author.name }}', post.get('author', 'RenderPhoenix'))
        post_date_formatted = format_full_date(post.get('date'))
        p_content = p_content.replace('{{ page.date | date: "%d %b %Y" }}', post_date_formatted)
        p_content = p_content.replace('{{ page.date | date: "%B %d, %Y" }}', post_date_formatted)
        p_content = p_content.replace('{{ page.date }}', post_date_formatted)
        p_content = re.sub(r'\{%\s*if\s+page\.categories\s*%\}.*?\{%\s*endif\s*%\}', 'Devlog', p_content)

        if post.get('image'):
            p_content = p_content.replace('{% if page.image %}', '').replace('{% endif %}', '').replace('{{ page.image | relative_url }}', post['image'])

        full_html = def_layout_html.replace('{{ content }}', p_content)
        full_html = clean_liquid_tags(full_html, post)

        out_dir = os.path.join(SITE_DIR, 'blog', slug)
        os.makedirs(out_dir, exist_ok=True)
        
        # 1. Output HTML
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(full_html)
            
        # 2. Output raw Markdown in same directory and at /blog/<slug>.md
        raw_md = post.get('raw_content', '')
        with open(os.path.join(out_dir, 'index.md'), 'w', encoding='utf-8') as f:
            f.write(raw_md)
        with open(os.path.join(SITE_DIR, 'blog', f"{slug}.md"), 'w', encoding='utf-8') as f:
            f.write(raw_md)
            
        print(f"Built post page -> _site/blog/{slug}/ (index.html, index.md, {slug}.md)")

    # 4. Load Services
    services = []
    serv_file = os.path.join(ROOT_DIR, '_data', 'services.yml')
    if os.path.exists(serv_file):
        with open(serv_file, 'r', encoding='utf-8') as f:
            services = yaml.safe_load(f) or []

    # 5. Load Team
    team = []
    team_file = os.path.join(ROOT_DIR, '_data', 'team.yml')
    if os.path.exists(team_file):
        with open(team_file, 'r', encoding='utf-8') as f:
            team = yaml.safe_load(f) or []

    def render_service_card(serv):
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

    def render_team_card(mem):
        avatar_url = mem.get('avatar', '')
        name = mem.get('name', '')
        if avatar_url:
            avatar_html = f'<img src="{avatar_url}" alt="{name}" class="team-avatar-img" width="80" height="80" loading="lazy" />'
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

    featured_services_cards = ''.join([render_service_card(s) for s in services[:3]])
    all_services_cards = ''.join([render_service_card(s) for s in services])
    all_team_cards = ''.join([render_team_card(m) for m in team])

    # Build static pages with rendered card grids
    pages = ['index.html', 'about/index.html', 'services/index.html', 'work/index.html', 'blog/index.html', 'contact/index.html', '404.html']

    featured_projects_cards = ''.join([render_project_card(p) for p in projects[:3]])
    all_projects_cards = ''.join([render_project_card(p) for p in projects])

    featured_post = posts[0] if posts else {}
    featured_post_card = render_post_card(featured_post, featured=True) if featured_post else ''
    latest_posts_cards = ''.join([render_post_card(p) for p in posts[:2]])
    all_posts_cards = ''.join([render_post_card(p) for p in posts])

    sidebar_items_cards = ''.join([render_sidebar_item(p) for p in projects[:4]])
    merged_publications_cards = (
        (render_post_card(posts[1], card_class="card-horizontal") if len(posts) > 1 else '') +
        (render_project_card(projects[0], card_class="card-wide") if len(projects) > 0 else '') +
        ''.join([render_post_card(p) for p in posts[2:]]) +
        ''.join([render_project_card(p) for p in projects[1:]])
    )

    for p in pages:
        src_path = os.path.join(ROOT_DIR, p)
        if not os.path.exists(src_path):
            continue
        
        meta, body = load_frontmatter_and_content(src_path)
        body = render_includes(body)

        # Replace project card loops
        body = re.sub(r'\{%\s*assign\s+featured_projects\s*=[\s\S]*?\{%\s*endfor\s*%\}', featured_projects_cards, body)
        body = re.sub(r'\{%\s*assign\s+sorted_projects\s*=[\s\S]*?\{%\s*endfor\s*%\}', all_projects_cards, body)

        # Replace post card loops
        body = re.sub(r'\{%\s*assign\s+featured_post\s*=[\s\S]*?\{%\s*include\s+post-card\.html[\s\S]*?\{%\s*endif\s*%\}', featured_post_card, body)
        body = re.sub(r'\{%\s*for\s+post\s+in\s+site\.posts\s+limit:2\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', latest_posts_cards, body)
        body = re.sub(r'\{%\s*assign\s+top_post\s*=[\s\S]*?\{%\s*endif\s*%\}', featured_post_card, body)
        body = re.sub(r'\{%\s*for\s+proj\s+in\s+site\.projects\s+limit:4\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', sidebar_items_cards, body)
        body = re.sub(r'\{%\s*for\s+post\s+in\s+site\.posts\s*%\}[\s\S]*?\{%\s*endfor\s*%\}[\s\S]*?\{%\s*for\s+proj\s+in\s+site\.projects\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', merged_publications_cards, body)
        body = re.sub(r'\{%\s*for\s+post\s+in\s+site\.posts\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', all_posts_cards, body)
        
        # Replace services and team loops
        body = re.sub(r'\{%\s*for\s+service\s+in\s+site\.data\.services\s+limit:3\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', featured_services_cards, body)
        body = re.sub(r'\{%\s*for\s+service\s+in\s+site\.data\.services\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', all_services_cards, body)
        body = re.sub(r'\{%\s*for\s+member\s+in\s+site\.data\.team\s*%\}[\s\S]*?\{%\s*endfor\s*%\}', all_team_cards, body)
        
        layout_type = meta.get('layout', 'default')
        if layout_type == 'page':
            p_title = meta.get('title', '')
            p_desc = meta.get('description', '')
            header_img = meta.get('header_image', '')

            content_html = page_layout_body
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
            content_html = content_html.replace('{{ content }}', body)
        else:
            content_html = body

        final_html = def_layout_html.replace('{{ content }}', content_html)
        final_html = clean_liquid_tags(final_html, meta)

        out_path = os.path.join(SITE_DIR, p)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"Built main page -> _site/{p}")

    # Build search.json
    import json
    search_data = []
    for post in posts:
        search_data.append({
            "title": post.get('title', ''),
            "url": f"/blog/{post['slug']}/",
            "description": post.get('description', ''),
            "content": re.sub(r'<[^>]+>', '', post.get('body', ''))[:300],
            "type": "Article",
            "category": "Blog",
            "date": format_full_date(post.get('date')),
            "tags": post.get('tags', [])
        })
    for proj in projects:
        search_data.append({
            "title": proj.get('title', ''),
            "url": f"/work/{proj['slug']}/",
            "description": proj.get('description', ''),
            "content": re.sub(r'<[^>]+>', '', proj.get('body', ''))[:300],
            "type": "Project",
            "category": proj.get('category', ''),
            "date": format_full_date(proj.get('date')),
            "tags": proj.get('tags', [])
        })

    with open(os.path.join(SITE_DIR, 'search.json'), 'w', encoding='utf-8') as f:
        json.dump(search_data, f, indent=2)
    print("Built search.json -> _site/search.json")

    search_js_dir = os.path.join(SITE_DIR, 'assets', 'js')
    os.makedirs(search_js_dir, exist_ok=True)
    with open(os.path.join(search_js_dir, 'search-data.js'), 'w', encoding='utf-8') as f:
        f.write("window.SEARCH_INDEX = " + json.dumps(search_data, indent=2) + ";\n")
    print("Built search-data.js -> _site/assets/js/search-data.js")

    # Build sitemap.xml with Google Image Extension
    site_url = 'https://renderphoenix.com'
    
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

    sitemap_entries = [
        f"""  <url>
    <loc>{site_url}/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
{brand_images_xml}
  </url>""",
        f"""  <url>
    <loc>{site_url}/about/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
    <image:image>
      <image:loc>{site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.png</image:loc>
      <image:title>RenderPhoenix Studio Logo</image:title>
    </image:image>
  </url>""",
        f"""  <url>
    <loc>{site_url}/services/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""",
        f"""  <url>
    <loc>{site_url}/work/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""",
        f"""  <url>
    <loc>{site_url}/blog/</loc>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>""",
        f"""  <url>
    <loc>{site_url}/contact/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""",
        f"""  <url>
    <loc>{site_url}/images/brand/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
{brand_images_xml}
  </url>"""
    ]

    for post in posts:
        post_slug = post['slug']
        post_img = post.get('image', '')
        img_xml = ""
        if post_img:
            img_xml = f"""
    <image:image>
      <image:loc>{site_url}{post_img}</image:loc>
      <image:title>{post.get('title', '')}</image:title>
    </image:image>"""
        sitemap_entries.append(f"""  <url>
    <loc>{site_url}/blog/{post_slug}/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>{img_xml}
  </url>""")

    for proj in projects:
        proj_slug = proj['slug']
        proj_img = proj.get('cover_image', '')
        img_xml = ""
        if proj_img and not proj_img.endswith('image-not-found.svg'):
            img_xml = f"""
    <image:image>
      <image:loc>{site_url}{proj_img}</image:loc>
      <image:title>{proj.get('title', '')}</image:title>
    </image:image>"""
        sitemap_entries.append(f"""  <url>
    <loc>{site_url}/work/{proj_slug}/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>{img_xml}
  </url>""")

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + '\n'.join(sitemap_entries) + '\n</urlset>\n'
    with open(os.path.join(SITE_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)
    with open(os.path.join(ROOT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)
    print("Built sitemap.xml -> _site/sitemap.xml & workspace root")

    # Build automated AI context files (llm.txt, llms.txt, and llms-full.txt)
    build_llm_indexes(projects, posts)

    # Copy root static files (robots.txt, CNAME, site.webmanifest, etc.)
    static_root_files = ['robots.txt', 'CNAME', 'site.webmanifest']
    for s_file in static_root_files:
        s_src = os.path.join(ROOT_DIR, s_file)
        if os.path.exists(s_src):
            shutil.copy2(s_src, os.path.join(SITE_DIR, s_file))
            print(f"Copied {s_file} -> _site/{s_file}")

def build_llm_indexes(projects, posts):
    site_url = 'https://renderphoenix.com'
    
    # 1. Standard llm.txt & llms.txt index
    llm_content = f"""# RenderPhoenix — Comprehensive Studio Context & Documentation

This document provides a complete, machine-readable overview of RenderPhoenix for large language models (LLMs), AI assistants, search crawlers, and automated indexers.

## 1. Studio Identity & Core Philosophy
RenderPhoenix is an independent interactive creative studio based in Bangladesh. The studio works across:
- Standalone Game Development (Unreal Engine 5, Unity, C#, C++)
- 3D World Design & Level Architecture (Blender, Substance Painter)
- Real-Time Game Assets & Vehicle Add-Ons
- Technical Art, Shaders (HLSL/GLSL), and VFX
- Digital Experiences & Scientific Interactive Simulations

Studio Tagline: "We are not just a company that makes digital things. We build worlds."

## 2. Detailed History & Milestones
- 2019: Founded by Tasrif Ibn Mizan under the initial studio name Minehutt. Focused on community creation, custom maps, and level design.
- January 30, 2021: Official re-branding to RenderPhoenix to establish a broader visual identity in real-time art and 3D modeling.
- 1 August 2022: Experienced a severe security incident where core social accounts and communication channels were compromised. Despite this, the studio demonstrated resilience by continuing operations and publishing content through 2024.
- 2024: Operations paused as the original team members dispersed into university studies and software careers.
- 2025: Team members competed in the NASA Space Apps Challenge 2025, creating a lunar settlement simulator and earning Regional Runner-Up.
- 22 August 2026: Official studio revival initiated by Cristo Parker to rebuild digital infrastructure, reassemble team capabilities, and expand into original games and 3D asset production.

## 3. Team Roster
- Tasrif Ibn Mizan: Founder. Established Minehutt in 2019 and RenderPhoenix in 2021.
- Cristo Parker: Manager. Spearheaded the 22 August 2026 revival and digital infrastructure rebuild.
- Uthowaipru Chowdhury: Indie Game Developer. Specializes in gameplay systems and mechanics.
- Faizul726: App Developer. Specializes in application software and client tooling.

## 4. Notable Works & Project Index (Raw Markdown)
"""
    for proj in projects:
        title = proj.get('title', '')
        slug = proj.get('slug', '')
        desc = proj.get('description', '')
        date = proj.get('date', '')
        year = str(date)[:4] if date else ''
        year_str = f" ({year})" if year else ''
        cat = proj.get('category', '')
        cat_str = f" [{cat}]" if cat else ''
        llm_content += f"- [{title}]({site_url}/work/{slug}.md){year_str}{cat_str}: {desc}\n"

    llm_content += "\n## 5. Editorial & Studio Devlogs (Raw Markdown)\n"
    for post in posts:
        title = post.get('title', '')
        slug = post.get('slug', '')
        desc = post.get('description', '')
        date_str = format_full_date(post.get('date'))
        date_badge = f" ({date_str})" if date_str else ''
        author = post.get('author', 'RenderPhoenix')
        llm_content += f"- [{title}]({site_url}/blog/{slug}.md){date_badge}: {desc} (Author: {author})\n"

    llm_content += f"""
## 6. Official Brand Identity & Logos
- [Media Kit & Brand Assets Web Directory]({site_url}/images/brand/): Interactive web portal with live previews, direct image URLs, and 1-click downloads for all official SVG and PNG assets.
- [Official Colored Logo (SVG)]({site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.svg): Primary studio vector mark in phoenix violet & flame pink.
- [Official Colored Logo (PNG)]({site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.png): High-resolution raster mark.
- [Official Text Colored Horizontal (SVG)]({site_url}/assets/images/brand/Renderphoenix%20Text%20Colored%20Horizontal.svg): Full horizontal colored brand wordmark.
- [Official White Logo (SVG)]({site_url}/assets/images/brand/Renderphoenix%20White%20Logo.svg): Monochrome white vector mark for dark overlays.
- [Official White Logo (PNG)]({site_url}/assets/images/brand/Renderphoenix%20White%20Logo.png): Monochrome white raster mark.
- [Official Black Logo (SVG)]({site_url}/assets/images/brand/Renderphoenix%20Black%20Logo.svg): Monochrome black vector mark for light backgrounds.

## 7. Technical Architecture of Official Website
- Static-First Engine: Statically generated site hosted on GitHub Pages with custom domain renderphoenix.com.
- Modular Markdown Endpoints: Every project and blog post is directly available as clean raw Markdown at `/work/<slug>.md` and `/blog/<slug>.md`.
- Design System: Custom CSS tokens, Inter & JetBrains Mono typography, responsive grid, zero heavy external frameworks.
- Client-side Static Search: Powers search through search.json and search-data.js index.
- Technical SEO & AI Ingestion: Full Open Graph, Twitter Cards, JSON-LD Organization schema, WebSite schema, Article schema, sitemap.xml with image extensions, robots.txt, llm.txt, llms.txt, and llms-full.txt.
- Full LLM Corpus: Available at `{site_url}/llms-full.txt`.
"""

    # Write to _site/llm.txt, _site/llms.txt, and root llm.txt, root llms.txt
    for dest in [os.path.join(SITE_DIR, 'llm.txt'), os.path.join(SITE_DIR, 'llms.txt'), os.path.join(ROOT_DIR, 'llm.txt'), os.path.join(ROOT_DIR, 'llms.txt')]:
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(llm_content)
    print("Built llm.txt & llms.txt -> _site/llm.txt, _site/llms.txt & workspace root")

    # 2. Build llms-full.txt containing the entire text corpus
    full_corpus = llm_content + "\n\n" + "=" * 80 + "\n# FULL DOCUMENTATION & PROJECT DETAILS\n" + "=" * 80 + "\n\n"
    
    full_corpus += "# --- SECTION: PROJECTS ---\n\n"
    for proj in projects:
        title = proj.get('title', '')
        slug = proj.get('slug', '')
        full_corpus += f"## Project: {title} (/work/{slug}.md)\n\n"
        full_corpus += proj.get('raw_content', '') + "\n\n"
        full_corpus += "-" * 40 + "\n\n"

    full_corpus += "# --- SECTION: DEVLOGS & ARTICLES ---\n\n"
    for post in posts:
        title = post.get('title', '')
        slug = post.get('slug', '')
        full_corpus += f"## Article: {title} (/blog/{slug}.md)\n\n"
        full_corpus += post.get('raw_content', '') + "\n\n"
        full_corpus += "-" * 40 + "\n\n"

    for dest in [os.path.join(SITE_DIR, 'llms-full.txt'), os.path.join(ROOT_DIR, 'llms-full.txt')]:
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(full_corpus)
    print("Built llms-full.txt -> _site/llms-full.txt & workspace root")

if __name__ == '__main__':
    build()
