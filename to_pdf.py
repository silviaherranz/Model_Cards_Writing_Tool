def md_to_pdf(md_template: str,
              context: dict,
              output_path: str,
              css: str | None = None,
              base_url: str | None = None) -> None:
    """
    Render a Markdown (Jinja2) template with `context` and export to a styled PDF.
    The default CSS mimics a clean model-card look (like your screenshot).
    """
    from jinja2 import Template
    from markdown import markdown
    from weasyprint import HTML, CSS

    # 1) Fill the Markdown template
    md_filled = Template(md_template).render(**context)

    # 2) Markdown → HTML
    body_html = markdown(
        md_filled,
        extensions=["extra", "tables", "sane_lists"]
    )

    # 3) HTML shell
    html = f"""<!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Document</title>
      </head>
      <body>
        {body_html}
      </body>
    </html>
    """

    # 4) “Model-card” CSS theme (override with `css=` if you want)
    default_css = """
    @page {
        size: A4;
        margin: 18mm 20mm;

        /* Footer with page numbers */
        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10pt;
            color: #6b7280;
        }

        /* Top-left header: document title */
        @top-left {
            content: "Card Metadata";
            font-weight: bold;
            font-size: 11pt;
            color: #111111;
        }

        /* Top-right header: date */
        @top-right {
            content: "{{ today }}";
            font-size: 10.5pt;
            color: #6b7280;
        }
    }


    :root{
      --text:#111111;
      --muted:#6b7280;        /* gray-500 */
      --rule:#1f2937;         /* gray-800 */
      --note-bg:#f3f4f6;      /* gray-100 */
      --note-border:#60a5fa;  /* blue-400 */
    }

    * { box-sizing: border-box; }
    html, body { color: var(--text); }

    body{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      line-height: 1.45;
      font-size: 12.5pt;
    }

    /* Title like in the screenshot */
    h1{
      font-size: 30pt;
      font-weight: 600;
      letter-spacing: -0.02em;
      margin: 0 0 8pt 0;
      padding: 0;
    }
    /* Thin divider under title and between sections */
    h1 + hr,
    hr{
      border: none;
      height: 1px;
      background: var(--rule);
      opacity: 0.65;
      margin: 10pt 0 16pt 0;
    }

    h2{
      font-size: 18pt;
      font-weight: 600;
      margin: 18pt 0 6pt 0;
    }
    h3{
      font-size: 14pt;
      font-weight: 600;
      margin: 14pt 0 6pt 0;
    }

    p, ul, ol{
      margin: 6pt 0 10pt 0;
    }
    ul, ol{ padding-left: 18pt; }

    strong{ font-weight: 650; }
    em{ font-style: italic; color: var(--muted); }

    /* Right-aligned date (use <div class="doc-date">2025-08-14</div> in your MD via raw HTML) */
    .doc-date{
      float: right;
      font-size: 10.5pt;
      color: var(--muted);
      margin-top: 2pt;
      margin-left: 12pt;
    }

    /* Nice callout for Markdown blockquotes */
    blockquote{
      margin: 8pt 0 12pt 0;
      padding: 8pt 12pt;
      background: var(--note-bg);
      border-left: 6px solid var(--note-border);
      color: #374151;
    }

    /* Tables (if you have them) */
    table{
      width: 100%;
      border-collapse: collapse;
      margin: 8pt 0 12pt 0;
      font-size: 12pt;
    }
    th, td{
      border: 1px solid #e5e7eb;
      padding: 6pt 8pt;
      vertical-align: top;
    }
    th{
      font-weight: 600;
      background: #fafafa;
    }

    /* Helper for manual page breaks: <div class="page-break"></div> */
    .page-break{ page-break-before: always; }
    """

    stylesheets = [CSS(string=(css or default_css))]
    HTML(string=html, base_url=base_url).write_pdf(output_path, stylesheets=stylesheets)


