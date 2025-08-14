## About Model Cards

- This model card aims to **enhance transparency and standardize the reporting of artificial intelligence (AI)-based applications** in the field of **Radiation Therapy**. It is designed for use by professionals in both research and clinical settings to support these objectives. However it includes items useful for current regulatory requirements, **it does not replace or fulfill regulatory requirements such as the EU Medical Device Regulation or equivalent standards**.

- A **“model”** is defined as the whole set of chained operations that compose an AI-based application. This typically includes a main learning architecture (i.e., with trainable parameters) inserted into a pipeline with pre-processing and post-processing steps. Please note that for safety and transparency purposes, providing information about the full pipeline, including the pre-processing and post-processing steps, is equally important as for the learning architecture itself.

- As a consequence to the model definition above, section 4 of the model card (*Evaluation data, methodology, and results / commissioning*) contains information about the evaluation of the full model pipeline (including pre- and post-processing steps) and not only the learning architecture.

- In order to keep the model card as readable and concise as possible, figures and tables, and other supporting material can be referred to in the information fields and are attached in an **Appendix**.

- **How to deal with changes in the model or in the model card?**
  - *Changes in the card*: In case you want to add or edit information in the card itself (e.g., new evaluation on different dataset, new contact person, new observed limitations, etc), please use the “Versioning” fields (in Card Metadata section) to keep track of the changes from one version to another, and properly indicate the version number.
  - *Changes in the model*: We consider that any change in the model will lead to a new model version and thus a new associated model card. Please use the “Versioning” fields (in Model Basic information section) to keep track of the changes from one model version to another, and properly indicate the version number.

- **Contact:** rtmodelcard@googlegroups.com

We see the model card as a tool to be adapted to the needs of our community, which might change according to the evolution and implementation challenges of AI in Radiation Therapy, both in research and clinical environments. If you would like to propose changes or edits in the model card, please contact our group for further discussion. Also, please indicate any (open source) repository where the model card and/or model are available.