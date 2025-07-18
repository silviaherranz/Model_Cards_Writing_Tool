import streamlit as st
import utils
from render import (
    render_field,
    section_divider,
    title_header,
)

model_card_schema = utils.get_model_card_schema()


def technical_specifications_render():
    from side_bar import sidebar_render

    sidebar_render()

    st.markdown("## Technical Specifications"
    "In this section, the user must include...")

    if "learning_architecture_forms" not in st.session_state:
        st.session_state.learning_architecture_forms = {"Learning Architecture 1": {}}

    title_header("1. Model overview", size="1.1rem")
    title_header("Model pipeline", size="1rem", bottom_margin="0.5em")
    # render_schema_section(model_card_schema["technical_specifications"], section_prefix="technical_specifications")
    section = model_card_schema["technical_specifications"]
    render_field(
        "model_pipeline_summary",
        section["model_pipeline_summary"],
        "technical_specifications",
    )
    render_field(
        "model_pipeline_figure",
        section["model_pipeline_figure"],
        "technical_specifications",
    )

    section_divider()
    # Row 1: model_inputs and model_outputs
    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "model_inputs", section["model_inputs"], "technical_specifications"
        )
    with col2:
        render_field(
            "model_outputs", section["model_outputs"], "technical_specifications"
        )

    # Row 2: pre_processing and post_processing with larger boxes
    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "pre-processing", section["pre-processing"], "technical_specifications"
        )
    with col2:
        render_field(
            "post-processing",
            section["post-processing"],
            "technical_specifications",
        )

    # Optional: Render any other leftover fields
    # for key in section:
    #     if key not in ["model_inputs", "model_outputs", "pre_processing", "post_processing"]:
    #         render_field(key, section[key], "technical_specifications")

    section_divider()
    # -- Learning Architecture Header --
    title_header("2. Learning Architecture", size="1rem", bottom_margin="0.5em")
    utils.light_header_italics(
        "If several models are used (e.g. cascade, cycle, tree,...), repeat this section for each of them."
    )
    # Add before the UI block (safe initialization)
    if "selected_learning_arch_to_delete" not in st.session_state:
        st.session_state.selected_learning_arch_to_delete = None
    # -- Cleaner Button Layout --
    with st.container():
        col1, col2, col3 = st.columns([1.8, 2, 1.2])

        with col1:
            st.markdown("<div style='margin-top: 6px;'>", unsafe_allow_html=True)
            st.button("➕ Add Learning Architecture", key="add_learning_arch")
            st.markdown("</div>", unsafe_allow_html=True)

        # with col2:
        #     forms = list(st.session_state.learning_architecture_forms.keys())
        #     delete_index = st.selectbox(
        #         label=".",
        #         options=forms,
        #         key="learning_architecture_delete_select_clean",
        #         label_visibility="hidden"
        #     )
        with col2:
            forms = list(st.session_state.learning_architecture_forms.keys())
            # Slight vertical alignment fix for the dropdown
            st.markdown(
                "<div style='height: 1px; margin-top: -28px;'></div>",
                unsafe_allow_html=True,
            )
            delete_index = st.selectbox(
                label=".",
                options=forms,
                index=0,
                key="learning_architecture_delete_select_clean",
                label_visibility="collapsed",
            )
            # st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div style='margin-top: 6px;'>", unsafe_allow_html=True)
            if st.button("🗑️ Delete", key="delete_learning_arch_clean"):
                if not delete_index:
                    st.warning("Please select a model to delete.")
                else:
                    selected_key = delete_index
                    selected_index = int(
                        selected_key.split()[-1]
                    )  # Extracts the index number

                    # Remove the selected form
                    st.session_state.learning_architecture_forms.pop(selected_key)

                    # Remove all session keys related to that form
                    keys_to_remove = [
                        k
                        for k in list(st.session_state.keys())
                        if k.startswith(f"learning_architecture_{selected_index}_")
                    ]
                    for k in keys_to_remove:
                        del st.session_state[k]

                    # Shift all later forms down by 1 to fill the gap
                    for i in range(selected_index + 1, len(forms) + 1):
                        old_prefix = f"learning_architecture_{i}_"
                        new_prefix = f"learning_architecture_{i - 1}_"
                        for k in list(st.session_state.keys()):
                            if k.startswith(old_prefix):
                                new_key = k.replace(old_prefix, new_prefix)
                                st.session_state[new_key] = st.session_state.pop(k)

                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # -- Add New Architecture on Click --
        if st.session_state.get("add_learning_arch", False):
            n = len(st.session_state.learning_architecture_forms)
            st.session_state.learning_architecture_forms[
                f"Learning Architecture {n + 1}"
            ] = {}
            st.rerun()

    # --- TABS FOR EACH LEARNING ARCHITECTURE ---
    tab_labels = list(st.session_state.learning_architecture_forms.keys())
    if not tab_labels:
        st.warning(
            "At least one learning architecture is required. Please add one."
        )
    else:
        tabs = st.tabs(tab_labels)

        for i, tab in enumerate(tabs):
            with tab:
                section = model_card_schema["learning_architecture"]
                prefix = f"learning_architecture_{i}"

                # Row 1: Parameters and Inputs
                col1, col2 = st.columns([2, 1])
                with col1:
                    render_field(
                        "total_number_trainable_parameters",
                        section["total_number_trainable_parameters"],
                        prefix,
                    )
                with col2:
                    render_field(
                        "number_of_inputs", section["number_of_inputs"], prefix
                    )
                # with col3:
                render_field("input_content", section["input_content"], prefix)

                # Row 2: Additional input details (optional)
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field(
                        "additional_information_input_content",
                        section["additional_information_input_content"],
                        prefix,
                    )
                with col2:
                    render_field("input_format", section["input_format"], prefix)

                render_field("input_size", section["input_size"], prefix)

                # Row 3: Output details
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field(
                        "number_of_outputs", section["number_of_outputs"], prefix
                    )
                with col2:
                    render_field(
                        "output_content", section["output_content"], prefix
                    )
                render_field(
                    "additional_information_output_content",
                    section["additional_information_output_content"],
                    prefix,
                )
                # You can continue rendering other fields similarly, skipping the ones you don't want
                for field in [
                    "output_format",
                    "output_size",
                    "loss_function",
                    "batch_size",
                    "regularisation",
                    "architecture_figure",
                    "uncertainty_quantification_techniques",
                    "explainability_techniques",
                    "additional_information_ts",
                    "citation_details_ts",
                ]:
                    if field in section:
                        render_field(field, section[field], prefix)

    section_divider()
    title_header("3. Hardware & Software", size="1rem")
    # render_schema_section(model_card_schema["hw_and_sw"], section_prefix="hw_and_sw")
    section = model_card_schema["hw_and_sw"]
    # Row 1: Libraries and Dependencies (longer input, full width)
    render_field(
        "libraries_and_dependencies",
        section["libraries_and_dependencies"],
        "hw_and_sw",
    )

    # Row 2: Hardware + Inference time side-by-side
    col1, col2 = st.columns(2)
    with col1:
        render_field(
            "hardware_recommended", section["hardware_recommended"], "hw_and_sw"
        )
    with col2:
        render_field(
            "inference_time_for_recommended_hw",
            section["inference_time_for_recommended_hw"],
            "hw_and_sw",
        )
    col1, col2 = st.columns(2)
    with col1:
        render_field(
            "installation_getting_started",
            section["installation_getting_started"],
            "hw_and_sw",
        )
    with col2:
        render_field(
            "environmental_impact", section["environmental_impact"], "hw_and_sw"
        )
