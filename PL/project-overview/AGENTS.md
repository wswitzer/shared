# Public project overview

This directory is the public, privacy-safe project brief for PL-OS.

- Edit `project-overview.json` for status, decisions, questions, and actions.
- Keep `index.html` as a stable renderer over that JSON.
- Update `meta.lastUpdated` whenever the public brief changes.
- Never include names, email addresses, meeting links, credentials, private documents, student data, or confidential client details.
- Keep wording understandable to a non-technical stakeholder in under two minutes.
- Run `node PL/project-overview/validate.mjs` after changing the JSON.
- The page is deployed by `.github/workflows/pages.yml` after changes reach `main`.

The page is a public summary, not the source of truth for product requirements, architecture, or private project records.