"""
Set up (and perform?) the main calculations in this script.
"""
# Imports:
import numpy as np

from utilities.fixed_params import \
    time_max_post_discharge_yr, \
    utilities, \
    discount_factor_QALYs_perc, \
    cost_ae_gbp, \
    cost_elective_bed_day_gbp, \
    cost_non_elective_bed_day_gbp, \
    cost_residential_day_gbp, \
    WTP_QALY_gpb
from utilities.models import \
    find_iDeath, \
    find_pDeath_yr1, \
    find_pDeath_yrn, \
    find_lpDeath_yrn, \
    find_survival_time_for_pDeath, \
    calculate_qaly, \
    find_A_E_Count, \
    find_NEL_Count, \
    find_EL_Count, \
    find_residential_care_average_time, \
    find_tDeath

# Functions:
# def find_hazard_with_time(time_list_yr, age_input, sex_input, mrs_input):
#     hazard_list = []
#     for year in time_list_yr:
#         hazard = iDeath(age_input, sex_input, mrs_input, year)
#         hazard_list.append(hazard)

#     # Convert to survival:
#     hazard_list = np.array(hazard_list)
#     survival_list = 1.0 - hazard_list

#     return hazard_list, survival_list


def find_cumhazard_with_time(time_list_yr, age, sex, mrs):
    # Start with hazard in year 0, which is 0:
    hazard_list = [0.0]
    for year in time_list_yr[1:]:
        if year == 1:
            hazard_yr1 = find_pDeath_yr1(age, sex, mrs)
            hazard = hazard_yr1
        else:
            hazard_orig, hazard = find_pDeath_yrn(
                age, sex, mrs, year, hazard_yr1
                )
        # Manual override if the value is too big:
        hazard = 1.5 if hazard > 1.5 else hazard
        # Add this value to list:
        hazard_list.append(hazard)

    # Convert to survival:
    hazard_list = np.array(hazard_list)
    survival_list = 1.0 - hazard_list

    return hazard_list, survival_list


def calculate_survival_iqr(age, sex, mRS):
    pDeath_yr1 = find_pDeath_yr1(age, sex, mRS)
    lpDeath_yrn = find_lpDeath_yrn(age, sex, mRS)

    years_to_note = []
    for pDeath in [0.5, 0.25, 0.75]:
        survival_time, survival_yrs, time_log, eqperc = \
            find_survival_time_for_pDeath(pDeath, pDeath_yr1, lpDeath_yrn)
        years_to_note.append(survival_time)
        if pDeath == 0.5:
            life_expectancy = age + survival_time

    years_to_note.append(life_expectancy)
    return years_to_note


def main_probabilities(age_input, sex_input, mrs_input):
    # Define the time steps to test survival and risk at.
    # This is a list containing [0, 1, 2, ..., time_max_post_discharge_yr].
    time_list_yr = np.arange(0, time_max_post_discharge_yr+1, 1)

    # Find hazard and survival for all mRS:
    all_hazard_lists = []
    all_survival_lists = []
    for mRS in range(6):
        hazard_list, survival_list = find_cumhazard_with_time(
            time_list_yr, age_input, sex_input, mRS)
        all_hazard_lists.append(hazard_list)
        all_survival_lists.append(survival_list)

    # Find probability of death:
    hazard_list = all_hazard_lists[mrs_input]
    invalid_inds_for_pDeath = np.where(hazard_list >= 1.0)[0] + 1
    # Add one to the index because we start hazard_list from year 0
    # but pDeath_list from year 1.
    # Calculate pDeath:
    pDeath_list = []
    for year in time_list_yr[1:]:
        pDeath = find_iDeath(age_input, sex_input, mrs_input, year)
        pDeath_list.append(pDeath)
    pDeath_list = np.array(pDeath_list)

    # Find when survival=0%:
    time_of_zero_survival = find_tDeath(age_input, sex_input, mrs_input, 1.0)

    return (time_list_yr, all_hazard_lists, all_survival_lists,
            pDeath_list, invalid_inds_for_pDeath, time_of_zero_survival)


def main_survival_times(age, sex):
    # Calculate values:
    survival_times = []
    for mRS in range(6):
        years_to_note = calculate_survival_iqr(age, sex, mRS)
        # Place values in table:
        survival_times.append(years_to_note)
    # Convert to array for slicing later:
    survival_times = np.array(survival_times)
    return survival_times


def main_qalys(median_survival_times):
    qalys = []
    for i in range(6):
        qaly = calculate_qaly(
            utilities[i], median_survival_times[i], dfq=0.035)
        qalys.append(qaly)
    return qalys


