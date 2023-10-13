"""
Set up the main calculations in this script.
"""
# Imports:
import numpy as np

# Import constants:
import utilities_lifetime.fixed_params
# Import functions for calculating various quantities:
import utilities_lifetime.models


# #####################################################################
# ############################ Mortality ##############################
# #####################################################################

def find_cumhazard_with_time(time_list_yr, age, sex, mrs, fixed_params):
    """
    For each year in the input list, find the cumulative probability
    of death and the survival percentage.

    AL - I'm confused about what is hazard and what is pDeath.
    The description in the Word doc doesn't match the Excel sheet.
    For now, I'm collecting hazard (Gompertz, year>1)
    but not using it elsewhere in the code.

    Inputs:
    time_list_year - list or array. List of integer years.

    Returns:
    pDeath_list    - array. List of cumulative probability of death
                     in each year.
    survival_list  - array. List of survival for each year.
    """
    # Store hazards in here. First value will be from year 2.
    hazard_list = [0.0, 0.0]
    # Start with prob in year 0, which is zero:
    pDeath_list = [0.0]
    for year in time_list_yr[1:]:
        if year == 1:
            pDeath_yr1 = utilities_lifetime.models.\
                find_pDeath_yr1(age, sex, mrs, fixed_params)
            pDeath = pDeath_yr1
        else:
            hazard, pDeath = utilities_lifetime.models.find_FDeath_yrn(
                age, sex, mrs, year, fixed_params, pDeath_yr1
                )
            hazard_list.append(hazard)
        # Manual override if the value is too big:
        # AL has changed this value from Excel's 1.5.
        pDeath = 1.0 if pDeath > 1.0 else pDeath
        # Add this value to list:
        pDeath_list.append(pDeath)

    # Convert to survival:
    pDeath_list = np.array(pDeath_list)
    survival_list = 1.0 - pDeath_list

    return pDeath_list, survival_list, hazard_list


def calculate_prob_death_per_year(age_input, sex_input, mrs, time_list_yr, fixed_params):
    """
    WRITE ME
    """
    pDeath_list = []
    for year in time_list_yr[1:]:
        pDeath = utilities_lifetime.models.find_iDeath(
            age_input, sex_input, mrs, year, fixed_params)
        pDeath_list.append(pDeath)
    pDeath_list = np.array(pDeath_list)
    return pDeath_list


def calculate_survival_iqr(age, sex, mRS, fixed_params):
    """
    Find the median and IQR survival times in years and the life
    expectancy given this age, sex, and mRS.

    Returns:
    years_to_note - list. Contains [median, lower IQR, upper IQR,
                    life expectancy] for this patient.
    """
    # Probability of death in year one:
    pDeath_yr1 = utilities_lifetime.models.find_pDeath_yr1(age, sex, mRS, fixed_params)
    # Linear predictor for years after year one:
    lpDeath_yrn = utilities_lifetime.models.find_lpDeath_yrn(age, sex, mRS, fixed_params)

    years_to_note = []
    # Loop over three probabilities: median, lower IQR, then upper IQR.
    for pDeath in [0.5, 0.25, 0.75]:
        # Calculate the time when survival is equal to input pDeath*
        # *(adjusted for year one death chance if necessary).
        survival_time, survival_yrs, time_log, eqperc = \
            utilities_lifetime.models.find_survival_time_for_pDeath(
                pDeath, pDeath_yr1, lpDeath_yrn, fixed_params)
        years_to_note.append(survival_time)

        if pDeath == 0.5:
            # If this is the median value, use it to find life
            # expectancy.
            life_expectancy = age + survival_time

    years_to_note.append(life_expectancy)
    return years_to_note


# #####################################################################
# ############################ Resources ##############################
# #####################################################################

def find_resource_count_for_all_years(
        age, sex, mrs, median_survival_years, count_function, fixed_params,
        average_care_year=np.NaN, care_home=0
        ):
    """
    Calculates amount of the input resource used over the remaining
    lifetime of this patient.

    Inputs:
    median_survival_years     - list or array. List of six floats, each
                                of which is the median survival year
                                for each mRS score.
    count_function            - function. The name of a function for
                                calculating resource use in a given year.
                                Intended options: find_A_E_Count,
                                find_NEL_Count, find_EL_Count.
    care_home                 - int. Set to 1 if using the time in care
                                resource so that the right function
                                is used.
    average_care_year_per_mRS - list or array. For each mRS score, the
                                average time per year spent in
                                residential care (units of years).
                                Only needed if counting care years.

    Returns:
    counts_per_mRS - list. Contains six lists, one for each mRS,
                     and each of which contains the resource use
                     for each year from 1 to the median survival
                     year (rounded up).
    """

    # Split survival year into two parts:
    death_year = np.ceil(median_survival_years)
    # remainder = median_survival_years % 1

    # Calculate the resource use over all of the years alive:
    years_to_tabulate = np.arange(1, death_year+1)

    counts = []
    previous_count = 0.0
    for year in years_to_tabulate:
        if year < death_year:
            if care_home == 0:
                count = count_function(age, sex, mrs, year, fixed_params)
            else:
                count = utilities_lifetime.models.\
                    find_residential_care_average_time(
                        average_care_year, year)
        elif year == death_year:
            if care_home == 0:
                count = count_function(
                    age, sex, mrs, median_survival_years, fixed_params)
            else:
                count = utilities_lifetime.models.\
                    find_residential_care_average_time(
                        average_care_year,
                        median_survival_years)

        # Subtract the count up until this year:
        count -= previous_count
        # Add this value to the running total:
        counts.append(count)
        # Set value of previous_count for the next loop:
        previous_count += count
    return counts