md_template = """
<div class="doc-date">{{ today }}</div>
# Card Metadata
with relevant information about the model card itself

**Creation Date** *(required)*  
2025/08/05  

---

## Versioning
> Version number of the model card is set to 0.0 by default, change it to reflect the current version of the model card. You can introduce manually the number or use the up and down arrows to change it.

**Version Number** *(required)*: `0.50`  
**Version Changes** *(required)*: Cambios  

---

**DOI**: hello

# Model Basic Information
with the main information to use the model

**Name** *(required)*: Silvia  
**Creation Date** *(required)*: 2025/08/03  

---

## Versioning
*Note that any change in an existing model is considered as a new version and thus a new model card associated with it should be filled in.*

**Version Number** *(required)*: `22.44.7777`  
**Version Changes** *(required)*: changes  

---

**DOI**: doi iiiii

## Model Scope

**Summary** *(required)*: whcqfgjkjqljhgf  
**Anatomical Site** *(required)*: HN  

---

### Clearance

**Type** *(required)*: tipo  

**Approved by**  
- **Name(s)** *(required)*: luis  
- **Institution(s)** *(required)*: uam  
- **Contact Email(s)** *(required)*: luis@guapo.com  


**Additional Information**: infooo
**Intended Users**: hjhj  
**Observed Limitations *(required)***: ijjj  
**Potential Limitations**: ijjjjjjjjbgu  
**Type of Learning Architecture *(required)***: kkkv


## Developed by

**Name** *(required)*: uijhgyft  
**Institution** *(required)*: uhgc  
**Contact Email(s)** *(required)*: okihju@gmail.co  

---

**Conflict of Interest** *(required)*: jjj  

---

**Software License** *(required)*: j  
**Code Source**: j  
**Model Source**: j  

---

**Citation Details**: j  
**URL info**: jojiuyg

# Technical Specifications
*(i.e. model pipeline, learning architecture, software and hardware)*

## 1. Model Overview

### Model pipeline

**Summary** *(required)*: hola  

**Figure**  
*If too big or not readable, please indicate the figure number and attach it to the appendix*

### Model Inputs *(required)*

CT, 4DCT  


### Model Outputs *(required)*
4DCT  

---
**Input Format**: jk  
**Input Size** *(required)*: [128]  

**Number of outputs** *(required)*: 8  

**Output Content** *(required)*: RTDOSE  

**Additional Information regarding input content**: fghjkl  

**Output Format**: 7  
**Output Size** *(required)*: [4567890]  

**Loss Function** *(required)*: jj  
**Batch Size**: 8  
**Regularisation**: j

**Pre-processing** *(required)*: 6  
**Post-processing** *(required)*: 7

**Architecture Figure** *(required)*  

*If too big or not readable, please indicate the figure number and attach it to the appendix*  

---

**Uncertainty Quantification Techniques** *(required)*: ghjkl  

**Explainability Techniques** *(required)*: hnjmk,l  

**Additional Information**: ghjk  

**Citation Details**: ghjk

## 3. Hardware & Software

**Libraries and Dependencies**: gg  

**Hardware recommended**: vfgbhnj  
**Inference time (s) for recommended hardware**: 4.6  

**Installation / Getting started**: vfgbhnj  
**Environmental Impact**: vgbhn

# Training Data, Methodology, and Information
Containing all information about training and validation data (in case of a fine-tuned model, this section contains information about the tuning dataset)

## Fine tuned from
*These fields are only relevant for fine-tuned models. For tuned models, the training data will contain the tuning data information. Indicate NA if not applicable.*

**Model Name** *(required)*:  
**URL/DOI to Model Card** *(required)*:  
**Tuning Technique** *(required)*:




## 1. General Information
*Note that all fields refer to the raw training data used in 'Model inputs' (i.e. before pre-processing steps).*

**Total size** *(required)*:  
**Number of patients** *(required)*:  

**Source** *(required)*:  
**Inclusion / exclusion criteria** *(required)*:  

**Acquisition period** *(required)*:  

**Type of Data Augmentation** *(required)*:  
**Strategy for Data Augmentation**:  

**URL info**:

## 2. Technical Characteristics
*(i.e. image acquisition protocol, treatment details, ...)*

### CT — Model Inputs
*Must be NA or a list of exactly three decimal numbers in square brackets (e.g. [1.0, 2.5, 3.14]). Integers must include '.0'.*

**Image resolution** *(required)*: NA if Not Applicable  
**Patient positioning** *(required)*: NA if Not Applicable  

**Scan(s) manufacturer and model** *(required)*: NA if Not Applicable  
**Scan(s) acquisition parameters**: NA if Not Applicable  
**Scan(s) reconstruction parameters** *(required)*: NA if Not Applicable  

**Field of View (FOV)**: NA if Not Applicable
**Reference Standard** *(required)*:  

**Reference Standard QA** *(required)*:  

**Additional Information**:

## 3. Patient Demographics and Clinical Characteristics

**ICD10/11**:  
**TNM staging**:  

**Age** *(required)*: [median, range]  
**Sex** *(required)*:  
**BMI**: [median, range]  

**Target volume [cm³]**: e.g. [PTV ~ 245, [130–350]]  

**Additional information**:  

**Validation strategy** *(required)*:  
**Validation data partition** *(required)*:  
**Weights Initialization**:  

**Epochs**:  
**Optimiser**:  
**Learning Rate**:  

**Train and Validation Loss Curves** *(required)*  
*If too big or not readable, please indicate the figure number and attach it to the appendix*  

**Model Choice Criteria** *(required)*:  

**Inference Method** *(required)*:

# Evaluation Data, Methodology, and Results / Commissioning
Containing all info about the evaluation data and procedure. Because it is common to evaluate your model on a different dataset, this section can be repeated as many times as needed.

We refer to evaluation results for models that are evaluated but not necessarily with a clinical implementation in mind, and commissioning for models that are specifically evaluated within a clinical environment with clinic-specific data.

**Evaluation Date** *(required)*: 2025/08/05  

---

## Evaluated by
*Same as 'Approved by'*  
Evaluation team is the same as the approval team. Fields auto-filled.  

---

**Evaluation Frame** *(required)*: hj  

### Evaluation Dataset

### 1. General Information
*Must be one or more lists of integers in square brackets, e.g. [80] or [80, 82, 78], separated by commas if multiple.*  
*Must be a positive integer with up to 100000 digits, or a power of ten (e.g. 10^6, 10 ^ 6, or 10⁶).*

**Total size** *(required)*: j  
**Number of patients** *(required)*: j

**Source** *(required)*: jgy  

**Acquisition period** *(required)*: v  
**Inclusion / exclusion criteria** *(required)*:  

**URL info**: dd

## 2. Technical Characteristics
*(i.e. image acquisition protocol, treatment details, ...)*

### CT — Model Inputs

**Image resolution** *(required)*: NA  
**Patient positioning** *(required)*: NA  

**Scan(s) manufacturer and model** *(required)*: NA  

**Scan(s) acquisition parameters** *(required)*: NA  
**Scan(s) reconstruction parameters** *(required)*: NA  

**Field of View (FOV)**: NA

**Reference Standard** *(required)*: NA  

**Reference Standard QA** *(required)*: NAN  

**Additional Information**: NANA  

---

## 3. Patient Demographics and Clinical Characteristics

**ICD10/11**: NA  
**TNM staging**: NANAN  

**Age** *(required)*: AN  
**Sex** *(required)*:  

**Target volume [cm³]**: AMAN  
**BMI**: N  

**Additional information**: NANAN
## Quantitative Evaluation

### Geometric Metrics

**Type** *(required)*:  

**Surface DSC** / **HD (Hausdorff Distance)**

**Metric Specifications** *(required)*: BHNJ  
**onVolume** *(required)*: A_Carotid_R  

**Sample Data**: GHJK  

**Mean Data** *(required)*: [1.0, 2.5, 3.14, 4.0]  

**Figure**  
*If too big or not readable, please indicate the figure number and attach it to the appendix*

### Dose Metrics

**Type** *(required)*:  

**D96**

**Metric Specifications** *(required)*: GHJ  
**onVolume** *(required)*: A_Carotid_R  

**Treatment modality** *(required)*: External beam radiation therapy (EBRT) - Protons - Scanning beam single-field optimization  

**Dose Engine** *(required)*: Monte Carlo  
**Dose Grid Resolution** *(required)*: [1.0, 2.5, 3.14]  
**TPS Vendor**: HHH  

**Sample Data**: NBG
**Mean Data** *(required)*: [1.0, 2.5, 3.14, 4.0]  

**Figure**  
*If too big or not readable, please indicate the figure number and attach it to the appendix*  

---

### IOV (Inter-Observer Variability)
**Method**:  
**Results**:  


### Uncertainty Metrics
**Method** *(required)*: JJJJ  
**Description** *(required)*: FGHJKL

### Other
**Method**: JJJJ
**Results**: FGHJKL

## Qualitative Evaluation

**Evaluators information** *(required)*: HELLO  

### Likert Scoring

**Method** *(required)*: JHJJ  
**Results** *(required)*: J  

**Explainability**: J  

**Citation Details**: J



# Other Considerations

**Responsible Use and Ethical Considerations**: FVGHJKLÑ  

**Risk Analysis**: LKJHGFGHJKL  

**Post-Market Surveillance / Live Monitoring**: ÑKJHBGV
"""

from datetime import date

context = {
    "today": date.today().isoformat(),
}

md_to_pdf(md_template, context, "model_card.pdf")
