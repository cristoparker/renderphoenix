# RenderPhoenix Content & Maintenance Guide

This guide details how team members can maintain, update, and add new content to the RenderPhoenix website without modifying core HTML structure.

---

## 1. How to Add a New Project
1. Create a new markdown file in `_projects/` named `your-project-slug.md`.
2. Add the required frontmatter:
   ```yaml
   ---
   title: "Project Title"
   slug: "project-title"
   description: "Brief summary for card display."
   category: "Game" # Allowed categories: Game, Environment, Interactive, UI, Add-On
   year: 2026
   status: "active" # Allowed statuses: active, completed, archived, in-development
   cover_image: "/assets/images/projects/your-cover.jpg"
   technologies:
     - "Blender"
     - "Unreal Engine"
   featured: true
   tags:
     - "game"
     - "3d"
   ---
   ```
3. Write your project description below the frontmatter using standard Markdown.
4. Save the file. Jekyll will generate `/work/project-title/` automatically.

---

## 2. How to Add a Blog Post
1. Create a new file in `_posts/` with the date format `YYYY-MM-DD-post-title.md`.
2. Add frontmatter:
   ```yaml
   ---
   layout: post
   title: "Your Post Title"
   description: "Summary of post."
   date: 2026-08-22 00:00:00 +0600
   categories:
     - studio
   tags:
     - news
   author: "RenderPhoenix"
   image: "/assets/images/blog/cover.jpg"
   featured: true # Set to true to highlight at top of blog
   ---
   ```
3. Write your article in Markdown. Standard code snippets (` ```python `) and blockquotes (`>`) will be styled automatically.

---

## 3. How to Update Services
1. Open `_data/services.yml`.
2. Add or modify service entries:
   ```yaml
   - title: "New Service Name"
     slug: "new-service"
     icon: "code"
     order: 6
     featured: true
     short_description: "Short summary..."
     description: "Full service description..."
     technologies:
       - "Tech 1"
       - "Tech 2"
     capabilities:
       - "Capability A"
       - "Capability B"
   ```

---

## 4. How to Update Team Profiles
1. Open `_data/team.yml`.
2. Add team member details:
   ```yaml
   - name: "Member Name"
     role: "Specialist Role"
     username: "username"
     bio: "Short bio..."
     active: true
   ```

---

## 5. How to Modify Navigation & Social Links
- **Header & Footer Links**: Edit `_data/navigation.yml`.
- **Social Profiles**: Update `_data/navigation.yml` under `footer.resources`.
- **SEO & Canonical Defaults**: Edit `_config.yml` or `_includes/seo.html`.
