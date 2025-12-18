/* Scripts for the Smart Excel Toolbox page */

// --- Inline tool group + popovers (compare/merge/export) ---
(function () {
  const group = document.getElementById('inlineToolGroup');
  if (!group) return;

  group.addEventListener('click', (ev) => {
    const btn = ev.target.closest('.tool-btn');
    if (!btn) return;
    const action = btn.dataset.action;
    const chk = document.getElementById(`chk-${action}`);
    if (!chk) return;
    const next = !chk.checked;
    chk.checked = next;
    btn.setAttribute('aria-pressed', String(next));
  });

  group.querySelectorAll('.tool-btn').forEach((btn) => {
    const action = btn.dataset.action;
    const chk = document.getElementById(`chk-${action}`);
    if (chk) btn.setAttribute('aria-pressed', String(chk.checked));
  });
})();

(function () {
  const chk = document.getElementById('chk-compare');
  const btn = document.getElementById('compareBtn');
  const pop = document.getElementById('comparePopover');
  const sel = document.getElementById('compareModeSelect');
  const badge = document.getElementById('compareBadge');
  const strict = document.getElementById('compareStrict');
  const applyBtn = document.getElementById('compareApplyBtn');

  const labelMap = { columns: 'Columns', values: 'Values', summary: 'Summary' };

  function refresh() {
    if (!badge || !sel) return;
    badge.textContent = labelMap[sel.value] || 'Columns';
    if (btn && chk) btn.setAttribute('aria-pressed', String(chk.checked));
  }

  let hideTimer = null;
  function showPopover() {
    if (!pop) return;
    clearTimeout(hideTimer);
    pop.classList.remove('hidden');
  }
  function hidePopoverSoon() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => pop?.classList.add('hidden'), 120);
  }

  btn?.addEventListener('click', showPopover);
  ['pointerenter', 'mouseenter'].forEach((ev) => btn?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach((ev) => btn?.addEventListener(ev, hidePopoverSoon));
  ['pointerenter', 'mouseenter'].forEach((ev) => pop?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach((ev) => pop?.addEventListener(ev, hidePopoverSoon));
  btn?.addEventListener('focus', showPopover);
  btn?.addEventListener('blur', hidePopoverSoon);
  pop?.addEventListener('focusout', hidePopoverSoon);

  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape') pop?.classList.add('hidden');
  });

  applyBtn?.addEventListener('click', () => {
    if (chk) chk.checked = true;
    refresh();
    pop?.classList.add('hidden');
  });

  sel?.addEventListener('change', refresh);
  chk?.addEventListener('change', refresh);
  refresh();
})();

(function () {
  const chk = document.getElementById('chk-merge');
  const btn = document.getElementById('mergeBtn');
  const pop = document.getElementById('mergePopover');
  const sel = document.getElementById('mergeModeSelect');
  const badge = document.getElementById('mergeBadge');
  const keep = document.getElementById('mergeKeepUnmatched');
  const applyBtn = document.getElementById('mergeApplyBtn');

  const labelMap = { inner: 'Inner', left: 'Left', right: 'Right', outer: 'Outer' };

  function refresh() {
    if (badge && sel) badge.textContent = labelMap[sel.value] || 'Inner';
    if (btn && chk) btn.setAttribute('aria-pressed', String(chk.checked));
  }

  let hideTimer = null;
  function showPopover() {
    if (!pop) return;
    clearTimeout(hideTimer);
    pop.classList.remove('hidden');
  }
  function hidePopoverSoon() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => pop?.classList.add('hidden'), 120);
  }

  btn?.addEventListener('click', showPopover);
  ['pointerenter', 'mouseenter'].forEach((ev) => btn?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach((ev) => btn?.addEventListener(ev, hidePopoverSoon));
  ['pointerenter', 'mouseenter'].forEach((ev) => pop?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach((ev) => pop?.addEventListener(ev, hidePopoverSoon));
  btn?.addEventListener('focus', showPopover);
  btn?.addEventListener('blur', hidePopoverSoon);
  pop?.addEventListener('focusout', hidePopoverSoon);

  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape') pop?.classList.add('hidden');
  });

  applyBtn?.addEventListener('click', () => {
    if (chk) chk.checked = true;
    refresh();
    pop?.classList.add('hidden');
  });

  sel?.addEventListener('change', refresh);
  chk?.addEventListener('change', refresh);
  refresh();
})();

