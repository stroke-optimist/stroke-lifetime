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

# Container scripts:
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

    # ###########################
    # ########## SETUP ##########
    # ###########################

    # Place the user inputs in the sidebar:
    with st.sidebar:
        # Place these container now and add stuff to them later:
        container_patient_detail_inputs = st.container()
        container_model_type_inputs = st.container()
        # Add an empty header for breathing room in the sidebar:
        st.markdown('# ')

    with container_model_type_inputs:
        st.markdown(
            '''
            ## Model type
            Choose between showing results for each mRS band individually
            (mRS), or aggregating results into two categories (Dichotomous).
            '''
            )
        model_input_str = (
            utilities_lifetime.container_inputs.model_type_input())
        # model_input_str is a string, either "mRS" or "Dichotomous".

    with container_patient_detail_inputs:
        st.markdown('## Select the patient details.')
        age, sex_str, sex, mrs_input = (
            utilities_lifetime.container_inputs.patient_detail_inputs(
                model_input_str))
        # sex_str is a string, either "Female" or "Male".
        # sex is an integer,  0 for female and 1 for male.
        # age and mrs_input are both integers.

    # #####################################
    # ######### MAIN CALCULATIONS #########
    # #####################################

    # Get the fixed parameters dictionary.
    # This is found via a function because the parameters used
    # depend on whether we're using the separate-mRS or the dichotomous
    # model.
    fixed_params = get_fixed_params(model_input_str)

    if model_input_str == 'mRS':
        # Create results for all mRS scores [0, 1, ..., 5]:
        mrs_to_run = range(6)
    else:
        # In the dichotomous model we give one set of parameters to
        # mRS < 3 and a second set to mRS >=3. So just run two mRS
        # values to save repeats.
        mrs_to_run = [0, 5]

    # Store results dictionaries in here:
    results_dict_list = []
    for mrs in mrs_to_run:
        # For each mRS score, use the following function to calculate
        # everything useful for displaying in the app. The function
        # returns a dictionary.
        results_dict = calc.main_calculations(
            age,
            sex,
            sex_str,
            mrs,
            fixed_params
            )

        # Store this dictionary in the list of dicts:
        results_dict_list.append(results_dict)

    # Turn all results dictionaries into a single data frame:
    df = pd.DataFrame(results_dict_list)

    # #####################################
    # ######### CHANGE IN OUTCOME #########
    # #####################################

    # Take a column from the dataframe that contains one value for
    # each mRS score from 0 to 5. Turn those six values into a 6x6
    # grid to show the change in the value between mRS scores.

    # ##### QALYs #####
    qalys_table = calc.build_table_qaly_by_change_in_outcome(
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

    # For each topic, run the main() function in the container script.
    # That function pulls out all of the relevant data from "df" and
    # draws all of the tables, plots, "details" and "example" boxes
    # and everything else that is displayed on the app.

    with tabs[0]:
        st.header('Mortality')
        utilities_lifetime.container_mortality.main(
            df,
            mrs_input,
            fixed_params,
            model_input_str
            )

    with tabs[1]:
        st.header('QALYs')
        utilities_lifetime.container_qalys.main(
            df,
            mrs_input,
            fixed_params,
            qalys_table,
            model_input_str
            )

    with tabs[2]:
        st.header('Resources and costs')
        utilities_lifetime.container_resources.main(
            df,
            mrs_input,
            fixed_params,
            table_discounted_cost,
            model_input_str
            )

    with tabs[3]:
        st.header('Cost-effectiveness')
        utilities_lifetime.container_costeffectiveness.main(
            df,
            mrs_input,
            fixed_params,
            table_cost_effectiveness,
            model_input_str
            )

    # ----- The end! -----


if __name__ == '__main__':
    main()
