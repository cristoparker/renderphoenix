import os
import re
import json
from typing import List, Dict, Any
from .config import Config
from .models import Project, Post
from .utils import format_full_date

_TAG_RE = re.compile(r'<[^>]+>')
_MD_RE = re.compile(r'[#*_`>\[\]()!|-]+')


def _snippet(text: str, limit: int = 300) -> str:
    """Plain-text excerpt with HTML tags and Markdown punctuation removed."""
    text = _MD_RE.sub(' ', _TAG_RE.sub(' ', text or ''))
    return re.sub(r'\s+', ' ', text).strip()[:limit]


class SearchIndexer:
    """Writes _site/search.json, fetched on demand by the search dialog in main.js."""

    @staticmethod
    def build_indexes(projects: List[Project], posts: List[Post], pages_info: List[Dict[str, Any]]) -> None:
        entries: List[Dict[str, Any]] = []

        for p in pages_info:
            slug = p.get('slug', '')
            if not p.get('title') or slug == '404':
                continue
            entries.append({
                "title": p['title'],
                "url": f"/{slug}/" if slug else "/",
                "description": p.get('desc', ''),
                "content": _snippet(p.get('content_snippet', '')),
                "type": "Legal" if p.get('type') == 'legal' else "Page",
                "tags": [slug] if slug else ["home"],
            })

        for post in posts:
            entries.append({
                "title": post.title,
                "url": f"/blog/{post.slug}/",
                "description": post.description,
                "content": _snippet(post.body),
                "type": "Article",
                "date": format_full_date(post.date),
                "tags": post.tags,
            })

        for proj in projects:
            entries.append({
                "title": proj.title,
                "url": f"/work/{proj.slug}/",
                "description": proj.description,
                "content": _snippet(proj.body),
                "type": proj.category or "Project",
                "date": format_full_date(proj.date),
                "tags": proj.tags + proj.technologies,
            })

        with open(os.path.join(Config.SITE_DIR, 'search.json'), 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, separators=(',', ':'))
        print(f"Built search.json -> _site/search.json ({len(entries)} entries)")
