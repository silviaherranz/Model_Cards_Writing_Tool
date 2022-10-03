import streamlit as st
from persist import persist, load_widget_state
from middleMan import get_card,writingPrompt,apply_view
#from specific_extraction import extract_it


global variable_output

def main():
    cs_body()
   


def cs_body():
    
    st.markdown('# Model Card Contact')
    st.text_area("Mediums to use, in order to contact the model creators.", key=persist("Model_card_contact"), )

        
   
    
    

if __name__ == '__main__':
    load_widget_state()
    main()