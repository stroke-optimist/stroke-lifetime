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
            # Find linear predictor:
            lp_yr1 = utilities_lifetime.models.find_lpDeath_yr1(age, sex, mrs, 
                fixed_params['lg_mean_ages'], fixed_params['lg_coeffs'])
            pDeath_yr1 = utilities_lifetime.models.\
                find_pDeath_yr1(lp_yr1)
            pDeath = pDeath_yr1
        else:
            lp_yrn = utilities_lifetime.models.find_lpDeath_yrn(age, sex, mrs,
                fixed_params['gz_mean_age'], fixed_params['gz_coeffs'])
            hazard, pDeath = utilities_lifetime.models.find_FDeath_yrn(
                year, fixed_params['gz_gamma'], pDeath_yr1, lp_yrn
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


def calculate_prob_death_per_year(
        time_list_yr,
        gz_gamma,
        pDeath_yr1,
        lp_yrn
        ):
    """
    WRITE ME
    """
    pDeath_list = []
    for year in time_list_yr[1:]:
        pDeath = utilities_lifetime.models.find_iDeath(
            year, gz_gamma, lp_yrn, pDeath_yr1)
        pDeath_list.append(pDeath)
    pDeath_list = np.array(pDeath_list)
    return pDeath_list


def calculate_survival_iqr(
        age,
        gz_gamma,
        lpDeath_yrn,
        pDeath_yr1
        ):
    """
    Find the median and IQR survival times in years and the life
    expectancy given this age, sex, and mRS.

    Returns:
    years_to_note - list. Contains [median, lower IQR, upper IQR,
                    life expectancy] for this patient.
    """
    # Probability of death in year one:

    years_to_note = []
    # Loop over three probabilities: median, lower IQR, then upper IQR.
    for pDeath in [0.5, 0.25, 0.75]:
        # Calculate the time when survival is equal to input pDeath*
        # *(adjusted for year one death chance if necessary).
        survival_time, survival_yrs, time_log, eqperc = \
            utilities_lifetime.models.find_survival_time_for_pDeath(
                pDeath, pDeath_yr1, lpDeath_yrn, gz_gamma)
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
        median_survival_years,
        count_function,
        coeffs=[],
        average_care_year=np.NaN,
        LP=None
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
            if LP is None:
                count = (utilities_lifetime.models.
                         find_residential_care_average_time(
                            average_care_year, year))
            else:
                count = count_function(LP, coeffs, year)

        elif year == death_year:
            if LP is None:
                count = (utilities_lifetime.models.
                         find_residential_care_average_time(
                            average_care_year, median_survival_years))
            else:
                count = count_function(LP, coeffs, median_survival_years)

        # Subtract the count up until this year:
        count -= previous_count
        # Add this value to the running total:
        counts.append(count)
        # Set value of previous_count for the next loop:
        previous_count += count
    return counts


def find_discounted_resource_use_for_all_years(resource_list, discount_factor_QALYs_perc):
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
            discount_factor_QALYs_perc / 100.0
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
        lp_yr1,
        lp_yrn,
        pDeath_list,
        invalid_inds_for_pDeath,
        hazard_list,
        survival_list,
        fhazard_list,
        survival_times,
        time_of_zero_survival,
        A_E_lp,
        NEL_lp,
        EL_lp,
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
        A_E_discounted_list,
        NEL_discounted_list,
        EL_discounted_list,
        care_years_discounted_list,
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

    # Fill the dictionary:
    variables_dict = dict(
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
        survival_meds_IQRs=survival_times,
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
        A_E_count=A_E_count_list,
        # lambda_A_E=lambda_A_E,
        # Non-elective bed days
        LP_NEL=NEL_lp,
        NEL_count=NEL_count_list,
        # Elective bed days
        LP_EL=EL_lp,
        EL_count=EL_count_list,
        # Care home
        care_years=care_years_list,
        # For cost conversions:
        # For details in discounted cost calculations:
        A_E_counts_by_year=A_E_counts,
        NEL_counts_by_year=NEL_counts,
        EL_counts_by_year=EL_counts,
        care_years_by_year=care_years,
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
    return variables_dict
