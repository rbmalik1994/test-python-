/* Scripts for the Smart PDF Toolbox page */

(function () {
  // Improved popover hover/focus handlers for Compress popover.
  const chk = document.getElementById('chk-compress');
  const btn = document.getElementById('compressBtn');
  const pop = document.getElementById('compressPopover');
  const sel = document.getElementById('compressLevelSelect');
  const badge = document.getElementById('compressBadge');
  const applyBtn = document.getElementById('compressApplyBtn');

  const labelMap = { default: 'Balanced', fast: 'Fast', best: 'Best', none: 'None' };

  function refreshButtonUI() {
    const level = sel ? sel.value : 'default';
    const pretty = labelMap[level] || level;
    if (chk && chk.checked) {
      badge.innerText = pretty;
      badge.classList.remove('hidden');
      btn.setAttribute('aria-pressed', 'true');
      btn.classList.add('bg-red-50', 'border-red-300');
    } else {
      badge.classList.add('hidden');
      btn.setAttribute('aria-pressed', 'false');
      btn.classList.remove('bg-red-50', 'border-red-300');
    }
    if (typeof updateCompressInfo === 'function') updateCompressInfo();
  }

  let hideTimer = null;
  function showPopover() {
    if (!pop) return;
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
    pop.classList.remove('hidden');
    btn.setAttribute('aria-expanded', 'true');
    adjustPopover();
  }
  function hidePopoverSoon() {
    if (!pop) return;
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
      pop.classList.add('hidden');
      btn.setAttribute('aria-expanded', 'false');
    }, 220);
  }

  btn?.addEventListener('click', (ev) => {
    ev.preventDefault();
    if (chk) {
      chk.checked = !chk.checked;
      if (chk.checked) btn.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.04)' }, { transform: 'scale(1)' }], { duration: 260 });
    }
    refreshButtonUI();
    try { if (chk && chk.checked) showPopover(); else hidePopoverSoon(); } catch (e) { /* ignore */ }
  });

  ['pointerenter', 'mouseenter'].forEach(ev => btn?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach(ev => btn?.addEventListener(ev, hidePopoverSoon));
  ['pointerenter', 'mouseenter'].forEach(ev => pop?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach(ev => pop?.addEventListener(ev, hidePopoverSoon));

  btn?.addEventListener('focus', showPopover);
  btn?.addEventListener('blur', hidePopoverSoon);
  pop?.addEventListener('focusout', hidePopoverSoon);
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape') {
      if (pop) pop.classList.add('hidden');
      btn?.setAttribute('aria-expanded', 'false');
      btn?.focus();
    }
  });

  applyBtn?.addEventListener('click', () => {
    if (chk) chk.checked = true;
    refreshButtonUI();
    if (pop) pop.classList.add('hidden');
    btn?.setAttribute('aria-expanded', 'false');
    btn?.focus();
    if (sel && sel.value === 'best') { try { launchConfetti(); } catch (e) { /* ignore */ } }
  });

  sel?.addEventListener('change', refreshButtonUI);
  refreshButtonUI();
  chk?.addEventListener('change', refreshButtonUI);

  function adjustPopover() {
    if (!pop) return;
    const rect = pop.getBoundingClientRect();
    if (rect.right > window.innerWidth - 8) { pop.style.right = '0'; pop.style.left = 'auto'; }
    else { pop.style.left = ''; pop.style.right = ''; }
  }
  window.addEventListener('resize', adjustPopover);
  setTimeout(adjustPopover, 50);
})();

