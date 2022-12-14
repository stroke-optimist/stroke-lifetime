"""
Streamlit app template.

Because a long app quickly gets out of hand,
try to keep this document to mostly direct calls to streamlit to write
or display stuff. Use functions in other files to create and
organise the stuff to be shown. In this example, most of the work is
done in functions stored in files named container_(something).py
"""
# ----- Imports -----
import streamlit as st

# Constants and custom functions:
from utilities.fixed_params import page_setup, perc_care_home_over70, \
    perc_care_home_not_over70
from utilities.inputs import write_text_from_file
# Containers:
import utilities.container_inputs
import utilities.container_mortality
import utilities.container_qalys
import utilities.container_resources
import utilities.container_costeffectiveness
import utilities.main_calculations


# ###########################
# ##### START OF SCRIPT #####
# ###########################
# ----- Page setup -----
page_setup()

# Title:
st.markdown('# Interactive demo')
# Draw a blue information box:
st.info(
    ':information_source: ' +
    'For acronym reference, see the introduction page.'
    )
# Intro text:
write_text_from_file('pages/text_for_pages/2_Intro_for_demo.txt',
                     head_lines_to_skip=2)


# ###########################
# ########## SETUP ##########
# ###########################

# Place the user inputs in the sidebar:
with st.sidebar:
    age_input, sex_input_str, sex_input, mRS_input = \
        utilities.container_inputs.main_user_inputs()


# ##################################
# ########## CALCULATIONS ##########
# ##################################

# Calculate the important quantities:
# Probabilities:
(time_list_yr, all_hazard_lists, all_survival_lists,
 pDeath_list, invalid_inds_for_pDeath, time_of_zero_survival) \
    = utilities.main_calculations.main_probabilities(
        age_input, sex_input, mRS_input)

# Survival times:
survival_times \
    = utilities.main_calculations.main_survival_times(age_input, sex_input)

# QALYs:
median_survival_times = survival_times[:, 0]
qalys = utilities.main_calculations.main_qalys(median_survival_times)
qalys_table = \
    utilities.main_calculations.make_table_qaly_by_change_in_outcome(qalys)

# Resource use:
# Choose which list of care home percentage rates to use
# based on the age input.
if age_input > 70:
    perc_care_home = perc_care_home_over70
else:
    perc_care_home = perc_care_home_not_over70
# Define the "Average care (Years)" from Resource_Use sheet.
average_care_year_per_mRS = 0.95 * perc_care_home

A_E_count_list, NEL_count_list, EL_count_list, care_years_list = \
    utilities.main_calculations.main_resource_use(
        median_survival_times, age_input, sex_input,
        average_care_year_per_mRS
        )

# Discounted resource use:
(
    A_E_discounted_cost,
    NEL_discounted_cost,
    EL_discounted_cost,
    care_years_discounted_cost,
    total_discounted_cost,
    # For details explanation:
    A_E_counts_per_mRS, 
    NEL_counts_per_mRS, 
    EL_counts_per_mRS, 
    care_years_per_mRS
) = \
    utilities.main_calculations.main_discounted_resource_use(
        age_input, sex_input, median_survival_times,
        average_care_year_per_mRS
        )

table_discounted_cost = utilities.main_calculations.\
    build_table_discounted_change(total_discounted_cost)

table_cost_effectiveness = utilities.main_calculations.\
    main_cost_effectiveness(qalys_table, table_discounted_cost)

# Build a dictionary of variables used in these calculations.
# This is mostly for the use of the detailed explanations and examples.
variables_dict = utilities.main_calculations.build_variables_dict(
    age_input, sex_input, mRS_input, pDeath_list,
    all_survival_lists[mRS_input], survival_times,
    A_E_count_list, NEL_count_list, EL_count_list, care_years_list,
    qalys, total_discounted_cost,
    A_E_counts_per_mRS[mRS_input],
    NEL_counts_per_mRS[mRS_input],
    EL_counts_per_mRS[mRS_input],
    care_years_per_mRS[mRS_input],
    A_E_discounted_cost,
    NEL_discounted_cost,
    EL_discounted_cost,
    care_years_discounted_cost,
    )


# ###########################
# ######### RESULTS #########
# ###########################

# Put each section into its own tab.
tabs = st.tabs(['Mortality', 'QALYs', 'Resources', 'Cost'])

with tabs[0]:
    st.header('Mortality')
    utilities.container_mortality.main(
        time_list_yr, all_survival_lists,
        mRS_input, all_hazard_lists,
        pDeath_list, invalid_inds_for_pDeath, survival_times,
        time_of_zero_survival, variables_dict)


with tabs[1]:
    st.header('QALYs')
    utilities.container_qalys.main(
        survival_times, qalys, qalys_table, variables_dict)


with tabs[2]:
    st.header('Resources and costs')
    utilities.container_resources.main(
        A_E_count_list, NEL_count_list, EL_count_list, care_years_list,
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost,
        table_discounted_cost,
        variables_dict
        )


with tabs[3]:
    st.header('Cost-effectiveness')
    utilities.container_costeffectiveness.main(
        table_cost_effectiveness, variables_dict)

# ----- The end! -----
