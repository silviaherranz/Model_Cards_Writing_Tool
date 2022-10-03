import streamlit as st
from persist import persist, load_widget_state
from middleMan import get_card,writingPrompt,apply_view
#from specific_extraction import extract_it


global variable_output

def main():
    cs_body()
   


def cs_body():

    st.markdown('# Glossary [optional]')
    st.text_area("Include relevant terms and calculations in this section that can help readers understand the model or model card.",height = 200, key=persist("Glossary"))
   
        
        
    
    

if __name__ == '__main__':
    load_widget_state()
    main()