(function () {
  // Improved popover hover/focus handlers for Merge popover.
  const chk = document.getElementById('chk-merge');
  const btn = document.getElementById('mergeBtn');
  const pop = document.getElementById('mergePopover');
  const sel = document.getElementById('mergeModePages');
  const badge = document.getElementById('mergeBadge');
  const applyBtn = document.getElementById('mergeApplyBtn');

  const labelMap = { default: 'Pages', pages: 'Pages', files: 'Files', files_pages: 'Files + Pages', none: 'None' };

  function refreshButtonUI() {
    const level = sel ? sel.value : 'default';
    const pretty = labelMap[level] || level;
    if (chk && chk.checked) {
      badge.innerText = pretty;
      badge.classList.remove('hidden');
      btn.setAttribute('aria-pressed', 'true');
      btn.classList.add('bg-red-50', 'border-red-300');
    } else {
      badge.classList.add('hidden');
      btn.setAttribute('aria-pressed', 'false');
      btn.classList.remove('bg-red-50', 'border-red-300');
    }
    if (typeof parsePagesInput === 'function') parsePagesInput();
  }

  let hideTimer = null;
  function showPopover() {
    if (!pop) return;
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
    pop.classList.remove('hidden');
    btn.setAttribute('aria-expanded', 'true');
    adjustPopover();
  }
  function hidePopoverSoon() {
    if (!pop) return;
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
      pop.classList.add('hidden');
      btn.setAttribute('aria-expanded', 'false');
    }, 220);
  }

  btn?.addEventListener('click', (ev) => {
    ev.preventDefault();
    if (chk) {
      chk.checked = !chk.checked;
      if (chk.checked) btn.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.04)' }, { transform: 'scale(1)' }], { duration: 220 });
    }
    refreshButtonUI();
    try { if (chk && chk.checked) showPopover(); else hidePopoverSoon(); } catch (e) { /* ignore */ }
  });

  ['pointerenter', 'mouseenter'].forEach(ev => btn?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach(ev => btn?.addEventListener(ev, hidePopoverSoon));
  ['pointerenter', 'mouseenter'].forEach(ev => pop?.addEventListener(ev, showPopover));
  ['pointerleave', 'mouseleave'].forEach(ev => pop?.addEventListener(ev, hidePopoverSoon));

  btn?.addEventListener('focus', showPopover);
  btn?.addEventListener('blur', hidePopoverSoon);
  pop?.addEventListener('focusout', hidePopoverSoon);
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape') {
      if (pop) pop.classList.add('hidden');
      btn?.setAttribute('aria-expanded', 'false');
      btn?.focus();
    }
  });

  applyBtn?.addEventListener('click', () => {
    if (chk) chk.checked = true;
    refreshButtonUI();
    if (pop) pop.classList.add('hidden');
    btn?.setAttribute('aria-expanded', 'false');
    btn?.focus();
  });

  sel?.addEventListener('change', refreshButtonUI);
  refreshButtonUI();
  chk?.addEventListener('change', refreshButtonUI);

  function adjustPopover() {
    if (!pop) return;
    const rect = pop.getBoundingClientRect();
    if (rect.right > window.innerWidth - 8) { pop.style.right = '0'; pop.style.left = 'auto'; }
    else { pop.style.left = ''; pop.style.right = ''; }
  }
  window.addEventListener('resize', adjustPopover);
  setTimeout(adjustPopover, 50);
})();

(function () {
  // Make the inline toggle-group keyboard accessible and keep hidden checkboxes in sync.
  const group = document.getElementById('inlineToolGroup');
  if (!group) return;

  group.addEventListener('click', (ev) => {
    if (ev.defaultPrevented) return;

    const btn = ev.target.closest('.tool-btn');
    if (!btn) return;
    const action = btn.getAttribute('data-action');
    if (!action) return;
    const checkbox = Array.from(document.querySelectorAll('.action-checkbox')).find(n => n.value === action);
    if (!checkbox) return;
    checkbox.checked = !checkbox.checked;
    const pressed = checkbox.checked;
    btn.setAttribute('aria-pressed', String(pressed));
    btn.classList.toggle('bg-red-50', pressed);
    btn.classList.toggle('border-red-300', pressed);
    if (typeof updateCompressInfo === 'function') updateCompressInfo();
  });

  group.querySelectorAll('.tool-btn').forEach(b => {
    b.setAttribute('tabindex', '0');
    b.addEventListener('keydown', (ev) => {
      if (ev.key === ' ' || ev.key === 'Enter') { ev.preventDefault(); b.click(); }
    });
  });
})();

const config = window.pdfToolboxConfig || {};
const uploadUrl = config.uploadUrl || '';
const processUrl = config.processUrl || '';
const pdfToWordUrl = config.pdfToWordUrl || '';
const pdfToExcelUrl = config.pdfToExcelUrl || '';
const uploadsPreviewBase = config.uploadsPreviewBase || '';
const generatedBase = config.generatedBase || '';

let uploadedFilename = '';
const perFileState = {};
let uploadedFiles = [];
const openTabs = [];
let activeTab = null;

function debounce(fn, wait) {
  let t = null;
  return function (...args) {
    if (t) clearTimeout(t);
    t = setTimeout(() => { t = null; fn.apply(this, args); }, wait);
  };
}

function storageKeyFor(serverName) { return `rx_pdf_state_${serverName}`; }
function savePerFileState(serverName) {
  if (!serverName || !perFileState[serverName]) return;
  try { localStorage.setItem(storageKeyFor(serverName), JSON.stringify(perFileState[serverName])); } catch (e) { /* ignore */ }
}
function loadPerFileState(serverName) {
  if (!serverName) return null;
  try {
    const raw = localStorage.getItem(storageKeyFor(serverName));
    if (raw) return JSON.parse(raw);
  } catch (e) { /* ignore */ }
  return null;
}

function registerUploadedFile(file, serverName, totalPages) {
  const existingIdx = uploadedFiles.findIndex(f => f.serverName === serverName);
  const fileObj = { clientName: file.name, size: file.size, serverName: serverName, total_pages: totalPages };
  if (existingIdx !== -1) uploadedFiles.splice(existingIdx, 1);
  uploadedFiles.push(fileObj);

  const existing = loadPerFileState(serverName) || { selectedPages: [], rotations: {} };
  perFileState[serverName] = Object.assign({ total_pages: totalPages, clientName: file.name, size: file.size }, existing);
  savePerFileState(serverName);

  uploadedFilename = serverName;
  updateUploadedFilesSelect();
  const nameEl = document.getElementById('uploadedName');
  if (nameEl) nameEl.innerText = fileObj.clientName;
  openPreviewTab(serverName);
  refreshSelectedInfo();
}

