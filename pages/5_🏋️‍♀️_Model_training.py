import streamlit as st
from persist import persist, load_widget_state

global variable_output

def main():
  
    cs_body()
  

def cs_body():
    
    st.markdown('# Training Details')
    st.write("Provide an overview of the Training Data and Training Procedure for this model")
    left, middle, right = st.columns([2,1,7])

    with left: 
        st.write("\n")
        st.write("\n")
        st.markdown('## Training Data:')
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
    with middle:
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown(' \n ## Training Procedure')
    with left:
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
       
        st.markdown('#### Preprocessing:')
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown('#### Speeds, Sizes, Time:')
        
    with right:
        #soutput_jinja = parse_into_jinja_markdown()
        
        st.text_area("", help ="Ideally this links to a Dataset Card.", key=persist("training_Data"))
        #st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        
        st.text_area("",key=persist("model_preprocessing"))
        st.text_area("", help = "This section provides information about throughput, start/end time, checkpoint size if relevant, etc.", key=persist("Speeds_Sizes_Times"))
   
   
   
   
    

if __name__ == '__main__':
    load_widget_state()
    main()