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

def main_probabilities(age_input, sex_input, mrs_input):
    """
    Calculate useful quantities about mortality.

    Returns:
    time_list_yr            - np.array. Years from 0 to max year
                              as defined in fixed_params.py.
    all_hazard_lists        - List of arrays, one for each mRS.
                              Each list contains the cumulative
                              hazard for each year in the range
                              1 to max year.
    all_survival_lists      - List of arrays, one for each mRS.
                              Each list contains the cumulative
                              survival for each year in the range
                              1 to max year.
    pDeath_list             - np.array. Prob of death in each year
                              from 1 to max year (fixed_params.py).
    invalid_inds_for_pDeath - np.array. Contains indices of pDeath
                              where survival is below 0%.
    time_of_zero_survival   - float. Years from discharge to when
                              survival probability is zero.
    """
    # Define the time steps to test survival and risk at.
    # This list contains [0, 1, 2, ..., time_max_post_discharge_yr].
    time_list_yr = np.arange(
        0, utilities_lifetime.fixed_params.time_max_post_discharge_yr+1, 1)

    # Find hazard and survival for all mRS:
    all_hazard_lists = []
    all_survival_lists = []
    all_fhazard_lists = []
    for mRS in range(6):
        hazard_list, survival_list, fhazard_list = \
            find_cumhazard_with_time(time_list_yr, age_input, sex_input, mRS)
        all_hazard_lists.append(hazard_list)
        all_survival_lists.append(survival_list)
        all_fhazard_lists.append(fhazard_list)

    # Separate out the hazard for selected mRS:
    hazard_list = all_hazard_lists[mrs_input]
    # For this mRS, find where survival is less than 0% and so the
    # calculated probability of death is invalid.
    invalid_inds_for_pDeath = np.where(hazard_list >= 1.0)[0] + 1
    # Add one to the index because we start hazard_list from year 0
    # but pDeath_list from year 1.

    # Calculate pDeath, the probability of death in each year,
    # for the selected mRS:
    pDeath_list = []
    for year in time_list_yr[1:]:
        pDeath = utilities_lifetime.models.find_iDeath(
            age_input, sex_input, mrs_input, year)
        pDeath_list.append(pDeath)
    pDeath_list = np.array(pDeath_list)

    # Find when survival=0% for the survival vs. time chart:
    time_of_zero_survival = utilities_lifetime.models.find_t_zero_survival(
        age_input, sex_input, mrs_input, 1.0)

    return (time_list_yr, all_hazard_lists, all_survival_lists,
            all_fhazard_lists, pDeath_list, invalid_inds_for_pDeath,
            time_of_zero_survival)


