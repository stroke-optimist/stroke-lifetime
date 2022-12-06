"""
All of the content for the Inputs section.
"""
# Imports
import streamlit as st


def main_user_inputs():
    st.subheader('Select the patient details.')
    # Age:
    age_input = st.number_input(
        'Age (years):',
        min_value=45,
        max_value=90,
        value=73,
        step=1,
        help='Ranges from 45 to 90.'
        )

    # Sex:
    sex_input_str = st.radio(
        'Sex:',
        ['Male', 'Female'],
        horizontal=True
        )
    # Change 'Male'/'Female' to 1 or 0: 
    sex_input = 1 if sex_input_str == 'Male' else 0

    # mRS:
    mRS_input = st.slider(
        'mRS at discharge:',
        min_value=0,
        max_value=5,
        value=0,      # Default value
        step=1
        )

    return age_input, sex_input_str, sex_input, mRS_input
