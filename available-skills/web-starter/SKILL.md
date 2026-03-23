---
name: web-starter
description: Scaffold a new web project with modern best practices. Use when the user says "create a website", "new web project", "landing page", "scaffold", "starter", or "set up a web app".
argument-hint: "[project type] [tech preferences]"
disable-model-invocation: true
---

# Web Project Scaffolder

Create a properly structured web project with modern tooling and best practices.

## Process

### Step 1: Gather Requirements
Ask about:
1. **Type**: Static site, SPA, SSR app, landing page, dashboard, portfolio?
2. **Tech**: React/Next.js, Vue/Nuxt, Svelte/SvelteKit, vanilla HTML/CSS/JS?
3. **Styling**: Tailwind, CSS Modules, vanilla CSS, styled-components?
4. **Features needed**: Auth, database, API, forms, payments?
5. **Deployment target**: Vercel, Netlify, self-hosted, static hosting?

### Step 2: Create Structure
Adapt to chosen tech. Example for Next.js + Tailwind:
```
project/
├── src/
│   ├── app/              # App router pages
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Home page
│   │   └── globals.css   # Global styles
│   ├── components/       # Reusable components
│   │   └── ui/           # Base UI components
│   └── lib/              # Utilities and helpers
├── public/               # Static assets
├── CLAUDE.md             # Project-specific Claude instructions
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── .gitignore
```

### Step 3: Implement Foundation
Create with:
- **Semantic HTML**: Proper landmarks, heading hierarchy
- **Responsive base**: Mobile-first with fluid breakpoints
- **Accessible defaults**: Focus styles, ARIA labels, skip nav
- **Performance**: Proper font loading, image optimization setup
- **Type safety**: TypeScript configured properly
- **Development tooling**: Linting, formatting configured

### Step 4: Create CLAUDE.md
Generate a lean CLAUDE.md for the new project with:
- Tech stack and commands
- Project-specific conventions
- File organization rules

### Step 5: Verify
- Project builds without errors
- Development server starts
- Basic page renders correctly
- No accessibility violations in base template
