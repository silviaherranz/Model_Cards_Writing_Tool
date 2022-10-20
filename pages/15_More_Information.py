import streamlit as st
from persist import persist, load_widget_state


global variable_output

def main():
    cs_body()
   


def cs_body():
   
        
    st.markdown('# More Information [optional]')
    st.text_area("Any additional information",height = 200, key=persist("More_info"))
    
   
    
    

if __name__ == '__main__':
    load_widget_state()
    main()