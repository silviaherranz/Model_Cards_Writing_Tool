from pathlib import Path
import streamlit as st

from utils import hide_streamlit_chrome

def model_card_info_render():
    hide_streamlit_chrome()
    st.markdown("""
    <style>
    /* hide Streamlit Cloud’s top-right toolbar (includes the GitHub icon) */
    div[data-testid="stToolbar"] { visibility: hidden; height: 0; }

    /* optional: also hide the 'Manage app' badge and footer */
    a[data-testid="viewerBadge_link"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)
    from side_bar import sidebar_render
    sidebar_render()

    md_file = Path("about.md")
    if not md_file.exists():
        st.error(f"File '{md_file}' not found.")
        return

    # CSS para justificar párrafos y listas
    st.markdown("""
        <style>
        .block-container p, .block-container li {
            text-align: justify;
        }
        </style>
    """, unsafe_allow_html=True)

    # Renderiza el Markdown normalmente
    st.markdown(md_file.read_text(encoding="utf-8"))
