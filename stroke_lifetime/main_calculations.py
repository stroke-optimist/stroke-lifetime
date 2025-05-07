"""
Set up the main calculations in this script.

The function main_calculations() runs through everything important
and stores the results in a dictionary.
"""
# Imports:
import numpy as np

# Import functions for calculating various quantities:
from . import models as model


# #####################################################################
# ######################## Overall function ###########################
# #####################################################################

def main_calculations(
        age: float,
        sex: int,
        sex_str: str,
        mrs: int,
        fixed_params: dict,
        model_type_str: str
        ):
    """
    Calculates everything useful for lifetime outcomes.

    Inputs:
    -------
    age            - float or int. Patient's age in years.
    sex            - int. Patient's sex, 0 for female and 1 for male.
    sex_str        - str. Either "Male" or "Female".
    mrs            - int. Patient's mRS score from 0 to 5.
    fixed_params   - dict. Contains fixed parameters independent
                     of the model results.
    model_type_str - str. Separate "mRS" or "Dichotomous" model.

    Returns:
    --------
    results_dict - dict. All of the useful results. Keys:
        age                                         - float.
        sex                                         - int.
        sex_label                                   - str.
        model_type_str                              - str.
        mrs                                         - int.
        outcome_type                                - str.
        years                                       - np.array.
        death_in_year_1_prob                        - float.
        death_in_year_1_lp                          - float.
        death_in_year_n_lp                          - float.
        death_in_year_n_probs                       - np.array.
        death_in_year_n_probs_first_invalid_index   - float.
        hazard_by_year                              - np.array.
        survival_by_year                            - np.array.
        fhazard_by_year                             - np.array.
        survival_meds_IQRs                          - np.array.
        survival_year1                              - float.
        year_when_zero_survival                     - float.
        qalys                                       - float.
        qalys_by_year                               - np.array.
        raw_qalys_by_year                           - np.array.
        total_discounted_cost                       - float.
        lp_ae                                       - float.
        ae_count                                    - float.
        lp_nel                                      - float.
        nel_count                                   - float.
        lp_el                                       - float.
        el_count                                    - float.
        care_years                                  - float.
        ae_counts_by_year                           - np.array.
        nel_counts_by_year                          - np.array.
        el_counts_by_year                           - np.array.
        care_years_by_year                          - np.array.
        ae_discounted_by_year                       - np.array.
        nel_discounted_by_year                      - np.array.
        el_discounted_by_year                       - np.array.
        care_years_discounted_by_year               - np.array.
        ae_discounted_cost                          - float.
        nel_discounted_cost                         - float.
        el_discounted_cost                          - float.
        care_years_discounted_cost                  - float.
        net_benefit                                 - float.
    """
    if mrs not in range(0, 6):
        # If mRS is 6 (dead) or other invalid value,
        # return a dictionary of placeholder empty data.

        # Assign these placeholder values:
        a = np.array([])  # empty array
        f = np.nan        # Not a Number
        s = 'n/a'         # string

        # These parameters will be placed in the dictionary later:
        outcome_type = s
        death_in_year_1_lp = f
        death_in_year_1_prob = f
        death_in_year_n_lp = f
        years = a
        hazard_by_year = a
        survival_by_year = a
        fhazard_by_year = a
        death_in_year_n_probs = a
        death_in_year_n_probs_first_invalid_index = f
        survival_median_years = f
        survival_lower_quartile_years = f
        survival_upper_quartile_years = f
        life_expectancy = f
        year_when_zero_survival = f
        qalys = f
        qalys_by_year = a
        raw_qalys_by_year = a
        ae_lp = f
        ae_count = f
        ae_count_by_year = a
        ae_discounted_by_year = a
        ae_discounted_cost = f
        nel_lp = f
        nel_count = f
        nel_count_by_year = a
        nel_discounted_by_year = a
        nel_discounted_cost = f
        el_lp = f
        el_count = f
        el_count_by_year = a
        el_discounted_by_year = a
        el_discounted_cost = f
        care_years = f
        care_years_by_year = a
        care_years_discounted_by_year = a
        care_years_discounted_cost = f
        total_discounted_cost = f
        net_benefit = f
    else:
        # ##################################
        # ########## CALCULATIONS ##########
        # ##################################

        # Shared for all patients.
        # Times for hazard with time calculations:
        # This list contains [0, 1, 2, ..., time_max_post_discharge_year].
        years = np.arange(
            0, fixed_params['time_max_post_discharge_year'] + 1, 1)

        # Choose which list of care home percentage rates to use
        # based on the age input.
        average_care_year_per_mRS = model.find_average_care_year_per_mRS(
            age,
            fixed_params['perc_care_home_over70'],
            fixed_params['perc_care_home_not_over70']
            )

        # Use the mRS score to label this patient as independent or
        # dependent in the dichotomous model.
        outcome_type = 'Dependent' if mrs > 2 else 'Independent'

        # ##### Mortality #####

        # Linear predictors:
        death_in_year_1_lp = model.find_lpDeath_year1(
            age,
            sex,
            mrs,
            fixed_params['lg_mean_ages'],
            fixed_params['lg_coeffs']
            )
        death_in_year_n_lp = model.find_lpDeath_yearn(
            age,
            sex,
            mrs,
            fixed_params['gz_mean_age'],
            fixed_params['gz_coeffs']
            )

        # Probability of death in year 1:
        death_in_year_1_prob = model.find_pDeath_year1(death_in_year_1_lp)

        # Find hazard and survival:
        # The following arrays contain one value for each year in the
        # range 1 to max year (defined in fixed_params.py).
        # Cumulative hazard, cumulative survival, output from Gompertz.
        hazard_by_year, survival_by_year, fhazard_by_year = (
            find_cumhazard_with_time(
                years,
                fixed_params['gz_gamma'],
                death_in_year_1_prob,
                death_in_year_n_lp
                ))

        # Find indices where survival is less than 0% and so the
        # calculated probability of death is invalid.
        death_in_year_n_probs_invalid_inds = (
            np.where(hazard_by_year >= 1.0)[0] + 1)
        try:
            # If there are invalid values, only store the first:
            death_in_year_n_probs_first_invalid_index = (
                death_in_year_n_probs_invalid_inds[0])
        except IndexError:
            # If there are no invalid values, store Not A Number:
            death_in_year_n_probs_first_invalid_index = np.nan
        # Add one to the index because we start hazard_by_year from year 0
        # but death_in_year_n_probs from year 1.

        # Calculate pDeath, the probability of death in each year
        # from 1 to max year (fixed_params.py).
        death_in_year_n_probs = calculate_prob_death_per_year(
            years,
            fixed_params['gz_gamma'],
            death_in_year_1_prob,
            death_in_year_n_lp
            )

        # Find when survival=0% for the survival vs. time chart:
        # Years from discharge to when survival probability is zero
        # (i.e. hazard probability is 1.0).
        year_when_zero_survival = model.find_time_for_this_hazard(
            fixed_params['gz_gamma'],
            death_in_year_1_prob,
            death_in_year_n_lp,
            hazard_prob=1.0
            )

        # Survival times:
        survival_median_years, _, _, _ = model.find_survival_time_for_pDeath(
            0.5,
            death_in_year_1_prob,
            death_in_year_n_lp,
            fixed_params['gz_gamma']
            )
        survival_lower_quartile_years, _, _, _ = (
            model.find_survival_time_for_pDeath(
                0.25,
                death_in_year_1_prob,
                death_in_year_n_lp,
                fixed_params['gz_gamma']
                )
            )
        survival_upper_quartile_years, _, _, _ = (
            model.find_survival_time_for_pDeath(
                0.75,
                death_in_year_1_prob,
                death_in_year_n_lp,
                fixed_params['gz_gamma']
                )
            )
        life_expectancy = survival_median_years + age

        # ##### QALYs #####
        # Pick out some fixed parameters:

        qalys, qalys_by_year, raw_qalys_by_year = model.calculate_qaly(
            fixed_params['utility_list'][mrs],
            survival_median_years,
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
        ae_lp = model.find_lp_ae_count(
            age,
            sex,
            mrs,
            fixed_params['lg_mean_ages'],
            fixed_params['ae_coeffs'],
            fixed_params['ae_mRS']
            )
        nel_lp = model.find_lp_nel_count(
            age,
            sex,
            mrs,
            fixed_params['lg_mean_ages'],
            fixed_params['nel_coeffs'],
            fixed_params['nel_mRS']
            )
        el_lp = model.find_lp_el_count(
            age,
            sex,
            mrs,
            fixed_params['lg_mean_ages'],
            fixed_params['el_coeffs'],
            fixed_params['el_mRS']
            )
        # Fixed parameter for care home usage:
        average_care_year = average_care_year_per_mRS[mrs]

        # Resource use across the median survival time in years:
        ae_count = model.find_ae_count(
            ae_lp,
            fixed_params['ae_coeffs'],
            survival_median_years
            )
        nel_count = model.find_nel_count(
            nel_lp,
            fixed_params['nel_coeffs'],
            survival_median_years
            )
        el_count = model.find_el_count(
            el_lp,
            fixed_params['el_coeffs'],
            survival_median_years
            )
        care_years = model.find_residential_care_average_time(
            average_care_year,
            survival_median_years
            )

        # Calculate the non-discounted values:
        # Each list contains one float for each year in the range
        # from year=1 to year=median_survival_year (rounded up).
        ae_count_by_year = find_resource_count_for_all_years(
            survival_median_years,
            model.find_ae_count,
            coeffs=fixed_params['ae_coeffs'],
            LP=ae_lp
            )
        nel_count_by_year = find_resource_count_for_all_years(
            survival_median_years,
            model.find_nel_count,
            coeffs=fixed_params['nel_coeffs'],
            LP=nel_lp
            )
        el_count_by_year = find_resource_count_for_all_years(
            survival_median_years,
            model.find_el_count,
            coeffs=fixed_params['el_coeffs'],
            LP=el_lp
            )
        care_years_by_year = find_resource_count_for_all_years(
            survival_median_years,
            model.find_residential_care_average_time,
            average_care_year=average_care_year
            )

        # Find discounted lists:
        ae_discounted_by_year = (
            find_discounted_resource_use_for_all_years(
                ae_count_by_year,
                fixed_params['discount_factor_QALYs_perc']
                )
            )
        nel_discounted_by_year = (
            find_discounted_resource_use_for_all_years(
                nel_count_by_year,
                fixed_params['discount_factor_QALYs_perc']
                )
            )
        el_discounted_by_year = (
            find_discounted_resource_use_for_all_years(
                el_count_by_year,
                fixed_params['discount_factor_QALYs_perc']
                )
            )
        care_years_discounted_by_year = (
            find_discounted_resource_use_for_all_years(
                care_years_by_year,
                fixed_params['discount_factor_QALYs_perc']
                )
            )

        # Find discounted costs:
        ae_discounted_cost = (
            fixed_params['cost_ae_gbp'] *
            np.sum(ae_discounted_by_year)
            )
        nel_discounted_cost = (
            fixed_params['cost_non_elective_bed_day_gbp'] *
            np.sum(nel_discounted_by_year)
            )
        el_discounted_cost = (
            fixed_params['cost_elective_bed_day_gbp'] *
            np.sum(el_discounted_by_year)
            )
        care_years_discounted_cost = (
            fixed_params['cost_residential_day_gbp'] * 365 *
            np.sum(care_years_discounted_by_year)
            )
        # Sum for total costs:
        total_discounted_cost = np.sum([
            ae_discounted_cost,
            nel_discounted_cost,
            el_discounted_cost,
            care_years_discounted_cost
        ])

        # ##### COST EFFECTIVENESS #####
        net_benefit = (
            fixed_params['wtp_qaly_gpb'] * qalys - total_discounted_cost)

    # ##### General #####
    # Build a dictionary of variables used in these calculations.
    # This is mostly for the use of the detailed explanations and examples,
    # which is why it's incomplete. Other bits (e.g. from fixed_params)
    # get added to the dictionary in the function itself.
    results_dict = dict(
        # Input variables:
        age=age,
        sex=sex,
        sex_label=sex_str,
        model_type=model_type_str,
        mrs=mrs,
        outcome_type=outcome_type,
        # ----- For mortality: -----
        death_in_year_1_lp=death_in_year_1_lp,
        death_in_year_1_prob=death_in_year_1_prob,
        death_in_year_n_lp=death_in_year_n_lp,
        years=years,
        hazard_by_year=hazard_by_year,
        survival_by_year=survival_by_year,
        fhazard_by_year=fhazard_by_year,
        death_in_year_n_probs=death_in_year_n_probs,
        death_in_year_n_probs_first_invalid_index=(
            death_in_year_n_probs_first_invalid_index),
        survival_median_years=survival_median_years,
        survival_lower_quartile_years=survival_lower_quartile_years,
        survival_upper_quartile_years=survival_upper_quartile_years,
        life_expectancy=life_expectancy,
        year_when_zero_survival=year_when_zero_survival,
        # ----- For QALYs: -----
        qalys_total=qalys,
        qalys_by_year=qalys_by_year,
        raw_qalys_by_year=raw_qalys_by_year,
        # ----- For resource use: -----
        # A&E:
        ae_lp=ae_lp,
        ae_count=ae_count,
        ae_counts_by_year=ae_count_by_year,
        ae_discounted_by_year=ae_discounted_by_year,
        ae_discounted_cost=ae_discounted_cost,
        # Non-elective bed days
        nel_lp=nel_lp,
        nel_count=nel_count,
        nel_counts_by_year=nel_count_by_year,
        nel_discounted_by_year=nel_discounted_by_year,
        nel_discounted_cost=nel_discounted_cost,
        # Elective bed days
        el_lp=el_lp,
        el_count=el_count,
        el_counts_by_year=el_count_by_year,
        el_discounted_by_year=el_discounted_by_year,
        el_discounted_cost=el_discounted_cost,
        # Care home
        care_years=care_years,
        care_years_by_year=care_years_by_year,
        care_years_discounted_by_year=care_years_discounted_by_year,
        care_years_discounted_cost=care_years_discounted_cost,
        # Total
        total_discounted_cost=total_discounted_cost,
        # ----- For cost-effectiveness -----
        net_benefit=net_benefit
        )

    return results_dict


# #####################################################################
# ############################ Mortality ##############################
# #####################################################################

def find_cumhazard_with_time(
        years,
        gz_gamma,
        death_in_year_1_prob,
        death_in_year_n_lp
        ):
    """
    For each year in the input list, find the cumulative probability
    of death and the survival percentage.

    AL - I'm confused about what is hazard and what is pDeath.
    The description in the Word doc doesn't match the Excel sheet.
    For now, I'm collecting hazard (Gompertz, year>1)
    but not using it elsewhere in the code.

    Inputs:
    -------
    years                - list or array. List of integer years.
    gz_gamma             - float. Gompertz gamma coefficient.
    death_in_year_1_prob - float. Probability of death in year 1.
    death_in_year_n_lp   - float. Linear predictor for probability
                           of death after year 1.

    Returns:
    --------
    death_in_year_n_probs - array. List of cumulative probability
                            of death in each year.
    survival_by_year      - array. List of survival for each year.
    hazard_by_year        - array. List of hazard for each year.
    """
    # Store hazards in here. First value will be from year 2.
    hazard_by_year = [0.0, 0.0]
    # Start with prob in year 0, which is zero:
    death_in_year_n_probs = [0.0]
    for year in years[1:]:
        if year == 1:
            pDeath = death_in_year_1_prob
        else:
            hazard, pDeath = model.find_FDeath_yearn(
                year, gz_gamma, death_in_year_1_prob, death_in_year_n_lp
                )
            hazard_by_year.append(hazard)
        # Manual override if the value is too big:
        # AL has changed this value from Excel's 1.5.
        pDeath = 1.0 if pDeath > 1.0 else pDeath
        # Add this value to list:
        death_in_year_n_probs.append(pDeath)

    # Convert to survival:
    death_in_year_n_probs = np.array(death_in_year_n_probs)
    survival_by_year = 1.0 - death_in_year_n_probs

    return death_in_year_n_probs, survival_by_year, hazard_by_year


def calculate_prob_death_per_year(
        years,
        gz_gamma,
        death_in_year_1_prob,
        death_in_year_n_lp
        ):
    """
    Calculate the probability of death during each year.

    Inputs:
    -------
    years                - list or array. List of integer years.
    gz_gamma             - float. Gompertz gamma coefficient.
    death_in_year_1_prob - float. Probability of death in year 1.
    death_in_year_n_lp   - float. Linear predictor for probability
                           of death after year 1.

    Returns:
    --------
    death_in_year_n_probs - np.array. Probability of death during
                            each year given in the input time list.
    """
    death_in_year_n_probs = []
    for year in years[1:]:
        pDeath = model.find_iDeath(
            year, gz_gamma, death_in_year_n_lp, death_in_year_1_prob)
        death_in_year_n_probs.append(pDeath)
    death_in_year_n_probs = np.array(death_in_year_n_probs)
    return death_in_year_n_probs


def calculate_survival_iqr(
        age,
        gz_gamma,
        lpDeath_yearn,
        death_in_year_1_prob
        ):
    """
    Find the median and IQR survival times and life expectancy.

    Inputs:
    -------
    age                  - float. Patient's age.
    gz_gamma             - Gompertz gamma coefficient.
    lpDeath_yearn        - float. Linear predictor for probability
                           of death after year one.
    death_in_year_1_prob - float. Probability of death in year one.

    Returns:
    years_to_note - list. Contains [median, lower IQR, upper IQR,
                    life expectancy] for this patient.
    """
    years_to_note = []
    # Loop over three probabilities: median, lower IQR, then upper IQR.
    for pDeath in [0.5, 0.25, 0.75]:
        # Calculate the time when survival is equal to input pDeath*
        # *(adjusted for year one death chance if necessary).
        survival_time, survival_years, time_log, eqperc = \
            model.find_survival_time_for_pDeath(
                pDeath, death_in_year_1_prob, lpDeath_yearn, gz_gamma)
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
        average_care_year=np.nan,
        LP=None
        ):
    """
    Calculates amount of the input resource used over the remaining
    lifetime of this patient.

    Inputs:
    -------
    median_survival_years     - list or array. List of six floats, each
                                of which is the median survival year
                                for each mRS score.
    count_function            - function. The name of a function for
                                calculating resource use in a given year.
                                Intended options: find_ae_count,
                                find_nel_count, find_el_count.
    coeffs                    - list or array. Coefficients for this
                                resource type model.
    average_care_year         - float. The average time per year spent
                                in residential care (units of years).
                                Only needed if counting care years.
    LP                        - float. The linear predictor for this
                                resource type. Not needed for time in
                                care.

    Returns:
    --------
    counts - list. Contains the resource use for each year from 1 to
             the median survival year (rounded up).
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
                count = (model.find_residential_care_average_time(
                    average_care_year, year))
            else:
                count = count_function(LP, coeffs, year)

        elif year == death_year:
            if LP is None:
                count = (model.find_residential_care_average_time(
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


def find_discounted_resource_use_for_all_years(
        resource_list,
        discount_factor_QALYs_perc
        ):
    """
    Convert the input resource list to a discounted resource list.

    From Resource_Use sheet in Excel v7.

    Inputs:
    -------
    resource_list              - list or array. List of resource use
                                 in each year of the remaining
                                 lifetime (not cumulative).
    discount_factor_QALYs_perc - float. Discount factor for QALYs.

    Returns:
    --------
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
        c = 1.0 + discount_factor_QALYs_perc / 100.0
        discounted_resource = val * (1.0 / ((c)**(year - 1.0)))
        # Store in list:
        discounted_resource_list.append(discounted_resource)
    return discounted_resource_list


