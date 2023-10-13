"""
Interactive demo for Streamlit.

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

    # Place the user inputs in the sidebar:
    with st.sidebar:
        st.markdown('## Select the patient details.')
        # Place this container now and add stuff to it later:
        container_patient_detail_inputs = st.container()

        st.markdown('## Model type')
        st.markdown(''.join([
            'Choose between showing results for each mRS band individually ',
            '(mRS), or aggregating results into two categories (Dichotomous). '
        ]))
        # Place this container now and add stuff to it later:
        container_model_type_inputs = st.container()

        # Add an empty header for breathing room in the sidebar:
        st.markdown('# ')

    with container_model_type_inputs:
        model_input_str = (
            utilities_lifetime.container_inputs.model_type_input())
        # model_input_str is a string, either "mRS" or "Dichotomous".

    with container_patient_detail_inputs:
        age, sex_str, sex, mRS_input = (
            utilities_lifetime.container_inputs.
            patient_detail_inputs(model_input_str))
        # sex_str is a string, either "Female" or "Male".
        # sex is an integer,  0 for female and 1 for male.
        # age and mRS_input are both integers.


    # #####################################
    # ######### MAIN CALCULATIONS #########
    # #####################################

    # Fixed parameters:
    fixed_params = get_fixed_params(model_input_str)

    # Store results dictionaries in here:
    results_dict_list = []
    for mrs in range(6):
        results_dict = calc.main_calculations(
            age,
            sex,
            mrs,
            model_input_str,
            fixed_params
            )

        # Store this dictionary in the list of dicts:
        results_dict_list.append(results_dict)

        if mrs == mRS_input:
            # Pick out the results and fixed parameters dicts:
            variables_dict = dict(**results_dict, **fixed_params)

    # Turn all results dictionaries into a single data frame:
    df = pd.DataFrame(results_dict_list)

    # #####################################
    # ######### CHANGE IN OUTCOME #########
    # #####################################

    # qalys is a list of six floats, i.e. one QALY value for each mRS.
    # total_discounted_cost is a list of six floats, i.e. one value per mRS.

    # ##### QALYs #####
    qalys_table = calc.make_table_qaly_by_change_in_outcome(
        df['qalys']
        )
    # qalys_table is a 2D np.array, 6 rows by 6 columns, that contains
    # the data for the "Discounted QALYs by change in outcome" table,
    # and invalid cells already contain either '-' or '' depending.

    # ##### Resource use #####
    table_discounted_cost = calc.build_table_discounted_change(
        df['total_discounted_cost']
        )
    # table_discounted_cost is a 2D np.array, 6 rows by 6 columns, that
    # contains the data for the "Discounted total costs by change in
    # outcome" table, and invalid cells already contain either '-' or ''.

    # ##### Cost-effectiveness #####
    table_cost_effectiveness = calc.build_table_cost_effectiveness(
        df['net_benefit']
        )
    # table_cost_effectiveness is a 2D np.array, 6 rows by 6 columns, that
    # contains the data for the "Discounted total Net Benefit by change in
    # outcome" table, and invalid cells already contain either '-' or ''.

    # ###########################
    # ######### RESULTS #########
    # ###########################

    # Put each section into its own tab.
    tabs = st.tabs(['Mortality', 'QALYs', 'Resources', 'Cost'])

    with tabs[0]:
        st.header('Mortality')
        utilities_lifetime.container_mortality.main(
            df.loc[0]['time_list_yr'],
            df['survival_list'],
            mRS_input,
            df['hazard_list'],
            variables_dict['pDeath_list'],
            variables_dict['invalid_inds_for_pDeath'],
            np.array(df['survival_meds_IQRs'].tolist()),
            variables_dict['time_of_zero_survival'],
            variables_dict,
            fixed_params
            )

    with tabs[1]:
        st.header('QALYs')
        utilities_lifetime.container_qalys.main(
            variables_dict['survival_meds_IQRs'],
            variables_dict['qalys'],
            variables_dict['qaly_list'],
            variables_dict['qaly_raw_list'],
            qalys_table,
            np.array(df['survival_meds_IQRs'].tolist()),  # To get 2d array
            df['qalys'],
            variables_dict,
            fixed_params
            )

    with tabs[2]:
        st.header('Resources and costs')
        utilities_lifetime.container_resources.main(
            df['A_E_count'],
            df['NEL_count'],
            df['EL_count'],
            df['care_years'],
            df['A_E_discounted_cost'],
            df['NEL_discounted_cost'],
            df['EL_discounted_cost'],
            df['care_years_discounted_cost'],
            df['total_discounted_cost'],
            table_discounted_cost,
            variables_dict
            )

    with tabs[3]:
        st.header('Cost-effectiveness')
        utilities_lifetime.container_costeffectiveness.main(
            table_cost_effectiveness,
            df['qalys'],
            df['total_discounted_cost'],
            variables_dict
            )

    # ----- The end! -----


if __name__ == '__main__':
    main()
