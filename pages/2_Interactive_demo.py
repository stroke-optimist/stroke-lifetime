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

# from utilities_lifetime.inputs import write_text_from_file
# Models for calculating various quantities:
import utilities_lifetime.models
# Container scripts (which will be called after the calculations):
import utilities_lifetime.container_inputs
import utilities_lifetime.container_mortality
import utilities_lifetime.container_qalys
import utilities_lifetime.container_resources
import utilities_lifetime.container_costeffectiveness
# The home of the main calculation functions:
import utilities_lifetime.main_calculations
# Fixed parameters:
from utilities_lifetime.fixed_params import time_max_post_discharge_yr


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
        model_input_str = utilities_lifetime.container_inputs.\
            model_type_input()
        # model_input_str is a string, either "mRS" or "Dichotomous".

    with container_patient_detail_inputs:
        age_input, sex_input_str, sex_input, mRS_input = \
            utilities_lifetime.container_inputs.\
            patient_detail_inputs(model_input_str)
        # sex_input_str is a string, either "Female" or "Male".
        # sex_input is an integer,  0 for female and 1 for male.
        # age_input and mRS_input are both integers.

    # ##################################
    # ########## CALCULATIONS ##########
    # ##################################

    # Shared for all patients.
    # Times for hazard with time calculations:
    # This list contains [0, 1, 2, ..., time_max_post_discharge_yr].
    time_list_yr = np.arange(0, time_max_post_discharge_yr+1, 1)

    # Choose which list of care home percentage rates to use
    # based on the age input.
    average_care_year_per_mRS = utilities_lifetime.models.\
        find_average_care_year_per_mRS(age_input)

    # ################################
    # ######### SEPARATE mRS #########
    # ################################
    # Store results dictionaries in here:
    results_dict_list = []
    for mrs in range(6):
        # ##### Mortality #####
        # Probabilities:
        (
            hazard_list,              # np.array. Cumulative hazard for
            #                         #   each year in the range
            #                         #   1 to max year.
            survival_list,            # np.array. Cumulative survival
            #                         # for each year in the range
            #                         #   1 to max year.
            fhazard_list,             # np.array. Output from
            #                         #   the Gompertz predictor.
            pDeath_list,              # np.array. Prob of death in each year
            #                         #   from 1 to max year (fixed_params.py).
            invalid_inds_for_pDeath,  # np.array. Contains indices of pDeath
            #                         #   where survival is below 0%.
            time_of_zero_survival     # float. Years from discharge to when
            #                         #   survival probability is zero.
        ) \
            = utilities_lifetime.main_calculations.\
            main_probabilities(age_input, sex_input, mrs, time_list_yr)

        # Survival times:
        survival_times = utilities_lifetime.main_calculations.\
            main_survival_times(age_input, sex_input, mrs)
        # survival_times is a list containing
        # [median, lower IQR, upper IQR, life expectancy].
        # Pull out just the median time:
        median_survival_time = survival_times[0]

        # ##### QALYs #####
        qalys, qaly_list, qaly_raw_list = \
            utilities_lifetime.main_calculations.main_qalys(
                median_survival_time, age_input, sex_input, mrs)

        # ##### Resource use #####
        average_care_year = average_care_year_per_mRS[mrs]
        # Resource uses:
        A_E_count = utilities_lifetime.models.\
            find_A_E_Count(age_input, sex_input, mrs,
                           median_survival_time)
        NEL_count = utilities_lifetime.models.\
            find_NEL_Count(age_input, sex_input, mrs,
                           median_survival_time)
        EL_count = utilities_lifetime.models.\
            find_EL_Count(age_input, sex_input, mrs,
                          median_survival_time)
        care_years = utilities_lifetime.models.\
            find_residential_care_average_time(
                average_care_year,
                median_survival_time
                )

        # Discounted resource use:
        (   #                            # cost x discounted number of...
            A_E_discounted_cost,         # ... A&E admissions.
            NEL_discounted_cost,         # ... non-elective bed days.
            EL_discounted_cost,          # ... elective bed days.
            care_years_discounted_cost,  # ... years in care.
            total_discounted_cost,       # sum of these four ^ values.
            # Return the following for printing examples in details sections.
            #   Each list contains one float for each year in the range
            #   from year=1 to year=median_survival_year (rounded up).
            #                            # Non-discounted number of...
            A_E_counts_by_year,          # ... A&E admissions.
            NEL_counts_by_year,          # ... non-elective bed days.
            EL_counts_by_year,           # ... elective bed days.
            care_years_by_year           # ... years in care.
        ) = \
            utilities_lifetime.main_calculations.main_discounted_resource_use(
            age_input, sex_input, mrs, median_survival_time,
            average_care_year)

        # ##### General #####
        # Build a dictionary of variables used in these calculations.
        # This is mostly for the use of the detailed explanations and examples,
        # which is why it's incomplete. Other bits (e.g. from fixed_params)
        # get added to the dictionary in the function itself.
        results_dict = utilities_lifetime.main_calculations.build_variables_dict(
            age_input,
            sex_input,
            mRS_input,
            pDeath_list,
            invalid_inds_for_pDeath,
            hazard_list,
            survival_list,
            fhazard_list,
            survival_times,
            time_of_zero_survival,
            A_E_count,
            NEL_count,
            EL_count,
            care_years,
            qalys,
            qaly_list,
            qaly_raw_list,
            total_discounted_cost,
            A_E_counts_by_year,
            NEL_counts_by_year,
            EL_counts_by_year,
            care_years_by_year,
            A_E_discounted_cost,
            NEL_discounted_cost,
            EL_discounted_cost,
            care_years_discounted_cost,
            )
        # Store this dictionary in the list of dicts:
        results_dict_list.append(results_dict)

        if mrs == mRS_input:
            variables_dict = results_dict

    # #####################################
    # ######### CHANGE IN OUTCOME #########
    # #####################################

    # qalys is a list of six floats, i.e. one QALY value for each mRS.
    qalys_all_mrs = [d['qalys'] for d in results_dict_list]
    # total_discounted_cost is a list of six floats, i.e. one value per mRS.
    total_discounted_cost_all_mrs = [d['total_discounted_cost']
                                     for d in results_dict_list]

    # ##### QALYs #####
    qalys_table = utilities_lifetime.main_calculations.\
        make_table_qaly_by_change_in_outcome(qalys_all_mrs)
    # qalys_table is a 2D np.array, 6 rows by 6 columns, that contains
    # the data for the "Discounted QALYs by change in outcome" table,
    # and invalid cells already contain either '-' or '' depending.

    # ##### Resource use #####
    table_discounted_cost = utilities_lifetime.main_calculations.\
        build_table_discounted_change(total_discounted_cost_all_mrs)
    # table_discounted_cost is a 2D np.array, 6 rows by 6 columns, that
    # contains the data for the "Discounted total costs by change in
    # outcome" table, and invalid cells already contain either '-' or ''.

    # ##### Cost-effectiveness #####
    table_cost_effectiveness = utilities_lifetime.main_calculations.\
        main_cost_effectiveness(qalys_table, table_discounted_cost)
    # table_cost_effectiveness is a 2D np.array, 6 rows by 6 columns, that
    # contains the data for the "Discounted total Net Benefit by change in
    # outcome" table, and invalid cells already contain either '-' or ''.

    # ###########################
    # ######### RESULTS #########
    # ###########################

    # Pick some more bits out of the results dictionaries:
    all_survival_lists = np.array([d['survival_list'] for d in results_dict_list])
    all_hazard_lists = np.array([d['hazard_list'] for d in results_dict_list])
    all_survival_times = np.array([d['survival_meds_IQRs'] for d in results_dict_list])
    A_E_count_list = [d['A_E_count'] for d in results_dict_list]
    NEL_count_list = [d['NEL_count'] for d in results_dict_list]
    EL_count_list = [d['EL_count'] for d in results_dict_list]
    care_years_list = [d['care_years'] for d in results_dict_list]
    A_E_discounted_cost_list = [d['A_E_discounted_cost'] for d in results_dict_list]
    NEL_discounted_cost_list = [d['NEL_discounted_cost'] for d in results_dict_list]
    EL_discounted_cost_list = [d['EL_discounted_cost'] for d in results_dict_list]
    care_years_discounted_cost_list = [d['care_years_discounted_cost'] for d in results_dict_list]
    total_discounted_cost_list = [d['total_discounted_cost'] for d in results_dict_list]

    # Put each section into its own tab.
    tabs = st.tabs(['Mortality', 'QALYs', 'Resources', 'Cost'])

    with tabs[0]:
        st.header('Mortality')
        utilities_lifetime.container_mortality.main(
            time_list_yr,
            all_survival_lists,
            mRS_input,
            all_hazard_lists,
            variables_dict['pDeath_list'],
            variables_dict['invalid_inds_for_pDeath'],
            all_survival_times,
            variables_dict['time_of_zero_survival'],
            variables_dict
            )

    with tabs[1]:
        st.header('QALYs')
        utilities_lifetime.container_qalys.main(
            variables_dict['survival_meds_IQRs'],
            variables_dict['qalys'],
            variables_dict['qaly_list'],
            variables_dict['qaly_raw_list'],
            qalys_table,
            all_survival_times,
            qalys_all_mrs,
            variables_dict
            )

    with tabs[2]:
        st.header('Resources and costs')
        utilities_lifetime.container_resources.main(
            A_E_count_list,
            NEL_count_list,
            EL_count_list,
            care_years_list,
            A_E_discounted_cost_list,
            NEL_discounted_cost_list,
            EL_discounted_cost_list,
            care_years_discounted_cost_list,
            total_discounted_cost_list,
            table_discounted_cost,
            variables_dict
            )

    with tabs[3]:
        st.header('Cost-effectiveness')
        utilities_lifetime.container_costeffectiveness.main(
            table_cost_effectiveness,
            qalys_all_mrs,
            total_discounted_cost_list,
            variables_dict
            )

    # ----- The end! -----


if __name__ == '__main__':
    main()
