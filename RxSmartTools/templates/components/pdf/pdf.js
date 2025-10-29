/* Minimal PDF component enhancement (placeholder)
   Extend this file to add upload + page rendering logic.
*/
(function(){
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  function init(){
    const up = document.getElementById('pdfUpload');
    const status = document.getElementById('pdf-status');
    if (!up) return;
    up.addEventListener('change', () => {
      const f = up.files[0];
      if (f) status.textContent = `Selected ${f.name} (${Math.round(f.size/1024)} KB)`;
    });
  }
})();
