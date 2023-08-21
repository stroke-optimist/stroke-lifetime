import streamlit as st

from utilities_lifetime.fixed_params import page_setup
from utilities_lifetime.inputs import write_text_from_file

# Set up the tab title and emoji:
page_setup()

st.warning(''.join([
    ':warning: __To do:__ ',
    'The text on this page will be updated on the next release.'
]))

write_text_from_file('pages/text_for_pages/5_Citation.txt',
                     head_lines_to_skip=2)
