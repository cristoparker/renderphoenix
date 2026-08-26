import os
from typing import List, Dict, Any
from .config import Config
from .models import Project, Post
from .utils import format_full_date

class LLMGenerator:
    """Generates machine-readable AI & LLM context files (llms.txt and llms-full.txt)."""

    @staticmethod
    def build_indexes(projects: List[Project], posts: List[Post], compiled_pages: List[Dict[str, Any]]) -> None:
        site_url = Config.SITE_URL

        # 1. Standard llms.txt index
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

## 4. Main Pages & Canonical Markdown Endpoints
- [About RenderPhoenix]({site_url}/about.md): Comprehensive studio history, founders, timeline, resilience milestones, and 2026 revival details.
- [Services & Capabilities]({site_url}/services.md): Technical overview of studio capabilities (Unreal Engine 5, Unity, Blender, C#, C++, shaders, asset production, and simulation prototypes).
- [Work Portfolio]({site_url}/work.md): Complete index of all interactive works, games, 3D worlds, and addons.
- [Blog]({site_url}/blog.md): Index of studio announcements, retrospectives, and engineering devlogs.
- [Get in Touch]({site_url}/contact.md): Studio contact information, inquiry categories, and collaboration details.

## 5. Notable Works & Project Index (Raw Markdown)
"""
        for proj in projects:
            title = proj.title
            slug = proj.slug
            desc = proj.description
            date = proj.date
            year = str(date)[:4] if date else ''
            year_str = f" ({year})" if year else ''
            cat = proj.category
            cat_str = f" [{cat}]" if cat else ''
            llm_content += f"- [{title}]({site_url}/work/{slug}.md){year_str}{cat_str}: {desc}\n"

        llm_content += "\n## 6. Editorial & Studio Devlogs (Raw Markdown)\n"
        for post in posts:
            title = post.title
            slug = post.slug
            desc = post.description
            date_str = format_full_date(post.date)
            date_badge = f" ({date_str})" if date_str else ''
            author = post.author or 'RenderPhoenix'
            llm_content += f"- [{title}]({site_url}/blog/{slug}.md){date_badge}: {desc} (Author: {author})\n"

        llm_content += f"""
## 7. Legal, Privacy & Compliance (Raw Markdown)
- [Privacy Policy]({site_url}/privacy-policy.md): Official Privacy Policy detailing our strict no-tracking architecture, zero-account database model, and third-party service interactions.
- [DMCA & Copyright Policy]({site_url}/dmca.md): Official Digital Millennium Copyright Act compliance notice, designated copyright agent contact, takedown request checklist, and counter-notification procedures.

## 8. Official Brand Identity & Logos
- [Media Kit & Brand Assets Web Directory]({site_url}/images/brand/): Interactive web portal with live previews, direct image URLs, and 1-click downloads for all official SVG and PNG assets.
- [Official Colored Logo (SVG)]({site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.svg): Primary studio vector mark in phoenix violet & flame pink.
- [Official Colored Logo (PNG)]({site_url}/assets/images/brand/Renderphoenix%20Colored%20Logo.png): High-resolution raster mark.
- [Official Text Colored Horizontal (SVG)]({site_url}/assets/images/brand/Renderphoenix%20Text%20Colored%20Horizontal.svg): Full horizontal colored brand wordmark.
- [Official White Logo (SVG)]({site_url}/assets/images/brand/Renderphoenix%20White%20Logo.svg): Monochrome white vector mark for dark overlays.
- [Official White Logo (PNG)]({site_url}/assets/images/brand/Renderphoenix%20White%20Logo.png): Monochrome white raster mark.
- [Official Black Logo (SVG)]({site_url}/assets/images/brand/Renderphoenix%20Black%20Logo.svg): Monochrome black vector mark for light backgrounds.

## 9. Technical Architecture of Official Website
- Static-First Engine: Statically generated site hosted on GitHub Pages with custom domain renderphoenix.com.
- Modular Markdown Endpoints: Every project, blog post, and legal policy is directly available as clean raw Markdown at `/work/<slug>.md`, `/blog/<slug>.md`, `/about.md`, `/services.md`, `/contact.md`, `/privacy-policy.md`, and `/dmca.md`.
- Design System: Custom CSS tokens, Inter & JetBrains Mono typography, responsive grid, zero heavy external frameworks.
- Client-side Static Search: Powers search through search.json and search-data.js index.
- Technical SEO & AI Ingestion: Full Open Graph, Twitter Cards, JSON-LD Organization schema, WebSite schema, Article schema, sitemap.xml with image extensions, robots.txt, llms.txt, and llms-full.txt.
- Full LLM Corpus: Available at `{site_url}/llms-full.txt`.
"""

        # Write to _site/llms.txt and root llms.txt
        for dest in [os.path.join(Config.SITE_DIR, 'llms.txt'), os.path.join(Config.ROOT_DIR, 'llms.txt')]:
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(llm_content)
        print("Built llms.txt -> _site/llms.txt & workspace root")

        # 2. Build llms-full.txt containing the entire text corpus
        full_corpus = llm_content + "\n\n" + "=" * 80 + "\n# FULL DOCUMENTATION & PROJECT DETAILS\n" + "=" * 80 + "\n\n"

        # Core studio pages (about, services, contact)
        full_corpus += "# --- SECTION: STUDIO CORE PAGES ---\n\n"
        for pcfg in compiled_pages:
            slug = pcfg['slug']
            if slug in ('about', 'services', 'contact'):
                md_path = os.path.join(Config.ROOT_DIR, slug, 'index.md')
                if os.path.exists(md_path):
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    full_corpus += f"## Page: {pcfg['title']} (/{slug}.md)\n\n"
                    full_corpus += content + "\n\n"
                    full_corpus += "-" * 40 + "\n\n"

        full_corpus += "# --- SECTION: PROJECTS ---\n\n"
        for proj in projects:
            title = proj.title
            slug = proj.slug
            full_corpus += f"## Project: {title} (/work/{slug}.md)\n\n"
            full_corpus += proj.raw_content + "\n\n"
            full_corpus += "-" * 40 + "\n\n"

        full_corpus += "# --- SECTION: DEVLOGS & ARTICLES ---\n\n"
        for post in posts:
            title = post.title
            slug = post.slug
            full_corpus += f"## Article: {title} (/blog/{slug}.md)\n\n"
            full_corpus += post.raw_content + "\n\n"
            full_corpus += "-" * 40 + "\n\n"

        full_corpus += "# --- SECTION: LEGAL, PRIVACY & COMPLIANCE ---\n\n"
        for pcfg in compiled_pages:
            slug = pcfg['slug']
            if pcfg.get('type') == 'legal':
                md_path = os.path.join(Config.ROOT_DIR, slug, 'index.md')
                if os.path.exists(md_path):
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    full_corpus += f"## Legal Document: {pcfg['title']} (/{slug}.md)\n\n"
                    full_corpus += content + "\n\n"
                    full_corpus += "-" * 40 + "\n\n"

        for dest in [os.path.join(Config.SITE_DIR, 'llms-full.txt'), os.path.join(Config.ROOT_DIR, 'llms-full.txt')]:
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(full_corpus)
        print("Built llms-full.txt -> _site/llms-full.txt & workspace root")
