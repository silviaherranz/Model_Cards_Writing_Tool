import streamlit as st
from persist import persist, load_widget_state
import json
import requests
#from specific_extraction import extract_it


# global variable_output


def get_cached_data():
    # json.load(open('file_TG263.json'))
    struct_dict = {"Target":["GTV","CTV","PTV"],"Anatomy":["SpinalCord","BrainStem"]}
    

    r = requests.get('https://huggingface.co/api/models-tags-by-type')
    tags_data = r.json()
    libraries = [x['id'] for x in tags_data['library']]
    return struct_dict, libraries

def main():
    cs_body()
   


def cs_body():
    
    struct_dict, libraries = get_cached_data()
    st.header('Technical Specifications')
    st.write("Provide an overview of any additional technical specifications for this model")
    st.markdown('##### Model architecture')
    st.number_input("Total number of trainable parameters [million]",value=5,key=persist("nb_parameters"))
    left, middle, right = st.columns(3)
    nlines = int(left.number_input("Input channels", 0, 20, 1))
    for i in range(nlines):
        type_input = middle.selectbox(f"Input type # {i}", list(struct_dict.keys()))
        right.selectbox("Input",struct_dict[type_input], help="From https://aapm.onlinelibrary.wiley.com/doi/pdf/10.1002/acm2.12701")
    st.text_input("Loss function",placeholder="MSE", key=persist("loss_function"))
    st.number_input("Batch size",value=1,key=persist("batch_size"))
    left, right = st.columns(2)
    nlines = int(left.number_input("Patch dimension", 2, 3, 3))
    # cols = st.columns(ncol)
    for i in range(nlines):
        right.number_input(f"Dim [px] # {i}", key=i,value=128)
    arch_fig = st.file_uploader("Figure of the architecture",type=['png','jpg'])
    if arch_fig is not None:
        st.image(arch_fig)
    
    st.multiselect("Library/Dependencies", libraries, default=[libraries[0]], help="The name of the library this model came from (Ex. pytorch, timm, spacy, keras, etc.). This is usually automatically detected in model repos, so it is not required.", key=persist('libraries'))
    st.text_input("Hardware recommended", placeholder="GPU 20Gb RAM", key=persist("hardware"))
    st.number_input("Inference time for recommended hardware [seconds]",value=10, key=persist("inference_time"))
    st.text_area("Installation / Getting started", placeholder="Installation procedure / code to run inference", key=persist("get_started_code"))


        
   
    
    

if __name__ == '__main__':
    load_widget_state()
    main()