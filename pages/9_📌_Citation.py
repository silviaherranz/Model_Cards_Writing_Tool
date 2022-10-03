import streamlit as st
from persist import persist, load_widget_state
from pathlib import Path

from middleMan import apply_view,writingPrompt

global variable_output

def main():
    cs_body()

def cs_body():

    st.markdown('# Citation')
    st.write("If there is a paper or blog post introducing the model, the APA and Bibtex information for that should go in this section")
    left, right = st.columns([2,4])
    
    #st.markdown('### Model Description')
    

    with left: 
        st.write("\n")
        st.write("\n")
        st.markdown('### BibTeX:')
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown('### APA:')
        
        
    with right:
        
        st.text_area("", key=persist("bibtex_citation"))
        st.text_area("", key=persist("APA_citation"))
        #st.write("\n")
  
   
   
    
    
    

if __name__ == '__main__':
    load_widget_state()
    main()