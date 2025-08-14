from pathlib import Path
import streamlit as st

def model_card_info_render():
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