async function uploadFile(file) {
  const queue = document.getElementById('uploadQueue');
  let row = null; let progressBar = null; let status = null;
  if (queue) {
    row = document.createElement('div');
    row.className = 'bg-gray-900 text-white border border-gray-700 rounded-md p-2 shadow-sm flex flex-col';
    row.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="text-sm font-medium truncate" title="${file.name}">${file.name}</div>
        <div class="text-xs text-gray-300 status">Uploading...</div>
      </div>
      <div class="w-full bg-gray-700 h-2 rounded overflow-hidden mt-2">
        <div class="progress-bar bg-red-600 h-2 w-0" style="width:0%"></div>
      </div>
    `;
    queue.appendChild(row);
    progressBar = row.querySelector('.progress-bar');
    status = row.querySelector('.status');
  }

  return new Promise((resolve) => {
    try {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', uploadUrl);
      xhr.upload.onprogress = (ev) => {
        if (ev.lengthComputable && progressBar && status) {
          const pct = Math.round((ev.loaded / ev.total) * 100);
          progressBar.style.width = pct + '%';
          status.innerText = pct + '%';
        }
      };
      xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
          let data = null;
          try { data = JSON.parse(xhr.responseText); } catch (e) { data = null; }
          if (xhr.status >= 200 && xhr.status < 300 && data && data.filename) {
            if (progressBar) progressBar.style.width = '100%';
            if (status) status.innerText = 'Done';
            registerUploadedFile(file, data.filename, data.total_pages || 0);
            setTimeout(() => { if (row) row.remove(); }, 1600);
            resolve(data);
          } else {
            if (status) status.innerText = 'Error';
            if (row) row.classList.add('opacity-80');
            setTimeout(() => { if (row) row.remove(); }, 2000);
            resolve(null);
          }
        }
      };
      const fd = new FormData();
      fd.append('pdf', file);
      xhr.send(fd);
    } catch (err) {
      if (status) status.innerText = 'Error';
      if (row) row.classList.add('opacity-80');
      setTimeout(() => { if (row) row.remove(); }, 2000);
      resolve(null);
    }
  });
}

function makePageRow(i) {
  const div = document.createElement('div');
  div.className = 'flex items-center justify-between p-2 bg-white rounded-md mb-2 border border-gray-100';
  div.innerHTML = `
    <div class="flex items-center">
      <input class="page-checkbox" type="checkbox" value="${i}" id="p${i}" />
      <label for="p${i}" class="ml-2 text-sm">Page ${i}</label>
    </div>
    <div class="flex items-center">
      <button class="rotate-btn text-red-600" data-page="${i}" title="Rotate page by 90°">🔁</button>
      <span id="angle-${i}" class="angle-display text-sm ml-2">0°</span>
      <button class="remove-page-btn ml-3 text-sm text-gray-500" data-page="${i}" title="Remove this page">🗑️</button>
    </div>
  `;
  return div;
}

function loadPages(total, serverName) {
  const container = document.getElementById('pagesList');
  container.innerHTML = '';
  if (!serverName) serverName = uploadedFilename;
  if (!serverName) return;
  if (!perFileState[serverName]) perFileState[serverName] = { selectedPages: [], rotations: {}, total_pages: total };
  perFileState[serverName].total_pages = total;

  const selPages = new Set(perFileState[serverName].selectedPages || []);
  const rotations = perFileState[serverName].rotations || {};

  for (let i = 1; i <= total; i++) {
    const row = makePageRow(i);
    const cb = row.querySelector('.page-checkbox');
    if (cb) cb.checked = selPages.has(i);
    const angleEl = row.querySelector(`#angle-${i}`) || row.querySelector('.angle-display');
    if (angleEl) angleEl.innerText = (rotations[i] || 0) + '°';
    container.appendChild(row);
  }

  document.querySelectorAll('.page-checkbox').forEach(cb => {
    cb.addEventListener('change', function () {
      const val = parseInt(this.value, 10);
      const st = perFileState[serverName] || (perFileState[serverName] = { selectedPages: [], rotations: {} });
      if (this.checked) {
        if (!st.selectedPages.includes(val)) st.selectedPages.push(val);
      } else {
        st.selectedPages = st.selectedPages.filter(x => x !== val);
      }
      savePerFileState(serverName);
      try { if (typeof refreshSelectedInfo === 'function') refreshSelectedInfo(); } catch (e) { /* ignore */ }
    });
  });

  document.querySelectorAll('.rotate-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const p = parseInt(this.getAttribute('data-page'), 10);
      const st = perFileState[serverName] || (perFileState[serverName] = { selectedPages: [], rotations: {} });
      if (!st.rotations[p]) st.rotations[p] = 0;
      st.rotations[p] = (st.rotations[p] + 90) % 360;
      const angleEl = document.getElementById(`angle-${p}`);
      if (angleEl) angleEl.innerText = st.rotations[p] + '°';
      const thumb = document.getElementById(`thumb-${serverName}-p${p}`);
      if (thumb) {
        thumb.style.transform = `rotate(${st.rotations[p]}deg)`;
        thumb.style.transition = 'transform 240ms ease';
      }
      savePerFileState(serverName);
    });
  });

  document.querySelectorAll('.remove-page-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const p = parseInt(this.getAttribute('data-page'), 10);
      const row = this.closest('div');
      if (row) row.remove();
      const thumb = document.getElementById(`thumb-${serverName}-p${p}`);
      if (thumb) thumb.remove();
      const st = perFileState[serverName] || (perFileState[serverName] = { selectedPages: [], rotations: {} });
      st.selectedPages = st.selectedPages.filter(x => x !== p);
      delete st.rotations[p];
      savePerFileState(serverName);
      const angleEl = document.getElementById(`angle-${p}`);
      if (angleEl) angleEl.innerText = 'removed';
      try { if (typeof refreshSelectedInfo === 'function') refreshSelectedInfo(); } catch (e) { /* ignore */ }
    });
  });

  try { if (typeof refreshSelectedInfo === 'function') refreshSelectedInfo(); } catch (e) { /* ignore */ }
}

