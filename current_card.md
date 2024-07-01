---
language: 
  - en
license: openrail
---

# {{ model_id }}

<!--> Provide a quick summary of what the model is/does. <!-->

#  Table of Contents

- [{{ model_id }}](#-model_id-)
- [Table of Contents](#table-of-contents)
- [Model Details](#model-details)
  - [Model Description](#model-description)
- [Uses](#uses)
  - [Direct Use](#direct-use)
  - [Downstream Use [Optional]](#downstream-use-optional)
  - [Out-of-Scope Use](#out-of-scope-use)
- [Bias, Risks, and Limitations](#bias-risks-and-limitations)
  - [Recommendations](#recommendations)
- [Training Details](#training-details)
  - [Training Data](#training-data)
  - [Training Procedure](#training-procedure)
    - [Preprocessing](#preprocessing)
    - [Speeds, Sizes, Times](#speeds-sizes-times)
- [Evaluation](#evaluation)
  - [Testing Data, Factors & Metrics](#testing-data-factors--metrics)
    - [Testing Data](#testing-data)
    - [Factors](#factors)
    - [Metrics](#metrics)
  - [Results](#results)
- [Model Examination](#model-examination)
- [Environmental Impact](#environmental-impact)
- [Technical Specifications [optional]](#technical-specifications-optional)
  - [Model Architecture and Objective](#model-architecture-and-objective)
  - [Compute Infrastructure](#compute-infrastructure)
    - [Hardware](#hardware)
    - [Software](#software)
- [Citation](#citation)
- [Glossary [optional]](#glossary-optional)
- [More Information [optional]](#more-information-optional)
- [Model Card Authors [optional]](#model-card-authors-optional)
- [Model Card Contact](#model-card-contact)
- [How to Get Started with the Model](#how-to-get-started-with-the-model)


# Model Details

## Model Description

<!--> This section provides basic information about what the model is, its current status, and where it came from.. <!-->
{{ the_model_description | default("More information needed", true)}}

- **Developed by:** {{ developers | default("More information needed", true)}}
- **Shared by [Optional]:** {{ shared_by | default("More information needed", true)}}
- **Model type:** Language model
- **Language(s) (NLP):** {{ language | default("More information needed", true)}}
- **License:** {{ license | default("More information needed", true)}}
- **Related Models:** {{ related_models | default("More information needed", true)}}
    - **Parent Model:** {{ parent_model | default("More information needed", true)}}
- **Resources for more information:** {{ more_resources | default("More information needed", true)}}

# Uses

<!--> Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. <!-->

## Direct Use

<!--> This section is for the model use without fine-tuning or plugging into a larger ecosystem/app. <!-->

{{ direct_use | default("More information needed", true)}}

## Downstream Use [Optional]

<!--> This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app <!-->

{{ downstream_use | default("More information needed", true)}}

## Out-of-Scope Use

<!--> This section addresses misuse, malicious use, and uses that the model will not work well for. <!-->

{{ out_of_scope_use | default("More information needed", true)}}

# Bias, Risks, and Limitations

<!--> This section is meant to convey both technical and sociotechnical limitations. <!-->

{{ bias_risks_limitations | default("More information needed", true)}}

## Recommendations

<!--> This section is meant to convey recommendations with respect to the bias, risk, and technical limitations. <!-->

{{ bias_recommendations | default("Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model. More information needed for further recomendations.", true)}}

# Training Details

## Training Data

<!--> This should link to a Data Card, perhaps with a short stub of information on what the training data is all about as well as documentation related to data pre-processing or additional filtering. <!-->

{{ training_data | default("More information needed", true)}}

## Training Procedure

<!--> This relates heavily to the Technical Specifications. Content here should link to that section when it is relevant to the training procedure. <!-->

### Preprocessing

{{ preprocessing | default("More information needed", true)}}

### Speeds, Sizes, Times

<!--> This section provides information about throughput, start/end time, checkpoint size if relevant, etc. <!-->

{{ speeds_sizes_times | default("More information needed", true)}}
 
# Evaluation

<!--> This section describes the evaluation protocols and provides the results. <!-->

## Testing Data, Factors & Metrics

### Testing Data

<!--> This should link to a Data Card if possible. <!-->

{{ testing_data | default("More information needed", true)}}

### Factors

<!--> These are the things the evaluation is disaggregating by, e.g., subpopulations or domains. <!-->

{{ testing_factors | default("More information needed", true)}}

### Metrics

<!--> These are the evaluation metrics being used, ideally with a description of why. <!-->

{{ testing_metrics | default("More information needed", true)}}

## Results 

{{ results | default("More information needed", true)}}

# Model Examination

{{ model_examination | default("More information needed", true)}}

# Environmental Impact

<!--> Total emissions (in grams of CO2eq) and additional considerations, such as electricity usage, go here. Edit the suggested text below accordingly <!-->

Carbon emissions can be estimated using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700).

- **Hardware Type:** {{ hardware | default("More information needed", true)}}
- **Hours used:** {{ hours_used | default("More information needed", true)}}
- **Cloud Provider:** {{ cloud_provider | default("More information needed", true)}}
- **Compute Region:** {{ cloud_region | default("More information needed", true)}}
- **Carbon Emitted:** {{ co2_emitted | default("More information needed", true)}}

# Technical Specifications [optional]

## Model Architecture and Objective

{{ model_specs | default("More information needed", true)}}

## Compute Infrastructure

{{ compute_infrastructure | default("More information needed", true)}}

### Hardware

{{ hardware | default("More information needed", true)}}

### Software

{{ software | default("More information needed", true)}}

# Citation

<!--> If there is a paper or blog post introducing the model, the APA and Bibtex information for that should go in this section. <!-->

**BibTeX:**

{{ citation_bibtex | default("More information needed", true)}}

**APA:**

{{ citation_apa | default("More information needed", true)}}

# Glossary [optional]

<!--> If relevant, include terms and calculations in this section that can help readers understand the model or model card. <!-->

{{ glossary | default("More information needed", true)}}

# More Information [optional]

{{ more_information | default("More information needed", true)}}

# Model Card Authors [optional]

{{ model_card_authors | default("More information needed", true)}}

# Model Card Contact

{{ model_card_contact | default("More information needed", true)}}

# How to Get Started with the Model

Use the code below to get started with the model.

<details>
<summary> Click to expand </summary>

{{ get_started_code | default("More information needed", true)}}

</details>


