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

@st.cache
def get_icd():
    # Get ICD10 list
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = '3bc9c811-7f2e-4dab-a2dc-940e47a38fef_a6108252-4503-4ff7-90ab-300fd27392aa'
    client_secret = 'xPj7mleWf1Bilu9f7P10UQmBPvL5F6Wgd8/rJhO1T04='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'
    # set data to post
    payload = {'client_id': client_id, 
            'client_secret': client_secret, 
            'scope': scope, 
            'grant_type': grant_type}
    # make request
    r = requests.post(token_endpoint, data=payload, verify=False).json()
    token = r['access_token']
    # access ICD API
    uri = 'https://id.who.int/icd/release/10/2019/C00-C75'
    # HTTP header fields to set
    headers = {'Authorization':  'Bearer '+token, 
            'Accept': 'application/json', 
            'Accept-Language': 'en',
            'API-Version': 'v2'}        
    # make request           
    r = requests.get(uri, headers=headers, verify=False)
    print("icd",r.json())
    icd_map =[]
    for child in r.json()['child']: 
        r_child = requests.get(child, headers=headers,verify=False).json()
        icd_map.append(r_child["code"]+" "+r_child["title"]["@value"])
    return icd_map

@st.cache    
def get_treatment_mod():
    url = "https://clinicaltables.nlm.nih.gov/loinc_answers?loinc_num=21964-2"
    r = requests.get(url).json()
    treatment_mod = [treatment['DisplayText'] for treatment in r]
    return treatment_mod


@st.cache
def get_cached_data():
    languages_df = pd.read_html("https://hf.co/languages")[0]
    languages_map = pd.Series(languages_df["Language"].values, index=languages_df["ISO code"]).to_dict()

    license_df = pd.read_html("https://huggingface.co/docs/hub/repositories-licenses")[0]
    license_map = pd.Series(
        license_df["License identifier (to use in repo card)"].values, index=license_df.Fullname
    ).to_dict()

    available_metrics = [x['id'] for x in requests.get('https://huggingface.co/api/metrics').json()]

    r = requests.get('https://huggingface.co/api/models-tags-by-type')
    tags_data = r.json()
    libraries = [x['id'] for x in tags_data['library']]
    tasks = [x['id'] for x in tags_data['pipeline_tag']]

    icd_map = get_icd()
    treatment_mod = get_treatment_mod()
    return languages_map, license_map, available_metrics, libraries, tasks, icd_map, treatment_mod


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


def main_page():
    today=date.today()
    		
    if "model_name" not in st.session_state:
        # Initialize session state.
        st.session_state.update({
            # Model Basic Information
            "model_version": 0,
            "icd10": [],
            "treatment_modality": [],
            "prescription_levels": [],
            "additional_information": "",
            "motivation": "",
            "model_class":"",
            "creation_date": today,
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
    languages_map, license_map, available_metrics, libraries, tasks, icd_map, treatment_mod = get_cached_data()

    ## form UI setting 
    st.header("Model basic information (Dose prediction)")

    warning_placeholder = st.empty()

    st.text_input("Model Name", key=persist("model_name"))
    st.number_input("Version",key=persist("model_version"),step=0.1)
    st.text("Intended use:")
    left, right = st.columns([4,2])
    left.multiselect("Treatment site ICD10",list(icd_map), help="Reference ICD10 WHO: https://icd.who.int/icdapi",key=persist("icd10"))
    right.multiselect("Treatment modality", list(treatment_mod), help="Reference LOINC Modality Radiation treatment: https://loinc.org/21964-2", key=persist("treatment_modality"))
    left, right = st.columns(2)
    nlines = int(left.number_input("Number of prescription levels", 0, 20, 1))
    # cols = st.columns(ncol)
    for i in range(nlines):
        right.number_input(f"Prescription [Gy] # {i}", key=i)
    st.text_area("Additional information", placeholder = "Bilateral cases only", help="E.g. Bilateral cases only", key=persist('additional_information'))
    st.text_area("Motivation for development", key=persist('motivation'))
    st.text_area("Class", placeholder="RULE 11, FROM MDCG 2021-24", key=persist('model_class'))
    st.date_input("Creation date", key=persist('creation_date'))
    st.text_area("Type of architecture",value="UNet", key=persist('architecture'))

    st.text("Developed by:")
    left, middle, right = st.columns(3)
    left.text_input("Name", key=persist('dev_name'))
    middle.text_input("Institution", placeholder = "University/clinic/company", key=persist('dev_institution'))
    right.text_input("Email", key=persist('dev_email'))

    st.text_area("Funded by", key=persist('funded_by'))
    st.text_area("Shared by", key=persist('shared_by'))
    st.selectbox("License", [""] + list(license_map.values()), help="The license associated with this model.", key=persist("license"))
    st.text_area("Fine tuned from model", key=persist('finetuned_from'))
    st.text_area("Related Research Paper", help="Research paper related to this model.", key=persist("research_paper"))
    st.text_input("Related GitHub Repository", help="Link to a GitHub repository used in the development of this model", key=persist("git_repo"))
    # st.selectbox("Library Name", [""] + libraries, help="The name of the library this model came from (Ex. pytorch, timm, spacy, keras, etc.). This is usually automatically detected in model repos, so it is not required.", key=persist('library_name'))
    # st.text_input("Parent Model (URL)", help="If this model has another model as its base, please provide the URL link to the parent model", key=persist("Parent_Model_name"))
    # st.text_input("Datasets (comma separated)", help="The dataset(s) used to train this model. Use dataset id from https://hf.co/datasets.", key=persist("datasets"))
    # st.multiselect("Metrics", available_metrics, help="Metrics used in the training/evaluation of this model. Use metric id from https://hf.co/metrics.", key=persist("metrics"))
    # st.selectbox("Task", [""] + tasks, help="What task does this model aim to solve?", key=persist('task'))
    # st.text_input("Tags (comma separated)", help="Additional tags to add which will be filterable on https://hf.co/models. (Ex. image-classification, vision, resnet)", key=persist("tags"))
    # st.text_input("Author(s) (comma separated)", help="The authors who developed this model. If you trained this model, the author is you.", key=persist("the_authors"))
    # s
    # st.text_input("Carbon Emitted:", help="You can estimate carbon emissions using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700)", key=persist("Model_c02_emitted"))
   
    # st.header("Technical specifications")
    # st.header("Training data, methodology, and results")
    # st.header("Evaluation data, methodology, and results / commissioning")
    # st.header("Ethical use considerations")

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

        if submit:
            if len(repo_id.split('/')) == 2:
                repo_url = create_repo(repo_id, exist_ok=True, token=token)
                new_url = card_upload(pj(),repo_id, token=token)
                # images_upload([st.session_state['architecture_filename'], st.session_state["age_fig_filename"], st.session_state["sex_fig_filename"]],repo_id, token=token)
                st.success(f"Pushed the card to the repo [here]({new_url})!") # note: was repo_url
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