def find_cumhazard_with_time(time_list_yr, age, sex, mrs):
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
            pDeath_yr1 = utilities_lifetime.models.find_pDeath_yr1(age, sex, mrs)
            pDeath = pDeath_yr1
        else:
            hazard, pDeath = utilities_lifetime.models.find_FDeath_yrn(
                age, sex, mrs, year, pDeath_yr1
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


def main_survival_times(age, sex):
    """
    Find the median and IQR survival times in years and the life
    expectancy for each mRS score for a patient of this age and sex.

    Wrapper for calculate_survival_iqr for multiple mRS.

    Returns:
    survival_times - np.array of six lists, one for each mRS.
                     Each list contains [median, lower IQR, upper IQR,
                     life expectancy].
    """
    # Calculate values:
    survival_times = []
    for mRS in range(6):
        years_to_note = calculate_survival_iqr(age, sex, mRS)
        # Place values in table:
        survival_times.append(years_to_note)
    # Convert to array for slicing later:
    survival_times = np.array(survival_times)
    return survival_times


def calculate_survival_iqr(age, sex, mRS):
    """
    Find the median and IQR survival times in years and the life
    expectancy given this age, sex, and mRS.

    Returns:
    years_to_note - list. Contains [median, lower IQR, upper IQR,
                    life expectancy] for this patient.
    """
    # Probability of death in year one:
    pDeath_yr1 = utilities_lifetime.models.find_pDeath_yr1(age, sex, mRS)
    # Linear predictor for years after year one:
    lpDeath_yrn = utilities_lifetime.models.find_lpDeath_yrn(age, sex, mRS)

    years_to_note = []
    # Loop over three probabilities: median, lower IQR, then upper IQR.
    for pDeath in [0.5, 0.25, 0.75]:
        # Calculate the time when survival is equal to input pDeath*
        # *(adjusted for year one death chance if necessary).
        survival_time, survival_yrs, time_log, eqperc = \
            utilities_lifetime.models.find_survival_time_for_pDeath(
                pDeath, pDeath_yr1, lpDeath_yrn)
        years_to_note.append(survival_time)

        if pDeath == 0.5:
            # If this is the median value, use it to find life
            # expectancy.
            life_expectancy = age + survival_time

    years_to_note.append(life_expectancy)
    return years_to_note


# #####################################################################
# ############################## QALYs ################################
# #####################################################################

def main_qalys(median_survival_times):
    """
    For each time in the input list, calculate the associated QALYs.

    Wrapper for calculate_qaly for multiple mRS.

    Inputs:
    median_survival_times - list or array. List of floats. Intended to
                            be the list of median survival times for
                            multiple values of mRS.

    Returns:
    qalys - list. Contains six floats, i.e. one QALY value for each mRS.
    """
    qalys = []
    for i, time in enumerate(median_survival_times):
        qaly = utilities_lifetime.models.calculate_qaly(
            utilities_lifetime.fixed_params.utility_list[i], time,
            dfq=utilities_lifetime.fixed_params.discount_factor_QALYs_perc/100.0)
        qalys.append(qaly)
    return qalys


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


# #####################################################################
# ############################ Resources ##############################
# #####################################################################

def main_resource_use(
        median_survival_years, age, sex,
        average_care_year_per_mRS
        ):
    """
    Find lists of resource use across the given number of years
    for each value of mRS.

    Wrapper for the various count functions for all mRS.

    Inputs:
    median_survival_years     - list or array. List of six floats, each
                                of which is the median survival year
                                for each mRS score.
    average_care_year_per_mRS - list or array. For each mRS score, the
                                average time per year spent in
                                residential care (units of years).

    Returns:
    Each of these is a list of six values, one for each mRS.
    A_E_count_list  - Number of A&E admissions.
    NEL_count_list  - Number of non-elective bed days.
    EL_count_list   - Number of elective bed days.
    care_years_list - Number of years in residential care.
    """
    # Store values in these lists:
    A_E_count_list = []
    NEL_count_list = []
    EL_count_list = []
    care_years_list = []
    for mRS in range(6):
        # Calculate values:
        A_E_count = utilities_lifetime.models.\
            find_A_E_Count(age, sex, mRS, median_survival_years[mRS])
        NEL_count = utilities_lifetime.models.\
            find_NEL_Count(age, sex, mRS, median_survival_years[mRS])
        EL_count = utilities_lifetime.models.\
            find_EL_Count(age, sex, mRS, median_survival_years[mRS])
        years_in_care = utilities_lifetime.models.find_residential_care_average_time(
            average_care_year_per_mRS[mRS], median_survival_years[mRS])
        # Populate lists:
        A_E_count_list.append(A_E_count)
        NEL_count_list.append(NEL_count)
        EL_count_list.append(EL_count)
        care_years_list.append(years_in_care)
    return A_E_count_list, NEL_count_list, EL_count_list, care_years_list


def main_discounted_resource_use(
        age, sex, median_survival_years, average_care_year_per_mRS):
    """
    Find the discounted resource use and costs for each mRS.

    Inputs:
    median_survival_years     - list or array. List of six floats, each
                                of which is the median survival year
                                for each mRS score.
    average_care_year_per_mRS - list or array. For each mRS score, the
                                average time per year spent in
                                residential care (units of years).

    Returns:
    Each of these is a np.array of six values, one for each mRS score.
    Cost x discounted number of...
      A_E_discounted_cost        - ... A&E admissions.
      NEL_discounted_cost        - ... non-elective bed days.
      EL_discounted_cost         - ... elective bed days.
      care_years_discounted_cost - ... years in care.
      total_discounted_cost      - sum of these four ^ values.

    Each of these is a list of six lists, one for each mRS.
    Each mRS list contains one float for each year in the range
    from year=1 to year=median_survival_year (rounded up).
    Non-discounted number of...
      A_E_counts_per_mRS         - ... A&E admissions.
      NEL_counts_per_mRS         - ... non-elective bed days.
      EL_counts_per_mRS          - ... elective bed days.
      care_years_per_mRS         - ... years in care.
    """
    # Find non-discounted lists for each category:
    # Calculate the non-discounted values:
    # Each of these is an array of six lists, and the length of each of
    # the six lists depends on the median survival year. Longer
    # survival means longer list.
    A_E_counts_per_mRS = find_resource_count_for_all_years(
        age, sex, median_survival_years, utilities_lifetime.models.find_A_E_Count)
    NEL_counts_per_mRS = find_resource_count_for_all_years(
        age, sex, median_survival_years, utilities_lifetime.models.find_NEL_Count)
    EL_counts_per_mRS = find_resource_count_for_all_years(
        age, sex, median_survival_years, utilities_lifetime.models.find_EL_Count)
    care_years_per_mRS = find_resource_count_for_all_years(
        age, sex, median_survival_years,
        utilities_lifetime.models.find_residential_care_average_time,
        1, average_care_year_per_mRS)

    # Find discounted lists for each category:
    # Each of these is a np.array of six values, one for each mRS.
    A_E_count_discounted_list = \
        find_discounted_resource_use(A_E_counts_per_mRS)
    NEL_count_discounted_list = \
        find_discounted_resource_use(NEL_counts_per_mRS)
    EL_count_discounted_list = \
        find_discounted_resource_use(EL_counts_per_mRS)
    care_years_discounted_list = \
        find_discounted_resource_use(care_years_per_mRS)

    # Convert to costs:
    # Each of these is a np.array of six values, one for each mRS.
    A_E_discounted_cost = (
        A_E_count_discounted_list *
        utilities_lifetime.fixed_params.cost_ae_gbp
        )
    NEL_discounted_cost = (
        NEL_count_discounted_list *
        utilities_lifetime.fixed_params.cost_non_elective_bed_day_gbp
        )
    EL_discounted_cost = (
        EL_count_discounted_list *
        utilities_lifetime.fixed_params.cost_elective_bed_day_gbp
        )
    care_years_discounted_cost = (
        care_years_discounted_list *
        utilities_lifetime.fixed_params.cost_residential_day_gbp * 365
        )

    # Sum for total costs:
    # Gives an array of six values, one for each mRS score.
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
        total_discounted_cost,
        # For details explanation:
        A_E_counts_per_mRS,
        NEL_counts_per_mRS,
        EL_counts_per_mRS,
        care_years_per_mRS
    )


