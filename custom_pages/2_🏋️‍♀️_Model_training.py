import streamlit as st
import pandas as pd
from persist import persist, load_widget_state
import numpy as np
import matplotlib.pyplot as plt

global variable_output


def main():
    cs_body()


def convert_csv():
    d = {"col1": [], "col2": []}
    df = pd.DataFrame(data=d, columns=["Age", "Sex"])
    return df.to_csv().encode("utf-8")


def cs_body():
    st.header("Training Data and Methodology")
    st.write(
        "Provide an overview of the Training Data and Training Procedure for this model"
    )
    st.markdown("##### Training dataset")
    left, right = st.columns(2)
    left.number_input("Training set size", value=100)
    right.number_input("Validation set size", value=20)
    st.text("Demographical and clinical characteristics")
    left, right = st.columns(2)  # , vertical_alignment ="center")
    left.download_button("Download Template", data=convert_csv(), file_name="file.csv")
    demo = right.file_uploader("Load template", type=["csv"])
    if demo is not None:
        left, right = st.columns(2)  # , vertical_alignment ="center")

        fig, ax = plt.subplots()
        ax.set_title("Age distribution")
        ax.hist(np.random.normal(loc=40, scale=4.0, size=500))
        age = left.pyplot(fig)

        fig, ax = plt.subplots()
        ax.pie([45, 55], labels=["Men", "Women"])
        right.pyplot(fig)
    st.text_input("Source", placeholder="Brats challenge/ Clinic ...")
    st.text("Acquisition date")
    left, right = st.columns(2)
    left.date_input("From")
    right.date_input("To")


if __name__ == "__main__":
    load_widget_state()
    main()
