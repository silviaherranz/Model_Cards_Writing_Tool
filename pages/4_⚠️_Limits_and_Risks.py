import streamlit as st
from persist import persist, load_widget_state



global variable_output

def main():
    cs_body()

def cs_body():
    
    st.markdown('# Bias, Risks, and Limitations')
    st.text_area("Use this section to convey both technical and sociotechnical limitations",help="Provide an overview of the possible Limitations and Risks that may be associated with this model", key=persist("Model_Limits_n_Risks"), )
    left, right = st.columns([2,4])
    
    #st.markdown('### Model Description')
    

    with left: 
        st.write("\n")
        st.write("\n")
        st.markdown('### Recommendations:')
        
        
    with right:
        #soutput_jinja = parse_into_jinja_markdown()
        st.text_area("",help="This section is meant to convey recommendations with respect to the bias, risk, and technical limitations. ", key=persist("Recommendations"))
        #st.write("\n")
  
    
    

if __name__ == '__main__':
    load_widget_state()
    main()