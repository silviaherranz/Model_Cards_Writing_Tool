# tests/test_uploads_manager.py
from pathlib import Path

import pytest

import uploads_manager as um


class DummyUploadFile:
    """Very small shim for Streamlit's UploadedFile in tests."""
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def getbuffer(self) -> bytes:
        return self._data


@pytest.fixture(autouse=True)
def patch_streamlit(fake_st, monkeypatch):
    """
    Replace uploads_manager.st with our fake Streamlit for every test.
    """
    monkeypatch.setattr(um, "st", fake_st, raising=True)
    # Ensure clean state each test
    fake_st.session_state.clear()
    yield


def test_ensure_upload_state_initializes_keys():
    um.ensure_upload_state()
    st = um.st
    assert um.REG_APPENDIX_UPLOADS in st.session_state
    assert um.REG_ALL_PATHS in st.session_state
    assert um.REG_RENDER_UPLOADS in st.session_state
    assert um.REG_APPENDIX_NONCE in st.session_state


def test_save_appendix_files_adds_and_ignores_duplicates(tmp_path: Path):
    um.ensure_upload_state()

    f1 = DummyUploadFile("report.pdf", b"%PDF-1.4...")
    f2 = DummyUploadFile("report.pdf", b"%PDF-1.4...different")  # duplicate by name
    saved = um.save_appendix_files([f1, f2], tmp_path)
    assert saved is True

    # Only one entry registered for the original name
    app = um.st.session_state[um.REG_APPENDIX_UPLOADS]
    assert list(app.keys()) == ["report.pdf"]
    meta = app["report.pdf"]
    assert Path(meta["path"]).exists()

    # Also registered in render uploads by stored_name
    rend = um.st.session_state[um.REG_RENDER_UPLOADS]
    assert meta["stored_name"] in rend
    assert rend[meta["stored_name"]]["name"] == "report.pdf"


def test_field_overwrite_and_delete(tmp_path: Path):
    um.ensure_upload_state()

    # Overwrite writes a file and registers it
    upl = DummyUploadFile("img.png", b"\x89PNG\r\n\x1a\n")
    meta = um.field_overwrite("myfield", upl, folder=str(tmp_path))
    p = Path(meta["path"])
    assert p.exists()
    assert um.field_current("myfield") == meta

    # Delete removes the file and clears state
    um.field_delete("myfield")
    assert not p.exists()
    assert um.field_current("myfield") is None


def test_uploader_key_and_bump():
    um.ensure_upload_state()

    k1 = um.uploader_key_for("abc")
    # same without bump
    assert um.uploader_key_for("abc") == k1

    um.bump_uploader("abc")
    k2 = um.uploader_key_for("abc")
    assert k2 != k1


def test_clear_all_uploads_removes_everything(tmp_path: Path):
    um.ensure_upload_state()

    # Create two files via both flows
    upl1 = DummyUploadFile("a.txt", b"hello")
    upl2 = DummyUploadFile("b.txt", b"world")

    um.save_appendix_files([upl1], tmp_path)
    um.field_overwrite("k", upl2, folder=str(tmp_path))

    # Sanity: paths were registered
    all_paths = set(um.st.session_state[um.REG_ALL_PATHS])
    assert all_paths  # not empty
    for p in all_paths:
        assert Path(p).exists()

    um.clear_all_uploads()

    # Registries cleared
    assert um.st.session_state[um.REG_APPENDIX_UPLOADS] == {}
    assert um.st.session_state[um.REG_RENDER_UPLOADS] == {}
    # Files deleted
    for p in all_paths:
        assert not Path(p).exists()


def test_sanitize_filename_blocks_dirs_and_weird_chars(tmp_path: Path):
    # name with directories and weird chars
    dangerous = "../evil/../../bad name$$$.csv"
    safe = um.sanitize_filename(dangerous)
    assert "/" not in safe and "\\" not in safe
    assert safe.endswith(".csv")
    assert safe.startswith("bad_name") or safe.startswith("..") is False


def test_preview_file_returns_true_for_known_types(tmp_path: Path, monkeypatch):
    # Create a "png" file (content not validated by preview; it just passes the path to st.image)
    png_path = tmp_path / "fake.png"
    png_path.write_bytes(b"\x89PNG\r\n\x1a\n...")

    assert um.preview_file(str(png_path)) is True

    # Unsupported extension returns False
    bin_path = tmp_path / "blob.bin"
    bin_path.write_bytes(b"\x00\x01")
    assert um.preview_file(str(bin_path)) is False

    # PDF returns True
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 ...")
    assert um.preview_file(str(pdf_path)) is True
