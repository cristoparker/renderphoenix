import os
import yaml
from typing import Tuple, Dict, Any, List
from .config import Config
from .models import Project, Post, Service, TeamMember

class ContentLoader:
    """Loads and parses markdown collections, frontmatter, and YAML data files."""

    @staticmethod
    def load_frontmatter_and_content(filepath: str) -> Tuple[Dict[str, Any], str]:
        """Parses a file with optional YAML frontmatter into a (meta_dict, body_string) tuple."""
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

    @classmethod
    def load_projects(cls) -> List[Project]:
        """Loads and sorts all projects from _projects/*.md."""
        projects: List[Project] = []
        if not os.path.exists(Config.PROJECTS_DIR):
            return projects

        for fname in os.listdir(Config.PROJECTS_DIR):
            if fname.endswith('.md'):
                fpath = os.path.join(Config.PROJECTS_DIR, fname)
                meta, body = cls.load_frontmatter_and_content(fpath)
                slug = meta.get('slug', fname.replace('.md', ''))
                
                proj = Project(
                    title=meta.get('title', slug),
                    slug=slug,
                    description=meta.get('description', ''),
                    category=meta.get('category', 'Project'),
                    developer=meta.get('developer', ''),
                    date=meta.get('date'),
                    version=str(meta.get('version', '')) if meta.get('version') else '',
                    platform=meta.get('platform', ''),
                    platforms=meta.get('platforms', []) if isinstance(meta.get('platforms'), list) else [],
                    license=meta.get('license', ''),
                    downloads=str(meta.get('downloads', '')) if meta.get('downloads') else '',
                    award=meta.get('award', ''),
                    cover_image=meta.get('cover_image', ''),
                    youtube_url=meta.get('youtube_url', ''),
                    youtube_author=meta.get('youtube_author', ''),
                    demo_url=meta.get('demo_url') or meta.get('live_demo_url') or '',
                    demo_label=meta.get('demo_label', 'Launch Live Demo'),
                    download_links=meta.get('download_links', []) if isinstance(meta.get('download_links'), list) else [],
                    download_url=meta.get('download_url', ''),
                    download_label=meta.get('download_label', 'Download Project'),
                    github_url=meta.get('github_url') or meta.get('github') or meta.get('repo_url') or '',
                    github_label=meta.get('github_label', 'View on GitHub'),
                    docs_url=meta.get('docs_url', ''),
                    docs_label=meta.get('docs_label', 'Documentation'),
                    mcpedl_url=meta.get('mcpedl_url', ''),
                    technologies=meta.get('technologies', []) if isinstance(meta.get('technologies'), list) else [],
                    tags=meta.get('tags', []) if isinstance(meta.get('tags'), list) else [],
                    featured=bool(meta.get('featured', False)),
                    body=body,
                    raw_content=meta.get('raw_content', ''),
                    meta=meta
                )
                projects.append(proj)

        projects.sort(key=lambda x: str(x.date or ''), reverse=True)
        return projects

    @classmethod
    def load_posts(cls) -> List[Post]:
        """Loads and sorts all blog posts/devlogs from _posts/YYYY-MM-DD-*.md."""
        posts: List[Post] = []
        if not os.path.exists(Config.POSTS_DIR):
            return posts

        for fname in os.listdir(Config.POSTS_DIR):
            if fname.endswith('.md'):
                fpath = os.path.join(Config.POSTS_DIR, fname)
                meta, body = cls.load_frontmatter_and_content(fpath)
                slug = fname[11:].replace('.md', '') if len(fname) > 11 and fname[10] == '-' else fname.replace('.md', '')
                
                cats = meta.get('categories', [])
                if isinstance(cats, str):
                    cats = [cats]
                tags = meta.get('tags', [])
                if isinstance(tags, str):
                    tags = [tags]

                post = Post(
                    title=meta.get('title', slug),
                    slug=slug,
                    description=meta.get('description', ''),
                    date=meta.get('date'),
                    author=meta.get('author', 'RenderPhoenix'),
                    categories=cats,
                    tags=tags,
                    image=meta.get('image', ''),
                    featured=bool(meta.get('featured', False)),
                    body=body,
                    raw_content=meta.get('raw_content', ''),
                    meta=meta
                )
                posts.append(post)

        posts.sort(key=lambda x: str(x.date or ''), reverse=True)
        return posts

    @classmethod
    def load_services(cls) -> List[Service]:
        """Loads services from _data/services.yml."""
        serv_file = os.path.join(Config.DATA_DIR, 'services.yml')
        if not os.path.exists(serv_file):
            return []

        with open(serv_file, 'r', encoding='utf-8') as f:
            raw_services = yaml.safe_load(f) or []

        services: List[Service] = []
        for s in raw_services:
            services.append(Service(
                title=s.get('title', ''),
                slug=s.get('slug', ''),
                description=s.get('description', ''),
                short_description=s.get('short_description', s.get('description', '')),
                capabilities=s.get('capabilities', []) if isinstance(s.get('capabilities'), list) else [],
                icon=s.get('icon', ''),
                meta=s
            ))
        return services

    @classmethod
    def load_team(cls) -> List[TeamMember]:
        """Loads team roster from _data/team.yml."""
        team_file = os.path.join(Config.DATA_DIR, 'team.yml')
        if not os.path.exists(team_file):
            return []

        with open(team_file, 'r', encoding='utf-8') as f:
            raw_team = yaml.safe_load(f) or []

        team: List[TeamMember] = []
        for m in raw_team:
            team.append(TeamMember(
                name=m.get('name', ''),
                role=m.get('role', ''),
                bio=m.get('bio', ''),
                avatar=m.get('avatar', ''),
                meta=m
            ))
        return team
