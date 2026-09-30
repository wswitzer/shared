# Chris Gaca World Song Library — Content Inventory & Migration Dataset

This directory contains the complete, high-confidence content inventory, asset archive, and forensic migration dataset extracted from Chris Gaca's original WordPress site ([chrisgaca.wordpress.com](https://chrisgaca.wordpress.com/)).

## Deliverables & Documents

- **[CHRIS_CONTENT_INVENTORY_REPORT.md](CHRIS_CONTENT_INVENTORY_REPORT.md)**: Comprehensive 14-section audit report detailing methodology, song catalog, language analysis, taxonomy corrections, media inventory, and architectural recommendations.
- **[songs.json](songs.json)**: Canonical database of all 22 discovered songs with verified titles, original scripts, languages, cultural contexts, personal stories, teaching notes, YouTube IDs, and file links.
- **[songs.csv](songs.csv)**: Spreadsheet table mapping all 22 songs across 18 metadata and resource columns.
- **[pages.json](pages.json)**: Structured schema of non-song pages (About/Home, Collection History, Recommended Sites, and Redirect Notice).
- **[attachments.json](attachments.json)**: Registry of all 21 uploaded WordPress documents and images with original URLs, file sizes, and paths.
- **[url-map.csv](url-map.csv)**: Legacy URL migration matrix providing 301 redirect mappings for all legacy posts, pages, and categories.
- **[crawl-urls.txt](crawl-urls.txt)**: Complete list of all 67 internal URLs crawled.
- **[external-links.csv](external-links.csv)**: Catalog of all outbound external links and YouTube performance targets.
- **[chris-gaca-content-inventory.zip](chris-gaca-content-inventory.zip)**: Self-contained zip archive containing the entire inventory package.

## Subdirectories

- **`downloads/`**: Structured by country and song slug (`downloads/<Country>/<Song>/`), containing all 18 source documents (16 `.doc`/`.docx`, 2 `.pdf`), 3 uploaded images (score excerpts and chorus photo), and 16 plain-text transcripts (`.txt`) extracted from the Word documents.
- **`raw_api/`**: Raw JSON payloads directly extracted from WordPress REST API endpoints (`posts_wp_v2.json`, `categories.json`, `comments.json`, `sitemap.xml`, etc.).
