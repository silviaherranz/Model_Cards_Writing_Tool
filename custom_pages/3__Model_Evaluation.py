import streamlit as st
from persist import persist, load_widget_state

global variable_output


def main():
    cs_body()


def cs_body():
    # stateVariable = 'Model_Eval'
    # help_text ='Detail the Evaluation Results for this model'
    # col1.header('Model Evaluation')
    st.markdown("# Evaluation")
    st.text_area(
        " This section describes the evaluation protocols and provides the results. ",
        help="Detail the Evaluation Results for this model",
    )
    st.markdown("## Testing Data, Factors & Metrics:")
    left, right = st.columns([2, 4])

    # st.markdown('### Model Description')

    with left:
        st.write("\n")
        st.write("\n")
        st.markdown("#### Testing Data:")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        # st.write("\n")
        st.markdown("#### Factors:")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown("#### Metrics:")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown("#### Results:")

    with right:
        # soutput_jinja = parse_into_jinja_markdown()
        st.text_area(
            "",
            help="Ideally this links to a Dataset Card.",
            key=persist("Testing_Data"),
        )
        # st.write("\n")
        st.text_area(
            "",
            help="What are the foreseeable characteristics that will influence how the model behaves? This includes domain and context, as well as population subgroups.",
            key=persist("Factors"),
        )
        st.text_area(
            "",
            help="What metrics will be used for evaluation in light of tradeoffs between different errors?",
            key=persist("Metrics"),
        )
        st.text_area("", key=persist("Model_Results"))


if __name__ == "__main__":
    load_widget_state()
    main()
