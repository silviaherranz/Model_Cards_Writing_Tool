import streamlit as st
from persist import persist, load_widget_state
#from middleMan import get_card,writingPrompt,apply_view
import pandas as pd
import requests

#from specific_extraction import extract_it


global variable_output

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
    #return languages_map, license_map, available_metrics, libraries, tasks
    return license_map


def cs_body():
    license_map= get_cached_data()
    Supervision_learning_method_list = ["Unsupervised","Semi-supervised","Self-supervised","Supervised","Reinforcement Learning"]
    Machine_Learning_Type_list = ["Neural Network","SVM","Decision Trees"]
    Modality_List = ["Computer Vision","Natural Language Processing","Audio","Speech","Multimodal","Tabular"]

    #st.set_page_config(layout="wide") ## not yet supported on the hub
    st.markdown('## Model Details')
    st.markdown('### Model Description')
    st.text_area("Provide a 1-2 sentence summary of what this model is.", help="The model description provides basic details about the model. This includes the architecture, version, if it was introduced in a paper, if an original implementation is available, the author, and general information about the model. Any copyright should be attributed here. General information about training procedures, parameters, and important disclaimers can also be mentioned in this section.", key=persist('model_description'))

    left, right = st.columns([4,6])
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    with st.container():
        with left: 
            st.write("\n")
            st.write("\n")
            st.markdown('### Developed By:')
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.markdown('### Shared By [optional]:')
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.markdown('### License:')
            st.write("\n")
            
            st.markdown('### Model Type:')
            
        with right:
            st.text_input("",help="Developed By work", key=persist("Model_developers"))
            st.write("\n")
            st.text_input("",help="Shared By work",key=persist("shared_by"))
            st.write("\n")
            st.selectbox("",[""] + list(license_map.values()), help="Licenses work", key=persist("license"))
        
    with st.container():
        
        with sub_col1:
            st.multiselect(" Supervision/Learning Method", [""]+ Supervision_learning_method_list, key=persist("Supervision_learning_method"))
        with sub_col2:
            st.multiselect("Machine Learning Type",[""]+Machine_Learning_Type_list, key=persist("Machine_Learning_Type"))
        with sub_col3:
            st.multiselect("Modality",[""]+Modality_List, key=persist("Modality"))
        

def main():
    cs_body()

    


if __name__ == '__main__':
    load_widget_state()
    main()