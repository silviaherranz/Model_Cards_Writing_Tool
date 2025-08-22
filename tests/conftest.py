import sys
import pathlib
from types import SimpleNamespace
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]  # carpeta del repo
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


@pytest.fixture
def fake_st():
    """
    Minimal stand-in for streamlit used by uploads_manager:
    - session_state: plain dict
    - image/markdown/code: no-ops
    """
    st = SimpleNamespace()
    st.session_state = {}

    def _noop(*args, **kwargs):
        return None

    st.image = _noop
    st.markdown = _noop
    st.code = _noop
    st.columns = lambda sizes: (SimpleNamespace(), SimpleNamespace())
    st.caption = _noop
    st.button = lambda *a, **k: False
    st.text_input = lambda *a, **k: ""
    st.file_uploader = lambda *a, **k: None
    st.info = _noop
    st.expander = pytest.fixture  # never used in these tests

    return st
