import streamlit as st


def create_helpicon(
    label: str,
    description: str,
    field_format: str,
    example: str,
    required: bool = False,
) -> None:
    """
    Render an inline help tooltip with a required asterisk.

    :param label: The label for the help icon.
    :type label: str
    :param description: The description to show in the tooltip.
    :type description: str
    :param field_format: The format of the field.
    :type field_format: str
    :param example: An example of the field.
    :type example: str
    :param required: Whether the field is required, defaults to False
    :type required: bool, optional
    """
    required_tag = (
        "<span style='color: black; font-size: 1.2em;'>*</span>" if required else ""
    )

    st.markdown(
        """
        <style>
        .tooltip-inline { display: inline-block; position: relative; margin-left: 6px; cursor: pointer; font-size: 1em; color: #999; }
        .tooltip-inline .tooltiptext { visibility: hidden; width: 320px; background-color: #f9f9f9; color: #333; text-align: left; border-radius: 6px; border: 1px solid #ccc; padding: 10px; position: absolute; top: 125%; left: 0; z-index: 10; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); font-weight: normal; font-size: 0.95em; line-height: 1.4; white-space: normal; word-wrap: break-word; display: inline-block; }
        .tooltip-inline:hover .tooltiptext { visibility: visible; }
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
