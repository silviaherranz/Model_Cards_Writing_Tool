import streamlit as st
from persist import persist, load_widget_state


global variable_output

def main():
    cs_body()
   


def cs_body():

    st.markdown('# Glossary [optional]')
    st.text_area("Terms used in the model card that need to be clearly defined in order to be accessible across audiences go here.",height = 200, key=persist("Glossary"))
   
        
        
    
    

if __name__ == '__main__':
    load_widget_state()
    main()