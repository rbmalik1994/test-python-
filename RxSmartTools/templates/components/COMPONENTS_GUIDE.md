# Components Guide — Global strategies and component contracts

This document collects the remaining plans and decisions for the `templates/components/` architecture: Global CSS strategy, JS enhancement policy, server endpoint mapping, progressive enhancement flows, accessibility and i18n checklist, security & performance rules, testing & CI plan, migration steps, and an optional build pipeline.

---

## 1. Global CSS strategy

- Decision: Use Tailwind for utilities and a small `global.css` for CSS variables and edge-case helpers. During development use CDN; for production consider building Tailwind to reduce unused CSS.

- Rationale:
  - Tailwind utilities speed UI iteration and keep components consistent.
  - A small `global.css` stores tokens like `--brand`, `--accent`, `--radius` and tiny helpers not covered by Tailwind.

- Implementation options:
  1. CDN (fast to implement): include Tailwind CDN link in `_header.html`. Good for prototypes and small apps.
  2. Build (recommended for production): add Tailwind CLI or PostCSS pipeline to generate a production CSS file (purged) saved to `static/css/main.css` and referenced by `_header.html`.

- Example `global.css` tokens (place in `static/css/global.css` or `components/*/component.css`):

  :root {
    --brand: #4f46e5; /* indigo-600 */
    --accent: #06b6d4; /* teal-400 */
    --radius: 0.5rem;
  }

- Acceptance criteria:
  - Tailwind is included via `_header.html` (CDN or built file).
  - `global.css` exists with declared tokens and is imported after Tailwind.

## 2. JS enhancement policy

- Pattern: Progressive enhancement. Each component may ship an optional `component.js` that enhances the static HTML but is not required for baseline functionality.

- Module style:
  - Prefer ES modules (`<script type="module">`) if you use a modern build pipeline. For no-build setups use an IIFE pattern and attach to a single global namespace, e.g. `window.Components = window.Components || {}; Components.Excel = { init(config) { ... } };`.

- Public init API (recommended):
  - `Components.Excel.init(config)` — where `config` contains `columnsUrl`, `compareUrl`, and selectors or element references.

- Naming & asset placement:
  - `templates/components/<component>/<component>.js` — canonical source.
  - Build outputs (optional): `static/js/components/<component>.min.js`.

- Acceptance criteria:
  - Documented `init` API in each component `README.md`.
  - Component JS uses safe DOM rendering (no innerHTML with untrusted content).

## 3. Server endpoint mapping (examples)

General rules:
  - Each component supports JSON endpoints for AJAX + HTML fallback for no-JS clients.
  - Uploads return an `upload_id` for multi-step flows; server retains temporary files keyed by that ID.

Example: Excel component

- POST `/excel/columns` (AJAX)
  - Request: multipart/form-data { file1, file2 }
  - Response 200 JSON: { columns: ["A","B","C"], upload_id: "<uuid>" }
  - Errors: 400 for missing files, 422 for unreadable files, 413 for too large

- POST `/excel/compare` (form POST or AJAX)
  - Request: form fields { upload_id } OR files { file1, file2 } and arrays `merge_keys[]`, `compare_columns[]`
  - Response HTML: page with download links; OR JSON: { results: [ { filename, url } ], stats: { matched: n } }

Example: PDF component

- POST `/pdf/upload`
  - Request: multipart { pdf }
  - Response JSON: { filename, total_pages }

- POST `/pdf/process`
  - Request JSON: { filename, actions: ["merge","split"], pages: [1,2,5], rotations: {"1":90} }
  - Response JSON: { generated: ["out1.pdf"] }

Acceptance criteria:
  - Route list documented for each component with request and response shapes.

## 4. Progressive enhancement flow (JS vs no-JS)

Excel component (JS-enhanced):
  1. User selects both files in the form.
  2. `excel.js` intercepts file inputs and sends POST `/excel/columns` via AJAX.
  3. Server returns `columns` + `upload_id`.
  4. JS renders merge & compare checkboxes and fills hidden `upload_id`.
  5. User selects columns and submits; JS sends `/excel/compare` (AJAX) or lets the form submit normally.

