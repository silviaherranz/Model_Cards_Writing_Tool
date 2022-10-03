import streamlit as st
from persist import persist, load_widget_state
from middleMan import get_card,writingPrompt,apply_view


global variable_output

def main():

    cs_body()

def cs_body():
    # Model Cards
    card = get_card()
    
    st.markdown('# Uses')
    st.text_area("Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model",help="Model uses large work")
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
        st.text_area("",help="This section is for the model use without fine-tuning or plugging into a larger ecosystem/app.", key=persist("Direct_Use"))
        st.text_area("",help="This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/ap",key=persist("Downstream_Use"))
        st.text_area("", help=" This section addresses misuse, malicious use, and uses that the model will not work well for.", key=persist("Out-of-Scope_Use"))

   
    

if __name__ == '__main__':
    load_widget_state()
    main()