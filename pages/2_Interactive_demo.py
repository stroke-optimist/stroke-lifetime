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
import utilities_lifetime.models as model
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

    # ##################################
    # ########## CALCULATIONS ##########
    # ##################################

    # Shared for all patients.
    # Fixed parameters:
    fixed_params = get_fixed_params(model_input_str)
    # Times for hazard with time calculations:
    # This list contains [0, 1, 2, ..., time_max_post_discharge_yr].
    time_list_yr = np.arange(
        0, fixed_params['time_max_post_discharge_yr'] + 1, 1)

    # Choose which list of care home percentage rates to use
    # based on the age input.
    average_care_year_per_mRS = model.find_average_care_year_per_mRS(
        age,
        fixed_params['perc_care_home_over70'],
        fixed_params['perc_care_home_not_over70']
        )

    # ################################
    # ######### SEPARATE mRS #########
    # ################################
    # Store results dictionaries in here:
    results_dict_list = []
    for mrs in range(6):
        # ##### Mortality #####

        # Linear predictors:
        lp_yr1 = model.find_lpDeath_yr1(
            age,
            sex,
            mrs,
            fixed_params['lg_mean_ages'],
            fixed_params['lg_coeffs']
            )
        lp_yrn = model.find_lpDeath_yrn(
            age,
            sex,
            mrs,
            fixed_params['gz_mean_age'],
            fixed_params['gz_coeffs']
            )

        # Probability of death in year 1:
        pDeath_yr1 = model.find_pDeath_yr1(lp_yr1)

        # Find hazard and survival:
        # The following arrays contain one value for each year in the
        # range 1 to max year (defined in fixed_params.py).
        # Cumulative hazard, cumulative survival, output from Gompertz.
        hazard_list, survival_list, fhazard_list = (
            calc.find_cumhazard_with_time(
                time_list_yr,
                age,
                sex,
                mrs,
                fixed_params
                ))

        # Find indices where survival is less than 0% and so the
        # calculated probability of death is invalid.
        invalid_inds_for_pDeath = np.where(hazard_list >= 1.0)[0] + 1
        # Add one to the index because we start hazard_list from year 0
        # but pDeath_list from year 1.

        # Calculate pDeath, the probability of death in each year
        # from 1 to max year (fixed_params.py).
        pDeath_list = calc.calculate_prob_death_per_year(
            time_list_yr,
            fixed_params['gz_gamma'],
            pDeath_yr1,
            lp_yrn
            )

        # Find when survival=0% for the survival vs. time chart:
        # Years from discharge to when survival probability is zero.
        time_of_zero_survival = model.find_t_zero_survival(
            fixed_params['gz_gamma'],
            pDeath_yr1,
            lp_yrn,
            prob=1.0
            )

        # Survival times:
        survival_years_iqr = calc.calculate_survival_iqr(
            age,
            fixed_params['gz_gamma'],
            lp_yrn,
            pDeath_yr1
            )
        # survival_years_iqr is a list containing
        # [median, lower IQR, upper IQR, life expectancy].
        # Pull out just the median time:
        median_survival_time = survival_years_iqr[0]

        # ##### QALYs #####
        # Pick out some fixed parameters:

        qalys, qaly_list, qaly_raw_list = model.calculate_qaly(
            fixed_params['utility_list'][mrs],
            median_survival_time,
            age,
            sex,
            fixed_params['lg_mean_ages'][mrs],
            fixed_params['qaly_age_coeff'],
            fixed_params['qaly_age2_coeff'],
            fixed_params['qaly_sex_coeff'],
            dfq=fixed_params['discount_factor_QALYs_perc'] / 100.0
            )

        # ##### Resource use #####
        # Linear predictors:
        A_E_lp = model.find_lp_AE_Count(
            age,
            sex,
            mrs,
            fixed_params['lg_mean_ages'],
            fixed_params['A_E_coeffs'],
            fixed_params['A_E_mRS']
            )
        NEL_lp = model.find_lp_NEL_Count(
            age,
            sex,
            mrs,
            fixed_params['lg_mean_ages'],
            fixed_params['NEL_coeffs'],
            fixed_params['NEL_mRS']
            )
        EL_lp = model.find_lp_EL_Count(
            age,
            sex,
            mrs,
            fixed_params['lg_mean_ages'],
            fixed_params['EL_coeffs'],
            fixed_params['EL_mRS']
            )
        # Fixed parameter for care home usage:
        average_care_year = average_care_year_per_mRS[mrs]

        # Resource use across the median survival time in years:
        A_E_count = model.find_A_E_Count(
            A_E_lp,
            fixed_params['A_E_coeffs'],
            median_survival_time
            )
        NEL_count = model.find_NEL_Count(
            NEL_lp,
            fixed_params['NEL_coeffs'],
            median_survival_time
            )
        EL_count = model.find_EL_Count(
            EL_lp,
            fixed_params['EL_coeffs'],
            median_survival_time
            )
        care_years = model.find_residential_care_average_time(
            average_care_year,
            median_survival_time
            )

        # Calculate the non-discounted values:
        # Each list contains one float for each year in the range
        # from year=1 to year=median_survival_year (rounded up).
        A_E_count_by_year = calc.find_resource_count_for_all_years(
            median_survival_time,
            utilities_lifetime.models.find_A_E_Count,
            coeffs=fixed_params['A_E_coeffs'],
            LP=A_E_lp
            )
        NEL_count_by_year = calc.find_resource_count_for_all_years(
            median_survival_time,
            utilities_lifetime.models.find_NEL_Count,
            coeffs=fixed_params['NEL_coeffs'],
            LP=NEL_lp
            )
        EL_count_by_year = calc.find_resource_count_for_all_years(
            median_survival_time,
            utilities_lifetime.models.find_EL_Count,
            coeffs=fixed_params['EL_coeffs'],
            LP=EL_lp
            )
        care_years_by_year = calc.find_resource_count_for_all_years(
            median_survival_time,
            utilities_lifetime.models.find_residential_care_average_time,
            average_care_year=average_care_year
            )

        # Find discounted lists:
        A_E_discounted_list = (
            calc.find_discounted_resource_use_for_all_years(
                A_E_count_by_year, fixed_params['discount_factor_QALYs_perc'])
            )
        NEL_discounted_list = (
            calc.find_discounted_resource_use_for_all_years(
                NEL_count_by_year, fixed_params['discount_factor_QALYs_perc'])
            )
        EL_discounted_list = (
            calc.find_discounted_resource_use_for_all_years(
                EL_count_by_year, fixed_params['discount_factor_QALYs_perc'])
            )
        care_years_discounted_list = (
            calc.find_discounted_resource_use_for_all_years(
                care_years_by_year, fixed_params['discount_factor_QALYs_perc'])
            )

        # Find discounted costs:
        A_E_discounted_cost = (
            fixed_params['cost_ae_gbp'] *
            np.sum(A_E_discounted_list)
            )
        NEL_discounted_cost = (
            fixed_params['cost_non_elective_bed_day_gbp'] *
            np.sum(NEL_discounted_list)
            )
        EL_discounted_cost = (
            fixed_params['cost_elective_bed_day_gbp'] *
            np.sum(EL_discounted_list)
            )
        care_years_discounted_cost = (
            fixed_params['cost_residential_day_gbp'] * 365 *
            np.sum(care_years_discounted_list)
            )
        # Sum for total costs:
        total_discounted_cost = np.sum([
            A_E_discounted_cost,
            NEL_discounted_cost,
            EL_discounted_cost,
            care_years_discounted_cost
        ])

        # ##### General #####
        # Build a dictionary of variables used in these calculations.
        # This is mostly for the use of the detailed explanations and examples,
        # which is why it's incomplete. Other bits (e.g. from fixed_params)
        # get added to the dictionary in the function itself.
        results_dict = dict(
                # Input variables:
                age=age,
                sex=sex,
                mrs=mrs,
                # ----- For mortality: -----
                P_yr1=pDeath_list[0],
                LP_yr1=lp_yr1,
                LP_yrn=lp_yrn,
                pDeath_list=pDeath_list,
                invalid_inds_for_pDeath=invalid_inds_for_pDeath,
                hazard_list=hazard_list,
                survival_list=survival_list,
                fhazard_list=fhazard_list,
                survival_meds_IQRs=survival_years_iqr,
                survival_yr1=1.0-pDeath_list[0],
                time_of_zero_survival=time_of_zero_survival,
                # ----- For QALYs: -----
                qalys=qalys,
                qaly_list=qaly_list,
                qaly_raw_list=qaly_raw_list,
                # ----- For resource use: -----
                total_discounted_cost=total_discounted_cost,
                # A&E:
                LP_A_E=A_E_lp,
                A_E_count=A_E_count,
                # lambda_A_E=lambda_A_E,
                # Non-elective bed days
                LP_NEL=NEL_lp,
                NEL_count=NEL_count,
                # Elective bed days
                LP_EL=EL_lp,
                EL_count=EL_count,
                # Care home
                care_years=care_years,
                # For cost conversions:
                # For details in discounted cost calculations:
                A_E_counts_by_year=A_E_count_by_year,
                NEL_counts_by_year=NEL_count_by_year,
                EL_counts_by_year=EL_count_by_year,
                care_years_by_year=care_years_by_year,
                discounted_list_A_E=A_E_discounted_list,
                discounted_list_NEL=NEL_discounted_list,
                discounted_list_EL=EL_discounted_list,
                discounted_list_care=care_years_discounted_list,
                A_E_discounted_cost=A_E_discounted_cost,
                NEL_discounted_cost=NEL_discounted_cost,
                EL_discounted_cost=EL_discounted_cost,
                care_years_discounted_cost=care_years_discounted_cost,
                # ----- For cost-effectiveness -----
                )

        # Combine the separate dictionaries into one:
        results_dict = dict(**results_dict, **fixed_params)

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
    qalys_table = calc.make_table_qaly_by_change_in_outcome(qalys_all_mrs)
    # qalys_table is a 2D np.array, 6 rows by 6 columns, that contains
    # the data for the "Discounted QALYs by change in outcome" table,
    # and invalid cells already contain either '-' or '' depending.

    # ##### Resource use #####
    table_discounted_cost = calc.build_table_discounted_change(
        total_discounted_cost_all_mrs)
    # table_discounted_cost is a 2D np.array, 6 rows by 6 columns, that
    # contains the data for the "Discounted total costs by change in
    # outcome" table, and invalid cells already contain either '-' or ''.

    # ##### Cost-effectiveness #####
    table_cost_effectiveness = calc.main_cost_effectiveness(
        qalys_table, table_discounted_cost, fixed_params)
    # table_cost_effectiveness is a 2D np.array, 6 rows by 6 columns, that
    # contains the data for the "Discounted total Net Benefit by change in
    # outcome" table, and invalid cells already contain either '-' or ''.

    # ###########################
    # ######### RESULTS #########
    # ###########################

    # Pick some more bits out of the results dictionaries:
    all_survival_lists = np.array([d['survival_list'] for d in results_dict_list])
    all_hazard_lists = np.array([d['hazard_list'] for d in results_dict_list])
    all_survival_years_iqr = np.array([d['survival_meds_IQRs'] for d in results_dict_list])
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
            all_survival_years_iqr,
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
            all_survival_years_iqr,
            qalys_all_mrs,
            variables_dict,
            fixed_params
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
