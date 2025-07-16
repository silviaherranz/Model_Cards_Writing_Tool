from persist import persist, load_widget_state
from render import render_evaluation_section, render_field, title_header, create_helpicon, section_divider, render_schema_section
import streamlit as st
from pathlib import Path
from huggingface_hub import upload_file, create_repo
from datetime import date
from middleMan import parse_into_jinja_markdown as pj
from datetime import datetime
import pandas as pd
import tempfile
import json

with open("model_card_schema.json", "r") as f:
    model_card_schema = json.load(f)

def get_state(key, default=None):
    return st.session_state.get(key, default)

def light_header(text, size="16px", bottom_margin="1em"):
    st.markdown(f"""
        <div style='font-size: {size}; font-weight: normal; color: #444; margin-bottom: {bottom_margin};'>
            {text}
        </div>
    """, unsafe_allow_html=True)

def light_header_italics(text, size="16px", bottom_margin="1em"):
    st.markdown(f"""
        <div style='font-size: {size}; font-style: italic; font-weight: normal; color: #444; margin-bottom: {bottom_margin};'>
            {text}
        </div>
    """, unsafe_allow_html=True)


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

@st.cache_data(ttl=3600)
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
        key=persist("task"),
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
                field = key[len(prefix):]
                entry[field] = value
        evaluations.append(entry)
    return evaluations

