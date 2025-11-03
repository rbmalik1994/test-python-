import tempfile
from pathlib import Path
from pypdf import PdfWriter, PdfReader

from RxSmartTools.services import pdf_service


def _make_pdf(path: Path, pages: int):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=72, height=72)
    with path.open("wb") as f:
        writer.write(f)


def test_merge_pages_single_file(tmp_path):
    src = tmp_path / "one.pdf"
    _make_pdf(src, 5)
    out = tmp_path / "out.pdf"

    pdf_service.merge_pages(src, [1, 3, 5], out)
    r = PdfReader(out)
    assert len(r.pages) == 3


def test_merge_files_whole(tmp_path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    _make_pdf(a, 2)
    _make_pdf(b, 3)

    out = tmp_path / "merged.pdf"
    pdf_service.merge_files([a, b], out)
    r = PdfReader(out)
    assert len(r.pages) == 5


def test_merge_files_and_pages_invalid_page(tmp_path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    _make_pdf(a, 2)
    _make_pdf(b, 2)

    out = tmp_path / "merged_pages.pdf"
    mapping = {a: [1, 3], b: [1]}
    try:
        pdf_service.merge_selected_pages_from_multiple_files(mapping, out)
        assert False, "Expected ValueError for invalid page"
    except ValueError:
        pass
