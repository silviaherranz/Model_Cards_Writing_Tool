import streamlit as st
from persist import persist, load_widget_state
from jinja2 import Environment, FileSystemLoader

def parse_into_jinja_markdown():
    env = Environment(loader=FileSystemLoader('.'), autoescape=True)
    temp = env.get_template(st.session_state.markdown_upload)
   
    return (temp.render(model_id = st.session_state["model_name"],
        the_model_description = st.session_state["model_description"],developers=st.session_state["Model_developers"],shared_by = st.session_state["shared_by"],model_license = st.session_state['license'],
            direct_use = st.session_state["Direct_Use"], downstream_use = st.session_state["Downstream_Use"],out_of_scope_use = st.session_state["Out-of-Scope_Use"],
            bias_risks_limitations = st.session_state["Model_Limits_n_Risks"], bias_recommendations = st.session_state['Recommendations'],
            model_examination = st.session_state['Model_examin'],
            hardware= st.session_state['Model_hardware'], hours_used = st.session_state['hours_used'], cloud_provider = st.session_state['Model_cloud_provider'], cloud_region = st.session_state['Model_cloud_region'], co2_emitted = st.session_state['Model_c02_emitted'],
            citation_bibtex= st.session_state["APA_citation"], citation_apa = st.session_state['bibtex_citation'],
            training_data = st.session_state['training_data'], preprocessing =st.session_state['preprocessing'], speeds_sizes_times = st.session_state['Speeds_Sizes_Times'],
            model_specs = st.session_state['Model_specs'], compute_infrastructure = st.session_state['compute_infrastructure'],software = st.session_state['technical_specs_software'],
            glossary = st.session_state['Glossary'], 
            more_information = st.session_state['More_info'], 
            model_card_authors = st.session_state['the_authors'],
            model_card_contact = st.session_state['Model_card_contact'],
            get_started_code =st.session_state["Model_how_to"]
            ))

def main():
    st.write( parse_into_jinja_markdown())

if __name__ == '__main__':
    load_widget_state()
    main()