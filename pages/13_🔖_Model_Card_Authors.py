import streamlit as st
from persist import persist, load_widget_state



global variable_output

def main():
    cs_body()
   


def cs_body():
    # Model Cards
    #card = get_card()
    #card.save('current_editable.md')
    
    st.markdown('# Model Card Authors [optional]')
    st.text_area("This section also provides another layer of transparency and accountability. Whose views is this model card representing? How many voices were included in its construction? Etc.",height = 180, help = "The people who actually constructed the Model Card go here.",key=persist("the_authors"))
    
    
    

if __name__ == '__main__':
    load_widget_state()
    main()