(function () {
  const chk = document.getElementById('chk-export');
  const btn = document.getElementById('exportBtn');
  const pop = document.getElementById('exportPopover');
  const sel = document.getElementById('exportFormatSelect');
  const badge = document.getElementById('exportBadge');
  const headers = document.getElementById('exportWithHeaders');
  const applyBtn = document.getElementById('exportApplyBtn');

  const labelMap = { xlsx: 'XLSX', csv: 'CSV', json: 'JSON' };

  function refresh() {
    if (badge && sel) badge.textContent = labelMap[sel.value] || 'XLSX';
    if (btn && chk) btn.setAttribute('aria-pressed', String(chk.checked));
  }

  let hideTimer = null;
  function showPopover() {
    if (!pop) return;
    clearTimeout(hideTimer);
    pop.classList.remove('hidden');
  }
  function hidePopoverSoon() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => pop?.classList.add('hidden'), 120);
  }

  btn?.addEventListener('click', showPopover);
  ['pointerenter', 'mouseenter'].forEach((ev) => btn?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach((ev) => btn?.addEventListener(ev, hidePopoverSoon));
  ['pointerenter', 'mouseenter'].forEach((ev) => pop?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach((ev) => pop?.addEventListener(ev, hidePopoverSoon));
  btn?.addEventListener('focus', showPopover);
  btn?.addEventListener('blur', hidePopoverSoon);
  pop?.addEventListener('focusout', hidePopoverSoon);

  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape') pop?.classList.add('hidden');
  });

  applyBtn?.addEventListener('click', () => {
    if (chk) chk.checked = true;
    refresh();
    pop?.classList.add('hidden');
  });

  sel?.addEventListener('change', refresh);
  chk?.addEventListener('change', refresh);
  refresh();
})();

// --- Core state and helpers ---
const config = window.excelToolboxConfig || {};
const serverContext = window.excelServerContext || {};
const columnsUrl = config.columnsUrl || '';

const uploadInput = document.getElementById('excelUpload');
const uploadDrop = document.getElementById('uploadDrop');
const browseBtn = document.getElementById('browseBtn');
const file1Input = document.getElementById('file1');
const file2Input = document.getElementById('file2');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const columnsSection = document.getElementById('columns-section');
const mergeDiv = document.getElementById('merge-columns');
const compareDiv = document.getElementById('compare-columns');
const statusMessage = document.getElementById('statusMessage');
const sheetsList = document.getElementById('sheetsList');
const columnsList = document.getElementById('columnsList');
const previewTable = document.getElementById('previewTable');
const selectedFilename = document.getElementById('selectedFilename');
const selectedSheet = document.getElementById('selectedSheet');
const selectedColumns = document.getElementById('selectedColumns');
const selectedRows = document.getElementById('selectedRows');
const uploadedFilesCount = document.getElementById('uploadedFilesCount');
const explorerList = document.getElementById('uploadedFilesExplorerList');
const generatedList = document.getElementById('generatedList');
const sheetCount = document.getElementById('sheetCount');
const columnCount = document.getElementById('columnCount');
const formEl = document.getElementById('excelForm');

const filesState = [];
const perFileState = {};
let activeFileId = null;