def find_discounted_resource_use_for_all_years(resource_list, fixed_params):
    """
    Convert the input resource list to a discounted resource list.

    From Resource_Use sheet in Excel v7.

    Inputs:
    resource                 - list or array. List of the resource use
                               in each year of the remaining lifetime.
                               (not cumulative).

    Returns:
    discounted_resource_list - list. Contains the discounted resource
                               use for each year in the remaining
                               lifetime (not cumulative).
    """
    discounted_resource_list = []
    for i, val in enumerate(resource_list):
        # Start from year 1, which is the first (0th) element in
        # resource_list.
        year = i + 1
        # Define this to fit on one line more easily:
        c = (
            1.0 +
            fixed_params['discount_factor_QALYs_perc'] / 100.0
            )
        discounted_resource = val * (1.0 / ((c)**(year - 1.0)))
        discounted_resource_list.append(discounted_resource)
    return discounted_resource_list


# #####################################################################
# ######################## CHANGE IN OUTCOME ##########################
# #####################################################################

def make_table_qaly_by_change_in_outcome(qalys):
    """
    Make a table of the change in QALYs with change in outcome.

    This builds a 2D np.array, 6 rows by 6 columns, that contains
    the data for the "Discounted QALYs by change in outcome" table,
    and invalid cells already contain either '-' or '' depending.

    Inputs:
    qalys - list or array. The list of six QALYs, one for each mRS.

    Returns:
    table - np.array. The table of changes in QALYs.
    """
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


def build_table_discounted_change(total_discounted_cost):
    """
    Make a table of the change in QALYs with change in outcome.

    This builds a 2D np.array, 6 rows by 6 columns, that contains
    data for the "Discounted total costs by change in outcome" table,
    and invalid cells already contain either '-' or '' depending.

    Inputs:
    total_discounted_cost - list or array. The list of six discounted
                            resource use totals, one for each mRS,
                            summed over all four resources.

    Returns:
    table - np.array. The table of changes in discounted resource use.
    """
    # Turn into grid by change of outcome:
    # Keep formatted values in here:
    table = []
    for row in range(6):
        row_vals = []
        for column in range(6):
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


def main_cost_effectiveness(qaly_table, cost_table, fixed_params):
    """
    Make a table of net benefit by change in outcome, taking into
    account the willingness-to-pay threshold. The table is used for the
    "Discounted total Net Benefit by change in outcome" section.

    Each of the input and output tables are 6x6 in shape, where each
    row and each column is a different mRS score.

    Inputs:
    qaly_table               - array. Table of QALYs by change in
                               outcome.
    cost_table               - array. Table of discounted change in
                               cost by change in outcome.

    Returns:
    table_cost_effectiveness - array. Table with the cost effectiveness
                               values, and invalid data treated the
                               same as in the input QALY and cost
                               tables.
    """
    table_cost_effectiveness = (
        fixed_params['WTP_QALY_gpb'] * qaly_table) + cost_table
    return table_cost_effectiveness


# #####################################################################
# ############################## General ##############################
# #####################################################################

