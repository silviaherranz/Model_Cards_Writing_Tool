---
language: 
  - en
---

# {{ model_name }}

<!--> Provide a quick summary of what the model is/does. <!-->

#  Table of Contents

- [{{ model_name }}](#-model_name)
- [Table of Contents](#table-of-contents)
- [1. Model Basic Information](#model-basic-information)
- [2. Technical Specifications](#technical-specifications)
- [3. Training Details](#training-details)
- [4. Model Evaluation](#model-evaluation)
- [5. Model Examination](#model-examination)


# 1. Model Basic Information
<!--> This section provides basic information about what the model is, its current status, and where it came from.. <!-->
- **Version:** {{ version | default("0")}}
## 1.1. Intended use
- **Treatment site ICD10:** {{ icd10 | default("More information needed", true) }}
- **Treatment modality:** {{ treatment_modality | default("More information needed", true) }}
- **Prescription levels [Gy]:** {{ prescription_levels | default("More information needed", true)}}
- **Additional information:** {{ additional_information | default("More information needed", true)}}
- **Motivation for development:** {{ motivation | default("More information needed", true)}}
- **Class:** {{ model_class | default("More information needed", true)}}
- **Creation date:** {{ creation_date | default("More information needed", true)}}
- **Type of architecture** {{ architecture | default("More information needed", true)}}
## 1.2. Development and deployment
- **Developed by:** Name: {{ dev_name | default("More information needed", true)}}, Instutution: {{dev_institution | default("More information needed", true)}}, Email: {{ dev_email | default("More information needed", true)}}
- **Funded by:** {{ funded_by | default("More information needed", true)}}
- **Shared by:** {{ shared_by | default("More information needed", true)}}
- **License:** {{ license | default("More information needed", true)}}
- **Finetuned from model:** {{ finetuned_by | default("More information needed", true)}}
- **Related Research Paper(s):** {{ research_paper | default("More information needed", true)}}
- **Related Git Repository:** {{ git_repo | default("More information needed", true)}}

## 1.3. How to Get Started with the Model

Use the code below to get started with the model.
<details>
<summary> Click to expand </summary>

{{ get_started_code | default("More information needed", true)}}

</details>

# 2. Technical Specifications
## 2.1. Model architecture
- **Total number of parameters:** {{ nb_parameters | default("More information needed", true)}}
- **Input channels:** {{ input_channels | default("More information needed", true)}}
- **Loss function** {{ loss_function | default("More information needed", true)}}
- **Batch size** {{ batch_size | default("More information needed", true)}}
- **Patch dimension** {{ patch_dimension | default("More information needed", true)}}
<img width="100%" src="https://cdn-uploads.huggingface.co/production/uploads/65c9dbefd6cbf9dfed67367e/xGGUE5spRY6tar5R4VeKX.png" alt="error while loading image"> 
_Figure 1: Model architecture_ 

- **Libraries/Dependencies:** {{ libraries | default("More information needed", true)}}
- **Hardware recommended:** {{ hardware | default("More information needed", true)}}
- **Inference time for recommended [seconds]** {{ inference_time | default("More information needed", true)}}

# 3. Training Details
- **Training set size:** {{ training_set_size | default("More information needed", true)}}
- **Validation set size:** {{ validation_set_size | default("More information needed", true)}}

Age distribution | Sex distribution
--- | ---
![](age_distribution.png) | ![](sex_distribution.png)



- **Dataset source:** {{ dataset_source | default("More information needed", true)}}
- **Acquisition date** from {{ acquisition_from | default("More information needed", true)}} to {{ acquisition_to | default("More information needed", true)}} 
# 4. Model Evaluation

# 5. Model Examination
<!--> This section is for the model use without fine-tuning or plugging into a larger ecosystem/app. <!-->


