#  Model Card 

---

## 0. Card Metadata

**Creation date**: YYYY/MM/DD

### Versioning

- **Version number**: 0.00
- **Version changes**: 



---

## 1. Model Basic Information
**Name**: 
**Creation date**: YYYY/MM/DD

### Versioning

- **Version number**: 0.00
- **Version changes**: 


### Model scope

- **Summary**: 

- **Anatomical site**: 

### Clearance 

- **Type**: 

#### Approved by

- **Name(s)**: 
- **Institution(s)**: 
- **Contact email(s)**: 



**Observed limitations**: 


**Type of learning architecture**: 

### Developed by

- **Name**: 
- **Institution(s)**: 
- **Contact email(s)**: 

**Conflict of interest**: 

**Software licence**: 






---


## 2. Technical specifications

### 2.1 Model overview

#### Model pipeline
- **Summary:** None


- **Model inputs:** ['4DCBCT', 'AU']
- **Model outputs:** ['4DCT']
- **Pre-processing:** None
- **Post-processing:** None

---

### 2.2 Learning architecture(s)

#### Learning architecture 1 

- **Total number of trainable parameters:** None
- **Number of inputs:** None
- **Input content:** 
- **Input size:** None

- **Number of outputs:** None
- **Output content:** 
- **Output size:** None

- **Loss function:** None
- **Batch size:** None
- **Regularisation:** None


- **Uncertainty quantification techniques:** None
- **Explainability techniques:** None



---



### 2.3 Hardware & software

_No hardware and software details specified._


---



## 4. Evaluation Data Methodology, Results and Commissioning

### 1 1

**Evaluation date:** None
#### Evaluated by
- **Name(s):** None
- **Institution(s):** None
- **Contact email(s):** None
- **Same as approved person:** No


**Evaluation frame:** None

#### Evaluation dataset 
##### General information
- **Total size:** None
- **Number of patients:** None
- **Source:** None
- **Acquisition period:** None
- **Inclusion / Exclusion criteria:** None
- **URL info:** None

##### Technical specifications
- **4DCBCT** (model_inputs)
    - Patient positioning: VGV
    - Scan acquisition parameters: V
    - Scan reconstruction parameters: HJ
    - Fov: HJ
- **AU** (model_inputs)
    - Image resolution: NA
    - Patient positioning: NANANAN
    - Scanner model: NANNANAN
    - Scan reconstruction parameters: IK
    - Fov: O
- **4DCT** (model_outputs)
    - Image resolution: NA
    - Scanner model: JHKIL
    - Scan acquisition parameters: JKKJ
    - Scan reconstruction parameters: JK
    - Fov: KJ

- **Treatment modality:** 
- **Beam configuration and energy:** 
- **Dose engine:** None
- **Target volumes and prescription:** KJ
- **Number of fractions:** KJ
- **Reference standard:** None
- **Reference standard QA:** None
- **Additional information:** None

##### Patient demographics and clinical characteristics
- **ICD10/11:** None
- **TNM staging:** None
- **Age:** None
- **Sex:** None
- **Target volume (cm³):** None
- **BMI:** None
- **Additional information:** jkn

#### Quantitative evaluation

#### Dose Metrics

| Type | Metric Specifications | On Volume | Sample Data | Mean Data | Figure DM DP Appendix Label |
| ---|---|---|---|---|--- |
| GPR (Gamma Passing Rate) | None | None | None | None |  |


#### Qualitative evaluation
- **Evaluators information:** 

- **Likert scoring**
  - Method: 
  - Results: 

- **Turing test**
  - Method: 
  - Results: 

- **Time saving**
  - Method: 
  - Results: 

- **Other**
  - Method: 
  - Results: 

- **Explainability:** 
- **Citation details:** 




---

### 6. Other considerations

_No other considerations provided._