def make_table_qaly_by_change_in_outcome(qalys):
    table = []
    for row in range(6):
        row_vals = []
        for column in range(6):
            if column < row:
                diff = qalys[column] - qalys[row]
                row_vals.append(diff)
            elif column == row:
                row_vals.append('-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table, dtype=object)
    return table


def find_resource_count_for_all_years(
        age, sex, median_survival_years, count_function, care_home=0,
        average_care_year_per_mRS=[]
        ):
    counts_per_mRS = []
    for mrs in range(6):

        # Split survival year into two parts:
        death_year = np.ceil(median_survival_years[mrs])
        # remainder = median_survival_years % 1

        # Calculate the resource use over all of the years alive:
        years_to_tabulate = np.arange(1, death_year+1)

        counts = []
        previous_count = 0.0
        for year in years_to_tabulate:
            if year < death_year:
                if care_home == 0:
                    count = count_function(age, sex, mrs, year)
                else:
                    count = find_residential_care_average_time(
                        mrs, average_care_year_per_mRS, year)
            elif year == death_year:
                if care_home == 0:
                    count = count_function(
                        age, sex, mrs, median_survival_years[mrs])
                else:
                    count = find_residential_care_average_time(
                        mrs, average_care_year_per_mRS,
                        median_survival_years[mrs])

            # Subtract the count up until this year:
            count -= previous_count
            # Add this value to the running total:
            counts.append(count)
            # Set value of previous_count for the next loop:
            previous_count += count
        counts_per_mRS.append(counts)
    return counts_per_mRS


def main_resource_use(
        median_survival_years, age, sex,
        average_care_year_per_mRS
        ):
    # Store values in these lists:
    A_E_count_list = []
    NEL_count_list = []
    EL_count_list = []
    care_years_list = []
    for mRS in range(6):
        # Calculate values:
        A_E_count = find_A_E_Count(age, sex, mRS, median_survival_years[mRS])
        NEL_count = find_NEL_Count(age, sex, mRS, median_survival_years[mRS])
        EL_count = find_EL_Count(age, sex, mRS, median_survival_years[mRS])
        years_in_care = find_residential_care_average_time(
            mRS, average_care_year_per_mRS, median_survival_years[mRS])
        # Populate lists:
        A_E_count_list.append(A_E_count)
        NEL_count_list.append(NEL_count)
        EL_count_list.append(EL_count)
        care_years_list.append(years_in_care)
    return A_E_count_list, NEL_count_list, EL_count_list, care_years_list


def main_discounted_resource_use(
        age, sex, median_survival_years, average_care_year_per_mRS):
    # Find non-discounted lists for each category:
    # Calculate the non-discounted values:
    A_E_counts_per_mRS = find_resource_count_for_all_years(
        age, sex, median_survival_years, find_A_E_Count)
    NEL_counts_per_mRS = find_resource_count_for_all_years(
        age, sex, median_survival_years, find_NEL_Count)
    EL_counts_per_mRS = find_resource_count_for_all_years(
        age, sex, median_survival_years, find_EL_Count)
    care_years_per_mRS = find_resource_count_for_all_years(
        age, sex, median_survival_years,
        find_residential_care_average_time, 1, average_care_year_per_mRS)

    # Find discounted lists for each category:
    A_E_count_discounted_list = \
        find_discounted_resource_use(A_E_counts_per_mRS)
    NEL_count_discounted_list = \
        find_discounted_resource_use(NEL_counts_per_mRS)
    EL_count_discounted_list = \
        find_discounted_resource_use(EL_counts_per_mRS)
    care_years_discounted_list = \
        find_discounted_resource_use(care_years_per_mRS)

    # Convert to costs:
    A_E_discounted_cost = \
        A_E_count_discounted_list * cost_ae_gbp
    NEL_discounted_cost = \
        NEL_count_discounted_list * cost_non_elective_bed_day_gbp
    EL_discounted_cost = (
        EL_count_discounted_list *
        cost_elective_bed_day_gbp
        )
    care_years_discounted_cost = (
        care_years_discounted_list *
        cost_residential_day_gbp * 365
        )

    # Sum for total costs:
    total_discounted_cost = np.sum([
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost
    ], axis=0)

    return (
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
    )


def find_discounted_resource_use(counts_per_mRS):
    # Find discounted value for all years:
    total_discount_list = []
    for mRS in range(6):
        discounted_resource_list = \
            find_discounted_resource_use_for_all_years(
                counts_per_mRS[mRS], discount_factor_QALYs_perc)
        total_discounted_resource = np.sum(discounted_resource_list)
        total_discount_list.append(total_discounted_resource)
    return np.array(total_discount_list)


def find_discounted_resource_use_for_all_years(
        resource, discount_factor_QALYs_perc):
    """
    From Resource_Use sheet.
    """
    discounted_resource_list = []
    for i in range(len(resource)):
        year = i + 1
        discounted_resource = (
            resource[i] *
            (1.0 / (
                    (1.0 + discount_factor_QALYs_perc/100.0)**(year - 1.0)
                ))
        )
        discounted_resource_list.append(discounted_resource)
    return discounted_resource_list


def build_table_discounted_change(total_discounted_cost):
    # Turn into grid by change of outcome:
    # Keep formatted values in here:
    table = []
    for row in range(6):
        row_vals = []
        for column in range(6):
            # sign = ''
            if column < row:
                diff_val = (total_discounted_cost[row] -
                            total_discounted_cost[column])
                row_vals.append(diff_val)
            elif column == row:
                row_vals.append('-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table, dtype=object)
    return table


def main_cost_effectiveness(qaly_table, cost_table):
    table_cost_effectiveness = (WTP_QALY_gpb * qaly_table) + cost_table
    return table_cost_effectiveness
