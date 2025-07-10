# from yaml import load
from persist import persist, load_widget_state
import streamlit as st
from io import StringIO 
import tempfile
from pathlib import Path
import requests
from huggingface_hub import hf_hub_download, upload_file
import pandas as pd
from huggingface_hub import create_repo
import os
from datetime import date
from middleMan import parse_into_jinja_markdown as pj

import requests
import json

# Load schema once
with open("model_card_schema.json", "r") as f:
    model_card_schema = json.load(f)

def validate_required_fields(schema, session_state):
    missing_fields = []

    for section, fields in schema.items():
        for key, props in fields.items():
            full_key = f"{section}_{key}"  # match how we prefixed it in the form
            if props.get("required", False):
                value = session_state.get(full_key)
                if value in ("", None, [], {}):
                    label = props.get("label", key)
                    missing_fields.append(label)
    return missing_fields



@st.cache_data
def get_cached_data():

    license_df = pd.read_html("https://huggingface.co/docs/hub/repositories-licenses")[0]
    license_map = pd.Series(
        license_df["License identifier (to use in repo card)"].values, index=license_df.Fullname
    ).to_dict()
    return license_map


def card_upload(card_info,repo_id,token):
    #commit_message=None,
    repo_type = "model"
    commit_description=None,
    revision=None
    create_pr=None
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "README.md"
        tmp_path.write_text(str(card_info))
        url = upload_file(
                    path_or_fileobj=str(tmp_path),
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    token=token,
                    repo_type=repo_type,
                    # identical_ok=True,
                    revision=revision
                )
    return url

def images_upload(images_list,repo_id,token):
    repo_type = "model"
    commit_description=None,
    revision=None
    create_pr=None
    for img in images_list:
        if img is not None:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir) / "README.md"
                tmp_path.write_text(str(img))
                url = upload_file(
                            path_or_fileobj=str(tmp_path),
                            path_in_repo="README.md",
                            repo_id=repo_id,
                            token=token,
                            repo_type=repo_type,
                            # identical_ok=True,
                            revision=revision
                        )
    return url

def validate(self, repo_type="model"):
    """Validates card against Hugging Face Hub's model card validation logic.
    Using this function requires access to the internet, so it is only called
    internally by `modelcards.ModelCard.push_to_hub`.
    Args:
        repo_type (`str`, *optional*):
            The type of Hugging Face repo to push to. Defaults to None, which will use
            use "model". Other options are "dataset" and "space".
    """
    if repo_type is None:
        repo_type = "model"

    # TODO - compare against repo types constant in huggingface_hub if we move this object there.
    if repo_type not in ["model", "space", "dataset"]:
        raise RuntimeError(
            "Provided repo_type '{repo_type}' should be one of ['model', 'space',"
            " 'dataset']."
        )

    body = {
        "repoType": repo_type,
        "content": str(self),
    }
    headers = {"Accept": "text/plain"}

    try:
        r = requests.post(
            "https://huggingface.co/api/validate-yaml", body, headers=headers
        )
        r.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        if r.status_code == 400:
            raise RuntimeError(r.text)
        else:
            raise exc


## Save uploaded [markdown] file to directory to be used by jinja parser function 
def save_uploadedfile(uploadedfile):
    with open(uploadedfile.name,"wb") as f:
        f.write(uploadedfile.getbuffer())
    st.success("Saved File:{} to temp_uploaded_filed_Dir".format(uploadedfile.name))
    return uploadedfile.name 

