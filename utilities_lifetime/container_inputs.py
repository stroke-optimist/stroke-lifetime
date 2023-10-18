"""
All of the content for the Inputs section.
"""
# Imports
import streamlit as st


def patient_detail_inputs(model_input_str):
    """
    All input widgets for the patient details.

    Inputs:
    -------
    model_input_str - str. The model type. This affects whether the
                      mRS options are displayed as scores 0 to 5 or
                      as the words "dependent"/"independent".

    Returns:
    --------
    age_input     - int. The patient's age in years.
    sex_input_str - str. The word "Male" or "Female". Stored in the
                    main DataFrame output of the main calculations
                    function because it's clearer than the integer
                    value of sex_input.
    sex_input     - int. 1 for Male, 0 for Female. Used in calculations
                    where this value is multiplied by a coefficient.
    mRS_input     - int. mRS score for the patient. If the dichotomous
                    model type is in use, use mRS 0 for "independent"
                    and mRS 5 for "dependent", although mRS 0, 1, 2 use
                    one set of values and mRS 3, 4, 5 use another.
    """
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
    """
    Choose the model type, separate mRS or dichotomous.

    Returns:
    --------
    model_input_str - str. The model type. Used to decide which mRS
                      score input widget to use.
    """
    # Model type:
    model_input_str = st.radio(
        'Model type:',
        ['mRS', 'Dichotomous'],
        horizontal=True
        )

    return model_input_str
