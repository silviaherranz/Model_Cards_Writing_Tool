import streamlit as st
from persist import persist, load_widget_state
from middleMan import get_card,writingPrompt,apply_view
#from specific_extraction import extract_it


global variable_output

def main():
    cs_body()
   


def cs_body():
    
   
    st.markdown('# Technical Specifications [optional]')
    st.write("Provide an overview of any additional technical specifications for this model")
    left, right = st.columns([2,4])
    
    

    with left: 
        st.write("\n")
        st.write("\n")
        st.markdown('### Model Architecture and Objective:')
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown('### Compute Infrastructure:')
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
       
        st.markdown('##### Hardware:')
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown('##### Software:')
        
    with right:
        #soutput_jinja = parse_into_jinja_markdown()
        st.text_area("", key=persist("Model_specs"))
        #st.write("\n")
        st.text_area("",key=persist("compute_infrastructure"))
        st.text_area("", key=persist("Model_hardware"))
        st.text_area("", key=persist("technical_specs_software"))
        
   
    
    

if __name__ == '__main__':
    load_widget_state()
    main()