function uuid() {
  return (typeof crypto !== 'undefined' && crypto.randomUUID) ? crypto.randomUUID() : `f-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function debounce(fn, wait) {
  let t = null;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

function storageKey(id) {
  return `rx_excel_state_${id}`;
}

function savePerFileState(id) {
  if (!id || !perFileState[id]) return;
  try {
    localStorage.setItem(storageKey(id), JSON.stringify(perFileState[id]));
  } catch (_) {
    /* ignore quota errors */
  }
}

function loadPerFileState(id) {
  if (!id) return null;
  try {
    const raw = localStorage.getItem(storageKey(id));
    if (raw) return JSON.parse(raw);
  } catch (_) {
    return null;
  }
  return null;
}

function humanSize(bytes) {
  if (!bytes && bytes !== 0) return '-';
  const units = ['B', 'KB', 'MB', 'GB'];
  let b = bytes;
  let i = 0;
  while (b >= 1024 && i < units.length - 1) {
    b /= 1024;
    i += 1;
  }
  return `${b.toFixed(1)} ${units[i]}`;
}

function updateStatus(msg, variant = 'info') {
  if (!statusMessage) return;
  statusMessage.textContent = msg || '';
  statusMessage.classList.remove('text-red-700', 'text-emerald-700');
  if (variant === 'error') statusMessage.classList.add('text-red-700');
  if (variant === 'success') statusMessage.classList.add('text-emerald-700');
}

function setFileInputFromFile(input, file) {
  if (!input) return;
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
}

// --- Upload + parsing ---
async function parseWorkbook(file, record) {
  try {
    const buf = await file.arrayBuffer();
    const wb = XLSX.read(buf, { type: 'array' });
    const sheetNames = wb.SheetNames || [];
    record.sheets = sheetNames;
    record.selectedSheet = record.selectedSheet || sheetNames[0] || '';
    const sheet = wb.Sheets[record.selectedSheet];
    const rows = sheet ? XLSX.utils.sheet_to_json(sheet, { header: 1 }) : [];
    record.sample = rows.slice(0, 20);
    record.columns = (rows[0] || []).map((c) => String(c || ''));
    perFileState[record.id] = {
      selectedSheet: record.selectedSheet,
      columns: record.columns,
    };
    savePerFileState(record.id);
    if (record.id === activeFileId) {
      renderSheets();
      renderColumns();
      renderPreview();
    }
    renderExplorer();
  } catch (err) {
    updateStatus(`Could not read ${file.name}`, 'error');
    console.error(err);
  }
}

function registerFile(file) {
  const id = uuid();
  const restored = loadPerFileState(id) || {};
  const record = {
    id,
    file,
    name: file.name,
    size: file.size,
    sheets: [],
    columns: restored.columns || [],
    selectedSheet: restored.selectedSheet || '',
    sample: [],
  };
  filesState.push(record);
  if (!activeFileId) activeFileId = record.id;
  renderExplorer();
  parseWorkbook(file, record);
}

function assignHiddenInputs() {
  if (filesState[0]) setFileInputFromFile(file1Input, filesState[0].file);
  if (filesState[1]) setFileInputFromFile(file2Input, filesState[1].file);
  if (filesState[0] && filesState[1]) {
    fetchCommonColumns();
  }
}

function renderExplorer() {
  if (!explorerList) return;
  explorerList.innerHTML = '';
  if (!filesState.length) {
    explorerList.innerHTML = '<div class="text-xs text-gray-500">No files uploaded yet.</div>';
  }
  filesState.forEach((f, idx) => {
    const wrap = document.createElement('div');
    const isActive = f.id === activeFileId;
    const role = idx === 0 ? 'File 1' : idx === 1 ? 'File 2' : 'Extra';
    wrap.className = `flex items-center justify-between p-2 bg-white rounded-md border ${isActive ? 'border-emerald-300' : 'border-gray-200'}`;
    wrap.innerHTML = `
      <div class="flex flex-col">
        <button type="button" class="text-left text-sm font-medium text-gray-800 file-row">${f.name}</button>
        <span class="text-xs text-gray-500">${role} · ${humanSize(f.size)}</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="badge-pill">${role}</span>
        <button type="button" class="text-xs text-emerald-700 underline preview-file" data-id="${f.id}">Preview</button>
        <button type="button" class="text-xs text-red-500 underline remove-file" data-id="${f.id}">Remove</button>
      </div>
    `;
    explorerList.appendChild(wrap);
  });
  if (uploadedFilesCount) uploadedFilesCount.textContent = String(filesState.length);
  explorerList.querySelectorAll('.file-row, .preview-file').forEach((btn) => {
    btn.addEventListener('click', (ev) => {
      const id = ev.currentTarget.getAttribute('data-id') || filesState.find((f) => f.name === ev.currentTarget.textContent)?.id;
      if (!id) return;
      activeFileId = id;
      renderExplorer();
      renderSheets();
      renderColumns();
      renderPreview();
    });
  });
  explorerList.querySelectorAll('.remove-file').forEach((btn) => {
    btn.addEventListener('click', (ev) => {
      const id = ev.currentTarget.getAttribute('data-id');
      const idx = filesState.findIndex((f) => f.id === id);
      if (idx !== -1) filesState.splice(idx, 1);
      if (activeFileId === id) activeFileId = filesState[0]?.id || null;
      renderExplorer();
      renderSheets();
      renderColumns();
      renderPreview();
      assignHiddenInputs();
    });
  });
  assignHiddenInputs();
}

function renderSheets() {
  if (!sheetsList) return;
  const current = filesState.find((f) => f.id === activeFileId);
  sheetsList.innerHTML = '';
  if (!current || !current.sheets.length) {
    sheetsList.innerHTML = '<div class="text-xs text-gray-500">No sheets yet.</div>';
    if (sheetCount) sheetCount.textContent = '0';
    return;
  }
  current.sheets.forEach((sheet) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = sheet;
    btn.className = `w-full text-left px-2 py-1 rounded-md text-sm mb-1 ${sheet === current.selectedSheet ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-white border border-gray-200 text-gray-700'}`;
    btn.addEventListener('click', () => {
      current.selectedSheet = sheet;
      perFileState[current.id] = perFileState[current.id] || {};
      perFileState[current.id].selectedSheet = sheet;
      savePerFileState(current.id);
      parseWorkbook(current.file, current);
      renderSheets();
    });
    sheetsList.appendChild(btn);
  });
  if (sheetCount) sheetCount.textContent = String(current.sheets.length);
}