# #####################################################################
# ######################## CHANGE IN OUTCOME ##########################
# #####################################################################

def build_table_qaly_by_change_in_outcome(qalys):
    """
    Make a table of the change in QALYs with change in outcome.

    This builds a 2D np.array, 6 rows by 6 columns, that contains
    the data for the "Discounted QALYs by change in outcome" table,
    and invalid cells already contain either '-' or '' depending.

    Inputs:
    -------
    qalys - list or array. The list of six QALYs, one for each mRS.

    Returns:
    --------
    table - np.array. The table of changes in QALYs.
    """
    table = []
    for row in range(len(qalys)):
        row_vals = []
        for column in range(len(qalys)):
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
    Make a table of the change in cost with change in outcome.

    This builds a 2D np.array, 6 rows by 6 columns, that contains
    data for the "Discounted total costs by change in outcome" table,
    and invalid cells already contain either '-' or '' depending.

    Inputs:
    -------
    total_discounted_cost - list or array. The list of six discounted
                            resource use totals, one for each mRS,
                            summed over all four resources.

    Returns:
    --------
    table - np.array. The table of changes in discounted resource use.
    """
    # Turn into grid by change of outcome:
    # Keep formatted values in here:
    table = []
    for row in range(len(total_discounted_cost)):
        row_vals = []
        for column in range(len(total_discounted_cost)):
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


def build_table_cost_effectiveness(net_benefit):
    """
    Make a table of net benefit by change in outcome, taking into
    account the willingness-to-pay threshold. The table is used for the
    "Discounted total Net Benefit by change in outcome" section.

    Each of the input and output tables are 6x6 in shape, where each
    row and each column is a different mRS score.

    Inputs:
    -------
    qaly_table               - array. Table of QALYs by change in
                               outcome.
    cost_table               - array. Table of discounted change in
                               cost by change in outcome.

    Returns:
    --------
    table_cost_effectiveness - array. Table with the cost effectiveness
                               values, and invalid data treated the
                               same as in the input QALY and cost
                               tables.
    """
    # The following is equivalent to this:
    # table_cost_effectiveness = (wtp_qaly_gpb * qaly_table) + cost_table

    # Turn into grid by change of outcome:
    # Keep formatted values in here:
    table = []
    for row in range(len(net_benefit)):
        row_vals = []
        for column in range(len(net_benefit)):
            if column < row:
                diff_val = net_benefit[column] - net_benefit[row]
                row_vals.append(diff_val)
            elif column == row:
                row_vals.append('-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table, dtype=object)
    return table
