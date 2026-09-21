# Session Persistence & Theme Update

## Session persistence

The frontend now restores the authenticated session after a browser refresh.

- The JWT remains in `localStorage` under `token`.
- The signed-in user is cached under `essay_user` so the workspace can restore cleanly.
- On startup, the frontend validates the saved JWT through `GET /auth/me`.
- While validation is happening, a small session-restoration screen is shown instead of briefly rendering the wrong page.
- Expired/invalid sessions are cleared cleanly and the user is returned to sign-in.
- Dashboard/history/documents/analytics are refreshed after the session is restored.

## Visual theme

The interface now uses an editorial writing-studio palette rather than a generic neon/glassmorphism AI-dashboard style:

- Deep pine / ink backgrounds
- Parchment-inspired authentication surface
- Muted copper for primary actions and scores
- Sage and slate-blue supporting accents
- Serif editorial headings paired with clean UI typography
- Subtle borders and shadows instead of excessive glow/gradients
- Consistent original/improved writing panels

The design is intended to feel like a premium writing product built around essays and reading, not an AI-generated template.
