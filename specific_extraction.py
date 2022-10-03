import re
import streamlit as st
from modelcards import CardData, ModelCard
from markdownTagExtract import tag_checker,listToString,to_markdown
#from specific_extraction import extract_it


# from persist import persist
#global bytes_data


################################################################
#### Markdown parser logic #################################
################################################################

def file_upload():
    bytes_data = st.session_state.markdown_upload
    return bytes_data


# Sets up the basics
model_card_md = file_upload()  # this is where the new model card will be read in from
model_card_md = model_card_md#.decode("utf-8")
# Does metadata appear in any other format than this?
metadata_re = re.compile("^---(.*?)---", re.DOTALL)
header_re = re.compile("^\s*# (.*)", re.MULTILINE)
subheader_re = re.compile("^\s*## (.*)", re.MULTILINE)
subsubheader_re = re.compile("^\s*### (.*)", re.MULTILINE)
subsubsubheader_re = re.compile("^\s*#### (.*)", re.MULTILINE)
# We could be a lot more flexible on this re.
# We require keys to be bold-faced here.
# We don't have to require bold, as long as it's key:value
# **License:**
# Bold terms use ** or __
# Allows the mixing of ** and __ for bold but eh whatev
key_value_re = re.compile("^\s*([*_]{2}[^*_]+[*_]{2})([^\n]*)", re.MULTILINE)
# Hyphens or stars mark list items.
# Unordered list
list_item_re = re.compile("^\s*[-*+]\s+.*", re.MULTILINE)
# This is the ordered list
enum_re = re.compile("^\s*[0-9].*", re.MULTILINE)
table_re = re.compile("^\s*\|.*", re.MULTILINE)
text_item_re = re.compile("^\s*[A-Za-z(](.*)", re.MULTILINE)
# text_item_re = re.compile("^\s*#\s*.*", re.MULTILINE)
# Allows the mixing of -* and *- for italics but eh whatev
italicized_text_item_re = re.compile(
    "^[_*][^_*\s].*\n?.*[^_*][_*]$", flags=re.MULTILINE
)
tag_re = re.compile("^\s*<.*", re.MULTILINE)
image_re = re.compile("!\[.*\]\(.*\)", re.MULTILINE)


subheader_re_dict = {}
subheader_re_dict[header_re] = subheader_re
subheader_re_dict[subheader_re] = subsubheader_re
subheader_re_dict[subsubheader_re] = subsubsubheader_re


def get_metadata(section_text):
    return list(metadata_re.finditer(section_text))


def find_images(section_text):
    return list(image_re.finditer(section_text))


def find_tags(section_text):
    return list(tag_re.finditer(section_text))


def find_tables(section_text):
    return list(table_re.finditer(section_text))


def find_enums(section_text):
    return list(enum_re.finditer(section_text))


# Extracts the stuff from the .md file
def find_key_values(section_text):
    return list(key_value_re.finditer(section_text))


def find_lists(section_text):
    # Find lists: Those lines starting with either '-' or '*'
    return list(list_item_re.finditer(section_text))


def find_texts(section_text):
    # Find texts: Free writing within a section
    basic_text = list(text_item_re.finditer(section_text))
    ital_text = list(italicized_text_item_re.finditer(section_text))
    free_text = basic_text + ital_text
    return free_text


def find_headers(full_text):
    headers = list(header_re.finditer(full_text))
    subheaders = list(subheader_re.finditer(full_text))
    subsubheaders = list(subsubheader_re.finditer(full_text))
    subsubsubheaders = list(subsubsubheader_re.finditer(full_text))
    return (headers, subheaders, subsubheaders, subsubsubheaders)


metadata_list = get_metadata(model_card_md)
if metadata_list != []:
    metadata_end = metadata_list[-1].span()[-1]
    print("Metadata extracted")
    # Metadata processing can happen here.
    # For now I'm just ignoring it.
    model_card_md = model_card_md[metadata_end:]
else:
    print("No metadata found")

# Matches of all header types
headers_list = find_headers(model_card_md)
print("Headers extracted")
# This type of header (one #)
headers = headers_list[0]
## This type of header (two ##)
subheaders = headers_list[1]
### This type of header
subsubheaders = headers_list[2]
#### This type of header
subsubsubheaders = headers_list[3]

# Matches of bulleted lists
lists_list = find_lists(model_card_md)
print("Bulleted lists extracted")

enums_list = find_enums(model_card_md)
print("Enumerated lists extracted")

