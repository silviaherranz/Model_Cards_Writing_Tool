---
language:
  - en
pipeline_tag: image-to-image-translation
license: apache-2.0
---
#  Model Card 0.5

---

## 0. Card Metadata

**Creation date**: 2025/08/06

### Versioning

- **Version number**: 0.5
- **Version changes**: new limitations


**DOI**: 4567894793743589



---

## 1. Model Basic Information
**Name**: Modeloguay123

**Creation date**: 2022/08/03

### Versioning

- **Version number**: 33.77.4567
- **Version changes**: new page added


**DOI**: 115483.hh5.4


### Model scope

- **Summary**: auto-segmentation model

- **Anatomical site**: Thorax

### Clearance 

- **Type**: Approved for medical use

#### Approved by

- **Name(s)**: Ana

- **Institution(s)**: UCLouvain

- **Contact email(s)**: ana@gmail.com



**Intended users**: Radiation oncologists


**Observed limitations**: None


**Type of learning architecture**: Random Forest

### Developed by

- **Name**: Silvia

- **Institution(s)**: uam

- **Contact email(s)**: silvia@uam.es

**Conflict of interest**: NA

**Software licence**: apache-2.0






---


## 2. Technical specifications

### 2.1 Model overview

#### Model pipeline
- **Summary:** CT images are blue


- **Model inputs:** ['CT']

- **Model outputs:** ['RTSTRUCT_Acetabulums', 'CBCT']

- **Pre-processing:** cropping the body

- **Post-processing:** hole-filling

---

### 2.2 Learning architecture(s)

#### Learning architecture 1 

- **Total number of trainable parameters:** 4000000

- **Number of inputs:** 5

- **Input content:** 



- **Input size:** [128]

- **Number of outputs:** 1

- **Output content:** 



- **Output size:** [128, 56]

- **Loss function:** MSE

- **Batch size:** None

- **Regularisation:** None


- **Uncertainty quantification techniques:** Monte Carlo dropout

- **Explainability techniques:** LIME





---



### 2.3 Hardware & software



- **Libraries and dependencies:** Pytorch 3.9








---


## 3. Training Data Methodology and Information

#### Fine tuned form

- **Model name:** NA

- **URL/DOI to model card:** NA

- **Tuning technique:** NA

#### Training Dataset

##### General information

- **Total size:** [80]

- **Number of patients:** 7

- **Source:** Private dataset from ClinicsX

- **Acquisition period:** March 2025-August 2025

- **Inclusion / exclusion criteria:** Males were excluded

- **Type of data augmentation:** Flipping [left - right]

- **Strategy for data augmentation:** random


##### Technical specifications
- **CT** (model_inputs)
  - **Image resolution:** NA
  - **Patient positioning:** NA
  - **Scan(s) manufacturer and model:** NA
  - **Scan acquisition parameters:** NA
  - **Scan reconstruction parameters:** NA
  - **FOV:** NA
- **RTSTRUCT_Acetabulums** (model_outputs)
  - **Image resolution:** [5.9, 7.6, 3.0]
  - **Patient positioning:** Supine
  - **Scan(s) manufacturer and model:** NA
  - **Scan acquisition parameters:** NA
  - **Scan reconstruction parameters:** NA
  - **FOV:** NA
- **CBCT** (model_outputs)
  - **Image resolution:** [5.9, 7.6, 3.0]
  - **Patient positioning:** head to toes
  - **Scan(s) manufacturer and model:** NA
  - **Scan acquisition parameters:** NA
  - **Scan reconstruction parameters:** NA
  - **FOV:** [5.9, 7.6]






- **Reference standard:** NA

- **Reference standard QA:** delineations corrected by 3 doctors


##### Patient demographics and clinical characteristics



- **Age:** [7.5, 6.8]

- **Sex:** 60% F 40% M




**Validation strategy:** Cross-validation

**Validation data partition:** [20%]

 **Weights initialization:** Uniform




**Model choice criteria:** last epoch

**Inference method:** single fold

---



## 4. Evaluation Data Methodology, Results and Commissioning

### 1 Siemens sample evaluation

**Evaluation date:** 2025/08/05
#### Evaluated by
- **Name(s):** Ana
- **Institution(s):** UCLouvain
- **Contact email(s):** ana@gmail.com
- **Same as 'Approved by':** Yes


**Evaluation frame:** retrospective
 **Sanity check:** Model tested on a set of known images
#### Evaluation dataset 
##### General information
- **Total size:** [577, 567]
- **Number of patients:** 7
- **Source:** public dataset from ucm
- **Acquisition period:** March 2023- April 2024
- **Inclusion / Exclusion criteria:** children excluded
- **URL info:** None

##### Technical specifications
- **CT** (model_inputs)
    - **Image resolution:** NA
    - **Patient positioning:** NA
    - **Scanner model:** NA
    - **Scan acquisition parameters:** NA
    - **Scan reconstruction parameters:** NA
    - **Fov:** NA
- **RTSTRUCT_Acetabulums** (model_outputs)
    - **Image resolution:** [5.9, 7.6, 3.0]
    - **Patient positioning:** supine
    - **Scanner model:** NA
    - **Scan acquisition parameters:** NA
    - **Scan reconstruction parameters:** NA
    - **Fov:** NA
- **CBCT** (model_outputs)
    - **Image resolution:** NA
    - **Patient positioning:** NA
    - **Scanner model:** NA
    - **Scan acquisition parameters:** NA
    - **Scan reconstruction parameters:** NA
    - **Fov:** NA

- **Reference standard:** NA
- **Reference standard QA:** NA
 - **Additional information:** NA 
##### Patient demographics and clinical characteristics
- **Age:** [5.9, 7.6]
- **Sex:** 100% F


#### Quantitative evaluation



##### Image Similarity Metrics
**SSIM (Structural Similarity Index)**

| Field | Value |
|---|---|
| Type | SSIM (Structural Similarity Index) |
| On Volume | AirWay_Dist |
| Registration | NONRIGID |
| Sample Data | None |
| Mean Data | [5.9, 7.6, 3.0, 5.3] |
| Figure Appendix Label |  |




##### Dose Metrics
**GPR (Gamma Passing Rate)**

| Field | Value |
|---|---|
| Type | GPR (Gamma Passing Rate) |
| Metric Specifications | None |
| On Volume | Bone_Mastoid |
| Registration | NONE |
| Treatment Modality | External beam radiation therapy (EBRT) - Protons - Scanning beam single-field optimization |
| Dose Engine | Collapsed cone convolution |
| Dose Grid Resolution | [5.9, 7.6, 3.0] |
| TPS Vendor | RayStation |
| Sample Data | None |
| Mean Data | [5.9, 7.6, 3.0, 6.7] |
| Figure Appendix Label |  |




#### Qualitative evaluation
**Evaluators information:** 

**Likert scoring**

- Method: 
- Results: 

**Turing test**

- Method: 
- Results: 

**Time saving**

- Method: 
- Results: 

**Other**

- Method: 
- Results: 

**Explainability:** 

**Citation details:** 




---

## 5. Other considerations

_No other considerations provided._


---

