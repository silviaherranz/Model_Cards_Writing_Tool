from ast import parse
import streamlit as st
from persist import load_widget_state
from middleMan import parse_into_jinja_markdown as pj
import os

def main():
    ## call the jinja_parser
    st.write( pj())

  

if __name__ == '__main__':
    load_widget_state()
    main()