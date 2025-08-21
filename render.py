import os
import streamlit as st
from tg263 import RTSTRUCT_SUBTYPES
import html
import utils
import re
import numpy as np

DEFAULT_SELECT = "< PICK A VALUE >"


def selectbox_with_default(label, values, key=None, help=None):
    all_options = np.insert(np.array(values, object), 0, DEFAULT_SELECT)
    selected = st.selectbox(
        label,
        options=all_options,
        key=key,
        help=help,
        format_func=lambda x: "" if x == DEFAULT_SELECT else x,
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


def render_image_field(key, props, section_prefix):
    full_key = f"{section_prefix}_{key}"
    label = props.get("label") or key or "Field"
    description = props.get("description", "")
    example = props.get("example", "")
    field_type = props.get("type", "")
    required = props.get("required", False)

    create_helpicon(label, description, field_type, example, required)

    if "all_uploaded_paths" not in st.session_state:
        st.session_state.all_uploaded_paths = set()
    if "render_uploads" not in st.session_state:
        # Map: full_key -> {"path": str, "name": str}
        st.session_state.render_uploads = {}

    st.markdown(
        "<i>If too big or not readable, please indicate the figure number and attach it to the appendix",
        unsafe_allow_html=True,
    )

    st.info("To remove a file, please use the **Delete** button below — the cross in the uploader is disabled.")

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
            type=[
                "png","jpg","jpeg","gif","bmp","tiff","webp","svg",
                "dcm","dicom","nii","nifti","pdf","docx","doc",
                "pptx","ppt","txt","xlsx","xls","DICOM",
            ],
            key=f"{full_key}__uploader",  # keep a stable, unique key per field
            label_visibility="collapsed",
        )

        def _delete_previous_for_field():
            prev = st.session_state.render_uploads.get(full_key)
            if prev:
                try:
                    if os.path.exists(prev["path"]):
                        os.remove(prev["path"])
                except Exception:
                    pass
                st.session_state.all_uploaded_paths.discard(prev["path"])
                st.session_state.render_uploads.pop(full_key, None)
                st.session_state.pop(f"{full_key}_image", None)

        # 1) If user uploaded a new file this run, save & overwrite previous.
        if uploaded_image is not None:
            os.makedirs("uploads", exist_ok=True)
            safe_name = uploaded_image.name
            save_path = os.path.join("uploads", f"{full_key}_{safe_name}")

            # replace previous if existed
            _delete_previous_for_field()

            with open(save_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

            st.session_state.all_uploaded_paths.add(save_path)
            st.session_state.render_uploads[full_key] = {
                "path": save_path,
                "name": safe_name,
            }
            st.session_state[f"{full_key}_image"] = uploaded_image

        # 2) If no new upload this run, DO NOT delete anything.
        #    Instead, show what's persisted (if anything).
        existing = st.session_state.render_uploads.get(full_key)

        # Small UI to show current file and allow explicit removal
        if existing:
            st.caption(f"Current file: **{existing['name']}**")
            remove_clicked = st.button(
                "Remove file",
                key=f"{full_key}__remove_btn",
            )
            if remove_clicked:
                _delete_previous_for_field()
                st.rerun()
        else:
            st.caption("No file selected yet.")



def render_field(key, props, section_prefix):
    full_key = f"{section_prefix}_{key}"
    label = props.get("label") or key or "Field"
    description = props.get("description", "")
    example = props.get("example", "")
    field_type = props.get("type", "")
    required = props.get("required", False)
    options = props.get("options", [])
    placeholder = props.get("placeholder", "")

    pattern = props.get("format")
    if pattern:
        value = st.session_state.get(full_key)
        if value is not None and not re.match(pattern, str(value)):
            friendly_msg = props.get("format_description")
            st.error(friendly_msg)

    create_helpicon(label, description, field_type, example, required)

    try:
        safe_label = label.strip() or "Field"
        if key == "type_metrics_other":
            render_type_metrics_other(full_key, label)
            return
        if field_type == "select":
            if not options:
                st.warning(f"Field '{label}' is missing options for select dropdown.")
            else:
                if key in [
                    "input_content",
                    "output_content",
                    "model_inputs",
                    "model_outputs",
                ]:
                    content_list_key = f"{full_key}_list"
                    type_key = f"{full_key}_new_type"
                    subtype_key = f"{full_key}_new_subtype"

                    utils.load_value(content_list_key, default=[])
                    utils.load_value(type_key)
                    utils.load_value(subtype_key)

                    if st.session_state["_" + type_key] == "RTSTRUCT":
                        col1, col2, col3 = st.columns([2, 1, 0.4])
                        with col1:
                            st.selectbox(
                                label=".",
                                options=options,
                                key="_" + type_key,
                                on_change=utils.store_value,
                                args=[type_key],
                                label_visibility="hidden",
                                placeholder="-Select an option-",
                            )
                        with col2:
                            subtype_value = st.selectbox(
                                label=".",
                                options=RTSTRUCT_SUBTYPES + ["Other"],
                                key="_" + subtype_key,
                                on_change=utils.store_value,
                                args=[subtype_key],
                                label_visibility="hidden",
                                placeholder="-Select an option-",
                            )
                            st.info(
                                "If the structure name isn't in the dropdown menu, select **Other** and introduce the name manually."
                            )
                            if subtype_value == "Other":
                                custom_key = f"{subtype_key}_custom"
                                utils.load_value(custom_key, default="")
                                st.text_input(
                                    "Enter custom RTSTRUCT subtype",
                                    value=st.session_state.get(custom_key, ""),
                                    key=custom_key,
                                    placeholder="Introduce custom value",
                                )

                        with col3:
                            st.markdown(
                                "<div style='margin-top: 26px;'>",
                                unsafe_allow_html=True,
                            )
                            if st.button("➕", key=f"{full_key}_add_button"):
                                subtype = st.session_state.get(subtype_key, "")
                                if subtype == "Other":
                                    subtype = st.session_state.get(
                                        f"{subtype_key}_custom", ""
                                    )
                                entry = f"RTSTRUCT_{subtype}"
                                st.session_state[content_list_key].append(entry)
                                st.session_state[full_key] = st.session_state[
                                    content_list_key
                                ]
                            st.markdown("</div>", unsafe_allow_html=True)

                    else:
                        col1, col2, col3 = st.columns([2, 1, 0.5])

                        with col1:
                            st.selectbox(
                                label=".",
                                options=options,
                                key="_" + type_key,
                                on_change=utils.store_value,
                                args=[type_key],
                                label_visibility="hidden",
                                placeholder="-Select an option-",
                            )

                        selected_type = st.session_state.get(type_key)
                        custom_key = f"{full_key}_custom_text"
                        utils.load_value(custom_key, default="")

                        with col2:
                            st.markdown(
                                "<div style='margin-top: 26px;'>",
                                unsafe_allow_html=True,
                            )
                            if selected_type == "OT (Other)":
                                st.text_input(
                                    "Enter custom input",
                                    value=st.session_state.get(custom_key, ""),
                                    key=custom_key,
                                    label_visibility="collapsed",
                                    placeholder="Introduce custom value",
                                )
                                st.markdown("</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("&nbsp;", unsafe_allow_html=True)

                        with col3:
                            st.markdown(
                                "<div style='margin-top: 26px;'>",
                                unsafe_allow_html=True,
                            )
                            add_clicked = st.button("➕", key=f"{full_key}_add_button")
                            st.markdown("</div>", unsafe_allow_html=True)

                        if add_clicked:
                            if selected_type in [None, "", DEFAULT_SELECT]:
                                st.error("Please select an option before adding.")
                            elif selected_type == "OT (Other)":
                                custom_text = st.session_state.get(
                                    custom_key, ""
                                ).strip()
                                if not custom_text:
                                    st.error(
                                        "Please enter a custom name before adding."
                                    )
                                else:
                                    st.session_state[content_list_key].append(
                                        custom_text
                                    )
                                    st.session_state[full_key] = st.session_state[
                                        content_list_key
                                    ]
                            else:
                                entry = utils.strip_brackets(selected_type)
                                st.session_state[content_list_key].append(entry)
                                st.session_state[full_key] = st.session_state[
                                    content_list_key
                                ]

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
                            if st.button("Clear", key=f"{full_key}_clear_all"):
                                st.session_state[content_list_key] = []
                                st.session_state[full_key] = []
                                st.rerun()
                    return
                if key in ["treatment_modality_train", "treatment_modality_eval"]:
                    content_list_key2 = f"{full_key}_modality_list"
                    type_key2 = f"{full_key}_modality_type"

                    utils.load_value(content_list_key2, default=[])
                    utils.load_value(type_key2)

                    col1, col2 = st.columns([4, 0.5])

                    with col1:
                        st.selectbox(
                            label=".",
                            options=options,
                            key="_" + type_key2,
                            on_change=utils.store_value,
                            args=[type_key2],
                            label_visibility="hidden",
                            placeholder="-Select an option-",
                        )

                    add_clicked = False
                    with col2:
                        st.markdown(
                            "<div style='margin-top: 26px;'>", unsafe_allow_html=True
                        )
                        add_clicked = st.button(
                            "➕", key=f"{full_key}_modality_add_button"
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

                    raw_value2 = st.session_state.get(type_key2)
                    if add_clicked:
                        if raw_value2 in [None, "", DEFAULT_SELECT]:
                            st.error("Please select an option before adding.")
                        else:
                            entry = utils.strip_brackets(raw_value2)
                            st.session_state[content_list_key2].append(entry)
                            st.session_state[full_key] = st.session_state[
                                content_list_key2
                            ]

                    entries = st.session_state[content_list_key2]
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
                            if st.button("Clear", key=f"{full_key}_modality_clear_all"):
                                st.session_state[content_list_key2] = []
                                st.session_state[full_key] = []
                                st.rerun()
                    return

                if key in ["type_ism", "type_gm_seg"]:
                    type_key = full_key + "_selected"
                    type_list_key = full_key + "_list"
                    utils.load_value(type_key)
                    utils.load_value(type_list_key, default=[])
                    options = props.get("options", [])

                    col1, col2, col3 = st.columns([3.5, 0.5, 1])
                    with col1:
                        st.selectbox(
                            label=safe_label,
                            options=options,
                            key="_" + type_key,
                            on_change=utils.store_value,
                            args=[type_key],
                            label_visibility="hidden",
                            placeholder="-Select an option-",
                        )
                    add_clicked = False
                    error_msg = None

                    with col2:
                        st.markdown(
                            "<div style='margin-top: 26px;'>", unsafe_allow_html=True
                        )
                        add_clicked = st.button("➕", key=f"{full_key}_add_button")
                        st.markdown("</div>", unsafe_allow_html=True)

                    if add_clicked:
                        value = st.session_state.get(type_key)
                        if not value:
                            error_msg = "Please choose an image similarity metrics before adding."
                        elif value not in st.session_state[type_list_key]:
                            st.session_state[type_list_key].append(value)
                            st.session_state[full_key] = st.session_state[type_list_key]

                    if error_msg:
                        st.markdown(" ")
                        st.error(error_msg)

                    with col3:
                        if st.session_state[type_list_key]:
                            st.markdown(
                                "<div style='margin-top: 26px;'>",
                                unsafe_allow_html=True,
                            )
                            if st.button("Clear", key=f"{full_key}_clear_button"):
                                st.session_state[type_list_key] = []
                                st.session_state[full_key] = []
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

                    return

                if key in ["type_dose_dm", "type_dose_dm_seg", "type_dose_dm_dp"]:
                    static_options = [
                        "GPR (Gamma Passing Rate)",
                        "MAE (Mean Absolute Error)",
                        "MSE (Mean Squared Error)",
                        "Other",
                    ]
                    parametric_options = ["D", "V"]

                    dm_key = full_key
                    dm_list_key = f"{dm_key}_list"
                    dm_select_key = f"{dm_key}_selected"
                    dm_dynamic_key = f"{dm_key}_dyn"

                    utils.load_value(dm_list_key, default=[])
                    utils.load_value(dm_select_key)
                    utils.load_value(
                        dm_dynamic_key, default={"prefix": "D", "value": 95}
                    )

                    col1, col2, col3, col4 = st.columns([2, 2, 0.5, 1])
                    with col1:
                        st.selectbox(
                            "Select dose metric",
                            options=static_options + parametric_options,
                            key="_" + dm_select_key,
                            on_change=utils.store_value,
                            args=[dm_select_key],
                            label_visibility="hidden",
                            placeholder="-Select an option-",
                        )
                        dm_type = st.session_state[dm_select_key]

                    with col2:
                        val = None
                        if dm_type in parametric_options:
                            val_key = f"{dm_dynamic_key}_{dm_type}_value"
                            if val_key not in st.session_state:
                                st.session_state[val_key] = st.session_state[
                                    dm_dynamic_key
                                ]["value"]
                            st.markdown(
                                "<div style='margin-top: 26px;'>",
                                unsafe_allow_html=True,
                            )
                            val = st.number_input(
                                f"{dm_type} value",
                                min_value=1,
                                max_value=100,
                                value=st.session_state[val_key],
                                key=val_key,
                                label_visibility="collapsed",
                                placeholder=f"Enter {dm_type} value",
                            )
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.session_state[dm_dynamic_key] = {
                                "prefix": dm_type,
                                "value": val,
                            }

                        elif dm_type == "Other":
                            st.markdown(
                                "<div style='margin-top: 26px;'>",
                                unsafe_allow_html=True,
                            )
                            val = st.text_input(
                                label="Other dose metric",
                                label_visibility="collapsed",
                                placeholder="Enter custom name",
                                key=f"{dm_key}_other_text",
                            )
                            st.markdown("</div>", unsafe_allow_html=True)

                    add_clicked = False
                    error_msg = None

                    with col3:
                        st.markdown(
                            "<div style='margin-top: 26px;'>", unsafe_allow_html=True
                        )
                        add_clicked = st.button("➕", key=f"{dm_key}_add_button")
                        st.markdown("</div>", unsafe_allow_html=True)

                    if add_clicked:
                        metric = None
                        if not dm_type:
                            error_msg = (
                                "Please choose a dose metric type before adding."
                            )
                        elif dm_type in static_options and dm_type != "Other":
                            metric = dm_type
                        elif dm_type == "Other":
                            metric = val.strip() if val else ""
                            if not metric:
                                error_msg = (
                                    "Please enter a custom name for the dose metric."
                                )
                        elif dm_type in parametric_options:
                            val_struct = st.session_state.get(dm_dynamic_key, {})
                            if not val_struct:
                                error_msg = "Please enter a value for the dose metric."
                            else:
                                metric = f"{dm_type}{val_struct.get('value', '')}"

                        if error_msg:
                            st.markdown(" ")
                            st.error(error_msg)
                        elif metric and metric not in st.session_state[dm_list_key]:
                            st.session_state[dm_list_key].append(metric)
                            st.session_state[dm_key] = st.session_state[dm_list_key]

                    with col4:
                        if st.session_state[dm_list_key]:
                            st.markdown(
                                "<div style='margin-top: 26px;'>",
                                unsafe_allow_html=True,
                            )
                            if st.button("Clear", key=f"{dm_key}_clear_button"):
                                st.session_state[dm_list_key] = []
                                st.session_state[dm_key] = []
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

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
                    placeholder="-Select an option-",
                )

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


def render_type_metrics_other(full_key, label):
    metrics_list_key = f"{full_key}_list"
    metrics_selected_key = f"{full_key}_selected"

    utils.load_value(metrics_list_key, default=[])
    utils.load_value(metrics_selected_key)

    # Warning flag
    show_warning = False

    col1, col2, col3 = st.columns([3, 0.5, 1])
    with col1:
        st.text_input(
            label=".",
            key="_" + metrics_selected_key,
            on_change=utils.store_value,
            args=[metrics_selected_key],
            placeholder="Enter metric name (e.g. MSE)",
            label_visibility="hidden",
        )

    with col2:
        st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
        if st.button("➕", key=f"{full_key}_add_button"):
            value = st.session_state.get(metrics_selected_key, "")
            if value and value.strip():
                value = value.strip()
                if value not in st.session_state[metrics_list_key]:
                    st.session_state[metrics_list_key].append(value)
                    st.session_state[full_key] = st.session_state[metrics_list_key]
                else:
                    show_warning = True  # already exists
            else:
                show_warning = True  # empty input
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
        if st.button("Clear", key=f"{full_key}_clear_button"):
            st.session_state[metrics_list_key] = []
            st.session_state[full_key] = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if show_warning:
        st.warning("Please enter a valid metric name before adding.")


def create_helpicon(label, description, field_format, example, required=False):
    required_tag = (
        "<span style='color: black; font-size: 1.2em;'>*</span>" if required else ""
    )

    st.markdown(
        """
        <style>
        .tooltip-inline {
            display: inline-block;
            position: relative;
            margin-left: 6px;
            cursor: pointer;
            font-size: 1em;
            color: #999;
        }

        .tooltip-inline .tooltiptext {
            visibility: hidden;
            width: 320px;
            background-color: #f9f9f9;
            color: #333;
            text-align: left;
            border-radius: 6px;
            border: 1px solid #ccc;
            padding: 10px;
            position: absolute;
            top: 125%;
            left: 0;
            z-index: 10;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
            font-weight: normal;
            font-size: 0.95em;
            line-height: 1.4;
            white-space: normal;
            word-wrap: break-word;
            display: inline-block;
        }

        .tooltip-inline:hover .tooltiptext {
            visibility: visible;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    tooltip_html = f"""
    <div style='margin-bottom: 0px; font-weight: 500; font-size: 0.98em;'>
        {label} {required_tag}
        <span class="tooltip-inline">ⓘ
            <span class="tooltiptext">
                <strong>Description:</strong> {description}<br><br>
                <strong>Format:</strong> {field_format}<br><br>
                <strong>Example(s):</strong> {example}
            </span>
        </span>
    </div>
    """
    st.markdown(tooltip_html, unsafe_allow_html=True)
