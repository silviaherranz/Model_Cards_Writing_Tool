import streamlit as st
from persist import persist, load_widget_state

global variable_output

def main():

    cs_body()

def cs_body():
    
    st.markdown('# Uses')
    st.text_area("This section addresses questions around how the model is intended to be used, discusses the foreseeable users of the model (including those affected by the model), and describes uses that are considered out of scope or misuse of the model.")
    left, right = st.columns([2,4])
    
    #st.markdown('### Model Description')
    

    with left: 
        st.write("\n")
        st.write("\n")
        st.markdown('### Direct Use:')
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        #st.write("\n")
        st.markdown('### Downstream Use [Optional]:')
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown('### Out-of-Scope Use:')
        
    with right:
        st.text_area("",help="How can this model be used, without additional post-processing or further pipeline work?", key=persist("Direct_Use"))
        st.text_area("",help="How can this model be used, when incorporated into another system?",key=persist("Downstream_Use"))
        st.text_area("", help="What tasks will the model not work for?", key=persist("Out-of-Scope_Use"))

   
    

if __name__ == '__main__':
    load_widget_state()
    main()