async function loadThumbnails(url, total, serverName) {
  if (!serverName) serverName = uploadedFilename;
  if (!serverName) return;
  try {
    const previewContents = document.getElementById('previewContents');
    let tabNode = document.getElementById(`tab-${serverName}`);
    if (!tabNode) {
      tabNode = document.createElement('div');
      tabNode.id = `tab-${serverName}`;
      tabNode.className = 'tab-content hidden';
      const thumbs = document.createElement('div');
      thumbs.id = `thumbs-${serverName}`;
      thumbs.className = 'rounded-md grid grid-cols-2 sm:grid-cols-3 gap-3';
      tabNode.appendChild(thumbs);
      previewContents.appendChild(tabNode);
    }

    const token = Symbol('load');
    perFileState[serverName].loadToken = token;

    const pdf = await pdfjsLib.getDocument(url).promise;
    if (perFileState[serverName].loadToken !== token) return;

    const thumbsEl = document.getElementById(`thumbs-${serverName}`);
    if (!thumbsEl) return;
    thumbsEl.innerHTML = '';

    const seen = new Set();
    for (let i = 1; i <= total; i++) {
      if (seen.has(i)) continue;
      seen.add(i);
      const page = await pdf.getPage(i);
      if (perFileState[serverName].loadToken !== token) return;
      const viewport = page.getViewport({ scale: 0.7 });
      const canvas = document.createElement('canvas');
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
      const wrapper = document.createElement('div');
      wrapper.className = 'thumb-wrapper bg-gray-50 p-1 rounded-md flex items-center justify-center';
      wrapper.id = `thumb-${serverName}-p${i}`;
      wrapper.dataset.page = i;
      canvas.id = `canvas-${serverName}-p${i}`;
      canvas.style.display = 'block';
      canvas.style.maxWidth = '100%';
      canvas.style.height = 'auto';
      wrapper.style.transition = 'transform 240ms ease';
      wrapper.appendChild(canvas);
      const label = document.createElement('div');
      label.className = 'text-xs text-gray-600 mt-1 text-center';
      label.innerText = `Page ${i}`;
      const container = document.createElement('div');
      container.className = 'flex flex-col items-center';
      container.appendChild(wrapper);
      container.appendChild(label);
      thumbsEl.appendChild(container);

      const st = perFileState[serverName] || {};
      if (st.rotations && st.rotations[i]) {
        wrapper.style.transform = `rotate(${st.rotations[i]}deg)`;
      }
    }
  } catch (err) {
    console.warn('thumbnail load failed', err);
  }
}

function updateTabsUI() {
  const tabs = document.getElementById('previewTabs');
  tabs.innerHTML = '';
  openTabs.forEach((srv) => {
    const tbtn = document.createElement('button');
    tbtn.className = 'px-3 py-1 rounded-t-md bg-white border text-sm flex items-center space-x-2';
    tbtn.setAttribute('role', 'tab');
    tbtn.setAttribute('aria-selected', String(activeTab === srv));
    tbtn.tabIndex = 0;
    tbtn.innerHTML = `<span class="truncate max-w-[10rem]">${(perFileState[srv] && perFileState[srv].clientName) || srv}</span>`;
    if (activeTab === srv) tbtn.classList.add('font-semibold');
    tbtn.addEventListener('click', () => switchTab(srv));
    tbtn.addEventListener('keydown', (ev) => {
      if (ev.key === 'ArrowLeft') { const i = openTabs.indexOf(srv); if (i > 0) switchTab(openTabs[i - 1]); }
      if (ev.key === 'ArrowRight') { const i = openTabs.indexOf(srv); if (i < openTabs.length - 1) switchTab(openTabs[i + 1]); }
      if (ev.key === 'Delete' || ev.key === 'Escape') { closeTab(srv); }
    });

    const close = document.createElement('button');
    close.className = 'ml-2 p-1 rounded hover:bg-gray-100';
    close.setAttribute('aria-label', `Close ${srv}`);
    close.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>';
    close.addEventListener('click', (ev) => { ev.stopPropagation(); closeTab(srv); });
    tbtn.appendChild(close);
    tabs.appendChild(tbtn);
  });
}