function renderColumns() {
  if (!columnsList) return;
  const current = filesState.find((f) => f.id === activeFileId);
  columnsList.innerHTML = '';
  if (!current || !current.columns.length) {
    columnsList.innerHTML = '<div class="text-xs text-gray-500">Columns will appear after preview loads.</div>';
    if (columnCount) columnCount.textContent = '0';
    return;
  }
  current.columns.forEach((col) => {
    const chip = document.createElement('span');
    chip.className = 'checkbox-chip mb-1';
    chip.innerHTML = `<input type="checkbox" checked disabled><span>${col}</span>`;
    columnsList.appendChild(chip);
  });
  if (columnCount) columnCount.textContent = String(current.columns.length);
}

function renderPreview() {
  if (!previewTable) return;
  const current = filesState.find((f) => f.id === activeFileId);
  if (!current) {
    previewTable.innerHTML = '<div class="text-sm text-gray-500">Upload a file to see a preview.</div>';
    selectedFilename.textContent = 'None';
    selectedSheet.textContent = 'None';
    selectedColumns.textContent = '0';
    selectedRows.textContent = '0';
    return;
  }
  selectedFilename.textContent = current.name;
  selectedSheet.textContent = current.selectedSheet || 'First sheet';
  selectedColumns.textContent = String(current.columns.length || 0);
  selectedRows.textContent = String((current.sample?.length || 0) - 1);

  if (!current.sample || !current.sample.length) {
    previewTable.innerHTML = '<div class="text-sm text-gray-500">No data found in this sheet.</div>';
    return;
  }
  const [header = [], ...rows] = current.sample;
  const thead = header.map((h) => `<th>${h || ''}</th>`).join('');
  const tbody = rows
    .map((r) => `<tr>${(r || []).map((c) => `<td>${c ?? ''}</td>`).join('')}</tr>`)
    .join('');
  previewTable.innerHTML = `<table class="table-preview"><thead><tr>${thead}</tr></thead><tbody>${tbody}</tbody></table>`;
}

const fetchCommonColumns = debounce(async () => {
  if (!columnsUrl || !file1Input?.files?.length || !file2Input?.files?.length) return;
  loadingDiv?.classList.remove('hidden');
  errorDiv?.classList.add('hidden');
  try {
    const fd = new FormData();
    fd.append('file1', file1Input.files[0]);
    fd.append('file2', file2Input.files[0]);
    const resp = await fetch(columnsUrl, { method: 'POST', body: fd });
    const data = await resp.json();
    loadingDiv?.classList.add('hidden');
    if (!resp.ok || data.error) {
      if (errorDiv) {
        errorDiv.textContent = data.error || 'Unable to fetch columns';
        errorDiv.classList.remove('hidden');
      }
      return;
    }
    populateColumnSelectors(data.columns || []);
  } catch (err) {
    loadingDiv?.classList.add('hidden');
    if (errorDiv) {
      errorDiv.textContent = `Error fetching columns: ${err}`;
      errorDiv.classList.remove('hidden');
    }
  }
}, 200);

function populateColumnSelectors(columns) {
  if (!Array.isArray(columns)) return;
  mergeDiv.innerHTML = '';
  compareDiv.innerHTML = '';
  columns.forEach((col) => {
    const mergeLabel = document.createElement('label');
    mergeLabel.className = 'checkbox-chip';
    mergeLabel.innerHTML = `<input type="checkbox" name="merge_keys" value="${col}"><span>${col}</span>`;
    mergeDiv.appendChild(mergeLabel);

    const compareLabel = document.createElement('label');
    compareLabel.className = 'checkbox-chip';
    compareLabel.innerHTML = `<input type="checkbox" name="compare_columns" value="${col}" checked><span>${col}</span>`;
    compareDiv.appendChild(compareLabel);
  });
  columnsSection?.classList.remove('hidden');
}

// --- Events ---
uploadInput?.addEventListener('change', (e) => {
  const files = Array.from(e.target.files || []);
  files.forEach(registerFile);
  uploadInput.value = '';
});