key_value_list = find_key_values(model_card_md)
print("Key values extracted")

tables_list = find_tables(model_card_md)
print("Tables extracted")

tags_list = find_tags(model_card_md)
print("Markup tags extracted")

images_list = find_images(model_card_md)
print("Images extracted")

# Matches of free text within a section
texts_list = find_texts(model_card_md)
print("Free text extracted")


# List items have the attribute: value;
# This provides for special handling of those strings,
# allowing us to check if it's a list item in order to split/print ok.
LIST_ITEM = "List item"
KEY_VALUE = "Key: Value"
FREE_TEXT = "Free text"
ENUM_LIST_ITEM = "Enum item"
TABLE_ITEM = "Table item"
TAG_ITEM = "Markup tag"
IMAGE_ITEM = "Image"


def create_span_dict(match_list, match_type):
    """
    Creates a dictionary made out of all the spans.
    This is useful for knowing which types to fill out with what in the app.
    Also useful for checking if there are spans in the .md file that we've missed.
    """
    span_dict = {}
    for match in match_list:
        if len(match.group().strip()) > 0:
            span_dict[(match.span())] = (match.group(), match_type)
    return span_dict


metadata_span_dict = create_span_dict(metadata_list, "Metadata")
# Makes a little dict for each span type
header_span_dict = create_span_dict(headers, "# Header")
subheader_span_dict = create_span_dict(subheaders, "## Subheader")
subsubheader_span_dict = create_span_dict(subsubheaders, "### Subsubheader")
subsubsubheader_span_dict = create_span_dict(subsubsubheaders, "#### Subsubsubheader")
key_value_span_dict = create_span_dict(key_value_list, KEY_VALUE)
lists_span_dict = create_span_dict(lists_list, LIST_ITEM)
enums_span_dict = create_span_dict(enums_list, ENUM_LIST_ITEM)
tables_span_dict = create_span_dict(tables_list, TABLE_ITEM)
tags_span_dict = create_span_dict(tags_list, TAG_ITEM)
images_span_dict = create_span_dict(images_list, IMAGE_ITEM)
texts_span_dict = create_span_dict(texts_list, FREE_TEXT)

# We don't have to have these organized by type necessarily.
# Doing it here for clarity.
all_spans_dict = {}
all_spans_dict["headers"] = header_span_dict
all_spans_dict["subheaders"] = subheader_span_dict
all_spans_dict["subsubheaders"] = subsubheader_span_dict
all_spans_dict["subsubsubheaders"] = subsubsubheader_span_dict
all_spans_dict[LIST_ITEM] = lists_span_dict
all_spans_dict[KEY_VALUE] = key_value_span_dict
all_spans_dict[TABLE_ITEM] = tables_span_dict
all_spans_dict[ENUM_LIST_ITEM] = enums_span_dict
all_spans_dict[TAG_ITEM] = tags_span_dict
all_spans_dict[IMAGE_ITEM] = images_span_dict
all_spans_dict[FREE_TEXT] = texts_span_dict


def get_sorted_spans(spans_dict):
    merged_spans = {}
    for span_dict in spans_dict.values():
        merged_spans.update(span_dict)
    sorted_spans = sorted(merged_spans)
    return sorted_spans, merged_spans


sorted_spans, merged_spans = get_sorted_spans(all_spans_dict)

# Sanity/Parse check. Have we captured all spans in the .md file?
if sorted_spans[0][0] != 0:
    print("FYI, our spans don't start at the start of the file.")
    print("We did not catch this start:")
    print(model_card_md[: sorted_spans[0][0]])

for idx in range(len(sorted_spans) - 1):
    last_span_end = sorted_spans[idx][1]
    new_span_start = sorted_spans[idx + 1][0]
    if new_span_start > last_span_end + 1:
        start_nonparse = sorted_spans[idx]
        end_nonparse = sorted_spans[idx + 1]
        text = model_card_md[start_nonparse[1] : end_nonparse[0]]
        if text.strip():
            print("Found an unparsed span in the file:")
            print(start_nonparse)
            print(" ---> ")
            print(end_nonparse)
            print(text)

