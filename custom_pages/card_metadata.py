"""Card Metadata page for the Model Cards Writing Tool."""

from __future__ import annotations

from typing import Any, TypedDict, cast

import streamlit as st

import utils
from render import FieldProps, render_field

TITLE = "Card Metadata"
SUBTITLE = "with relevant information about the model card itself"
SECTION_PREFIX = "card_metadata"

VERSIONING_HEADER = "Versioning"
VERSIONING_INFO = (
    "Version number of the model card is set to 0.0 by default, change it to "
    "reflect the current version of the model card. You can introduce "
    "manually the number or use the up and down arrows to change it."
)


class CardMetadata(TypedDict, total=False):
    """
    TypedDict for the 'Card Metadata' section.

    :param TypedDict: The base class for TypedDicts
    :type TypedDict: type
    :param total: If True, all fields are required, defaults to False
    :type total: bool, optional
    """

    card_creation_date: FieldProps
    version_number: FieldProps
    version_changes: FieldProps
    doi: FieldProps


def _render_navigation() -> None:
    """Render the navigation buttons."""
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_next = st.columns([9.4, 1])
    with col_next:
        if st.button("Next"):
            from custom_pages.model_basic_information import (  # noqa: PLC0415
                model_basic_information_render,
            )

            st.session_state.runpage = model_basic_information_render
            st.rerun()


def card_metadata_render() -> None:
    """Render the Card Metadata page."""
    from side_bar import sidebar_render  # noqa: PLC0415

    sidebar_render()

    schema_any: dict[str, Any] = utils.get_model_card_schema()
    section = cast("CardMetadata", schema_any.get(SECTION_PREFIX, {}))

    utils.title(TITLE)
    utils.subtitle(SUBTITLE)

    render_field(
        "card_creation_date",
        section["card_creation_date"],
        SECTION_PREFIX,
    )

    utils.section_divider()
    utils.title_header(VERSIONING_HEADER)
    st.info(VERSIONING_INFO)

    col1, col2 = st.columns([1, 3])
    with col1:
        render_field(
            "version_number",
            section["version_number"],
            SECTION_PREFIX,
        )
    with col2:
        render_field(
            "version_changes",
            section["version_changes"],
            SECTION_PREFIX,
        )

    utils.section_divider()
    render_field(
        "doi",
        section["doi"],
        SECTION_PREFIX,
    )
    _render_navigation()
