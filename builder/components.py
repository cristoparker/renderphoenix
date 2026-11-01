from typing import Union, Dict, Any, List, Optional
from .config import Config
from .models import Project, Post, Service, TeamMember
from .utils import format_full_date, iso_date, html_escape as esc
from .images import get_webp_url, get_thumbnail_url, get_image_dimensions
from .icons import icon, has_icon  # noqa: F401  (has_icon used by social_links)

Item = Union[Project, Post, Dict[str, Any]]


def _slugify(text: str) -> str:
    return '-'.join(''.join(c if c.isalnum() else ' ' for c in str(text).lower()).split())


def _is_external(url: str) -> bool:
    return str(url).startswith(('http://', 'https://'))


def _ext_attrs(url: str) -> str:
    return ' target="_blank" rel="noopener noreferrer"' if _is_external(url) else ''


class ComponentRenderer:
    """Renders reusable HTML components. All markup lives here so templates stay logic-free."""

    # ------------------------------------------------------------------ media
    @staticmethod
    def sources(url: str, widths: Optional[List[int]] = None) -> Dict[str, Any]:
        """Responsive sources for an image: {'src', 'srcset', 'dims'}. Thumbnails are 16:9 WebP
        crops at each width (capped at the source width); without Pillow it falls back to the original."""
        url = url or Config.FALLBACK_IMAGE
        full = get_webp_url(url)
        variants: Dict[int, str] = {}
        for w in widths or Config.THUMB_WIDTHS:
            t = get_thumbnail_url(url, w)
            d = get_image_dimensions(t) if t != full else None
            if d:
                variants[d[0]] = t
        if not variants:
            return {'src': full, 'srcset': '', 'dims': get_image_dimensions(full)}
        src = variants[max(variants)]
        return {'src': src, 'srcset': ', '.join(f'{u} {w}w' for w, u in sorted(variants.items())),
                'dims': get_image_dimensions(src)}

    @classmethod
    def image(cls, url: str, alt: str, cls_name: str = '', eager: bool = False,
              widths: Optional[List[int]] = None, sizes: str = Config.CARD_SIZES) -> str:
        """<img> for a 16:9 media frame, with intrinsic dimensions (no layout shift), a srcset,
        and lazy loading unless it is the page's main image.

        Images that are not 16:9 are shown whole (object-fit: contain) over a blurred, zoomed copy
        of themselves that fills the letterbox. The copy uses the same URL, so it costs no extra
        download."""
        src = cls.sources(url, widths)
        srcset = f' srcset="{src["srcset"]}" sizes="{sizes}"' if src['srcset'] else ''
        dims = src['dims']
        dim_attrs = f' width="{dims[0]}" height="{dims[1]}"' if dims else ''
        loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
        letterboxed = bool(dims) and abs(dims[0] / dims[1] - 16 / 9) > 0.03
        classes = ' '.join(c for c in (cls_name, 'fit-contain' if letterboxed else '') if c)
        cls_attr = f' class="{classes}"' if classes else ''
        img = f'<img src="{src["src"]}"{srcset} alt="{esc(alt)}"{cls_attr}{dim_attrs} {loading} decoding="async">'
        if not letterboxed:
            return img
        lazy = '' if eager else ' loading="lazy"'
        backdrop = (f'<img src="{src["src"]}"{srcset} alt="" aria-hidden="true" class="frame-blur"'
                    f'{dim_attrs}{lazy} decoding="async">')
        return backdrop + img

    @classmethod
    def preload(cls, url: str, widths: Optional[List[int]] = None, sizes: str = Config.CARD_SIZES) -> str:
        """<link rel=preload> matching image() exactly, so the browser fetches the same file once."""
        src = cls.sources(url, widths)
        if src['srcset']:
            return (f'<link rel="preload" as="image" href="{src["src"]}" imagesrcset="{src["srcset"]}" '
                    f'imagesizes="{sizes}" fetchpriority="high">')
        return f'<link rel="preload" as="image" href="{src["src"]}" fetchpriority="high">'

    # ------------------------------------------------------------- projects
    @classmethod
    def project_card(cls, proj: Item, eager: bool = False, heading: str = 'h3') -> str:
        """Portfolio card: image, meta line, title, short description."""
        title = proj.get('title', '')
        url = f"/work/{proj.get('slug', '')}/"
        cat = proj.get('category', '')
        downloads = proj.get('downloads')
        meta_left = esc(cat) + (f' · {esc(downloads)} downloads' if downloads else '')
        award = f'<span class="card-flag">{icon("award", 14)} Award</span>' if proj.get('award') else ''
        return f"""<article class="card" data-category="{_slugify(cat)}">
  <a class="card-link" href="{url}">
    <div class="card-media">{cls.image(proj.get('cover_image', ''), title, eager=eager)}{award}</div>
    <div class="card-meta"><span>{meta_left}</span><time datetime="{iso_date(proj.get('date'))}">{(iso_date(proj.get('date')) or '')[:4]}</time></div>
    <{heading} class="card-title">{esc(title)}</{heading}>
    <p class="card-desc">{esc(proj.get('description', ''))}</p>
  </a>
</article>"""

    @staticmethod
    def download_count(proj: Item) -> float:
        """Parses download strings like '285.1K+', '29,983' or '1.2M' into a number for sorting."""
        raw = str(proj.get('downloads') or '').upper().replace(',', '').replace('+', '').strip()
        mult = 1_000_000 if raw.endswith('M') else 1_000 if raw.endswith('K') else 1
        try:
            return float(raw.rstrip('KM')) * mult
        except ValueError:
            return 0.0

    @classmethod
    def showcase_projects(cls, projects: List[Project], limit: int = 8) -> List[Project]:
        """Featured projects first, each group ordered by downloads."""
        by_dl = sorted(projects, key=cls.download_count, reverse=True)
        return ([p for p in by_dl if p.featured] + [p for p in by_dl if not p.featured])[:limit]

    @classmethod
    def showcase(cls, projects: List[Project]) -> str:
        """Horizontally scrolling rail of large 16:9 project cards for the homepage."""
        cards = []
        for i, p in enumerate(cls.showcase_projects(projects)):
            stat = f'{esc(p.downloads)} downloads' if p.downloads else ('Award winner' if p.award else '')
            cards.append(
                f'<a class="show-card" href="/work/{p.slug}/">'
                f'<div class="show-media">{cls.image(p.cover_image, "", eager=(i == 0), widths=Config.SHOWCASE_WIDTHS, sizes=Config.SHOWCASE_SIZES)}</div>'
                f'<div class="show-meta"><span>{esc(p.category)}</span><span>{stat}</span></div>'
                f'<h3>{esc(p.title)}</h3></a>')
        return ''.join(cards)

    @classmethod
    def showcase_preload(cls, projects: List[Project]) -> str:
        top = cls.showcase_projects(projects, 1)
        return cls.preload(top[0].cover_image, Config.SHOWCASE_WIDTHS, Config.SHOWCASE_SIZES) if top else ''

    @classmethod
    def services_bento(cls, services: List[Service], projects: List[Project]) -> str:
        """Bento grid: award project as the large tile, featured services, and an 'all' tile."""
        tiles = []
        award = next((p for p in projects if p.award), None)
        if award:
            tiles.append(
                f'<a class="bento-tile bento-feature" href="/work/{award.slug}/">'
                f'<div class="bento-media">{cls.image(award.cover_image, "", sizes=Config.BENTO_SIZES)}</div>'
                f'<div class="bento-body"><p class="eyebrow">Recognition · {iso_date(award.date)[:4]}</p>'
                f'<h3>{esc(award.award)}</h3><p>{esc(award.description)}</p></div></a>')
        featured = [s for s in services if s.get('featured')] or services
        for serv in featured[:3]:
            ic = serv.get('icon', '')
            tiles.append(
                f'<a class="bento-tile" href="/services/#{esc(serv.get("slug", ""))}">'
                f'<span class="bento-icon">{icon(ic, 22) if has_icon(ic) else ""}</span>'
                f'<h3>{esc(serv.get("title", ""))}</h3><p>{esc(serv.get("short_description", ""))}</p></a>')
        tiles.append(f'<a class="bento-tile bento-dark" href="/services/"><h3>All capabilities</h3>'
                     f'<p>Technical art, shaders, simulations and more.</p>'
                     f'<span class="bento-arrow">{icon("arrow-up-right", 22)}</span></a>')
        return '<div class="bento">' + ''.join(tiles) + '</div>'

    @staticmethod
    def filter_chips(projects: List[Project]) -> str:
        """Category filter buttons, generated from the categories actually in use."""
        cats = sorted({p.category for p in projects if p.category})
        chips = ['<button type="button" class="chip" data-filter="all" aria-pressed="true">All</button>']
        chips += [f'<button type="button" class="chip" data-filter="{_slugify(c)}" aria-pressed="false">{esc(c)}</button>'
                  for c in cats]
        return '<div class="chips" role="group" aria-label="Filter projects by category">' + ''.join(chips) + '</div>'

    @staticmethod
    def project_specs(proj: Item) -> str:
        """Project facts as <dt>/<dd> pairs."""
        platforms = proj.get('platforms')
        rows = [
            ('Developer', proj.get('developer')),
            ('Category', proj.get('category')),
            ('Version', proj.get('version')),
            ('Platform', proj.get('platform') or (', '.join(platforms) if isinstance(platforms, list) else platforms)),
            ('Released', format_full_date(proj.get('date'))),
            ('License', proj.get('license')),
            ('Downloads', proj.get('downloads')),
        ]
        items = ''.join(f'<div><dt>{k}</dt><dd>{esc(v)}</dd></div>' for k, v in rows if v)
        techs = proj.get('technologies') or []
        if techs:
            items += '<div><dt>Built with</dt><dd>' + ', '.join(esc(t) for t in techs) + '</dd></div>'
        return f'<dl class="specs">{items}</dl>' if items else ''

    @staticmethod
    def project_actions(proj: Item) -> str:
        """Action buttons: demo, downloads, GitHub, docs, MCPEDL (first one is primary)."""
        actions = []
        if proj.get('demo_url'):
            actions.append((proj.get('demo_url'), proj.get('demo_label', 'Launch live demo'), 'play'))
        for idx, dl in enumerate(proj.get('download_links') or []):
            if isinstance(dl, dict) and dl.get('url'):
                actions.append((dl['url'], dl.get('label') or f'Download #{idx + 1}', 'download'))
            elif isinstance(dl, str):
                actions.append((dl, f'Download #{idx + 1}', 'download'))
        if not proj.get('download_links'):
            if proj.get('download_url'):
                actions.append((proj.get('download_url'), proj.get('download_label', 'Download'), 'download'))
            elif proj.get('mcpedl_url'):
                actions.append((proj.get('mcpedl_url'), 'View on MCPEDL', 'arrow-up-right'))
        if proj.get('github_url'):
            actions.append((proj.get('github_url'), proj.get('github_label', 'View on GitHub'), 'github'))
        if proj.get('docs_url'):
            actions.append((proj.get('docs_url'), proj.get('docs_label', 'Documentation'), 'book'))

        if not actions:
            return ''
        buttons = []
        for i, (url, label, ic) in enumerate(actions):
            variant = 'btn-primary' if i == 0 else 'btn-ghost'
            buttons.append(f'<a class="btn {variant} btn-block" href="{esc(url)}"{_ext_attrs(url)}>'
                           f'{icon(ic, 16)}<span>{esc(label)}</span></a>')
        return '<div class="actions">' + ''.join(buttons) + '</div>'

    @staticmethod
    def award_banner(proj: Item) -> str:
        award = proj.get('award')
        return f'<p class="award">{icon("award", 18)}<span>{esc(award)}</span></p>' if award else ''

    # ---------------------------------------------------------------- posts
    @classmethod
    def post_card(cls, post: Item, eager: bool = False) -> str:
        """Blog card with cover image."""
        title = post.get('title', '')
        url = f"/blog/{post.get('slug', '')}/"
        return f"""<article class="card">
  <a class="card-link" href="{url}">
    <div class="card-media">{cls.image(post.get('image', ''), title, eager=eager)}</div>
    <div class="card-meta"><span>{esc(cls.post_category(post))}</span><time datetime="{iso_date(post.get('date'))}">{format_full_date(post.get('date'))}</time></div>
    <h3 class="card-title">{esc(title)}</h3>
    <p class="card-desc">{esc(post.get('description', ''))}</p>
  </a>
</article>"""

    @staticmethod
    def post_row(post: Item) -> str:
        """Compact text-only post row for lists."""
        url = f"/blog/{post.get('slug', '')}/"
        return (f'<li><a class="row-link" href="{url}"><span class="row-title">{esc(post.get("title", ""))}</span>'
                f'<time class="row-meta" datetime="{iso_date(post.get("date"))}">{format_full_date(post.get("date"))}</time></a></li>')

    @staticmethod
    def post_category(post: Item) -> str:
        cats = post.get('categories') or []
        return str(cats[0]).capitalize() if isinstance(cats, list) and cats else 'Devlog'

    @staticmethod
    def tags(tags: List[str]) -> str:
        if not tags:
            return ''
        return '<ul class="tags" aria-label="Tags">' + ''.join(f'<li>#{esc(t)}</li>' for t in tags) + '</ul>'

    @staticmethod
    def post_nav(prev_post: Optional[Post], next_post: Optional[Post]) -> str:
        links = []
        if prev_post:
            links.append(f'<a class="pager-link" href="/blog/{prev_post.slug}/"><span>{icon("arrow-left", 14)} Previous</span>'
                         f'<strong>{esc(prev_post.title)}</strong></a>')
        if next_post:
            links.append(f'<a class="pager-link pager-next" href="/blog/{next_post.slug}/"><span>Next {icon("arrow-right", 14)}</span>'
                         f'<strong>{esc(next_post.title)}</strong></a>')
        return f'<nav class="pager" aria-label="More posts">{"".join(links)}</nav>' if links else ''

    # ------------------------------------------------------ studio content
    @staticmethod
    def service_item(serv: Union[Service, Dict[str, Any]], index: int, detailed: bool = False,
                     heading: str = 'h3') -> str:
        """Numbered capability row: title and one line. `detailed` adds the tools used."""
        tools = ''
        techs = serv.get('technologies') or []
        if detailed and techs:
            tools = f'<p class="service-tools">{" · ".join(esc(t) for t in techs)}</p>'
        anchor = f' id="{esc(serv.get("slug"))}"' if serv.get('slug') else ''
        return (f'<li class="service"{anchor}><span class="service-num">{index:02d}</span>'
                f'<div><{heading}>{esc(serv.get("title", ""))}</{heading}>'
                f'<p>{esc(serv.get("short_description") or serv.get("description", ""))}</p>{tools}</div></li>')

    @staticmethod
    def team_card(mem: Union[TeamMember, Dict[str, Any]]) -> str:
        """Team member card: avatar with role tag, name and short bio."""
        name = mem.get('name', '')
        avatar = mem.get('avatar', '')
        if avatar:
            src = avatar if _is_external(avatar) else get_webp_url(avatar)
            if 'avatars.githubusercontent.com' in src and '?' not in src:
                src += '?s=144'  # request a right-sized avatar instead of the 460px default
            media = f'<img src="{src}" alt="" width="72" height="72" loading="lazy" decoding="async">'
        else:
            media = f'<span aria-hidden="true">{esc(name[:1] or "R")}</span>'
        return (f'<li class="person"><div class="avatar">{media}</div>'
                f'<h3>{esc(name)}</h3><p class="person-role">{esc(mem.get("role", ""))}</p>'
                f'<p class="person-bio">{esc(mem.get("bio", ""))}</p></li>')

    @staticmethod
    def stats(items: List[Dict[str, Any]], tokens: Dict[str, Any]) -> str:
        cells = ''.join(f'<div><dt>{esc(s.get("label", ""))}</dt><dd>{esc(str(s.get("value", "")).format(**tokens))}</dd></div>'
                        for s in items)
        return f'<dl class="stats">{cells}</dl>'

    @staticmethod
    def timeline(items: List[Dict[str, Any]]) -> str:
        rows = ''.join(f'<li><span class="tl-year">{esc(t.get("year", ""))}</span><div><h3>{esc(t.get("title", ""))}</h3>'
                       f'<p>{esc(t.get("text", ""))}</p></div></li>' for t in items)
        return f'<ol class="timeline">{rows}</ol>'

    # ----------------------------------------------------------- navigation
    @staticmethod
    def nav_links(items: List[Dict[str, str]], current: str) -> str:
        """Header nav with `aria-current` on the active section."""
        out = []
        for item in items:
            url = item.get('url', '/')
            active = current == url or (url != '/' and current.startswith(url))
            cur = ' aria-current="page"' if active else ''
            out.append(f'<li><a href="{url}"{cur}>{esc(item.get("title", ""))}</a></li>')
        return ''.join(out)

    @staticmethod
    def link_list(items: List[Dict[str, str]]) -> str:
        return ''.join(f'<li><a href="{esc(i.get("url", ""))}"{_ext_attrs(i.get("url", ""))}>{esc(i.get("title", ""))}</a></li>'
                       for i in items)

    @staticmethod
    def social_links(items: List[Dict[str, str]]) -> str:
        out = []
        for i in items:
            title = i.get('title', '')
            name = title.lower()
            ic = icon(name, 18) if has_icon(name) else ''
            out.append(f'<li><a href="{esc(i.get("url", ""))}" target="_blank" rel="noopener noreferrer" '
                       f'aria-label="{esc(title)}" title="{esc(title)}">{ic}</a></li>')
        return ''.join(out)
