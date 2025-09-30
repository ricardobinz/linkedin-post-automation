# LinkedIn Post Generator (Frontend)

A minimal, modern UI to generate, edit, validate, publish, and review LinkedIn posts. Built with Vite + React + TypeScript.

## Features
- Generate draft post ideas (text + image placeholder)
- Edit title, text, and image (with regenerate image option)
- Validate posts to move them to the "Validated" list
- Publish validated posts (mock) and track them in History
- History view with filters by status: Draft, Validated, Posted, Deleted
- Clean, responsive UI with card/grid layout and status badges

## Tech Stack
- Vite 5
- React 18 + TypeScript
- React Router 6
- LocalStorage-backed store (no backend required)

## Getting Started

Prerequisites:
- Node.js 18+ and npm

Install dependencies and start the dev server:

```bash
npm install
npm run dev
```

The app will start on http://localhost:5173

Build for production:

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
  src/
    components/
      Header.tsx         # Top navigation and Generate Post button
      PostCard.tsx       # Post preview card with contextual actions
      StatusBadge.tsx    # Status chip (draft/validated/posted/deleted)
    pages/
      Dashboard.tsx      # Drafts list + generate/edit/validate/delete
      PostEditor.tsx     # Edit title/text/image, save, validate
      Validated.tsx      # Validated posts with Publish action
      History.tsx        # All posts with status filters and timestamps
    services/
      generator.ts       # Mock text + image generation utilities
    store/
      posts.ts           # LocalStorage-backed CRUD + status transitions
    styles/
      index.css          # Global modern styling and layout
    App.tsx              # Routes and page layout
    main.tsx             # React bootstrap
  index.html             # Entry HTML
  vite.config.ts         # Vite config with '@' alias → src/
  tsconfig.json          # TS paths ("@/*" → src/*)
```

## Data Model
- Statuses: `draft | validated | posted | deleted`
- Stored in `localStorage` under key `lpg_posts_v1`
- Timestamps tracked per status transition

## Notes / Next Steps
- The Publish action is currently a mock. To integrate with LinkedIn, wire a backend endpoint that calls the LinkedIn API, then update `PostsStore.publish()` to call it and record the result.
- UI is intentionally minimal and can be themed or extended.
- Images use `https://picsum.photos` with a seed for consistent placeholders.
