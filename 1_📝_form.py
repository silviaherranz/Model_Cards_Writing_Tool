from persist import persist, load_widget_state
from render import render_schema_section  # New import
import streamlit as st
from pathlib import Path
from huggingface_hub import upload_file, create_repo
from datetime import date
from middleMan import parse_into_jinja_markdown as pj
import pandas as pd
import tempfile
import json

# Load schema once
with open("model_card_schema.json", "r") as f:
    model_card_schema = json.load(f)

def get_state(key, default=None):
    return st.session_state.get(key, default)

def validate_required_fields(schema, session_state):
    missing_fields = []
    for section, fields in schema.items():
        for key, props in fields.items():
            full_key = f"{section}_{key}"
            if props.get("required", False):
                value = session_state.get(full_key)
                if value in ("", None, [], {}):
                    label = props.get("label", key)
                    missing_fields.append(label)
    return missing_fields

@st.cache_data(ttl=3600)  # Cache data for 1 hour (3600 seconds)

def get_cached_data():
    license_df = pd.read_html("https://huggingface.co/docs/hub/repositories-licenses")[0]
    return pd.Series(
        license_df["License identifier (to use in repo card)"].values, index=license_df.Fullname
    ).to_dict()

def card_upload(card_info, repo_id, token):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "README.md"
        tmp_path.write_text(json.dumps(card_info) if isinstance(card_info, dict) else str(card_info))
        url = upload_file(
            path_or_fileobj=str(tmp_path),
            path_in_repo="README.md",
            repo_id=repo_id,
            token=token,
            repo_type="model"
        )
    return url

def save_uploadedfile(uploadedfile):
    import time
    unique_name = f"{int(time.time())}_{uploadedfile.name}"
    with open(unique_name, "wb") as f:
        f.write(uploadedfile.getbuffer())
    st.success(f"Saved File: {unique_name} to temp dir")
    return unique_name

def main_page():
    today = date.today()
    # Ensure required keys are initialized to prevent KeyErrors
    defaults = {
        "model_name": "",
        "license": "",
        "markdown_upload": "current_card.md",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    if "model_name" not in st.session_state:
        with open("model_card_schema.json", "r") as file:
            json_data = json.load(file)
    # Removed unused license_map variable to avoid unnecessary calls to get_cached_data
    get_cached_data()  # Ensure cache is populated

    license_map = get_cached_data()

    st.header("Card Metadata")
    render_schema_section(model_card_schema["card_metadata"], section_prefix="card_metadata")

    st.header("Model basic information (Dose prediction)")
    render_schema_section(model_card_schema["model_basic_information"], section_prefix="model_basic_information")

    license = get_state("license")
    markdown_upload = get_state("markdown_upload", "current_card.md")

    do_warn = False
    warning_placeholder = st.empty()
    warning_msg = "Warning: The following fields are required but have not been filled in: "
    if not license:
        warning_msg += "\n- License"
        do_warn = True
    if do_warn:
        warning_placeholder.error(warning_msg)

    with st.sidebar:
        st.markdown("## Upload Model Card")
        st.markdown("#### Model Card must be in markdown (.md) format.")

        uploaded_file = st.file_uploader("Choose a file", type=['md'], help='Upload a markdown (.md) file')
        if uploaded_file is not None:
            name_of_uploaded_file = save_uploadedfile(uploaded_file)
            st.session_state.markdown_upload = name_of_uploaded_file
        else:
            st.session_state.markdown_upload = "current_card.md"
        try:
            out_markdown = Path(st.session_state.markdown_upload).read_text()
        except FileNotFoundError:
            st.error(f"File {st.session_state.markdown_upload} not found. Please upload a valid file.")
            out_markdown = ""


        st.markdown("## Export Loaded Model Card to Hub")
        with st.form("Upload to 🤗 Hub"):
            st.markdown("Use a token with write access from [here](https://hf.co/settings/tokens)")
            token = st.text_input("Token", type='password')
            repo_id = st.text_input("Repo ID")
            submit = st.form_submit_button('Upload to 🤗 Hub')

        if submit:
            missing = validate_required_fields(model_card_schema, st.session_state)
            if missing:
                st.error("Please complete the required fields: " + ", ".join(missing))
            elif len(repo_id.split('/')) == 2:
                create_repo(repo_id, exist_ok=True, token=token)
                card_content = pj(st.session_state)
                new_url = card_upload(card_content, repo_id, token=token)
                st.success(f"Pushed the card to the repo [here]({new_url})!")
            else:
                st.error("Repo ID invalid. It should be username/repo-name.")


def page_switcher(page):
    st.session_state.runpage = page

def main():
    st.header("About Model Cards")
    about_path = Path('about.md')
    if about_path.exists():
        st.markdown(about_path.read_text(), unsafe_allow_html=True)
    else:
        st.error("The file 'about.md' is missing. Please ensure it exists in the current working directory.")

    # Always show this button!
    if st.button('Create a Model Card 📝'):
        page_switcher(main_page)
        st.rerun()

if __name__ == '__main__':
    load_widget_state()
    if 'runpage' not in st.session_state:
        st.session_state.runpage = main
    st.session_state.runpage()
