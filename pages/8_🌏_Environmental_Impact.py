import streamlit as st
from persist import persist, load_widget_state
from pathlib import Path

from middleMan import apply_view,writingPrompt

global variable_output

def main():

    cs_body()


def cs_body():

    stateVariable = 'Model_carbon'
    help_text ='Provide an estimate for the carbon emissions: e.g hardware used, horus spent training, cloud provider '

    st.markdown('# Environmental Impact')
    st.markdown('###### Carbon emissions can be estimated using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700).')
    st.text_area("", help="Provide an estimate for the carbon emissions: e.g hardware used, horus spent training, cloud provider")

    left, right = st.columns([2,4])
    with left: 
        st.write("\n")
        st.write("\n")
        st.markdown('### Hardware Type:')
        st.write("\n")
        st.write("\n")
        #st.write("\n")
        st.markdown('### Hours used:')
        st.write("\n")
        st.write("\n")
        st.markdown('### Cloud Provider:')
        st.write("\n")
        st.write("\n")
        st.markdown('### Compute Region:')
        st.write("\n")
        st.write("\n")
        st.markdown('### Carbon Emitted:')
    with right:
        #soutput_jinja = parse_into_jinja_markdown()
        st.text_input("",key=persist("Model_hardware"))
        #st.write("\n")
        st.text_input("",help="sw",key=persist("hours_used"))
        st.text_input("",key=persist("Model_cloud_provider"))
        st.text_input("",key=persist("Model_cloud_region"))
        st.text_input("",help= 'in grams of CO2eq', key=persist("Model_c02_emitted")) ##to-do: auto calculate 
    
   
    
    

if __name__ == '__main__':
    load_widget_state()
    main()