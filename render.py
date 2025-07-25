import streamlit as st
from tg263 import RTSTRUCT_SUBTYPES
import html
import utils
import numpy as np 
DEFAULT_SELECT = "< PICK A VALUE >"


def selectbox_with_default(label, values, key=None, help=None):
    all_options = np.insert(np.array(values, object), 0, DEFAULT_SELECT)
    selected = st.selectbox(
        label,
        options=all_options,
        key=key,
        help=help,
        format_func=lambda x: "" if x == DEFAULT_SELECT else x
    )
    return selected


def render_schema_section(schema_section, section_prefix="", current_task=None):
    for key, props in schema_section.items():
        if should_render(props, current_task):
            render_field(key, props, section_prefix)


def has_renderable_fields(field_keys, schema_section, current_task):
    return any(
        key in schema_section and should_render(schema_section[key], current_task)
        for key in field_keys
    )


def render_fields(field_keys, schema_section, section_prefix, current_task):
    for key in field_keys:
        if key in schema_section and should_render(schema_section[key], current_task):
            render_field(key, schema_section[key], section_prefix)


def should_render(props, current_task):
    model_types = props.get("model_types")
    if not model_types:
        return True
    if current_task:
        return current_task.strip().lower() in map(str.lower, model_types)
    return False

def render_field(key, props, section_prefix):
    full_key = f"{section_prefix}_{key}"
    label = props.get("label") or key or "Field"
    description = props.get("description", "")
    example = props.get("example", "")
    field_type = props.get("type", "")
    required = props.get("required", False)
    options = props.get("options", [])
    placeholder = props.get("placeholder", "")

    create_helpicon(label, description, field_type, example, required)

    try:
        safe_label = label.strip() or "Field"
        if field_type == "select":
            if not options:
                st.warning(f"Field '{label}' is missing options for select dropdown.")
            else:
                if key in ["input_content", "output_content"]:
                    content_list_key = f"{full_key}_list"
                    type_key = f"{full_key}_new_type"
                    subtype_key = f"{full_key}_new_subtype"

                    # Initialize persistent values
                    utils.load_value(content_list_key, default=[])
                    utils.load_value(type_key)
                    utils.load_value(subtype_key)

                    if st.session_state["_" + type_key] == "RTSTRUCT":
                        col1, col2, col3 = st.columns([2, 2, 0.4])
                        with col1:
                            st.selectbox(
                                label="",
                                options=options,
                                key="_" + type_key,
                                on_change=utils.store_value,
                                args=[type_key],
                                label_visibility="hidden",
                                placeholder="-Select an option-"
                            )
                        with col2:
                            st.selectbox(
                                label="",
                                options=RTSTRUCT_SUBTYPES,
                                key="_" + subtype_key,
                                on_change=utils.store_value,
                                args=[subtype_key],
                                label_visibility="hidden",
                                placeholder="-Select an option-"
                            )
                        with col3:
                            st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
                            if st.button("➕", key=f"{full_key}_add_button"):
                                subtype = st.session_state.get(subtype_key, "")
                                entry = f"RTSTRUCT_{subtype}"
                                st.session_state[content_list_key].append(entry)
                                st.session_state[full_key] = st.session_state[content_list_key]
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        col1, col2 = st.columns([4, 0.5])
                        with col1:
                            st.selectbox(
                                "Select content type",
                                options=options,
                                key="_" + type_key,
                                on_change=utils.store_value,
                                args=[type_key],
                            )
                        with col2:
                            st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
                            if st.button("➕", key=f"{full_key}_add_button"):
                                raw_value = st.session_state.get(type_key, "")
                                entry = utils.strip_brackets(raw_value)
                                st.session_state[content_list_key].append(entry)
                                st.session_state[full_key] = st.session_state[content_list_key]
                            st.markdown("</div>", unsafe_allow_html=True)
                    entries = st.session_state[content_list_key]
                    if entries:
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            tooltip_items = [
                                f"<span title='{html.escape(item)}' style='margin-right: 6px; font-weight: 500; color: #333;'>{html.escape(utils.strip_brackets(item))}</span>"
                                for item in entries
                            ]
                            line = ", ".join(tooltip_items)
                            st.markdown(f"<span>{line}</span>", unsafe_allow_html=True)
                        with col2:
                            if st.button("🧹 Clear", key=f"{full_key}_clear_all"):
                                st.session_state[content_list_key] = []
                                st.session_state[full_key] = []
                                st.rerun()

                    return  # ✅ Prevent fallback selectbox from rendering

                if key == "treatment_modality":
                    content_list_key = f"{full_key}_list"
                    select_key = f"{full_key}_selected"

                    utils.load_value(content_list_key, default=[])
                    utils.load_value(select_key)

                    col1, col2 = st.columns([4, 0.5])
                    with col1:
                        st.selectbox(
                            "Select treatment modality",
                            options=options,
                            key="_" + select_key,
                            on_change=utils.store_value,
                            args=[select_key],
                            placeholder="-Select an option-"
                        )
                    with col2:
                        st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
                        if st.button("➕", key=f"{full_key}_add_button"):
                            entry = st.session_state.get(select_key, "")
                            if entry not in st.session_state[content_list_key]:
                                st.session_state[content_list_key].append(entry)
                                st.session_state[full_key] = st.session_state[content_list_key]
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Show selections
                    entries = st.session_state[content_list_key]
                    if entries:
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            tooltip_items = [
                                f"<span title='{html.escape(item)}' style='margin-right: 6px; font-weight: 500; color: #333;'>{html.escape(item)}</span>"
                                for item in entries
                            ]
                            line = ", ".join(tooltip_items)
                            st.markdown(f"**Selected Modalities:** {line}", unsafe_allow_html=True)
                        with col2:
                            if st.button("🧹 Clear", key=f"{full_key}_clear_all"):
                                st.session_state[content_list_key] = []
                                st.session_state[full_key] = []
                                st.rerun()

                    return  
                utils.load_value(full_key)
                st.selectbox(
                     safe_label,
                     options=options,
                     key="_" + full_key,
                     on_change=utils.store_value,
                     args=[full_key],
                     help=description,
                     label_visibility="hidden",
                     placeholder="-Select an option-"
                )



        elif field_type == "Image":
            st.markdown(
                "<i>If too big or not readable, please indicate the figure number and attach it to the appendix",
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns([1, 2])
            with col1:
                st.text_input(
                    label=".",
                    placeholder="e.g., Fig. 1",
                    key=f"{full_key}_appendix_note",
                    label_visibility="collapsed",
                )
            with col2:
                uploaded_image = st.file_uploader(
                    label=".",
                    type=["png", "jpg", "jpeg"],
                    key=full_key,
                    label_visibility="collapsed",
                )
            if uploaded_image:
                st.session_state[f"{full_key}_image"] = uploaded_image

        else:
            utils.load_value(full_key)
            st.text_input(
                safe_label,
                key="_" + full_key,
                on_change=utils.store_value,
                args=[full_key],
                label_visibility="hidden",
                placeholder=placeholder,
            )

    except Exception as e:
        st.error(f"Error rendering field '{label}': {str(e)}")

def create_helpicon(label, description, field_format, example, required=False):
    required_tag = (
        "<span style='color: black; font-size: 1.2em; cursor: help;' title='Required field'>*</span>"
        if required
        else ""
    )

    st.markdown(
        """
    <style>
    .tooltip-inline {
        display: inline-block;
        position: relative;
        margin-left: 4px;
        cursor: pointer;
        font-size: 0.8em;
        color: #999;
    }
    .tooltip-inline .tooltiptext {
        visibility: hidden;
        width: 260px;
        background-color: #f9f9f9;
        color: #333;
        text-align: left;
        border-radius: 6px;
        border: 1px solid #ccc;
        padding: 10px;
        position: absolute;
        bottom: 150%;
        left: 0;
        z-index: 10;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        font-weight: normal;
        font-size: 0.9em;
        line-height: 1.4;
    }
    .tooltip-inline:hover .tooltiptext {
        visibility: visible;
    }
    <style>
    /* Align number_input and text_input visually */
    div[data-testid="stNumberInput"] {
        margin-top: -6px !important;
    }
    div[data-testid="stTextInput"] {
        margin-top: 0px !important;
    }
    </style>

    </style>
    """,
        unsafe_allow_html=True,
    )
    tooltip_html = f"""
    <div style='margin-bottom: 0px; font-weight: 500; font-size: 0.98em;'>
        {label} {required_tag}
        <span class="tooltip-inline">ⓘ
            <span class="tooltiptext">
                <span style="font-weight: bold;">Description:</span> {description}<br><br>
                <span style="font-weight: bold;">Format:</span> {field_format}<br><br>
                <span style="font-weight: bold;">Example(s):</span> {example}
            </span>
        </span>
    </div>
    """
    st.markdown(tooltip_html, unsafe_allow_html=True)