def render_schema_section(schema_section, section_prefix=""):
    def render_field(key, props):
        full_key = f"{section_prefix}_{key}"
        label = props.get("label", key)
        description = props.get("description", "")
        example = props.get("example", "")
        field_type = props.get("type", "string")
        required = props.get("required", False)
        options = props.get("options", [])

        create_helpicon(label, description, field_type, example, required)

        if field_type == "select":
            st.selectbox("", options=options, key=persist(full_key), help=description)
        else:
            st.text_input("", key=persist(full_key), label_visibility="hidden")

    if section_prefix == "model_basic_information":
        with st.expander("Versioning"):
            for key in ["version_number", "version_changes"]:
                if key in schema_section:
                    render_field(key, schema_section[key])

        with st.expander("Model Scope"):
            for key in ["model_scope_summary", "model_scope_anatomical_site"]:
                if key in schema_section:
                    render_field(key, schema_section[key])

        for key, props in schema_section.items():
            if key in ["version_number", "version_changes", "model_scope_summary", "model_scope_anatomical_site"]:
                continue
            render_field(key, props)

    elif section_prefix == "card_metadata":
        with st.expander("Card Metadata"):
            for key in ["creation_date", "version_number", "version_changes", "doi"]:
                if key in schema_section:
                    render_field(key, schema_section[key])

        for key, props in schema_section.items():
            if key in ["creation_date", "version_number", "version_changes", "doi"]:
                continue
            render_field(key, props)

    else:
        for key, props in schema_section.items():
            render_field(key, props)



def input_with_inline_help(label, key, help_markdown):
            col1, col2 = st.columns([4, 1])
            with col1:
                value = st.text_input(label, key=key)
            with col2:
                if st.button("ℹ️", key=f"{key}_help"):
                    st.session_state[f"{key}_show_help"] = not st.session_state.get(f"{key}_show_help", False)

            if st.session_state.get(f"{key}_show_help", False):
                st.markdown(help_markdown)

            return value

def create_helpicon(var, Description, Format, Example, required=False):
    required_tag = "<span style='color: black; font-size: 1.2em; cursor: help;' title='Required field'>*</span>" if required else ""
    st.markdown("""
    <style>
    .tooltip-inline {
    display: inline-block;
    position: relative;
    margin-left: 4px;
    cursor: pointer;
    font-size: 0.8em;
    color: #999;  /* Make icon gray */
    }

    .tooltip-inline .tooltiptext {
      visibility: hidden;
      width: 260px;
      background-color: #f9f9f9;
      color: #333;
      text-align: left;
      border-radius: 6px;
      border: 1px solid #ccc;
      padding: 10px;
      position: absolute;
      bottom: 150%;
      left: 0;
      z-index: 10;
      box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
      font-weight: normal;
      font-size: 0.9em;  /* Smaller text inside the tooltip */
      line-height: 1.4;
    }

    .tooltip-inline:hover .tooltiptext {
      visibility: visible;
    }

    div[data-testid="stTextInput"] {
      margin-top: -10px;
    }
    </style>
    """, unsafe_allow_html=True)

    custom_label = f"""
    <div style='margin-bottom: -8px; font-weight: 500; font-size: 0.9em;'>
        {var} {required_tag}
        <span class="tooltip-inline">ⓘ
            <span class="tooltiptext">
                <span style="font-weight: bold;">Description:</span> {Description}<br><br>
                <span style="font-weight: bold;">Format:</span> {Format}<br><br>
                <span style="font-weight: bold;">Example(s):</span> {Example}
            </span>
        </span>
    </div>
    """

    st.markdown(custom_label, unsafe_allow_html=True)

def text_input(var,key_var,description,format,example):
    #create_helpicon(var,description,format,example)
    create_helpicon(var, description, props.get("type", ""), example, required=props.get("required", False))

    st.text_input(var, key=persist(key_var),label_visibility="hidden")