function switchTab(serverName) {
  if (!serverName) return;
  activeTab = serverName;
  document.querySelectorAll('#previewContents .tab-content').forEach(n => n.classList.add('hidden'));
  const node = document.getElementById(`tab-${serverName}`);
  if (node) node.classList.remove('hidden');
  uploadedFilename = serverName;
  const meta = uploadedFiles.find(x => x.serverName === serverName) || perFileState[serverName] || {};
  const nameEl = document.getElementById('selectedFilename'); if (nameEl) nameEl.innerText = meta.clientName || serverName;
  const total = (meta && meta.total_pages) || (perFileState[serverName] && perFileState[serverName].total_pages) || 1;
  loadPages(total, serverName);
  updateTabsUI();
}

function openPreviewTab(serverName) {
  if (!serverName) return;
  if (!openTabs.includes(serverName)) openTabs.push(serverName);
  const meta = uploadedFiles.find(x => x.serverName === serverName) || {};
  if (!perFileState[serverName]) perFileState[serverName] = loadPerFileState(serverName) || { selectedPages: [], rotations: {}, total_pages: meta.total_pages || 1, clientName: meta.clientName, size: meta.size };
  const total = perFileState[serverName].total_pages || meta.total_pages || 1;
  loadThumbnails((typeof uploadsPreviewBase !== 'undefined' ? uploadsPreviewBase : '') + serverName, total, serverName).then(() => {
    switchTab(serverName);
  }).catch(() => { switchTab(serverName); });
  updateTabsUI();
}

function closeTab(serverName) {
  const idx = openTabs.indexOf(serverName);
  if (idx === -1) return;
  openTabs.splice(idx, 1);
  const node = document.getElementById(`tab-${serverName}`);
  if (node) node.remove();
  if (activeTab === serverName) {
    const newActive = openTabs[idx] || openTabs[idx - 1] || null;
    if (newActive) switchTab(newActive);
    else {
      activeTab = null;
      document.getElementById('pagesList').innerHTML = '';
      document.querySelectorAll('#previewContents .tab-content').forEach(n => n.classList.add('hidden'));
      const nameEl = document.getElementById('selectedFilename'); if (nameEl) nameEl.innerText = 'None';
    }
  }
  updateTabsUI();
}

const pdfInput = document.getElementById('pdfUpload');
pdfInput?.addEventListener('change', async (e) => {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;
  for (const f of files) { await uploadFile(f); }
  try { pdfInput.value = ''; } catch (err) { /* ignore */ }
});

const clearBtn = document.getElementById('clearFileBtn');
clearBtn?.addEventListener('click', resetWorkspace);

const browseBtn = document.getElementById('browseBtn');
browseBtn?.addEventListener('click', () => {
  const fileInput = document.getElementById('pdfUpload');
  if (fileInput) fileInput.click();
});

function updateUploadedFilesSelect() {
  const sel = document.getElementById('uploadedFilesSelect');
  const list = document.getElementById('uploadedFilesExplorerList');
  const count = document.getElementById('uploadedFilesCount');
  if (!sel || !list || !count) return;
  sel.innerHTML = '<option value="">-- Select uploaded file --</option>';
  uploadedFiles.forEach(f => {
    const opt = document.createElement('option');
    opt.value = f.serverName;
    opt.text = `${f.clientName} (${Math.round(f.size / 1024)} KB)`;
    sel.appendChild(opt);
  });
  if (uploadedFiles.length) sel.value = uploadedFiles[uploadedFiles.length - 1].serverName;

  list.innerHTML = '';
  if (!uploadedFiles.length) {
    list.innerHTML = '<div class="text-xs text-gray-400 italic">No uploaded files yet.</div>';
    count.innerText = '0';
    return;
  }
  uploadedFiles.forEach(f => {
    const wrapper = document.createElement('div');
    wrapper.className = 'flex items-center justify-between p-2 rounded hover:bg-gray-50';
    wrapper.innerHTML = `
      <div class="flex items-center space-x-2">
        <input class="explorer-file-checkbox file-checkbox" type="checkbox" data-server="${f.serverName}" aria-label="Select ${f.clientName}" />
        <div class="text-sm truncate" style="max-width:160px">${f.clientName}</div>
        <div class="text-xs text-gray-400">${Math.round(f.size/1024)} KB</div>
      </div>
      <div class="flex items-center space-x-1">
        <button class="open-file-icon focus:outline-none p-1 rounded" data-server="${f.serverName}" title="Open preview (tab)" aria-label="Open ${f.clientName} in preview" tabindex="0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </button>
        <button class="preview-file-icon focus:outline-none p-1 rounded" data-server="${f.serverName}" title="Open raw file in new tab" aria-label="Preview ${f.clientName} in new window" tabindex="0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h6m0 0v6M13 7L21 15M3 5a2 2 0 012-2h6" />
          </svg>
        </button>
      </div>
    `;
    list.appendChild(wrapper);
  });
  count.innerText = String(uploadedFiles.length);

  list.querySelectorAll('.open-file-icon').forEach(b => b.addEventListener('click', (ev) => {
    const server = ev.currentTarget.getAttribute('data-server');
    if (!server) return;
    openPreviewTab(server);
  }));

  list.querySelectorAll('.preview-file-icon').forEach(b => b.addEventListener('click', (ev) => {
    const server = ev.currentTarget.getAttribute('data-server');
    if (!server) return;
    const url = (typeof uploadsPreviewBase !== 'undefined' ? uploadsPreviewBase : '') + server;
    try { window.open(url, '_blank'); } catch (e) { /* ignore */ }
  }));

  const debouncedSelectionChanged = debounce(() => {
    const checked = Array.from(list.querySelectorAll('.explorer-file-checkbox:checked')).map(n => n.getAttribute('data-server'));
    if (checked.length === 1) {
      openPreviewTab(checked[0]);
    }
    const selAllBtn = document.getElementById('selectAllBtnFiles');
    const clearBtn = document.getElementById('clearAllBtnFiles');
    if (selAllBtn) selAllBtn.disabled = uploadedFiles.length === 0;
    if (clearBtn) clearBtn.disabled = uploadedFiles.length === 0;
  }, 180);

  list.querySelectorAll('.explorer-file-checkbox').forEach(cb => cb.addEventListener('change', debouncedSelectionChanged));
  const selAllBtn = document.getElementById('selectAllBtnFiles');
  const clearBtn = document.getElementById('clearAllBtnFiles');
  if (selAllBtn) selAllBtn.disabled = uploadedFiles.length === 0;
  if (clearBtn) clearBtn.disabled = uploadedFiles.length === 0;
}

