# RenderPhoenix Official Website

Official website for **RenderPhoenix**, an independent interactive creative studio from Bangladesh building standalone games, 3D environments, game assets, and digital experiences.

- **Production Domain**: [renderphoenix.com](https://renderphoenix.com/)
- **Verified Community Profile**: [MCPEDL Profile](https://mcpedl.com/user/renderphoenix/)

---

## Technical Stack

- **Engine**: Jekyll (Static Site Generator)
- **Hosting**: GitHub Pages with custom domain (`CNAME`)
- **Styling**: Vanilla CSS with custom design tokens (`variables.css`)
- **Scripts**: Vanilla JavaScript (Mobile menu, fast static search, category filters)
- **Typography**: Space Grotesk (Headings), Inter (Body), JetBrains Mono (Code)
- **SEO & AI**: Full Open Graph, JSON-LD Schema, `sitemap.xml`, `robots.txt`, `llm.txt`

---

## Local Development Workflow

### Prerequisites
- Ruby 3.x+
- Bundler (`gem install bundler`)
- Jekyll (`gem install jekyll`)

### Running Locally

```bash
# Install dependencies
bundle install

# Run Jekyll development server
bundle exec jekyll serve
```

Access the local site at `http://localhost:4000`.

---

## Managing Content

### Adding a Project
To add a new project to the portfolio, create a markdown file inside `_projects/`:

```markdown
---
title: "New Game Project"
slug: "new-game-project"
description: "A short summary of the game."
category: "Game" # Options: Game, Environment, Interactive, UI, Add-On
year: 2026
status: "in-development" # Options: active, completed, archived, in-development
cover_image: "/assets/images/projects/new-game.svg"
technologies: ["Unreal Engine 5", "Blender", "C++"]
featured: true
tags: ["unreal", "game", "3d"]
---

Detailed description of the project goes here...
```

Jekyll will automatically output the page at `/work/new-game-project/`.

### Adding a Blog Post
Create a markdown file inside `_posts/`:

```markdown
---
layout: post
title: "Title of Post"
description: "Description for SEO and post previews."
date: 2026-08-22
categories:
  - development
tags:
  - devlog
author: "Cristo Parker"
image: "/assets/images/blog/example.jpg"
featured: false
---

Post content written in standard Markdown...
```

### Updating Services & Team
- **Services**: Edit `_data/services.yml`
- **Team**: Edit `_data/team.yml`
- **Navigation**: Edit `_data/navigation.yml`

---

## Deployment to GitHub Pages

1. Push all changes to the `main` or `master` branch.
2. Ensure `CNAME` contains `renderphoenix.com`.
3. In GitHub Repository Settings -> Pages, select the source branch.
4. GitHub Pages will build the site statically using Jekyll.

---

## Documentation Guide
For step-by-step content creation instructions, see [docs/content-guide.md](file:///home/sabit/Documents/GitHub/renderphoenix2/docs/content-guide.md).