def find_resource_count_for_all_years(
        age, sex, median_survival_years, count_function, care_home=0,
        average_care_year_per_mRS=[]
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
                    count = utilities_lifetime.models.\
                        find_residential_care_average_time(
                            average_care_year_per_mRS[mrs], year)
            elif year == death_year:
                if care_home == 0:
                    count = count_function(
                        age, sex, mrs, median_survival_years[mrs])
                else:
                    count = utilities_lifetime.models.\
                        find_residential_care_average_time(
                            average_care_year_per_mRS[mrs],
                            median_survival_years[mrs])

            # Subtract the count up until this year:
            count -= previous_count
            # Add this value to the running total:
            counts.append(count)
            # Set value of previous_count for the next loop:
            previous_count += count
        counts_per_mRS.append(counts)
    return counts_per_mRS


def find_discounted_resource_use(counts_per_mRS):
    """
    Calculates the summed discounted resource use over all years left
    in this patient's lifetime.

    Wrapper for all mRS for find_discounted_resource_use_for_all_years().

    Inputs:
    counts_per_mRS      - list or array. List of six lists (one per
                          mRS) where each mRS list has one value per
                          remaining survival year. The value (a float)
                          is the resource use during that year only.
                          Output from
                          find_resource_count_for_all_years().

    Returns:
    total_discount_list - np.array. Contains six floats, one for each mRS.
    """
    # Find discounted value for all years:
    total_discount_list = []
    for mRS in range(6):
        # Find list of discounted value in each year:
        discounted_resource_list = \
            find_discounted_resource_use_for_all_years(counts_per_mRS[mRS])
        # Sum values to get total discounted resouce over all years:
        total_discounted_resource = np.sum(discounted_resource_list)
        total_discount_list.append(total_discounted_resource)
    return np.array(total_discount_list)


def find_discounted_resource_use_for_all_years(resource_list):
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
        c = 1.0 + utilities_lifetime.fixed_params.discount_factor_QALYs_perc/100.0
        discounted_resource = val * (1.0 / ((c)**(year - 1.0)))
        discounted_resource_list.append(discounted_resource)
    return discounted_resource_list


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


# #####################################################################
# ######################## Cost effectiveness #########################
# #####################################################################

def main_cost_effectiveness(qaly_table, cost_table):
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
        utilities_lifetime.fixed_params.WTP_QALY_gpb * qaly_table) + cost_table
    return table_cost_effectiveness


# #####################################################################
# ############################## General ##############################
# #####################################################################

