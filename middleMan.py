import streamlit as st
from persist import persist, load_widget_state

# from pages.viewCardProgress import get_card
from modelcards import CardData, ModelCard
from markdownTagExtract import tag_checker, listToString, to_markdown

# from specific_extraction import extract_it
from modelcards import CardData, ModelCard
from jinja2 import Environment, FileSystemLoader


def is_float(value):
    try:
        float(value)
        return True
    except:
        return False


## Handles parsing jinja variable templates
def parse_into_jinja_markdown():
    env = Environment(loader=FileSystemLoader("."), autoescape=True)
    temp = env.get_template(st.session_state.markdown_upload)
    # to add:
    # - parent model
    # to fix:
    # citation on form: check box for bibtex or apa: then parse
    return temp.render(
        model_name=st.session_state["model_name"],
        model_version=st.session_state["model_version"],
        icd10=st.session_state["icd10"],
        treatment_modality=st.session_state["treatment_modality"],
        prescription_levels=st.session_state["prescription_levels"],
        additional_information=st.session_state["additional_information"],
        motivation=st.session_state["motivation"],
        model_class=st.session_state["model_class"],
        creation_date=st.session_state["creation_date"],
        architecture=st.session_state["architecture"],
        model_developers=st.session_state["model_developers"],
        funded_by=st.session_state["funded_by"],
        shared_by=st.session_state["shared_by"],
        license=st.session_state["license"],
        finetuned_from=st.session_state["finetuned_from"],
        research_paper=st.session_state["research_paper"],
        git_repo=st.session_state["git_repo"],
        nb_parameters=st.session_state["nb_parameters"],
        input_channels=st.session_state["input_channels"],
        loss_function=st.session_state["loss_function"],
        batch_size=st.session_state["batch_size"],
        patch_dimension=st.session_state["patch_dimension"],
        architecture_filename=st.session_state["architecture_filename"],
        libraries=st.session_state["libraries"],
        hardware=st.session_state["hardware"],
        inference_time=st.session_state["inference_time"],
        get_started_code=st.session_state["get_started_code"],
        training_set_size=st.session_state["training_set_size"],
        validation_set_size=st.session_state["validation_set_size"],
        age_fig_filename=st.session_state["age_fig_filename"],
        sex_fig_filename=st.session_state["sex_fig_filename"],
        dataset_source=st.session_state["dataset_source"],
        acquisition_from=st.session_state["acquisition_from"],
        acquisition_to=st.session_state["acquisition_to"],
        # direct_use = st.session_state["Direct_Use"], downstream_use = st.session_state["Downstream_Use"],out_of_scope_use = st.session_state["Out-of-Scope_Use"],
        # bias_risks_limitations = st.session_state["Model_Limits_n_Risks"], bias_recommendations = st.session_state['Recommendations'],
        # model_examination = st.session_state['Model_examin'],
        # speeds_sizes_times = st.session_state['Speeds_Sizes_Times'],
        # hardware= st.session_state['Model_hardware'], hours_used = st.session_state['hours_used'], cloud_provider = st.session_state['Model_cloud_provider'], cloud_region = st.session_state['Model_cloud_region'], co2_emitted = st.session_state['Model_c02_emitted'],
        # citation_bibtex= st.session_state["APA_citation"], citation_apa = st.session_state['bibtex_citation'],
        # training_data = st.session_state['training_Data'], preprocessing =st.session_state['model_preprocessing'],
        # model_specs = st.session_state['Model_specs'], compute_infrastructure = st.session_state['compute_infrastructure'],software = st.session_state['technical_specs_software'],
        # glossary = st.session_state['Glossary'],
        # more_information = st.session_state['More_info'],
        # model_card_authors = st.session_state['the_authors'],
        # model_card_contact = st.session_state['Model_card_contact'],
        # get_started_code =st.session_state["Model_how_to"],
        # repo_link = st.session_state["github_url"],
        # paper_link = st.session_state["paper_url"],
        # blog_link = st.session_state["blog_url"],
        # testing_data = st.session_state["Testing_Data"],
        # testing_factors = st.session_state["Factors"],
        # results = st.session_state['Model_Results'],
        # testing_metrics = st.session_state["Metrics"]
    )

""" def parse_into_json():
     """