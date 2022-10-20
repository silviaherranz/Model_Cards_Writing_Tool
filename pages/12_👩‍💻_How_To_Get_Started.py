import streamlit as st
from persist import persist, load_widget_state

from extract_code import read_file



global variable_output

def main():

    cs_body()

def cs_body():
    
    library_name = st.session_state.library_name
    model_name = st.session_state.model_name
    model_name_to_str = f"{model_name}"
    library_name_to_str = f"{library_name}"
    text_pass = read_file(library_name_to_str, model_name_to_str) ## get the how to get started code
    
    st.markdown('# How to Get Started with the Model')
    st.session_state['Model_how_to'] = text_pass
    st.text_area("Include relevant terms and calculations in this section that can help readers understand the model or model card.",height = 300, key=persist("Model_how_to"))
   
        

if __name__ == '__main__':
    load_widget_state()
    main()