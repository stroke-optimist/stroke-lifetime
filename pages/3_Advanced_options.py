"""
Interactive demo for Streamlit.

This page copies most of the calculations from the main demo page
and just displays them differently and provides a download option.

This script runs through everything from receiving user inputs
for age, sex, and mRS, to calculating all the quantities we need
for tables and charts of mortality, QALYs, resource use, and
cost effectiveness.

Most of the proper calculation functions are in main_calculations.py,
and most of the calls to write to streamlit are in the scripts
named container_(something).py.
"""
# ----- Imports -----
import streamlit as st
import numpy as np
import pandas as pd

# Add an extra bit to the path if we need to.
# Try importing something as though we're running this from the same
# directory as the landing page.
try:
    from utilities_lifetime.fixed_params import page_setup
except ModuleNotFoundError:
    # If the import fails, add the landing page directory to path.
    # Assume that the script is being run from the directory above
    # the landing page directory, which is called
    # streamlit_lifetime_stroke.
    import sys
    sys.path.append('./streamlit_lifetime_stroke/')
    # The following should work now:
    from utilities_lifetime.fixed_params import page_setup

# Container scripts (which will be called after the calculations):
import utilities_lifetime.container_inputs
import utilities_lifetime.container_mortality
import utilities_lifetime.container_qalys
import utilities_lifetime.container_resources
import utilities_lifetime.container_costeffectiveness
# The home of the main calculation functions:
import utilities_lifetime.main_calculations as calc
# Function to import fixed params for either mRS or dicho model:
from utilities_lifetime.fixed_params import get_fixed_params


def main():
    # ###########################
    # ##### START OF SCRIPT #####
    # ###########################
    # Set up the tab title and emoji:
    page_setup()

    # Page title:
    st.markdown('# Lifetime outcomes')
    # Draw a blue information box:
    st.info(
        ':information_source: ' +  # emoji
        'For acronym reference, see the introduction page.'
        )
    # # Intro text:
    # write_text_from_file('pages/text_for_pages/2_Intro_for_demo.txt',
    #                      head_lines_to_skip=2)

    # ###########################
    # ########## SETUP ##########
    # ###########################

    st.markdown('## Select the patient details.')
    # Place this container now and add stuff to it later:

    st.markdown('## Model type')
    st.markdown(''.join([
        'Choose between showing results for each mRS band individually ',
        '(mRS), or aggregating results into two categories (Dichotomous). '
    ]))

    with st.form('Age range selection'):

        # Values for initialising the select options:
        age_min = 70.0
        age_max = 75.0
        age_step = 1.0

        age_min = st.number_input(
            'Minimum age:',
            min_value=45.0,
            max_value=90.0,
            value=age_min,
            step=0.5,
            help='Ranges from 45 to 90.',
            key='age_min'
            )
        age_max = st.number_input(
            'Maximum age:',
            min_value=45.0,
            max_value=90.0,
            value=75.0,
            step=0.5,
            help='Ranges from 45 to 90.',
            key='age_max'
            )
        age_step = st.number_input(
            'Step:',
            min_value=0.5,
            max_value=45.0,
            value=1.0,
            step=0.5,
            help='Ranges from 0.5 to 45.',
            key='age_step'
            )
        
        model_input_str = (
            utilities_lifetime.container_inputs.model_type_input())
        # model_input_str is a string, either "mRS" or "Dichotomous".
        

        submitted = st.form_submit_button("Submit")
    if submitted:
        age_range = np.arange(age_min, age_max+1e-3, age_step)
        age_info = f'The age ranges from {age_min} to {age_max} in steps of {age_step}. The values are {age_range}.'
        st.markdown(age_info)

        if model_input_str == 'mRS':
            mrs_to_run = range(6)
        else:
            # In the dichotomous model we give one set of parameters to
            # mRS < 3 and a second set to mRS >=3. So just run two mRS
            # values to save repeats.
            mrs_to_run = [0, 5]

        patient_df = pd.DataFrame(columns=[
            'age', 'sex', 'sex_label', 'mrs', 'outcome_type'])
        count = 0
        for age in age_range:
            for sex in [0, 1]:
                sex_label = 'Male' if sex == 1 else 'Female'
                for mrs in mrs_to_run:
                    # Use the mRS score to label this patient as independent or
                    # dependent in the dichotomous model.
                    outcome_type = 'Dependent' if mrs > 2 else 'Independent'

                    patient_df.loc[count] = [
                        age, sex, sex_label, mrs, outcome_type]
                    count += 1


        # #####################################
        # ######### MAIN CALCULATIONS #########
        # #####################################

        # Get the fixed parameters dictionary.
        # This is found via a function because the parameters used
        # depend on whether we're using the separate-mRS or the dichotomous
        # model.
        fixed_params = get_fixed_params(model_input_str)


        # Store results dictionaries in here:
        results_dict_list = []

        for p in range(len(patient_df)):
            patient = patient_df.loc[p]

            age = patient['age']
            sex = patient['sex']
            sex_label = patient['sex_label']
            mrs = patient['mrs']

            # This is the same code as in "2_Interactive_demo.py".

            results_dict = calc.main_calculations(
                age,
                sex,
                sex_label,
                mrs,
                fixed_params
                )

            # Store this dictionary in the list of dicts:
            results_dict_list.append(results_dict)

        # Turn all results dictionaries into a single data frame:
        df = pd.DataFrame(results_dict_list)

        st.write(df)
        st.download_button(
            'Download these results as .csv',
            df.to_csv(),
            file_name='lifetime_outcomes_results.csv'
        )

        df_fixed_params = pd.DataFrame(
            index=fixed_params.keys()
            )
        df_fixed_params['mRS'] = get_fixed_params('mRS').values()
        df_fixed_params['Dichotomous'] = get_fixed_params('Dichotomous').values()
        st.write(df_fixed_params)

        # ----- The end! -----


if __name__ == '__main__':
    main()
