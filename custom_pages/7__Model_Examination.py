import streamlit as st
from persist import persist, load_widget_state

# from specific_extraction import extract_it

global variable_output


def main():
    cs_body()


def cs_body():
    # col1.header('Model Examination')
    # stateVariable = "Model_examin"
    # help_text = 'Give an overview of your model, the relevant research paper, who trained it, etc.'

    st.markdown("# Model Examination")
    st.text_area(
        "Experimental: Where explainability/interpretability work can go.",
        height=200,
        key=persist("Model_examin"),
    )
    # left, right = st.columns([2,4], gap="small")

    # st.markdown('### Model Description')


if __name__ == "__main__":
    load_widget_state()
    main()
