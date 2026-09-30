# Chris Gaca — Living Archive Pixel-Match Handoff

## Repository
`wswitzer/shared`

## Destination
Replace/update:
`chris-gaca/mockups/`

The package contains a prepared site under `site/`. Copy its contents into:
`chris-gaca/mockups/`

That means:
- `site/index.html` -> `chris-gaca/mockups/index.html`
- `site/style.css` -> `chris-gaca/mockups/style.css`
- `site/assets/*` -> `chris-gaca/mockups/assets/*`

Also copy:
- `reference/living-archive-target.png` -> `chris-gaca/mockups/reference/living-archive-target.png`
- `source-boards/*` -> optionally `chris-gaca/mockups/source-boards/*` for design reference

## Important
The PNG files in this package are the original/full-quality generated images from the design session. Do not replace them with Unsplash, stock imagery, screenshots, compressed copies, or newly generated approximations unless absolutely necessary.

The chosen design direction is the Living Archive mockup in:
`source-boards/chosen_living_archive_mockup.png`

The browser-comparison target is:
`reference/living-archive-target.png`

The screenshot/reference is the visual specification.

## Objective
Finish the prototype so the browser rendering matches the selected Living Archive mockup as closely as practical.

Do not redesign it.
Do not reinterpret the layout.
Do not switch to a generic WordPress/SaaS/tourism aesthetic.

## Required Playwright loop
1. Fetch current `main` first.
2. Copy the supplied package files into the repo path above.
3. Serve the repository locally with a simple static server.
4. Open `chris-gaca/mockups/index.html`.
5. Set Playwright viewport to exactly `1122 x 1367`.
6. Wait for fonts and all images to finish loading.
7. Capture a full-page screenshot.
8. Compare it against `chris-gaca/mockups/reference/living-archive-target.png`.
9. Fix the largest visible differences.
10. Repeat screenshot -> compare -> adjust until further changes have diminishing benefit.

Do not stop after one styling pass.

## Fidelity priority
### 1. Large geometry
Match first:
- overall page width
- header height
- hero height
- left/right hero split
- main gutters
- section spacing
- featured-card widths/heights
- six regional tiles in one row
- lower language/collections split
- footer height

### 2. Typography
Match:
- serif heading style
- headline size and exact wrapping
- nav scale
- body density
- section-heading size
- metadata scale
- letter spacing

### 3. Hero
This is the highest-impact section.
Use the supplied `hero_collage_reference.png` and/or recrop from the supplied full-resolution source boards to closely match the target.

Left side needs:
- warm cream/parchment background
- subtle decorative botanical/pattern element
- two-line `A living archive / of songs`
- compact supporting copy
- dark green rectangular CTA
- understated four-part info row

Right side needs to retain the layered archival collage feel.
Do not collapse it into one generic stock image.

### 4. Provided generated imagery
Use the full-quality supplied images.
You are encouraged to recrop them from `source-boards/` if the current crop is not exact enough.

Available site assets include:
- hero collage
- 4 featured archive card images
- region tiles
- curated collection images
- bottom-section reference crop

### 5. Featured Archive
Match the screenshot:
- four equal cards
- subtle border
- almost square corners
- compact image crop
- country label
- serif song title
- short description
- small resource row

### 6. Browse by Region
Match:
- six tiles on one row at 1122px
- narrow gaps
- strong photography
- region label over imagery
- subtle darkening/gradient for readability

### 7. Language / Collections
Match the asymmetrical two-column lower section.
Left: compact language cells.
Right: three collection cards using the supplied illustrated/editorial assets.

### 8. Footer
Match the deep forest green, decorative pattern, centered italic quote, and small right-side text.

## Visual comparison tools
Use whatever is useful locally:
- Playwright screenshots
- image overlay at 50% opacity
- pixel diff
- ImageMagick compare
- Python/Pillow difference images
- DOM bounding-box measurements
- computed CSS

Keep iteration screenshots, e.g.:
`tmp/chris-match-01.png`
`tmp/chris-match-02.png`
...

## Content accuracy
This is a prototype, so visual fidelity is the priority. Do not invent huge archive statistics as factual claims. Generic phrasing such as `A lifetime`, `Many languages`, etc. is acceptable.

## Responsive check
After desktop matching is strong, verify at:
- 1440px desktop
- 768px tablet
- 390px mobile

Do not degrade the 1122px target match merely to improve mobile aesthetics.

## Constraints
- Keep this isolated to `chris-gaca/mockups/`.
- Do not modify unrelated shared repo projects.
- Plain HTML/CSS/JS is preferred.
- Do not introduce a framework unless absolutely necessary.
- Do not replace supplied image assets with stock photography.

## Completion
Before stopping:
1. Capture final 1122x1367 screenshot.
2. Compare it against the reference.
3. Do one final discrepancy pass.
4. Check console errors, broken images, overflow, fonts, and horizontal scroll.
5. Commit the finished result.

Report:
- final commit SHA
- files changed
- final screenshot path
- remaining visible differences, if any
- confirmation that Playwright verification was performed at 1122x1367

Do not claim pixel-perfect if obvious differences remain.
