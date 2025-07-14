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

def light_header(text, size="16px", bottom_margin="1em"):
    st.markdown(
        f"""
        <div style='
            font-size: {size};
            font-weight: normal;
            color: #444;
            margin-bottom: {bottom_margin};
        '>{text}</div>
        """,
        unsafe_allow_html=True
    )

def validate_required_fields(schema, session_state, current_task=None):
    missing_fields = []
    for section, fields in schema.items():
        for key, props in fields.items():
            full_key = f"{section}_{key}"
            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (current_task and current_task in model_types):
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

def task_selector_page():
    st.header("Select Model Task")

    st.radio(
        "Choose the model type:",
        ["Image-to-Image translation", "Segmentation", "Dose prediction"],
        key="task",
        index=0
    )

    if st.button("Continue"):
        page_switcher(main_page)
        st.rerun()

def extract_evaluations_from_state():
    evaluations = []
    for i in range(len(st.session_state.evaluation_forms)):
        prefix = f"evaluation_{i}_"
        entry = {}
        for key, value in st.session_state.items():
            if key.startswith(prefix):
                field = key[len(prefix):]  # remove the prefix
                entry[field] = value
        evaluations.append(entry)
    return evaluations



def main_page():
    today = date.today()
    if "evaluation_forms" not in st.session_state:
        st.session_state.evaluation_forms = [{}]  # Empieza con un formulario vacío
    # Ensure required keys are initialized to prevent KeyErrors
    task = st.session_state.get("task", None)

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
    #st.header("Card Metadata")
    with st.expander("Card Metadata", expanded=False):
        render_schema_section(model_card_schema["card_metadata"], section_prefix="card_metadata", current_task=task)




    #st.header("Model basic information")
    task = st.session_state.get("task")

    def filter_fields_by_task(fields, task):
        filtered = {}
        for key, props in fields.items():
            if "model_types" not in props or task in props["model_types"]:
                filtered[key] = props
        return filtered

    filtered_fields = filter_fields_by_task(model_card_schema["model_basic_information"], task)

    with st.expander("Model Basic Information", expanded=False):
        render_schema_section(filtered_fields, section_prefix="model_basic_information", current_task=task)

    task = st.session_state.get("task", None)
    missing_required = validate_required_fields(model_card_schema, st.session_state, current_task=task)

    #light_header("Evaluation Data Methodology, Results & Commissioning")

    evaluation_schema = model_card_schema["evaluation_data_methodology_results_commisioning"]

    to_delete = None  # track index to delete

    light_header("Evaluation Data Methodology, Results & Commissioning")

    for i, eval_data in enumerate(st.session_state.evaluation_forms):
        with st.expander(f"Evaluation #{i+1}", expanded=False):
            render_schema_section(
                model_card_schema["evaluation_data_methodology_results_commisioning"],
                section_prefix=f"evaluation_{i}",
                current_task=task
            )

            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button(f"🗑️ Delete", key=f"delete_eval_{i}"):
                    to_delete = i


    # Delete outside loop to avoid rerun errors mid-loop
    if to_delete is not None:
        del st.session_state.evaluation_forms[to_delete]

        # Also remove session_state keys for this form
        keys_to_delete = [key for key in st.session_state.keys() if key.startswith(f"evaluation_{to_delete}_")]
        for key in keys_to_delete:
            del st.session_state[key]

        # Re-index remaining keys if needed (optional, for clarity)
        st.rerun()

    if st.button("➕ Add Another Evaluation"):
        st.session_state.evaluation_forms.append({})
        st.rerun()

    
    if missing_required:
        st.warning(
            "Warning: The following required fields are missing:\n\n"
            + "\n".join([f"- {field}" for field in missing_required])
        )


    # Sidebar for file upload and export
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
            task = st.session_state.get("task")
            missing_required = validate_required_fields(model_card_schema, st.session_state, current_task=task)

            if missing_required:
                st.error("Please complete the required fields:\n\n" + "\n".join([f"- {field}" for field in missing_required]))
            elif len(repo_id.split('/')) == 2:
                create_repo(repo_id, exist_ok=True, token=token)
                card_content = pj(st.session_state)
                new_url = card_upload(card_content, repo_id, token=token)
                st.success(f"Pushed the card to the repo [here]({new_url})!")
            else:
                st.error("Repo ID invalid. It should be username/repo-name.")

        # Estado de descarga
        if "show_download" not in st.session_state:
            st.session_state.show_download = False

        st.markdown("## Download Model Card")

        with st.form("Download model card form"):
            st.markdown("This will export your model card as a Markdown file.")
            download_submit = st.form_submit_button("📥 Download Model Card")

            if download_submit:
                task = st.session_state.get("task")
                missing_required = validate_required_fields(model_card_schema, st.session_state, current_task=task)

                if missing_required:
                    st.session_state.show_download = False
                    st.error(
                        "The following required fields are missing:\n\n" +
                        "\n".join([f"- {field}" for field in missing_required])
                    )
                else:
                    st.session_state.show_download = True

        # Mostrar el botón real de descarga fuera del form si todo es válido
        if st.session_state.get("show_download"):
            card_content = pj(st.session_state)
            st.download_button(
                label="📥 Click here to download",
                data=card_content,
                file_name="model_card.md",
                mime="text/markdown"
            )

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
        page_switcher(task_selector_page)
        st.rerun()

if __name__ == '__main__':
    load_widget_state()
    if 'runpage' not in st.session_state:
        st.session_state.runpage = main
    st.session_state.runpage()
