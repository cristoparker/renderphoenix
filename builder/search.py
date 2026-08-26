import os
import re
import json
from typing import List, Dict, Any
from .config import Config
from .models import Project, Post
from .utils import format_full_date

class SearchIndexer:
    """Generates static JSON and JavaScript search indices for client-side search."""

    @staticmethod
    def build_indexes(projects: List[Project], posts: List[Post], pages_info: List[Dict[str, Any]]) -> None:
        search_data: List[Dict[str, Any]] = []

        # 1. Pages & Legal documents
        for p in pages_info:
            slug = p.get('slug', '')
            title = p.get('title', '')
            desc = p.get('desc', '')
            p_type = p.get('type', 'page')

            if title and slug != '404':
                search_data.append({
                    "title": title,
                    "url": f"/{slug}/" if slug else "/",
                    "description": desc,
                    "content": p.get('content_snippet', desc)[:300],
                    "type": "Legal" if p_type == 'legal' else "Page",
                    "category": "Legal & Policies" if p_type == 'legal' else "Overview",
                    "date": "25 Aug 2026",
                    "tags": [slug] if slug else ["home"]
                })

        # 2. Blog articles
        for post in posts:
            search_data.append({
                "title": post.title,
                "url": f"/blog/{post.slug}/",
                "description": post.description,
                "content": re.sub(r'<[^>]+>', '', post.body)[:300],
                "type": "Article",
                "category": "Blog",
                "date": format_full_date(post.date),
                "tags": post.tags
            })

        # 3. Portfolio projects
        for proj in projects:
            search_data.append({
                "title": proj.title,
                "url": f"/work/{proj.slug}/",
                "description": proj.description,
                "content": re.sub(r'<[^>]+>', '', proj.body)[:300],
                "type": "Project",
                "category": proj.category,
                "date": format_full_date(proj.date),
                "tags": proj.tags
            })

        # Write _site/search.json
        search_json_path = os.path.join(Config.SITE_DIR, 'search.json')
        with open(search_json_path, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, indent=2)
        print("Built search.json -> _site/search.json")

        # Write _site/assets/js/search-data.js
        search_js_dir = os.path.join(Config.SITE_DIR, 'assets', 'js')
        os.makedirs(search_js_dir, exist_ok=True)
        search_data_js_path = os.path.join(search_js_dir, 'search-data.js')
        with open(search_data_js_path, 'w', encoding='utf-8') as f:
            f.write("window.SEARCH_INDEX = " + json.dumps(search_data, indent=2) + ";\n")
        print("Built search-data.js -> _site/assets/js/search-data.js")