def build_variables_dict(
        age,
        sex,
        mrs,
        pDeath_list,
        hazard_list,
        survival_list,
        fhazard_list,
        survival_times,
        A_E_count_list,
        NEL_count_list,
        EL_count_list,
        care_years_list,
        qalys,
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
    LP_yr1 = utilities_lifetime.models.find_lpDeath_yr1(age, sex, mrs)
    LP_yrn = utilities_lifetime.models.find_lpDeath_yrn(age, sex, mrs)
    LP_A_E = utilities_lifetime.models.find_lp_AE_Count(age, sex, mrs)
    LP_NEL = utilities_lifetime.models.find_lp_NEL_Count(age, sex, mrs)
    LP_EL = utilities_lifetime.models.find_lp_EL_Count(age, sex, mrs)
    discounted_list_A_E = \
        find_discounted_resource_use_for_all_years(A_E_counts)
    discounted_list_NEL = \
        find_discounted_resource_use_for_all_years(NEL_counts)
    discounted_list_EL = \
        find_discounted_resource_use_for_all_years(EL_counts)
    discounted_list_care = \
        find_discounted_resource_use_for_all_years(care_years)

    # Fill the dictionary:
    variables_dict = dict(
        # Input variables:
        age=age,
        sex=sex,
        mrs=mrs,
        # Constants from fixed_params file:
        lg_coeffs=utilities_lifetime.fixed_params.lg_coeffs,
        lg_mean_ages=utilities_lifetime.fixed_params.lg_mean_ages,
        gz_coeffs=utilities_lifetime.fixed_params.gz_coeffs,
        gz_mean_age=utilities_lifetime.fixed_params.gz_mean_age,
        gz_gamma=utilities_lifetime.fixed_params.gz_gamma,
        # ----- For mortality: -----
        P_yr1=pDeath_list[0],
        LP_yr1=LP_yr1,
        LP_yrn=LP_yrn,
        pDeath_list=pDeath_list,
        hazard_list=hazard_list,
        survival_list=survival_list,
        fhazard_list=fhazard_list,
        survival_meds_IQRs=survival_times,
        survival_yr1=1.0-pDeath_list[0],
        # ----- For QALYs: -----
        discount_factor_QALYs_perc=utilities_lifetime.fixed_params.\
        discount_factor_QALYs_perc,
        utility_list=utilities_lifetime.fixed_params.utility_list,
        qalys=qalys,
        # ----- For resource use: -----
        total_discounted_cost=total_discounted_cost,
        # A&E:
        A_E_coeffs=utilities_lifetime.fixed_params.A_E_coeffs,
        A_E_mRS=utilities_lifetime.fixed_params.A_E_mRS,
        LP_A_E=LP_A_E,
        A_E_count_list=A_E_count_list,
        # lambda_A_E=lambda_A_E,
        # Non-elective bed days
        NEL_coeffs=utilities_lifetime.fixed_params.NEL_coeffs,
        NEL_mRS=utilities_lifetime.fixed_params.NEL_mRS,
        LP_NEL=LP_NEL,
        NEL_count_list=NEL_count_list,
        # Elective bed days
        EL_coeffs=utilities_lifetime.fixed_params.EL_coeffs,
        EL_mRS=utilities_lifetime.fixed_params.EL_mRS,
        LP_EL=LP_EL,
        EL_count_list=EL_count_list,
        # Care home
        care_years_list=care_years_list,
        perc_care_home_over70=utilities_lifetime.fixed_params.\
        perc_care_home_over70,
        perc_care_home_not_over70=utilities_lifetime.fixed_params.\
        perc_care_home_not_over70,
        # For cost conversions:
        cost_ae_gbp=utilities_lifetime.fixed_params.cost_ae_gbp,
        cost_non_elective_bed_day_gbp=utilities_lifetime.fixed_params.\
        cost_non_elective_bed_day_gbp,
        cost_elective_bed_day_gbp=utilities_lifetime.fixed_params.\
        cost_elective_bed_day_gbp,
        cost_residential_day_gbp=utilities_lifetime.fixed_params.\
        cost_residential_day_gbp,
        # For details in discounted cost calculations:
        A_E_counts=A_E_counts,
        NEL_counts=NEL_counts,
        EL_counts=EL_counts,
        care_years=care_years,
        discounted_list_A_E=discounted_list_A_E,
        discounted_list_NEL=discounted_list_NEL,
        discounted_list_EL=discounted_list_EL,
        discounted_list_care=discounted_list_care,
        A_E_discounted_cost=A_E_discounted_cost,
        NEL_discounted_cost=NEL_discounted_cost,
        EL_discounted_cost=EL_discounted_cost,
        care_years_discounted_cost=care_years_discounted_cost,
        # ----- For cost-effectiveness -----
        WTP_QALY_gpb=utilities_lifetime.fixed_params.WTP_QALY_gpb
        )
    return variables_dict
