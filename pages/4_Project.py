import streamlit as st

from utilities.fixed_params import page_setup
from utilities.inputs import write_text_from_file

# Set up the tab title and emoji:
page_setup()

write_text_from_file('pages/text_for_pages/4_Project.txt',
                     head_lines_to_skip=2)