def build_variables_dict(
        fixed_params,
        age,
        sex,
        mrs,
        pDeath_list,
        invalid_inds_for_pDeath,
        hazard_list,
        survival_list,
        fhazard_list,
        survival_times,
        time_of_zero_survival,
        A_E_count_list,
        NEL_count_list,
        EL_count_list,
        care_years_list,
        qalys,
        qaly_list,
        qaly_raw_list,
        total_discounted_cost,
        A_E_counts,
        NEL_counts,
        EL_counts,
        care_years,
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        ):
    """
    Build a dictionary to gather useful variables in one place.

    This is used when printing values in the example calculations
    in the "details" sections. This function looks clunky but saves
    faff in importing the right variables to those examples.

    Inputs:
    loads of assorted constants, variables, lists...

    Returns:
    variables_dict - dictionary of useful quantities.
    """
    # Calculate some bits we're missing:
    # P_yr1 = find_pDeath_yr1(age, sex, mrs)
    LP_yr1 = utilities_lifetime.models.find_lpDeath_yr1(age, sex, mrs, fixed_params)
    LP_yrn = utilities_lifetime.models.find_lpDeath_yrn(age, sex, mrs, fixed_params)
    LP_A_E = utilities_lifetime.models.find_lp_AE_Count(age, sex, mrs, fixed_params)
    LP_NEL = utilities_lifetime.models.find_lp_NEL_Count(age, sex, mrs, fixed_params)
    LP_EL = utilities_lifetime.models.find_lp_EL_Count(age, sex, mrs, fixed_params)
    discounted_list_A_E = \
        find_discounted_resource_use_for_all_years(A_E_counts, fixed_params)
    discounted_list_NEL = \
        find_discounted_resource_use_for_all_years(NEL_counts, fixed_params)
    discounted_list_EL = \
        find_discounted_resource_use_for_all_years(EL_counts, fixed_params)
    discounted_list_care = \
        find_discounted_resource_use_for_all_years(care_years, fixed_params)

    # Fill the dictionary:
    variables_dict = dict(
        # Input variables:
        age=age,
        sex=sex,
        mrs=mrs,
        # Constants from fixed_params file:
        lg_coeffs=fixed_params['lg_coeffs'],
        lg_mean_ages=fixed_params['lg_mean_ages'],
        gz_coeffs=fixed_params['gz_coeffs'],
        gz_mean_age=fixed_params['gz_mean_age'],
        gz_gamma=fixed_params['gz_gamma'],
        # ----- For mortality: -----
        P_yr1=pDeath_list[0],
        LP_yr1=LP_yr1,
        LP_yrn=LP_yrn,
        pDeath_list=pDeath_list,
        invalid_inds_for_pDeath=invalid_inds_for_pDeath,
        hazard_list=hazard_list,
        survival_list=survival_list,
        fhazard_list=fhazard_list,
        survival_meds_IQRs=survival_times,
        survival_yr1=1.0-pDeath_list[0],
        time_of_zero_survival=time_of_zero_survival,
        # ----- For QALYs: -----
        discount_factor_QALYs_perc=fixed_params['discount_factor_QALYs_perc'],
        utility_list=fixed_params['utility_list'],
        qalys=qalys,
        qaly_list=qaly_list,
        qaly_raw_list=qaly_raw_list,
        # Constants from fixed_params file:
        qaly_age_coeff=fixed_params['qaly_age_coeff'],
        qaly_age2_coeff=fixed_params['qaly_age2_coeff'],
        qaly_sex_coeff=fixed_params['qaly_sex_coeff'],
        # ----- For resource use: -----
        total_discounted_cost=total_discounted_cost,
        # A&E:
        A_E_coeffs=fixed_params['A_E_coeffs'],
        A_E_mRS=fixed_params['A_E_mRS'],
        LP_A_E=LP_A_E,
        A_E_count=A_E_count_list,
        # lambda_A_E=lambda_A_E,
        # Non-elective bed days
        NEL_coeffs=fixed_params['NEL_coeffs'],
        NEL_mRS=fixed_params['NEL_mRS'],
        LP_NEL=LP_NEL,
        NEL_count=NEL_count_list,
        # Elective bed days
        EL_coeffs=fixed_params['EL_coeffs'],
        EL_mRS=fixed_params['EL_mRS'],
        LP_EL=LP_EL,
        EL_count=EL_count_list,
        # Care home
        care_years=care_years_list,
        perc_care_home_over70=fixed_params['perc_care_home_over70'],
        perc_care_home_not_over70=fixed_params['perc_care_home_not_over70'],
        # For cost conversions:
        cost_ae_gbp=fixed_params['cost_ae_gbp'],
        cost_non_elective_bed_day_gbp=fixed_params['cost_non_elective_bed_day_gbp'],
        cost_elective_bed_day_gbp=fixed_params['cost_elective_bed_day_gbp'],
        cost_residential_day_gbp=fixed_params['cost_residential_day_gbp'],
        # For details in discounted cost calculations:
        A_E_counts_by_year=A_E_counts,
        NEL_counts_by_year=NEL_counts,
        EL_counts_by_year=EL_counts,
        care_years_by_year=care_years,
        discounted_list_A_E=discounted_list_A_E,
        discounted_list_NEL=discounted_list_NEL,
        discounted_list_EL=discounted_list_EL,
        discounted_list_care=discounted_list_care,
        A_E_discounted_cost=A_E_discounted_cost,
        NEL_discounted_cost=NEL_discounted_cost,
        EL_discounted_cost=EL_discounted_cost,
        care_years_discounted_cost=care_years_discounted_cost,
        # ----- For cost-effectiveness -----
        WTP_QALY_gpb=fixed_params['WTP_QALY_gpb']
        )
    return variables_dict
