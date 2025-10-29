# Excel component

This component provides the UI skeleton for the Excel comparator. It supports progressive enhancement:

- Server-only flow (no JS): form posts to the server; server renders columns and results.
- JS-enhanced flow: `excel.js` will upload both files to `columnsUrl` and render selectable columns dynamically.

Files in this folder:

- `excel.html` — Jinja partial to include in pages.
- `excel.css` — small overrides and tokens complementing Tailwind.
- `excel.js` — optional JS to enhance UX.

Initialization:

The template injects a JSON config under `#excel-config` which should contain `columnsUrl` and `compareUrl`.

Include example:

{% raw %}{% include 'components/excel/excel.html' %}{% endraw %}