def main_page():
    today=date.today()
    		
    if "model_name" not in st.session_state:
        # Initialize session state.
        st.session_state.update({
            # Model Basic Information
            "model_version": "",
            "icd10": "",
            "treatment_modality": "",
            "prescription_levels": [],
            "additional_information": "",
            "motivation": "",
            "model_class":"",
            "creation_date": "",
            "architecture": "",
            "model_developers": "",
            "funded_by":"",
            "shared_by":"",
            "license": "",
            "finetuned_from": "",
            "research_paper": "",
            "git_repo": "",
            # Technical Specifications
            "nb_parameters": 5,
            "input_channels": [],
            "loss_function": "",
            "batch_size": 1,
            "patch_dimension": [],
            "architecture_filename":None,
            "libraries":[],
            "hardware": "",
            "inference_time": 10,
            "get_started_code": "",
            # Training Details
            "training_set_size":10,
            "validation_set_size":10,
            "age_fig_filename":"",
            "sex_fig_filename":"",
            "dataset_source": "",
            "acquisition_from": today,
            "acquisition_to": today,
            "markdown_upload": ""
        })
    ## getting cache for each warnings 
    license_map= get_cached_data()

    st.header("Card Metadata")
    render_schema_section(model_card_schema["card_metadata"], section_prefix="card_metadata")

    st.header("Model basic information (Dose prediction)")
    render_schema_section(model_card_schema["model_basic_information"], section_prefix="model_basic_information")



    # ## form UI setting 
    # st.header("Model basic information (Dose prediction)")
    # warning_placeholder = st.empty()
    # text_input("Name","model_name","","String, Free text format","DOSEPRED_VMAT_ORO_70005425Gy")
    # text_input("Creation date","creation_date","Date when the model was created (i.e. when the model was trained and/or selected in its current version)","""String, Formatted text as <code>YYYYMMDD</code>""","<code>20241001</code>")
    # with st.expander("Versioning"):
        
    #     text_input("Version number","model_version","Version number of the model card.","""<code>MM.mm.bbbb</code><br>
    #             • MM = major<br>
    #             • mm = minor<br>
    #             • bbbb = build<br>""","""<code>01.00.0000</code>""")
    #     text_input("Version changes","version_changes","""Describe the main changes or reason for upgrading the card with respect to the previous version.<br>
    #                     If this is the first version of the model card, indicate “NA” (Not Applicable)""","String, Free text format", "New limitations of the model are found”, ”new evaluation on a different dataset is added”, etc")
    
    # text_input("DOI", "doi","Unique Digital Object Identifier for the current version on the model. \
    #               If your model has been uploaded to a repository that provides DOI (e..g Zenodo, HuggingFace), we encourage you to indicate the corresponding DOI.","String, Free text format","")
    # with st.expander("Model Scope"):
    #     text_input("Summary","model_scope_summary","1 sentence summary of what the model does,\
    #                    including relevant information for model input and output. Detailed specifications for input/output should go in the section “Technical specifications”","String, Free text format","Auto-segmentation model of HN OARs on CT")
    #     text_input("Anatomical site","model_scope_Anasite","General body site","String, Formatted text as in StandardListValues =  {‘Brain’, ‘HN’, ‘Thorax’, ‘Abdomen’, ‘Pelvis’,’Other’}","HN")
    
    # with st.expander("Clearance"):
    #     text_input("Type","clearance_type","Disclose if the model has been approved for medical use or not, and the model's regulatory clearance, if any.","String, free text",\
    #                     "Approved for medical use (in-house) by hospital team, FDA approved, CE approved, IMDD available, Not-approved for medical use - only research use")
    #     st.caption("Approved by")
    #     tab1, tab2 = st.tabs(["Institution(s)", "Name(s)"])
    #     with tab1:
    #         text_input("Institution(s)","approved_by_institution","Institution(s) involved in the approval of the model. \
    #                        If several, separate them by commas.","String, Free text format","UCLouvain")
    #     with tab2:
    #         text_input("Name(s)","approved_by_names","Name of the person(s) who approved the model or contact person on behalf of  the team. \
    #             If several, separate them by commas.","String, Free text format","Maria Smith")
    #     text_input("Additional Information","approved_by_additional_info","Add any other information regarding the clearance / \
    #                   approval process you consider relevant (e.g. the qualification of the persons / team)","String, Free text format","")
    # text_input("Intended users","intended_users","Intended users of the model","String, Free text format","Radiation oncologists, medical physicists, and dosimetrists")
    # text_input("Observed limitations","observed_imitations","Existing biases or limitations of the model, and particular cases for which the model has been tested and shown poor performance.\
    #             Examples include imbalanced or missing training data, overfitting, generalizability and suitability for certain use cases,\
    #             or  de-identification methods used for the dataset that might influence the model performance (e.g. defacing of H&N scans)","String, Free text format","implants, contrast CT, post-operative patients, \
    #                 BMI > X, model not suitable for synthesising the nose since de-identification included defacing")
    # text_input("Potential limitations","potential_limitations","Potential biases or limitations of the model. \
    #            Specific cases, relevant to the model application (i.e. likely to arrive),  for which the model may show poor performance.","String, Free text format"," implants, contrast CT, post-operative patients, BMI > X")
    # text_input("Type of learning architecture","type_of_learning_architecture","Type of architecture for the learning model, if several models are used (e.g. cascade, cycle, tree,...), indicate all different types. ",\
    #            " String, Free text format","Random Forest, CNN, UNet, Transformers")
    # with st.expander("Developed by"):
    #     tab1, tab2 ,tab3= st.tabs(["Institution(s)", "Name(s)","Contact(s)"])
    #     with tab1:
    #         text_input("Institution(s)","developed_by_institution","Institution(s) involved in the model development.\
    #                     Indicate single or multi-institutions involved in the model creation (indicating the role of each institute or the type of collaboration) ","String, Free text format","UCLouvain")
    #     with tab2:
    #         text_input("Name(s)","developed_by_name","Name of the person(s) who developed the model or contact person on behalf of  the development team.\
    #                     If several, separate them by commas.","String, Free text format","Maria Smith")
    #     with tab3:
    #         text_input("Contact email(s)","developed_by_contact_email","Contact email for the development team or persons. If several, separate them by commas.","String, Free text format","")
    # text_input("Conflict of interest","conflict_of_interest","Disclose potential conflicts of interest, including, whenever applicable and possible, funding bodies involved in the development of the model.\
    #             Otherwise, indicate “NA” (Not Applicable)","String, Free text format","")
    # text_input("Software licence","software_licence","Software licence or copyright governing the use or redistribution of the model, source code and associated software to run it.\
    #             Types include free and open (e.g. permissive, copyleft) and non-free (i.e. proprietary licence)","String, Free text format","Apache 2.0, GPL, MIT")
    # text_input("Code source","code_source","Link(s) to repository (e.g. github/gitlab) or website where the code source of the learning architecture and inference pipeline is located. \
    #            If the code source is not made available, indicate “NA” (Not applicable), or eventually, you might use this field to indicate the location / path in your internal computers.","String, Free text format","")
    # text_input("Model source","model_source","Link to the trained learning model (i.e. weights) to run inference (e.g. HuggingFace, website, …).\
    #             If the trained model is not made available, indicate “NA” (Not applicable), or eventually, you might use this field to indicate the path / location  in your internal computers.","String, Free text format","")
    # text_input("Citation details","citation_details","Associated scientific paper(s)","String, Free text format","")
    # text_input("URL info","url_info","Link to a website with more information, or pdf ","String, Free text format","")

    # warnings setting
    # languages=st.session_state.languages or None
    license=st.session_state.license or None
    task = None #st.session_state.task or None
    markdown_upload = st.session_state.markdown_upload
    #uploaded_model_card = st.session_state.uploaded_model 
    # Handle any warnings...
    do_warn = False
    warning_msg = "Warning: The following fields are required but have not been filled in: "
    if not license:
        warning_msg += "\n- License"
        do_warn = True
    if do_warn:
        warning_placeholder.error(warning_msg)

    with st.sidebar:

        ######################################################
        ### Uploading a model card from local drive
        ######################################################
        st.markdown("## Upload Model Card")
       
        st.markdown("#### Model Card must be in markdown (.md) format.") 

        # Read a single file 
        uploaded_file = st.file_uploader("Choose a file", type = ['md'], help = 'Please choose a markdown (.md) file type to upload')
        if uploaded_file is not None:
            name_of_uploaded_file = save_uploadedfile(uploaded_file)
           
            st.session_state.markdown_upload = name_of_uploaded_file ## uploaded model card

        # elif st.session_state.task =='fill-mask' or 'translation' or 'token-classification' or ' sentence-similarity' or 'summarization' or 'question-answering' or 'text2text-generation' or 'text-classification' or 'text-generation' or 'conversational':
        #     print("YO",st.session_state.task)
        #     st.session_state.markdown_upload = "language_model_template1.md" ## language model template
        
        else:#if st.session_state.task:
            
            st.session_state.markdown_upload =  "current_card.md" ## default non language model template
        print("st.session_state.markdown_upload",st.session_state.markdown_upload)
        #########################################
        ### Uploading model card to HUB
        #########################################
        out_markdown =open( st.session_state.markdown_upload, "r+"
            ).read() 
        print_out_final = f"{out_markdown}"
        st.markdown("## Export Loaded Model Card to Hub")
        with st.form("Upload to 🤗 Hub"):
            st.markdown("Use a token with write access from [here](https://hf.co/settings/tokens)")
            token = st.text_input("Token", type='password')
            repo_id = st.text_input("Repo ID")
            submit = st.form_submit_button('Upload to 🤗 Hub', help='The current model card will be uploaded to a branch in the supplied repo ')

        # if submit:
        #     if len(repo_id.split('/')) == 2:
        #         repo_url = create_repo(repo_id, exist_ok=True, token=token)
        #         new_url = card_upload(pj(),repo_id, token=token)
        #         # images_upload([st.session_state['architecture_filename'], st.session_state["age_fig_filename"], st.session_state["sex_fig_filename"]],repo_id, token=token)
        #         st.success(f"Pushed the card to the repo [here]({new_url})!") # note: was repo_url
        #     else:
        #         st.error("Repo ID invalid. It should be username/repo-name. For example: nateraw/food")
        if submit:
            missing = validate_required_fields(model_card_schema, st.session_state)
            if missing:
                st.error("Please complete the required fields: " + ", ".join(missing))
            elif len(repo_id.split('/')) == 2:
                repo_url = create_repo(repo_id, exist_ok=True, token=token)
                new_url = card_upload(pj(), repo_id, token=token)
                st.success(f"Pushed the card to the repo [here]({new_url})!")
            else:
                st.error("Repo ID invalid. It should be username/repo-name. For example: nateraw/food")


        #########################################
        ### Download model card
        #########################################


        st.markdown("## Download current Model Card")

        if st.session_state.model_name is None or st.session_state.model_name== ' ':
            downloaded_file_name = 'current_model_card.md'
        else: 
            downloaded_file_name = st.session_state.model_name+'_'+'model_card.md'
        download_status = st.download_button(label = 'Download Model Card', data = pj(), file_name = downloaded_file_name, help = "The current model card will be downloaded as a markdown (.md) file")
        if download_status == True:
            st.success("Your current model card, successfully downloaded 🤗")


def page_switcher(page):
    st.session_state.runpage = page    

def main():
    
    st.header("About Model Cards")
    st.markdown(Path('about.md').read_text(), unsafe_allow_html=True)
    btn = st.button('Create a Model Card 📝',on_click=page_switcher,args=(main_page,))
    if btn:
        st.experimental_rerun() # rerun is needed to clear the page

if __name__ == '__main__':
    load_widget_state()
    if 'runpage' not in st.session_state :
        st.session_state.runpage = main
    st.session_state.runpage()