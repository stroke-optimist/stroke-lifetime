"""
Streamlit app for the stroke outcome model.
"""
import streamlit as st

from utilities_lifetime.fixed_params import page_setup
from utilities_lifetime.inputs import write_text_from_file

# Set up the tab title and emoji:
page_setup()

write_text_from_file('pages/text_for_pages/1_Intro.txt',
                     head_lines_to_skip=3)