Excel (no-JS fallback):
  1. User uploads both files via form POST to `/excel/compare`.
  2. Server extracts columns and re-renders the page with column checkbox groups.
  3. User selects columns and posts the form again; server generates results and renders download links.

UX notes:
  - Always show an aria-live `status` area for messages. After AJAX completion set focus to first interactive element (first checkbox or download link).

## 5. Accessibility & internationalization

- Accessibility checklist (apply to each component):
  - All inputs have `<label for>` or wrapped labels.
  - Group checkboxes in `<fieldset>` with `<legend>` for context.
  - Use `role="status"` and `aria-live="polite"` for loading/errors.
  - Ensure keyboard navigation for select-all buttons and checkboxes.
  - Provide visible focus states (Tailwind `focus:ring-2` etc.).
  - Ensure color contrast (WCAG AA) for buttons and alerts.

- i18n approach:
  - Keep UI strings in Jinja template variables or use Flask-Babel for translations.
  - For JS-rendered strings, embed a small `data-i18n` JSON block in the page or use `data-*` attributes delivered by the server.

Acceptance criteria:
  - A11y checklist documented and example `fieldset` usage present in `components/*/README.md`.

## 6. Security & performance guidelines

- Server config recommendations (Flask):
  - MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB (adjust as needed)
  - Allowed extensions: {'csv','xlsx','xls','pdf'} and validate MIME types where possible.
  - Use secure temporary directories with UUID-based filenames; remove after processing.
  - Sanitize any returned filenames and serve generated files via signed URLs or a protected route.

- Performance:
  - For large files, offload heavy processing to a background worker (Celery/RQ) and provide pollable status endpoints.
  - Cache static assets (CSS/JS) with long TTLs and fingerprinted filenames in production.

Acceptance criteria:
  - Security checklist present and Flask recommended settings documented.

## 7. Testing & CI plan

- Tests to write:
  - Flask endpoints: pytest tests for `/excel/columns`, `/excel/compare` and file validation edge cases. Use small fixture files in `tests/fixtures/`.
  - JS logic: jest + jsdom tests for `renderColumns`, `createCheckbox`, and event wiring.
  - Linting: ESLint for JS, stylelint for CSS, and ruff/flake8 for Python.

- Suggested GitHub Actions workflow steps:
  - Checkout, set up Python, install deps, run `ruff`/`pytest`.
  - Install Node (if using JS tests), run ESLint and jest, and fail on errors.

Acceptance criteria:
  - Test templates and a sample CI job are documented.

## 8. Migration & incremental plan

Objective: Replace `templates/excel.html` with `templates/components/excel/excel.html` without downtime.

Steps:
  1. Create a feature branch `feature/componentize-excel`.
  2. Copy UI into `templates/components/excel/excel.html` (already done for skeleton).
  3. Add `include` in the page that previously referenced `excel.html`: replace content with `{% include 'components/excel/excel.html' %}`.
  4. Keep old `templates/excel.html` as backup for quick revert.
  5. Deploy to staging and test both JS and no-JS flows.
  6. Once validated, remove old `templates/excel.html` and tidy imports.

Acceptance criteria:
  - New component included via Jinja include; staging tests for both flows pass.

## 9. Optional build pipeline (minimal)

- Minimal `package.json` sketch (optional):

  {
    "name": "rxsmarttools-front",
    "private": true,
    "devDependencies": {
      "tailwindcss": "^3.0.0",
      "esbuild": "^0.17.0"
    },
    "scripts": {
      "build:css": "tailwindcss -i ./src/input.css -o ./static/css/main.css --minify",
      "build:js": "esbuild ./src/js/index.js --bundle --outfile=./static/js/bundle.js --minify"
    }
  }

- Acceptance criteria:
  - If a build pipeline is required, provide this `package.json` and a short README describing build steps.

---

If you'd like, I can now:

- Implement the `excel.html` to inject an `#excel-config` JSON block (so `excel.js` can read `columnsUrl` and `compareUrl`) and include the `excel.js` script tag in `_footer.html`.
- Or implement the Flask endpoints `/excel/columns` and `/excel/compare` to complete the flow.

Which action should I take next? (I will update the todo list as I complete it.)
