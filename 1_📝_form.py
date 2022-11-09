from yaml import load
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
from middleMan import parse_into_jinja_markdown as pj

@st.cache
def get_cached_data():
    languages_df = pd.read_html("https://hf.co/languages")[0]
    languages_map = pd.Series(languages_df["Language"].values, index=languages_df["ISO code"]).to_dict()

    license_df = pd.read_html("https://huggingface.co/docs/hub/repositories-licenses")[0]
    license_map = pd.Series(
        license_df["License identifier (to use in model card)"].values, index=license_df.Fullname
    ).to_dict()

    available_metrics = [x['id'] for x in requests.get('https://huggingface.co/api/metrics').json()]

    r = requests.get('https://huggingface.co/api/models-tags-by-type')
    tags_data = r.json()
    libraries = [x['id'] for x in tags_data['library']]
    tasks = [x['id'] for x in tags_data['pipeline_tag']]
    return languages_map, license_map, available_metrics, libraries, tasks


def card_upload(card_info,repo_id,token):
    #commit_message=None,
    repo_type = "space"
    commit_description=None,
    revision=None,
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
                    identical_ok=True,
                    revision=revision,
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
    with open(os.path.join("temp_uploaded_filed_Dir",uploadedfile.name),"wb") as f:
        f.write(uploadedfile.getbuffer())
    st.success("Saved File:{} to temp_uploaded_filed_Dir".format(uploadedfile.name))
    return uploadedfile.name 

def main():
    if "model_name" not in st.session_state:
        # Initialize session state.
        st.session_state.update({
            "input_model_name": "",
            "languages": [],
            "license": "",
            "library_name": "",
            "datasets": "",
            "metrics": [],
            "task": "",
            "tags": "",
            "model_description": "Some cool model...",
            "the_authors":"",
            "Shared_by":"",
            "Model_details_text": "",
            "Model_developers": "",
            "blog_url":"",
            "Parent_Model_url":"",
            "Parent_Model_name":"",

            "Model_how_to": "",
            
            "Model_uses": "",
            "Direct_Use": "",
            "Downstream_Use":"",
            "Out-of-Scope_Use":"",

            "Model_Limits_n_Risks": "",
            "Recommendations":"",

            "training_Data": "",
            "model_preprocessing":"",
            "Speeds_Sizes_Times":"",



            "Model_Eval": "",
            "Testing_Data":"",
            "Factors":"",
            "Metrics":"",
            "Model_Results":"",

            "Model_c02_emitted": "",
            "Model_hardware":"",
            "hours_used":"",
            "Model_cloud_provider":"",
            "Model_cloud_region":"",

            "Model_cite": "",
            "paper_url": "",
            "github_url": "",
            "bibtex_citation": "",
            "APA_citation":"",

            "Model_examin":"",
            "Model_card_contact":"",
            "Model_card_authors":"",
            "Glossary":"",
            "More_info":"",

            "Model_specs":"",
            "compute_infrastructure":"",
            "technical_specs_software":"",

            "check_box": bool,
            "markdown_upload":" ",
            "legal_view":bool,
            "researcher_view":bool,
            "beginner_technical_view":bool,
            "markdown_state":"",
        })
    ## getting cache for each warnings 
    languages_map, license_map, available_metrics, libraries, tasks = get_cached_data()

    ## form UI setting 
    st.header("Model Card Form")

    warning_placeholder = st.empty()

    st.text_input("Model Name", key=persist("model_name"))
    st.text_area("Model Description", help="The model description provides basic details about the model. This includes the architecture, version, if it was introduced in a paper, if an original implementation is available, the author, and general information about the model. Any copyright should be attributed here. General information about training procedures, parameters, and important disclaimers can also be mentioned in this section.", key=persist('model_description'))
    st.multiselect("Language(s)", list(languages_map), format_func=lambda x: languages_map[x], help="The language(s) associated with this model. If this is not a text-based model, you should specify whatever language that is used in the dataset. For instance, if the dataset's labels are in english, you should select English here.", key=persist("languages"))
    st.selectbox("License", [""] + list(license_map.values()), help="The license associated with this model.", key=persist("license"))
    st.selectbox("Library Name", [""] + libraries, help="The name of the library this model came from (Ex. pytorch, timm, spacy, keras, etc.). This is usually automatically detected in model repos, so it is not required.", key=persist('library_name'))
    st.text_input("Parent Model (URL)", help="If this model has another model as its base, please provide the URL link to the parent model", key=persist("Parent_Model_name"))
    st.text_input("Datasets (comma separated)", help="The dataset(s) used to train this model. Use dataset id from https://hf.co/datasets.", key=persist("datasets"))
    st.multiselect("Metrics", available_metrics, help="Metrics used in the training/evaluation of this model. Use metric id from https://hf.co/metrics.", key=persist("metrics"))
    st.selectbox("Task", [""] + tasks, help="What task does this model aim to solve?", key=persist('task'))
    st.text_input("Tags (comma separated)", help="Additional tags to add which will be filterable on https://hf.co/models. (Ex. image-classification, vision, resnet)", key=persist("tags"))
    st.text_input("Author(s) (comma separated)", help="The authors who developed this model. If you trained this model, the author is you.", key=persist("the_authors"))
    st.text_input("Related Research Paper", help="Research paper related to this model.", key=persist("paper_url"))
    st.text_input("Related GitHub Repository", help="Link to a GitHub repository used in the development of this model", key=persist("github_url"))
    st.text_area("Bibtex Citation", help="Bibtex citations for related work", key=persist("bibtex_citations"))
    st.text_input("Carbon Emitted:", help="You can estimate carbon emissions using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700)", key=persist("Model_c02_emitted"))
   
   
    
    # warnings setting
    languages=st.session_state.languages or None
    license=st.session_state.license or None
    task = st.session_state.task or None
    markdown_upload = st.session_state.markdown_upload
    #uploaded_model_card = st.session_state.uploaded_model 
    # Handle any warnings...
    do_warn = False
    warning_msg = "Warning: The following fields are required but have not been filled in: "
    if not languages:
        warning_msg += "\n- Languages"
        do_warn = True
    if not license:
        warning_msg += "\n- License"
        do_warn = True
    if not task or not markdown_upload:
        warning_msg += "\n- Please choose a task or upload a model card"
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
           
            file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type} 
            name_of_uploaded_file = save_uploadedfile(uploaded_file)
           
            st.session_state.markdown_upload = name_of_uploaded_file ## uploaded model card

        elif st.session_state.task =='fill-mask' or 'translation' or 'token-classification' or ' sentence-similarity' or 'summarization' or 'question-answering' or 'text2text-generation' or 'text-classification' or 'text-generation' or 'conversational':
            #st.session_state.markdown_upload = open(
             #   "language_model_template1.md", "r+"
            #).read() 
            st.session_state.markdown_upload = "language_model_template1.md" ## language model template
        
        elif st.session_state.task:
            
            st.session_state.markdown_upload =  "current_card.md" ## default non language model template
       
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
    

       

if __name__ == '__main__':
    load_widget_state()
    main()
