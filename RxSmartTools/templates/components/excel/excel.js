/* Excel component JS (progressive enhancement)
   - Reads config from #excel-config
   - Handles file preview, fetch columns via AJAX, renders checkboxes safely
   - Keeps form fallback when JS disabled
*/
(function () {
  'use strict';

  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

  function createCheckbox(name, value, text) {
    const label = document.createElement('label');
    label.className = 'excel-checkbox-label inline-flex items-center gap-2';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.name = name;
    input.value = value;
    label.appendChild(input);
    label.appendChild(document.createTextNode(text));
    return label;
  }

  async function fetchJson(url, options = {}) {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error('Network response was not ok');
    return res.json();
  }

  function renderColumns(container, columns, name) {
    container.textContent = '';
    columns.forEach(col => container.appendChild(createCheckbox(name, col, col)));
  }

  function init() {
    const configNode = document.getElementById('excel-config');
    const config = configNode ? JSON.parse(configNode.textContent) : {};
    const file1 = qs('#file1');
    const file2 = qs('#file2');
    const status = qs('#status');
    const columnsSection = qs('#columns-section');
    const mergeContainer = qs('#merge-columns');
    const compareContainer = qs('#compare-columns');
    const uploadIdInput = qs('#upload_id');

    function showStatus(msg) { if (status) status.textContent = msg; }

    async function getColumns() {
      if (!file1.files.length || !file2.files.length) return;
      showStatus('Checking columns...');
      const fd = new FormData();
      fd.append('file1', file1.files[0]);
      fd.append('file2', file2.files[0]);
      try {
        const data = await fetchJson(config.columnsUrl, { method: 'POST', body: fd });
        if (data.error) { showStatus(data.error); return; }
        renderColumns(mergeContainer, data.columns, 'merge_keys');
        renderColumns(compareContainer, data.columns, 'compare_columns');
        columnsSection.classList.remove('hidden');
        if (uploadIdInput && data.upload_id) uploadIdInput.value = data.upload_id;
        showStatus('Columns loaded');
      } catch (err) {
        showStatus('Error fetching columns: ' + err.message);
      }
    }

    [file1, file2].forEach(el => el && el.addEventListener('change', () => {
      // small debounce
      setTimeout(getColumns, 300);
    }));

    // select-all handlers
    qsa('[data-action="merge-select-all"]').forEach(btn => btn.addEventListener('click', () => {
      qsa('#merge-columns input[type=checkbox]').forEach(cb => cb.checked = true);
    }));
    qsa('[data-action="compare-select-all"]').forEach(btn => btn.addEventListener('click', () => {
      qsa('#compare-columns input[type=checkbox]').forEach(cb => cb.checked = true);
    }));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