def main_page():
    today = date.today()
    if "task" not in st.session_state:
        st.session_state.task = "Image-to-Image translation"
    
    if "learning_architecture_forms" not in st.session_state:
        st.session_state.learning_architecture_forms = [{}]


    if "evaluation_forms" not in st.session_state:
        existing_keys = [k for k in st.session_state.keys() if k.startswith("evaluation_")]
        if existing_keys:
            indices = set(k.split("_")[1] for k in existing_keys if k.split("_")[1].isdigit())
            st.session_state.evaluation_forms = [{} for _ in indices]
        else:
            st.session_state.evaluation_forms = [{}]

    task = st.session_state.get("task", "Image-to-Image translation")

    for key, value in {
        "model_name": "",
        "license": "",
        "markdown_upload": "current_card.md"
    }.items():
        st.session_state.setdefault(key, value)

    get_cached_data()

    # with st.expander("Card Metadata", expanded=False):
    #     render_schema_section(model_card_schema["card_metadata"], section_prefix="card_metadata", current_task=task)
    with st.expander("Card Metadata", expanded=False):
        section = model_card_schema["card_metadata"]
        # Render creation_date
        #if "creation_date" in section:
            #render_field("creation_date", section["creation_date"], "card_metadata")
        if "creation_date" in section:
            props = section["creation_date"]
            label = props.get("label", "Creation Date")
            description = props.get("description", "")
            example = props.get("example", "")
            required = props.get("required", False)
            type = props.get("type", "date")

            create_helpicon(label, description, type, example, required)

            # Calendar input from 1900 to today
            date_value = st.date_input(
                "Select a date",
                min_value=datetime(1900, 1, 1),
                max_value=datetime.today(),
                key="creation_date_widget"
            )

            # Format date as YYYYMMDD (e.g., 20240102)
            formatted = date_value.strftime("%Y%m%d")

            # Store in session using your persistent key logic
            st.session_state[persist("card_metadata_creation_date")] = formatted

        title_header("Versioning", size="1rem", bottom_margin="0.01em", top_margin="0.5em")

        # Render version_number + version_changes in the same row using create_helpicon for labels
        if all(k in section for k in ["version_number", "version_changes"]):
            col1, col2 = st.columns([1, 3])
            with col1:
                props = section["version_number"]
                create_helpicon(
                    props.get("label", "Version Number"),
                    props.get("description", ""),
                    props.get("type", ""),
                    props.get("example", ""),
                    props.get("required", False),
                )
                st.number_input(
                    label=".",
                    min_value=0.0,
                    max_value=10000000000.0,
                    step=0.10,
                    format="%.2f",
                    key=persist("card_metadata_version_number"),
                    label_visibility="hidden"
                )

            with col2:
                props = section["version_changes"]
                create_helpicon(
                    props.get("label", "Version Changes"),
                    props.get("description", ""),
                    props.get("type", ""),
                    props.get("example", ""),
                    props.get("required", False),
                )
                st.text_input(
                    label=".",
                    key=persist("card_metadata_version_changes"),
                    label_visibility="hidden"
                )
        # Render all other metadata fields except the three already handled
        for key in section:
            if key not in ["creation_date", "version_number", "version_changes"]:
                render_field(key, section[key], "card_metadata")

    def filter_fields_by_task(fields, task):
        return {k: v for k, v in fields.items() if "model_types" not in v or task in v["model_types"]}

    with st.expander("Model Basic Information", expanded=False):
        #filtered_fields = filter_fields_by_task(model_card_schema["model_basic_information"], task)
        #render_schema_section(filtered_fields, section_prefix="model_basic_information", current_task=task)
        section = model_card_schema["model_basic_information"]
        # Line 1: name + creation_date
        if "name" in section and "creation_date" in section:
            col1, col2 = st.columns(2)
            with col1:
                render_field("name", section["name"], "model_basic_information")
            with col2:
                props = section["creation_date"]
                label = props.get("label", "Creation Date")
                description = props.get("description", "")
                example = props.get("example", "")
                required = props.get("required", False)
                field_type = props.get("type", "date")

                create_helpicon(label, description, field_type, example, required)

                date_value = st.date_input(
                    "Select a date",
                    min_value=datetime(1900, 1, 1),
                    max_value=datetime.today(),
                    key="model_basic_information_creation_date_widget"
                )

                formatted = date_value.strftime("%Y%m%d")
                st.session_state[persist("model_basic_information_creation_date")] = formatted

        section_divider()
        title_header("Versioning", size="1rem", bottom_margin="0.01em", top_margin="0.5em")
        # Line 2: version_number + version_changes
        if "version_number" in section and "version_changes" in section:
            col1, col2 = st.columns([1, 3])
            with col1:
                section["version_number"]["placeholder"] = "MM.mm.bbbb"
                render_field("version_number", section["version_number"], "model_basic_information")
            with col2:
                render_field("version_changes", section["version_changes"], "model_basic_information")
        section_divider()
        # Line 3: doi
        if "doi" in section:
            render_field("doi", section["doi"], "model_basic_information")
        section_divider()
        title_header("Model scope", size="1rem", bottom_margin="0.01em", top_margin="0.5em")
        # Line 4: summary + anatomical_site
        if "model_scope_summary" in section and "model_scope_anatomical_site" in section:
            col1, col2 = st.columns([2, 1])
            with col1:
                render_field("model_scope_summary", section["model_scope_summary"], "model_basic_information")
            with col2:
                render_field("model_scope_anatomical_site", section["model_scope_anatomical_site"], "model_basic_information")
        section_divider()
        # Line 5: Clearance 
        title_header("Clearance", size="1rem", bottom_margin="0.01em", top_margin="0.5em")
        # Render clearance_type
        if "clearance_type" in section:
            render_field("clearance_type", section["clearance_type"], "model_basic_information")
        # Grouped "Approved by"
        if all(k in section for k in [
            "clearance_approved_by_name",
            "clearance_approved_by_institution",
            "clearance_approved_by_contact_email"
        ]):
            title_header("Approved by", size="1rem", bottom_margin="0.5em")
            col1, col2, col3 = st.columns([1, 1.5, 1.5])
            with col1:
                render_field("clearance_approved_by_name", section["clearance_approved_by_name"], "model_basic_information")
            with col2:
                render_field("clearance_approved_by_institution", section["clearance_approved_by_institution"], "model_basic_information")
            with col3:
                render_field("clearance_approved_by_contact_email", section["clearance_approved_by_contact_email"], "model_basic_information")

        # Render additional information
        if "clearance_additional_information" in section:
            render_field("clearance_additional_information", section["clearance_additional_information"], "model_basic_information")

        section_divider()

        render_field("intended_users", section["intended_users"], "model_basic_information")
        render_field("observed_limitations", section["observed_limitations"], "model_basic_information")
        render_field("potential_limitations", section["potential_limitations"], "model_basic_information")
        render_field("type_of_learning_architecture", section["type_of_learning_architecture"], "model_basic_information")

        section_divider()

        # Developer Information
        title_header("Developed by", size="1rem", bottom_margin="0.5em")
        col1, col2, col3 = st.columns([1, 1.5, 1.5])
        with col1:
            render_field("developed_by_name", section["developed_by_name"], "model_basic_information")
        with col2:
            render_field("developed_by_institution", section["developed_by_institution"], "model_basic_information")
        with col3:
            render_field("developed_by_email", section["developed_by_email"], "model_basic_information")

        section_divider()

        render_field("conflict_of_interest", section["conflict_of_interest"], "model_basic_information")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            render_field("software_license", section["software_license"], "model_basic_information")
        with col2:
            render_field("code_source", section["code_source"], "model_basic_information")
        with col3:
            render_field("model_source", section["model_source"], "model_basic_information")

        col1, col2 = st.columns([1,1])
        with col1:
            render_field("citation_details", section["citation_details"], "model_basic_information")
        with col2:
            render_field("url_info", section["url_info"], "model_basic_information")




    missing_required = validate_required_fields(model_card_schema, st.session_state, current_task=task)
    
    with st.expander("Technical Specifications", expanded=False):
        title_header("Model overview", size="1.1rem")
        title_header("1. Model pipeline", size="1rem", bottom_margin="0.5em")
        #render_schema_section(model_card_schema["technical_specifications"], section_prefix="technical_specifications")
        section = model_card_schema["technical_specifications"]
        render_field("model_pipeline_summary", section["model_pipeline_summary"], "technical_specifications")
        render_field("model_pipeline_figure", section["model_pipeline_figure"], "technical_specifications")

        section_divider()
        # Row 1: model_inputs and model_outputs
        col1, col2 = st.columns([1, 1])
        with col1:
            render_field("model_inputs", section["model_inputs"], "technical_specifications")
        with col2:
            render_field("model_outputs", section["model_outputs"], "technical_specifications")

        # Row 2: pre_processing and post_processing with larger boxes
        col1, col2 = st.columns([1, 1])
        with col1:
            render_field("pre-processing", section["pre-processing"], "technical_specifications")
        with col2:
            render_field("post-processing", section["post-processing"], "technical_specifications")

        # Optional: Render any other leftover fields
        # for key in section:
        #     if key not in ["model_inputs", "model_outputs", "pre_processing", "post_processing"]:
        #         render_field(key, section[key], "technical_specifications")

        section_divider()
        # -- Learning Architecture Header --
        title_header("2. Learning Architecture", size="1rem", bottom_margin="0.5em")
        light_header_italics("If several models are used (e.g. cascade, cycle, tree,...), repeat this section for each of them.")
         # Add before the UI block (safe initialization)
        if "selected_learning_arch_to_delete" not in st.session_state:
            st.session_state.selected_learning_arch_to_delete = None
        # -- Cleaner Button Layout --
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.button("➕ Add Learning Architecture", key="add_learning_arch")
            
            with col2:
                if len(st.session_state.learning_architecture_forms) > 1:
                    selected_model_to_delete = st.selectbox(
                        "Delete a model:",
                        [f"Learning Architecture {i+1}" for i in range(len(st.session_state.learning_architecture_forms))],
                        key="learning_architecture_delete_select_clean"
                    )

                    if selected_model_to_delete:
                        selected_idx = int(selected_model_to_delete.split()[-1]) - 1
                        st.session_state.selected_learning_arch_to_delete = selected_idx

                    if st.button("🗑️ Delete", key="delete_learning_arch_clean"):
                        idx = st.session_state.get("selected_learning_arch_to_delete")
                        if idx is not None and idx < len(st.session_state.learning_architecture_forms):
                            del st.session_state.learning_architecture_forms[idx]

                            # Clean up corresponding keys
                            for key in list(st.session_state.keys()):
                                if key.startswith(f"learning_architecture_{idx}_"):
                                    del st.session_state[key]

                            # Shift all remaining keys down
                            for i in range(idx + 1, 100):  # arbitrary upper bound
                                for key in list(st.session_state.keys()):
                                    if key.startswith(f"learning_architecture_{i}_"):
                                        new_key = key.replace(f"learning_architecture_{i}_", f"learning_architecture_{i-1}_")
                                        st.session_state[new_key] = st.session_state.pop(key)

                            st.rerun()


            # -- Add New Architecture on Click --
            if st.session_state.get("add_learning_arch", False):
                st.session_state.learning_architecture_forms.append({})
                st.rerun()


        # --- TABS FOR EACH LEARNING ARCHITECTURE ---
        tab_labels = [f"Learning Architecture {i+1}" for i in range(len(st.session_state.learning_architecture_forms))]
        tabs = st.tabs(tab_labels)

        for i, tab in enumerate(tabs):
            with tab:
                render_schema_section(
                    model_card_schema["learning_architecture"],
                    section_prefix=f"learning_architecture_{i}"
                )

        section_divider()
        title_header("3. Hardware & Software", size="1rem")
        #render_schema_section(model_card_schema["hw_and_sw"], section_prefix="hw_and_sw")
        section = model_card_schema["hw_and_sw"]
        # Row 1: Libraries and Dependencies (longer input, full width)
        render_field("libraries_and_dependencies", section["libraries_and_dependencies"], "hw_and_sw")

        # Row 2: Hardware + Inference time side-by-side
        col1, col2 = st.columns(2)
        with col1:
            render_field("hardware_recommended", section["hardware_recommended"], "hw_and_sw")
        with col2:
            render_field("inference_time_for_recommended_hw", section["inference_time_for_recommended_hw"], "hw_and_sw")
        col1, col2 = st.columns(2)
        with col1:
            render_field("installation_getting_started", section["installation_getting_started"], "hw_and_sw")
        with col2:
            render_field("environmental_impact", section["environmental_impact"], "hw_and_sw")




    light_header("Evaluation Data Methodology, Results & Commissioning")
    light_header_italics("To be repeated as many times as evaluations sets used", bottom_margin="1em")

    to_delete = None
    for i, eval_data in enumerate(st.session_state.evaluation_forms):
        with st.expander(f"Evaluation {i+1}", expanded=False):
            render_evaluation_section(
                model_card_schema["evaluation_data_methodology_results_commisioning"],
                section_prefix=f"evaluation_{i}",
                current_task=task
            )
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button(f"🗑️ Delete", key=f"delete_eval_{i}"):
                    to_delete = i

    if to_delete is not None:
        del st.session_state.evaluation_forms[to_delete]
        for key in list(st.session_state.keys()):
            if key.startswith(f"evaluation_{to_delete}_"):
                del st.session_state[key]
        st.rerun()

    if st.button("➕ Add Another Evaluation"):
        st.session_state.evaluation_forms.append({})
        st.rerun()

    with st.expander("Other considerations", expanded=False):
        section = model_card_schema["other_considerations"]
        render_field("responsible_use_and_ethical_considerations", section["responsible_use_and_ethical_considerations"], "other_considerations")
        render_field("risk_analysis", section["risk_analysis"], "other_considerations")
        render_field("post_market_surveillance_live_monitoring", section["post_market_surveillance_live_monitoring"], "other_considerations")

    if missing_required:
        st.warning("Warning: The following required fields are missing:\n\n" + "\n".join([f"- {field}" for field in missing_required]))

    with st.sidebar:
        st.markdown("## Upload Model Card")
        uploaded_file = st.file_uploader("Choose a file", type=['md'], help='Upload a markdown (.md) file')
        if uploaded_file:
            st.session_state.markdown_upload = save_uploadedfile(uploaded_file)
        else:
            st.session_state.markdown_upload = "current_card.md"

        try:
            out_markdown = Path(st.session_state.markdown_upload).read_text()
        except FileNotFoundError:
            st.error(f"File {st.session_state.markdown_upload} not found. Please upload a valid file.")
            out_markdown = ""

        st.markdown("## Export Loaded Model Card to Hub")
        with st.form("Upload to 🤗 Hub"):
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

        if "show_download" not in st.session_state:
            st.session_state.show_download = False

        st.markdown("## Download Model Card")
        with st.form("Download model card form"):
            download_submit = st.form_submit_button("📥 Download Model Card")
            if download_submit:
                task = st.session_state.get("task")
                missing_required = validate_required_fields(model_card_schema, st.session_state, current_task=task)
                if missing_required:
                    st.session_state.show_download = False
                    st.error("The following required fields are missing:\n\n" + "\n".join([f"- {field}" for field in missing_required]))
                else:
                    st.session_state.show_download = True

        if st.session_state.get("show_download"):
            card_content = pj(st.session_state)
            st.download_button("📥 Click here to download", data=card_content, file_name="model_card.md", mime="text/markdown")

def page_switcher(page):
    st.session_state.runpage = page

def main():
    st.header("About Model Cards")
    about_path = Path('about.md')
    if about_path.exists():
        st.markdown(about_path.read_text(), unsafe_allow_html=True)
    else:
        st.error("The file 'about.md' is missing. Please ensure it exists in the current working directory.")

    if st.button('Create a Model Card 📝'):
        page_switcher(task_selector_page)
        st.rerun()

if __name__ == '__main__':
    # Pre-initialize problematic widget keys to avoid KeyErrors
    if "learning_architecture_delete_select_clean" not in st.session_state:
        st.session_state.learning_architecture_delete_select_clean = None
    load_widget_state()
    if 'runpage' not in st.session_state:
        st.session_state.runpage = main
    st.session_state.runpage()
