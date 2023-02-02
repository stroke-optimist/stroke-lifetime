"""
All of the content for the Inputs section.
"""
# Imports
import streamlit as st
import importlib
import utilities_lifetime.fixed_params

def patient_detail_inputs(model_input_str):
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

    if model_input_str == 'mRS':
        # mRS:
        mRS_input = st.slider(
            'mRS at discharge:',
            min_value=0,
            max_value=5,
            value=0,      # Default value
            step=1
            )
    else:
        dicho_input = st.radio(
            'Outcome at discharge:',
            ['Independent', 'Dependent'],
            horizontal=True
        )
        # The model is expecting an mRS input so select one
        # now based on the dichotomised input:
        mRS_input = 0 if dicho_input == 'Independent' else 5

    return age_input, sex_input_str, sex_input, mRS_input


def model_type_input():
    # Model type:
    model_input_str = st.radio(
        'Model type:',
        ['mRS', 'Dichotomous'],
        horizontal=True
        )
    try:
        model_input_str_before = st.session_state['lifetime_model_type']
    except KeyError:
        model_input_str_before = 'dummy'
    # Add the model type to the streamlit session state so
    # that it can be accessed in the models.py preamble.
    # (AL - this is a bit hacky but saves lots of rewrites and if/else
    # depending on the model type)
    st.session_state['lifetime_model_type'] = model_input_str
    if model_input_str != model_input_str_before:
        importlib.reload(utilities_lifetime.fixed_params)
    return model_input_str