# print(header_span_dict)
def section_map_to_help_text(text_retrieved):

    presit_states = {
        "## Model Details": "Give an overview of your model, the relevant research paper, who trained it, etc.",
        "## How to Get Started with the Model": "Give an overview of how to get started with the model",
        "## Limitations and Biases": "Provide an overview of the possible Limitations and Risks that may be associated with this model",
        "## Uses": "Detail the potential uses, intended use and out-of-scope uses for this model",
        "## Training": "Provide an overview of the Training Data and Training Procedure for this model",
        "## Evaluation Results": "Detail the Evaluation Results for this model",
        "## Environmental Impact": "Provide an estimate for the carbon emissions: Total emissions (in grams of CO2eq) and additional considerations, such as electricity usage, go here.",
        "## Citation Information": "How to best cite the model authors",
        "## Glossary": "If relevant, include terms and calculations in this section that can help readers understand the model or model card.",
        "## More Information": "Any additional information",
        "## Model Card Authors": "This section provides another layer of transparency and accountability. Whose views is this model card representing? How many voices were included in its construction? Etc.",
        "Model Card Contact": "Mediums to use, in order to contact the model creators",
        "##  Technical Specifications": " Additional technical information",
        '## Model Examination': " Examining the model",
    }

    for key in presit_states:
        if key == text_retrieved:
            return presit_states(key)


def section_map_to_persist(text_retrieved):

    presit_states = {
        "Model_details_text": "## Model Details",
        "Model_how_to": "## How to Get Started with the Model",
        "Model_Limits_n_Risks": "## Limitations and Biases",
        "Model_uses": "## Uses",
        "Model_training": "## Training",
        "Model_Eval": "## Evaluation Results",
        "Model_carbon": "## Environmental Impact",
        "Model_cite": "## Citation Information",
        "Glossary": "## Glossary",
        "More_info": "## More Information",
        "Model_card_authors": "## Model Card Authors",
        "Model_card_contact": "## Model Card Contact",
        "Technical_specs": "## Technical specifications",
        "Model_examin": "## Model Examination",
    }

    for key in presit_states:
        if presit_states[key] == text_retrieved:
            return key


def main():
    # st.write('here')
    print(extract_it("Model_details_text"))


def extract_headers():
    headers = {}
    subheaders = {}
    subsubheaders = {}
    subsubsubheaders = {}
    previous = (None, None, None, None)

    for s in sorted_spans:
        if merged_spans[s][1] == "# Header":
            headers[s] = (sorted_spans.index(s), previous[0])
            previous = (sorted_spans.index(s), previous[1], previous[2], previous[3])
        if merged_spans[s][1] == "## Subheader":
            subheaders[s] = (sorted_spans.index(s), previous[1])
            previous = (previous[0], sorted_spans.index(s), previous[2], previous[3])
        if merged_spans[s][1] == "### Subsubheader":
            subsubheaders[s] = (sorted_spans.index(s), previous[2])
            previous = (previous[0], previous[1], sorted_spans.index(s), previous[3])
        if merged_spans[s][1] == "#### Subsubsubheader":
            subsubsubheaders[s] = (sorted_spans.index(s), previous[3])
            previous = (previous[0], previous[1], previous[2], sorted_spans.index(s))

    return headers, subheaders, subsubheaders, subsubsubheaders


def stringify():
    headers, subheaders, subsubheaders, subsubsubheaders = extract_headers()
    headers_strings = {}
    subheaders_strings = {}
    subsubheaders_strings = {}
    subsubsubheaders_strings = {}

    first = None
    for i in headers:
        if headers[i][1] == None:
            continue
        sub_spans = sorted_spans[headers[i][1] : headers[i][0]]
        lines = []
        for x in sub_spans:
            lines.append(merged_spans[x][0])
        try:
            name = lines[0]
        except:
            name = "Model Details"
        lines = "".join(lines)
        # print(merged_spans[i][0] + "-------------------")
        # print(lines)
        headers_strings[
            name.replace("\n# ", "")
            .replace("    ", "")
            .replace("  ", "")
            .replace("\n", "")
            .replace("{{", "")
            .replace("}}", "")
        ] = lines
        first = i

    first = None
    for i in subheaders:
        if subheaders[i][1] == None:
            continue
        sub_spans = sorted_spans[subheaders[i][1] : subheaders[i][0]]
        lines = []
        for x in sub_spans:
            if merged_spans[x][1] == "## Subheader" and first == None:
                break
            elif merged_spans[x][1] == "# Header":
                break
            else:
                lines.append(merged_spans[x][0])
        try:
            name = lines[0]
        except:
            name = "Model Details"
        lines = "".join(lines)
        # print(merged_spans[i][0] + "-------------------")
        # print(lines)
        subheaders_strings[
            name.replace("\n# ", "").replace("    ", "").replace("  ", "")
        ] = lines
        first = i

    first = None
    for i in subsubheaders:
        if subsubheaders[i][1] == None:
            continue
        sub_spans = sorted_spans[subsubheaders[i][1] : subsubheaders[i][0]]
        lines = []
        for x in sub_spans:
            if merged_spans[x][1] == "## Subheader" or (
                merged_spans[x][1] == "### Subsubheader" and first == None
            ):
                break
            else:
                lines.append(merged_spans[x][0])
        lines = "".join(lines)

        subsubheaders_strings[
            merged_spans[i][0].replace("\n", "").replace("### ", "").replace("    ", "")
        ] = lines
        first = i

    for i in subsubsubheaders:
        if subsubsubheaders[i][1] == None:
            continue
        sub_spans = sorted_spans[subsubsubheaders[i][1] : subsubsubheaders[i][0]]
        lines = []
        for x in sub_spans:
            if (
                merged_spans[x][1] == "## Subheader"
                or merged_spans[x][1] == "### Subsubheader"
            ):
                break
            else:
                lines.append(merged_spans[x][0])
        lines = "".join(lines)

        subsubsubheaders_strings[
            merged_spans[i][0].replace("#### ", "").replace("**", "").replace("\n", "")
        ] = lines

    return (
        headers_strings,
        subheaders_strings,
        subsubheaders_strings,
        subsubsubheaders_strings,
    )