browseBtn?.addEventListener('click', () => uploadInput?.click());

if (uploadDrop) {
  uploadDrop.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadDrop.classList.add('dragging');
  });
  uploadDrop.addEventListener('dragleave', () => uploadDrop.classList.remove('dragging'));
  uploadDrop.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadDrop.classList.remove('dragging');
    const files = Array.from(e.dataTransfer?.files || []);
    files.forEach(registerFile);
  });
}

document.getElementById('clearFileBtn')?.addEventListener('click', () => {
  filesState.splice(0, filesState.length);
  activeFileId = null;
  if (explorerList) explorerList.innerHTML = '';
  if (columnsList) columnsList.innerHTML = '';
  if (sheetsList) sheetsList.innerHTML = '';
  if (previewTable) previewTable.innerHTML = '';
  if (uploadedFilesCount) uploadedFilesCount.textContent = '0';
  if (sheetCount) sheetCount.textContent = '0';
  if (columnCount) columnCount.textContent = '0';
  file1Input.value = '';
  file2Input.value = '';
  columnsSection?.classList.add('hidden');
  updateStatus('Cleared uploads');
});

document.getElementById('selectAllBtn')?.addEventListener('click', () => {
  previewTable.querySelectorAll('tbody input[type="checkbox"]').forEach((cb) => (cb.checked = true));
});

document.getElementById('clearAllBtn')?.addEventListener('click', () => {
  previewTable.querySelectorAll('tbody input[type="checkbox"]').forEach((cb) => (cb.checked = false));
});

document.getElementById('selectAllBtnFiles')?.addEventListener('click', () => {
  if (!explorerList) return;
  explorerList.querySelectorAll('input[type="checkbox"]').forEach((cb) => (cb.checked = true));
});

document.getElementById('clearAllBtnFiles')?.addEventListener('click', () => {
  if (!explorerList) return;
  explorerList.querySelectorAll('input[type="checkbox"]').forEach((cb) => (cb.checked = false));
});

document.getElementById('explorerToggle')?.addEventListener('click', (e) => {
  if (!explorerList) return;
  const hidden = explorerList.classList.toggle('hidden');
  e.currentTarget.setAttribute('aria-expanded', String(!hidden));
  e.currentTarget.textContent = hidden ? 'Expand' : 'Collapse';
});

const generateBtn = document.getElementById('generateBtn');
generateBtn?.addEventListener('click', () => {
  if (!file1Input?.files?.length || !file2Input?.files?.length) {
    updateStatus('Please upload at least two files to compare.', 'error');
    return;
  }
  updateStatus('Submitting files for comparison...');
  formEl?.requestSubmit();
});

// On load: show server-side results if present
(function showServerDownloads() {
  if (!generatedList) return;
  const links = [];
  if (serverContext.download1) links.push({ label: 'File 1 comparison', file: serverContext.download1 });
  if (serverContext.download2) links.push({ label: 'File 2 comparison', file: serverContext.download2 });
  generatedList.innerHTML = '';
  links.forEach((item) => {
    const li = document.createElement('li');
    li.innerHTML = `<a class="text-emerald-700 hover:underline" href="${(config.downloadBase || '') + item.file}">📥 ${item.label}</a>`;
    generatedList.appendChild(li);
  });
  if (links.length) launchConfetti();
})();

// --- Confetti (lightweight) ---
function launchConfetti() {
  const canvas = document.getElementById('confetti-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = (canvas.width = window.innerWidth);
  const h = (canvas.height = window.innerHeight);
  const pieces = Array.from({ length: 120 }, () => ({
    x: Math.random() * w,
    y: Math.random() * h - h,
    r: 4 + Math.random() * 4,
    c: `hsl(${130 + Math.random() * 40},70%,60%)`,
    s: 2 + Math.random() * 2,
    a: 0.5 + Math.random(),
  }));

  function draw() {
    ctx.clearRect(0, 0, w, h);
    pieces.forEach((p) => {
      ctx.fillStyle = p.c;
      ctx.globalAlpha = p.a;
      ctx.fillRect(p.x, p.y, p.r, p.r * 0.6);
      p.y += p.s;
      if (p.y > h) p.y = -10;
    });
    requestAnimationFrame(draw);
  }
  draw();
  setTimeout(() => ctx.clearRect(0, 0, w, h), 3000);
}

// kick off with any preselected files (if the server re-rendered after submit)
assignHiddenInputs();
renderExplorer();
renderSheets();
renderColumns();
renderPreview();
