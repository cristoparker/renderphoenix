from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Project:
    title: str
    slug: str
    description: str = ""
    category: str = "Project"
    developer: str = ""
    date: Any = None
    version: str = ""
    platform: str = ""
    platforms: List[str] = field(default_factory=list)
    license: str = ""
    downloads: str = ""
    award: str = ""
    cover_image: str = ""
    youtube_url: str = ""
    youtube_author: str = ""
    demo_url: str = ""
    demo_label: str = "Launch Live Demo"
    download_links: List[Dict[str, Any]] = field(default_factory=list)
    download_url: str = ""
    download_label: str = "Download Project"
    github_url: str = ""
    github_label: str = "View on GitHub"
    docs_url: str = ""
    docs_label: str = "Documentation"
    mcpedl_url: str = ""
    technologies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    featured: bool = False
    body: str = ""
    raw_content: str = ""
    markdown_url: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None and val != "" and val != []:
                return val
        return self.meta.get(key, default)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        return self.meta[key]

@dataclass
class Post:
    title: str
    slug: str
    description: str = ""
    date: Any = None
    author: str = "RenderPhoenix"
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    image: str = ""
    featured: bool = False
    body: str = ""
    raw_content: str = ""
    markdown_url: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None and val != "" and val != []:
                return val
        return self.meta.get(key, default)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        return self.meta[key]

@dataclass
class Service:
    title: str
    slug: str = ""
    description: str = ""
    short_description: str = ""
    capabilities: List[str] = field(default_factory=list)
    icon: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None and val != "" and val != []:
                return val
        return self.meta.get(key, default)

@dataclass
class TeamMember:
    name: str
    role: str = ""
    bio: str = ""
    avatar: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None and val != "" and val != []:
                return val
        return self.meta.get(key, default)

@dataclass
class PageInfo:
    slug: str
    title: str
    desc: str = ""
    type: str = "page"
    priority: float = 0.8
    freq: str = "monthly"