def extract_it(text_to_retrieve):
    print("Span\t\tType\t\tText")
    print("-------------------------------------")
    found_subheader = False
    current_subheader = " "
    page_state = " "
    help_text = " "
    #st.write("in cs- body here")

    (
        headers_strings,
        subheaders_strings,
        subsubheaders_strings,
        subsubsubheaders_strings,
    ) = stringify()

    h_keys = list(headers_strings.keys())
    sh_keys = list(subheaders_strings.keys())
    ssh_keys = list(subsubheaders_strings.keys())
    sssh_keys = list(subsubsubheaders_strings.keys())

    needed = [
        "model details",
        "howto",
        "limitations",
        "uses",
        "training",
        "evaluation",
        "environmental",
        "citation",
        "glossary",
        "more information",
        "authors",
        "contact",
    ]  # not sure what keyword should be used for citation, howto, and contact
    # info_strings = {
    #     "details": "## Model Details",
    #     "howto": "## How to Get Started with the Model",
    #     "limitations": "## Limitations and Biases",
    #     "uses": "## Uses",
    #     "training": "## Training",
    #     "evaluation": "## Evaluation Results",
    #     "environmental": "## Environmental Impact",
    #     "citation": "## Citation Information",
    #     "glossary": "## Glossary",
    #     "more information": "## More Information",
    #     "authors": "## Model Card Authors",
    #     "contact": "## Model Card Contact",
    # }
    info_strings = {
        "model details": "",
        "howto": "",
        "limitations": "",
        "uses": "",
        "training": "",
        "evaluation": "",
        "environmental": "",
        "citation": "",
        "glossary": "",
        "more information": "",
        "authors": "",
        "contact": "",
    }

    for x in needed:
        for l in h_keys:
            if x in l.lower():
                info_strings[x] = info_strings[x] + headers_strings[l]
        for i in sh_keys:
            if x in i.lower():
                info_strings[x] = info_strings[x] + subheaders_strings[i]
        for z in ssh_keys:
            try:
                if x in z.lower():
                    info_strings[x] = info_strings[x] + subsubheaders_strings[z]
            except:
                continue
        for y in sssh_keys:
            try:
                if x in y.lower():
                    info_strings[x] = info_strings[x] + subsubsubheaders_strings[y]
            except:
                continue

    extracted_info = {
        "Model_details_text": info_strings["model details"],
        "Model_how_to": info_strings["howto"],
        "Model_Limits_n_Risks": info_strings["limitations"],
        "Model_uses": info_strings["uses"],
        "Model_training": info_strings["training"],
        "Model_Eval": info_strings["evaluation"],
        "Model_carbon": info_strings["environmental"],
        "Model_cite": info_strings["citation"],
        "Glossary": info_strings["glossary"],
        "More_info": info_strings["more information"],
        "Model_card_authors": info_strings["authors"],
        "Model_card_contact": info_strings["contact"],
        "Technical_specs": "## Technical specifications",
        "Model_examin": "## Model Examination",
    }

    #text_to_retrieve = "Model_details_text"

    new_t = extracted_info[text_to_retrieve] + " "

    return(new_t)


if __name__ == "__main__":

    main()