const uploadedFilesSelect = document.getElementById('uploadedFilesSelect');
uploadedFilesSelect?.addEventListener('change', function () {
  const val = this.value;
  if (!val) return;
  const found = uploadedFiles.find(x => x.serverName === val);
  if (!found) return;
  uploadedFilename = found.serverName;
  const nameEl = document.getElementById('uploadedName');
  if (nameEl) nameEl.innerText = found.clientName;
  loadPages(found.total_pages);
  loadThumbnails(`${uploadsPreviewBase}${uploadedFilename}`, found.total_pages);
  updateCompressInfo();
});

const uploadDrop = document.getElementById('uploadDrop');
if (uploadDrop) {
  uploadDrop.addEventListener('dragover', e => { e.preventDefault(); uploadDrop.classList.add('bg-red-100'); });
  uploadDrop.addEventListener('dragleave', () => { uploadDrop.classList.remove('bg-red-100'); });
  uploadDrop.addEventListener('drop', e => {
    e.preventDefault(); uploadDrop.classList.remove('bg-red-100');
    const files = Array.from(e.dataTransfer.files || []);
    if (!files.length) return;
    try {
      const input = document.getElementById('pdfUpload');
      if (input) input.files = e.dataTransfer.files;
    } catch (err) { /* ignore */ }
    (async function () {
      for (const f of files) {
        await uploadFile(f);
      }
    })();
  });
}

document.getElementById('selectAllBtn')?.addEventListener('click', () => {
  document.querySelectorAll('.page-checkbox').forEach(cb => { cb.checked = true; cb.dispatchEvent(new Event('change')); });
});

document.getElementById('clearAllBtn')?.addEventListener('click', () => {
  document.querySelectorAll('.page-checkbox').forEach(cb => { cb.checked = false; cb.dispatchEvent(new Event('change')); });
});

document.getElementById('selectAllBtnFiles')?.addEventListener('click', () => {
  document.querySelectorAll('.file-checkbox').forEach(cb => { cb.checked = true; cb.dispatchEvent(new Event('change')); });
});

document.getElementById('clearAllBtnFiles')?.addEventListener('click', () => {
  document.querySelectorAll('.file-checkbox').forEach(cb => { cb.checked = false; cb.dispatchEvent(new Event('change')); });
});

function getCheckedActions() {
  const actions = [];
  document.querySelectorAll('.action-checkbox:checked').forEach(node => actions.push(node.value));
  return actions;
}

function updateCompressInfo() {
  const info = document.getElementById('compressInfo');
  if (info) info.classList.add('hidden');
}

function parsePagesInput(str) {
  if (!str) return [];
  const out = new Set();
  str.split(',').map(s => s.trim()).forEach(part => {
    if (!part) return;
    if (part.includes('-')) {
      const [a, b] = part.split('-').map(x => parseInt(x, 10));
      if (!Number.isNaN(a) && !Number.isNaN(b)) {
        for (let i = Math.min(a, b); i <= Math.max(a, b); i++) out.add(i);
      }
    } else {
      const n = parseInt(part, 10);
      if (!Number.isNaN(n)) out.add(n);
    }
  });
  return Array.from(out).sort((a, b) => a - b);
}

function refreshSelectedInfo() {
  const fnameEl = document.getElementById('selectedFilename');
  const pagesEl = document.getElementById('selectedPagesInfo');
  try {
    const meta = (uploadedFiles || []).find(x => x.serverName === uploadedFilename) || {};
    if (fnameEl) fnameEl.innerText = meta.clientName || (uploadedFilename || 'None');
    const st = perFileState[uploadedFilename] || { selectedPages: [] };
    if (pagesEl) pagesEl.innerText = (st.selectedPages && st.selectedPages.length) ? st.selectedPages.join(',') : 'None';
  } catch (e) { /* ignore */ }
}

