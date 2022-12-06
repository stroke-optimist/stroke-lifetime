import streamlit as st

from utilities.fixed_params import page_setup
from utilities.inputs import write_text_from_file

# ----- Page setup -----
page_setup()

write_text_from_file('pages/text_for_pages/6_Resources.txt',
                     head_lines_to_skip=2)
