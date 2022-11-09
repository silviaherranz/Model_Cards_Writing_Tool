import streamlit as st
from persist import persist, load_widget_state
#from pages.viewCardProgress import get_card
from modelcards import CardData, ModelCard
from markdownTagExtract import tag_checker,listToString,to_markdown
#from specific_extraction import extract_it
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
    env = Environment(loader=FileSystemLoader('.'), autoescape=True)
    temp = env.get_template(st.session_state.markdown_upload)
    # to add: 
    # - parent model
    # to fix:
        # citation on form: check box for bibtex or apa: then parse 
    return (temp.render(model_id = st.session_state["model_name"],
        language = st.session_state["languages"],
        the_model_description = st.session_state["model_description"],developers=st.session_state["Model_developers"],shared_by = st.session_state["Shared_by"],model_license = st.session_state['license'],
        parent_model_link = st.session_state['Parent_Model_url'],
            direct_use = st.session_state["Direct_Use"], downstream_use = st.session_state["Downstream_Use"],out_of_scope_use = st.session_state["Out-of-Scope_Use"],
            bias_risks_limitations = st.session_state["Model_Limits_n_Risks"], bias_recommendations = st.session_state['Recommendations'],
            model_examination = st.session_state['Model_examin'],
            speeds_sizes_times = st.session_state['Speeds_Sizes_Times'],
            hardware= st.session_state['Model_hardware'], hours_used = st.session_state['hours_used'], cloud_provider = st.session_state['Model_cloud_provider'], cloud_region = st.session_state['Model_cloud_region'], co2_emitted = st.session_state['Model_c02_emitted'],
            citation_bibtex= st.session_state["APA_citation"], citation_apa = st.session_state['bibtex_citation'],
            training_data = st.session_state['training_Data'], preprocessing =st.session_state['model_preprocessing'],
            model_specs = st.session_state['Model_specs'], compute_infrastructure = st.session_state['compute_infrastructure'],software = st.session_state['technical_specs_software'],
            glossary = st.session_state['Glossary'], 
            more_information = st.session_state['More_info'], 
            model_card_authors = st.session_state['the_authors'],
            model_card_contact = st.session_state['Model_card_contact'],
            get_started_code =st.session_state["Model_how_to"],
            repo_link = st.session_state["github_url"],
            paper_link = st.session_state["paper_url"],
            blog_link = st.session_state["blog_url"],
            testing_data = st.session_state["Testing_Data"],
            testing_factors = st.session_state["Factors"],
            results = st.session_state['Model_Results'],
            testing_metrics = st.session_state["Metrics"]
            ))



################################################################
################################################################
################################################################
################## Below CURRENTLY Deprecated ##################
################################################################
################################################################
################################################################



def apply_view(page_state, not_code_pull,text_passed):
    not_important_section = True
    if st.session_state.legal_view == True:
        #user_view = 'legal_view'
        user_view_collapse={'Model_details_text','Model_uses','Model_Eval','Model_carbon','Model_cite', 'Glossary','Model_card_authors'}
        
    elif st.session_state.researcher_view == True:
        #user_view = 'researcher_view'
        user_view_collapse={'Model_details_text','Model_how_to','Model_training','Model_Limits_n_Risks', 'Glossary', 'Model_card_contact', 'Citation'}
        
    else:
        #user_view = 'beginner_technical_view'
        user_view_collapse={'Model_details_text','Model_how_to','Model_Eval','Model_uses', 'Glossary'} # Add Techical Spec
    

    for value in user_view_collapse:
        if value == page_state:
            not_important_section = False
            
    if not_important_section == True: #and st.session_state[user_view]:
        #st.markdown("here")
        text_return = out_text_out(not_code_pull,page_state,text_passed)
        out_text = "<details> <summary> Click to expand </summary>" +text_return + "</details>"
        return (out_text)
        
        #out_text = "<details>" + out_text + "</details>"
    else:
        text_return = out_text_out(not_code_pull,page_state,text_passed)
        out_text = text_return
        return (out_text)

def out_text_out(not_code_pull,page_state,out_text):
    if not_code_pull == True:
        out_text = extract_it(page_state)
        return(out_text)
    else: 
        out_text = out_text
        return(out_text)
        
def writingPrompt(page_state, help_text, out_text):
    #st.session_state.check_box = False 
    #extracted_how_to= tag_checker(markdown,start_tag,end_tag)
    
    
    
    #see_suggestion = column.checkbox("See Writing Prompt")
    
    st.session_state.check_box = True
    variable_output_prompt = st.text_area("Enter some text",height = 500, value =out_text, key=persist(out_text),
    help=help_text)
    st.session_state.page_state = persist(variable_output_prompt)
    #out_text = extract_it(page_state)
        
        
    #else:
        #st.session_state.check_box = True
        ##st.session_state.check_box = False
        #variable_output_prompt = st.text_area("Enter Text",value = ' ',key=persist(page_state),height = 500,help =help_text)
        
    return variable_output_prompt



def extract_section(current_template, start_tag, end_tag):
    current_Card_markdown= current_template

    extracted_how_to= tag_checker(current_Card_markdown,start_tag,end_tag)
    out_text = ' '.join(extracted_how_to)
    return out_text

def main():
    #card.save('current_card.md')
    return 