function resetWorkspace() {
  const input = document.getElementById('pdfUpload');
  if (input) input.value = '';

  const filename = uploadedFilename;
  if (filename && uploadUrl) {
    try {
      fetch(uploadUrl, { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename }) }).catch(() => { /* ignore */ });
    } catch (e) { /* ignore */ }
  }

  uploadedFilename = '';
  uploadedFiles = [];
  openTabs.splice(0, openTabs.length);
  activeTab = null;

  Object.keys(perFileState).forEach(k => {
    try { localStorage.removeItem(storageKeyFor(k)); } catch (e) { /* ignore */ }
    delete perFileState[k];
  });

  const previewContents = document.getElementById('previewContents'); if (previewContents) previewContents.innerHTML = '';
  const pages = document.getElementById('pagesList'); if (pages) pages.innerHTML = '';
  const gen = document.getElementById('generatedList'); if (gen) gen.innerHTML = '';
  const tabs = document.getElementById('previewTabs'); if (tabs) tabs.innerHTML = '';
  const selectedInfo = document.getElementById('selectedFilename'); if (selectedInfo) selectedInfo.innerText = 'None';
  const selectedPagesInfo = document.getElementById('selectedPagesInfo'); if (selectedPagesInfo) selectedPagesInfo.innerText = 'None';

  const explorerList = document.getElementById('uploadedFilesExplorerList');
  if (explorerList) explorerList.innerHTML = '<div class="text-xs text-gray-400 italic">No uploaded files yet.</div>';
  const filesCount = document.getElementById('uploadedFilesCount'); if (filesCount) filesCount.innerText = '0';
  const sel = document.getElementById('uploadedFilesSelect'); if (sel) sel.innerHTML = '<option value="">-- Select uploaded file --</option>';
  const queue = document.getElementById('uploadQueue'); if (queue) queue.innerHTML = '';
  const toggle = document.getElementById('explorerToggle'); if (toggle) { toggle.innerText = '−'; toggle.setAttribute('aria-expanded', 'true'); }

  document.querySelectorAll('.action-checkbox').forEach(n => { n.checked = false; });
  document.querySelectorAll('.tool-btn').forEach(b => { b.classList.remove('bg-red-50', 'border-red-300'); b.setAttribute('aria-pressed', 'false'); });

  updateUploadedFilesSelect();
  refreshSelectedInfo();
}

const explorerToggleBtn = document.getElementById('explorerToggle');
explorerToggleBtn?.addEventListener('click', () => {
  const list = document.getElementById('uploadedFilesExplorerList');
  if (!list) return;
  const hidden = list.classList.toggle('hidden');
  explorerToggleBtn.innerText = hidden ? '+' : '−';
  explorerToggleBtn.setAttribute('aria-expanded', String(!hidden));
});

function showGeneratedFiles(listNames) {
  console.log('listNames : ', listNames);
  const list = document.getElementById('generatedList');
  console.log('list : ', list);
  list.innerHTML = '';
  const seen = new Set();
  (listNames || []).forEach(name => {
     console.log('name : ', name);
    if (!name || seen.has(name)) return;
    seen.add(name);
    const li = document.createElement('div');
    li.className = 'flex items-center justify-between p-2 border rounded-md bg-white';
    li.innerHTML = `<span class="truncate max-w-xs">${name}</span>
      <div class="space-x-2">
        <a href='${generatedBase}${name}' target='_blank' class='text-red-600 text-sm'>Preview</a>
        <a href='${generatedBase}${name}' class='text-green-600 text-sm' download>Download</a>
      </div>`;
    list.appendChild(li);
  });
}

function applyRotationToPreview(page, angle) {
  const server = activeTab || uploadedFilename;
  if (!server) return;
  const wrapper = document.getElementById(`thumb-${server}-p${page}`) || document.getElementById(`thumb-p${page}`);
  if (!wrapper) return;
  wrapper.style.transform = `rotate(${angle}deg)`;
  wrapper.style.transition = 'transform 240ms ease';
}

document.getElementById('rotateSelectedBtn')?.addEventListener('click', () => {
  if (!uploadedFilename) { alert('Please upload a PDF first'); return; }
  const st = perFileState[uploadedFilename] || { selectedPages: [], rotations: {} };
  const angle = parseInt(document.getElementById('rotateAngle').value || '90', 10);
  if (!st.selectedPages || st.selectedPages.length === 0) { alert('Select pages to rotate'); return; }
  st.selectedPages.forEach(p => {
    if (!st.rotations[p]) st.rotations[p] = 0;
    st.rotations[p] = (st.rotations[p] + angle) % 360;
    const angleEl = document.getElementById(`angle-${p}`);
    if (angleEl) angleEl.innerText = st.rotations[p] + '°';
    applyRotationToPreview(p, st.rotations[p]);
  });
  savePerFileState(uploadedFilename);
});

function launchConfetti() {
  const canvas = document.getElementById('confetti-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
  resize(); window.addEventListener('resize', resize);

  const colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];
  const particles = [];
  const count = 80;
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * -canvas.height * 0.5,
      vx: (Math.random() - 0.5) * 6,
      vy: Math.random() * 6 + 2,
      size: Math.random() * 8 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      rot: Math.random() * Math.PI
    });
  }

  let t0 = performance.now();
  function frame(now) {
    const dt = (now - t0) / 1000; t0 = now;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.12;
      p.rot += 0.1;
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rot);
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      ctx.restore();
    });
    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
  setTimeout(() => { ctx.clearRect(0, 0, canvas.width, canvas.height); }, 2600);
}

document.getElementById('generateBtn')?.addEventListener('click', async () => {
  const actions = getCheckedActions();
  const explorerSelected = Array.from(document.querySelectorAll('.explorer-file-checkbox:checked')).map(n => n.getAttribute('data-server'));
  if (!uploadedFilename && explorerSelected.length === 0) { alert('Please upload a PDF first or select files from the Uploaded Files explorer'); return; }
  if (actions.length === 0) { alert('Select at least one action'); return; }

  const currentState = uploadedFilename ? (perFileState[uploadedFilename] || { selectedPages: [], rotations: {} }) : { selectedPages: [], rotations: {} };

  const rotatePagesInput = document.getElementById('rotatePagesInput').value;
  const rotatePagesParsed = parsePagesInput(rotatePagesInput);
  const rotations = Object.assign({}, currentState.rotations || {});
  if (rotatePagesParsed && rotatePagesParsed.length > 0) {
    const globalAngle = parseInt(document.getElementById('rotateAngle').value || '90', 10);
    rotatePagesParsed.forEach(page => {
      const cur = rotations[String(page)] || 0;
      rotations[String(page)] = (cur + globalAngle) % 360;
    });
  }

  const pagesForPrimary = Array.isArray(currentState.selectedPages) ? currentState.selectedPages.slice() : [];
  const payload = { actions: actions, pages: pagesForPrimary, rotations: rotations };
  const compressSelected = actions.includes('compress');
  const compressLevel = (document.getElementById('compressLevelSelect') && document.getElementById('compressLevelSelect').value) || 'default';

  const selectedFiles = (explorerSelected && explorerSelected.length) ? explorerSelected.slice() : (uploadedFilename ? [uploadedFilename] : []);

  if (selectedFiles.length > 0) payload.filenames = selectedFiles;
  else if (uploadedFilename) payload.filename = uploadedFilename;

  if (compressSelected) payload.compression_level = compressLevel;

  const mergeSelect = document.getElementById('mergeModePages');
  const mergeValue = mergeSelect ? mergeSelect.value : 'pages';
  let merge_mode = 'none';
  if (mergeValue === 'pages') merge_mode = 'pages_per_file';
  else if (mergeValue === 'files') merge_mode = 'files_whole';
  else if (mergeValue === 'files_pages') merge_mode = 'files_and_pages';
  payload.merge_mode = merge_mode;

  if (merge_mode === 'pages_per_file' || merge_mode === 'files_and_pages') {
    const filePageMap = {};
    const targets = (payload.filenames && payload.filenames.length) ? payload.filenames : (payload.filename ? [payload.filename] : []);
    targets.forEach(fn => {
      const st = perFileState[fn] || { selectedPages: [] };
      filePageMap[fn] = Array.isArray(st.selectedPages) ? st.selectedPages.slice() : [];
    });
    payload.file_page_map = filePageMap;
  }

  try {
    const resp = await fetch(processUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    console.log('Generate response', resp);
    const data = await resp.json();
    console.log('Generation result', data);
    showGeneratedFiles(data.generated || []);
    if (data.generated && data.generated.length > 0) { try { launchConfetti(); } catch (e) { /* ignore */ } }
  } catch (err) { console.warn('Generate failed', err); alert('Generation failed'); }
});

document.getElementById('pdfToWordBtn')?.addEventListener('click', async () => {
  if (!uploadedFilename) { alert('Upload a PDF first'); return; }
  const st = perFileState[uploadedFilename] || { selectedPages: [] };
  if (!st.selectedPages || st.selectedPages.length === 0) { alert('Select pages to export'); return; }
  const resp = await fetch(pdfToWordUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename: uploadedFilename, pages: st.selectedPages }) });
  const data = await resp.json();
  if (data.generated && data.generated.length) { showGeneratedFiles((data.generated || [])); try { launchConfetti(); } catch (e) { /* ignore */ } } else { alert('Conversion failed'); }
});

document.getElementById('pdfToExcelBtn')?.addEventListener('click', async () => {
  if (!uploadedFilename) { alert('Upload a PDF first'); return; }
  const st = perFileState[uploadedFilename] || { selectedPages: [] };
  if (!st.selectedPages || st.selectedPages.length === 0) { alert('Select pages to export'); return; }
  const resp = await fetch(pdfToExcelUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename: uploadedFilename, pages: st.selectedPages }) });
  const data = await resp.json();
  if (data.generated && data.generated.length) { showGeneratedFiles((data.generated || [])); try { launchConfetti(); } catch (e) { /* ignore */ } } else { alert('Conversion failed'); }
});
