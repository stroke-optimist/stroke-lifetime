"""
This script contains functions for the risk and resource use models.
These were adapted from the following R script:
  test.harnes.R, received 17/NOV/2022 from Peter McMeekin.
"""
# Imports:
import numpy as np

# Import constants:
# import utilities_lifetime.fixed_params as fixed_params


# #####################################################################
# ############################ Mortality ##############################
# #####################################################################

def find_lpDeath_yr1(age, sex, mrs, lg_mean_ages, lg_coeffs):
    """
    The linear predictor for logit year 1.

    Returns a float, the value of the linear predictor.
    """
    # The irrelevant mRS constants from lg_coeffs will be multiplied
    # by zero, but the one we want will be multiplied by one.
    mrss = [0, 0, 0, 0, 0, 0]
    mrss[mrs] = 1

    ivs = np.array([
        1,
        age - lg_mean_ages[mrs],
        sex,
        *mrss
        ])

    lp = np.sum(lg_coeffs * ivs)
    return lp


def find_pDeath_yr1(lp):
    """
    Gets probability in year 1

    Returns a float, probability of death in year one.
    """
    # Logistic formula for probability:
    p = 1.0 / (1.0 + np.exp(-lp))
    return p


def find_lpDeath_yrn(age, sex, mrs, gz_mean_age, gz_coeffs):
    """
    linear predictor for Gompertz

    Returns a float, the value of the linear predictor.
    """
    # The irrelevant mRS constants from gz_coeffs will be multiplied
    # by zero, but the one we want will be multiplied by one.
    mrss = np.array([0, 0, 0, 0, 0, 0])
    mrss[mrs] = 1

    ivs = np.array([
        1,
        age - gz_mean_age,
        (age**2.0) - gz_mean_age**2.0,
        sex,
        *mrss * (age - gz_mean_age),
        *mrss
        ])

    lp = np.sum(gz_coeffs * ivs)

    return lp


def find_FDeath_yrn(yr, gz_gamma, p1, lp_yrn):
    """
    Cumm hazard Gompertz

    Inputs:
    yr       - float or int. The chosen year.
    p1       - float. Probability of death in year one.

    Returns:
    hazard   - float. The cumulative hazard in the chosen year.
    cum_prob - float. The cumulative probability of death by the
               chosen year.
    """
    # Convert input years to days:
    days = (yr - 1.0) * 365.0
    # ^ AL changed this definition of days to match the Excel
    # Calculations sheet.

    # Cumulative hazard at time t:
    hazard = (np.exp(lp_yrn) * (np.exp(days*gz_gamma) - 1.0) /
              gz_gamma)

    # Also calculate the adjustment for year 1.
    # Cumulative probability of death by time t:
    cum_prob = 1.0 - ((1.0 - hazard)*(1.0 - p1))
    return hazard, cum_prob


def find_iDeath(
        yr,
        gz_gamma,
        lp_yrn=None,
        pDeath_yr1=None
        ):
    """
    prob of death in year n

    If year>1, use cumulative probability of death in this year
    minus the cumulative probability of death in the previous year.

    Input:
    yr     - float or int, the year in question.

    lp_yrn - needed for year > 1.
    pDeath_yr1 - needed for year=1, 2.

    Returns:
    iDeath - float. The probability of death in the chosen year.
    """
    # rVal = 0.0

    # Death in year 1:
    # Find linear predictor:

    if yr == 1:
        # AL changed the above from original "if(yr==0)".
        iDeath = pDeath_yr1
    elif yr == 2:
        # AL changed the above from original
        # "else if (rVal == 1)"
        hazard0, p0 = find_FDeath_yrn(
            yr, gz_gamma, pDeath_yr1, lp_yrn
            )
        iDeath = 1.0 - np.exp(pDeath_yr1 - p0)
    else:
        hazard0, p0 = find_FDeath_yrn(yr, gz_gamma, pDeath_yr1, lp_yrn)
        hazard1, p1 = find_FDeath_yrn(yr-1.0, gz_gamma, pDeath_yr1, lp_yrn)
        iDeath = 1.0 - np.exp(p1 - p0)
    return iDeath


def find_t_zero_survival(gz_gamma, pd1, lp_yrn, prob=1.0):
    """
    Find the time where survival is zero.
    Based on find_tDeath.

    Inputs:
    prob           - float. Chosen probability of death.
                     Survival is zero when this prob is 1.0.

    Returns:
    years_to_death - float. Years from discharge until the input
                     probability of death is reached.
    """
    if pd1 < prob:
        # AL has changed the following line from R:
        # prob_prime = ((1.0 + prob)/(1.0 + pd1)) - 1.0
        # ... because using the following line instead
        # gives the expected result for the survival-time graph.
        prob_prime = prob
        # Invert the pDeath_yrn formula to get time:
        days = (
            np.log(
                (
                    gz_gamma *
                    prob_prime *
                    np.exp(-lp_yrn)
                ) + 1.0
            ) /
            gz_gamma
            )
        # Convert days to years:
        years_to_death = (days/365) + 1
    else:
        # AL - is the following correct?
        years_to_death = (
            np.log(prob) /
            (np.log(1.0 - pd1)/365.0)
            / 365.0
        )
    return years_to_death


# def find_tDeath(age, sex, mrs, prob):
#     """
#     AL - this is currently unused in the Streamlit app as of
#          Feb 3rd 2023, and I think the "else" condition at least
#          contains errors. Commented this out for now so it's not
#          used by mistake.
#     Time of death based on probability, need to check year zero
#     Think it is fixed

#     "years_to_death" was called "rVal" in the R function.

#     Inputs:
#     prob           - float. Chosen probability of death.

#     Returns:
#     years_to_death - float. Years from discharge until the input
#                      probability of death is reached.
#     """
#     # Probability of death in year one:
#     pd1 = find_pDeath_yr1(age, sex, mrs)
#     if pd1 < prob:
#         prob_prime = ((1.0 + prob)/(1.0 + pd1)) - 1.0
#         # Linear predictor for death in year n:
#         glp = find_lpDeath_yrn(age, sex, mrs)
#         # Invert the pDeath_yrn formula to get time:
#         days = (
#             np.log(
#                 (
#                     fixed_params.gz_gamma *
#                     prob_prime *
#                     np.exp(-glp)
#                 ) + 1.0
#             ) /
#             fixed_params.gz_gamma
#             )
#         # Convert days to years:
#         years_to_death = (days/365) + 1
#     else:
#         # AL - is the following correct?
#         years_to_death = (
#             np.log(prob) /
#             (np.log(1.0 - pd1)/365.0)
#             / 365.0
#         )
#     return years_to_death


def find_survival_time_for_pDeath(pDeath, pDeath_yr1, lpDeath_yrn, gz_gamma):
    """
    Calculate the time when the probability of death is equal to
    the input probability, pDeath.

    From Calculations sheet in Excel v7.

    Inputs:
    pDeath        - float. Chosen probability of death. e.g. for
                      median, use pDeath=0.5. For lower IQR value,
                      use pDeath=0.25.
    pDeath_yr1    - float. Probability of death in year 1.
    lpDeath_yr1   - float. Linear predictor for death in year 1.

    Returns:
    survival_time - float. The survival time in years.
    survival_yrs  - float. Case 1 survival time.
    time_log      - float. Case 2 survival time.
    eqperc        - float. Adjusted input probability to account for
                      the chance of death during year one. a.k.a. P`.
    """
    # ----- Case 1: -----
    # Use this if input probability is greater than the probability
    # of death in year one.
    # Cells named "eq 50%", "eq 25%", "eq 75%":
    # This is called P`, prob prime, in the paper:
    eqperc = ((1.0 + pDeath)/(1.0 + pDeath_yr1)) - 1.0

    # Cells named "med yrs":
    if eqperc <= 0:
        survival_yrs = -1.0
    else:
        survival_yrs = (
            np.log(
                (
                    eqperc *
                    gz_gamma /
                    np.exp(lpDeath_yrn)
                ) + 1.0
            )
            / (gz_gamma*365.0)
        )
        # Note: one year added to median survival years as they
        # survive the first year.
        survival_yrs += 1.0

    # ----- Case 2: -----
    # Use this if input probability is less than or equal to the
    # probability of death in year one.
    # Cells named "time log":
    # AL - this needs an extra comment to explain why two 365s.
    # The result does match the Excel output.
    time_log_days = (
        np.log(1.0 - pDeath) /
        (np.log(1 - pDeath_yr1)/365.0)
    )
    time_log = time_log_days / 365.0

    # Choose which case to use:
    survival_time = survival_yrs if survival_yrs > 1.0 else time_log

    # Return all of the options anyway:
    return survival_time, survival_yrs, time_log, eqperc


# #####################################################################
# ############################## QALYs ################################
# #####################################################################

def calculate_qaly(
        util,
        med_survival_years,
        age,
        sex,
        average_age,
        qaly_age_coeff,
        qaly_age2_coeff,
        qaly_sex_coeff,
        dfq=0.035
        ):
    """
    Calculate the number of QALYs.

    Inputs:
    util               - float. Utility for this person's mRS score.
    med_survival_years - float. median survival years for this person.
    dfq                - float. Discount Factor QALYs, e.g. 3.5%.

    Returns:
    qaly               - float. Calculated number of QALYs.
    """
    qaly_list = []
    # Return this for printing a details table later:
    qaly_raw_list = []
    for year in np.arange(0, med_survival_years):
        # Calculate raw QALY
        raw_qaly = (
            util -
            ((age+year) - average_age) * qaly_age_coeff -
            ((age+year)**2.0 - average_age**2.0) *
            qaly_age2_coeff +
            sex * qaly_sex_coeff
        )
        if raw_qaly > 1:
            raw_qaly = 1
        qaly_raw_list.append(raw_qaly)
        # Calculate discounted QALY:
        qaly = raw_qaly * (1.0 + dfq)**(-year)

        # If this is the final year:
        if (year + age + 1) < (med_survival_years + age):
            scale_factor = 1
        elif (year + age + 1) < (med_survival_years + age + 1):
            # Find just the digits after the decimal place:
            if year == 0:
                # Modulus of zero raises an error.
                # When this condition is reached, med_survival_years
                # is less than one anyway so just use that value:
                scale_factor = med_survival_years
            else:
                scale_factor = med_survival_years % int(med_survival_years)
        else:
            # This shouldn't happen.
            scale_factor = 0
        qaly *= scale_factor

        # Add this discounted QALY to the list:
        qaly_list.append(qaly)

    # Sum up all of the values in the list:
    qaly = np.sum(qaly_list)
    return qaly, qaly_list, qaly_raw_list


def calculate_qaly_v7(util, med_survival_years, dfq=0.035):
    """
    Calculate the number of QALYs.

    This calculation was used in an older version of the Excel
    spreadsheet, NHCT v7.0. It currently goes unused in the
    Streamlit app.

    Inputs:
    util               - float. Utility for this person's mRS score.
    med_survival_years - float. median survival years for this person.
    dfq                - float. Discount Factor QALYs, e.g. 3.5%.

    Returns:
    qaly               - float. Calculated number of QALYs.
    """
    qaly = (
        util +
        util *
        ((1.0 + dfq)**(-1.0)) *
        (1.0 - (1 + dfq)**(-(med_survival_years - 1.0))) /
        (1.0 - (1 + dfq)**(-1.0))
        )
    return qaly


# #####################################################################
# ############################ Resources ##############################
# #####################################################################

def find_A_E_Count(A_E_lp, A_E_coeffs, yrs):
    """
    This section predicts the cumulative A_E admissions count for
    a given individual and a given number of years

    Inputs:
    yrs   - float. Number of years since discharge.

    Returns:
    Count - float. Number of admissions to A&E over input years.
    """
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(A_E_coeffs[3] * A_E_lp)
    # equation that estimates the A_E admissions count
    # Define this to help fit everything on one line:
    c = (-lambda_factor) * (yrs**A_E_coeffs[3])
    # Final count:
    Count = -np.log(np.exp(c))
    return Count


def find_lp_AE_Count(age, sex, mrs, lg_mean_ages, A_E_coeffs, A_E_mRS):
    """
    Linear predictor for A&E admissions count.

    Returns:
    A_E_lp - float.
    """
    # calculates the normalized age
    age_norm = age - lg_mean_ages[mrs]
    # calculates the linear predictor for A_E
    A_E_lp = (
        A_E_coeffs[0] +
        (A_E_coeffs[1]*age_norm) +
        (A_E_coeffs[2]*sex) +
        A_E_mRS[mrs]
    )
    return A_E_lp


def find_NEL_Count(NEL_lp, NEL_coeffs, yrs):
    """
    This section predicts the cumulative NEL bed days count for
    a given individual and a given number of years

    Inputs:
    yrs   - float. Number of years since discharge.

    Returns:
    Count - float. Number of non-elective bed days over input years.
    """
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(-NEL_lp)
    # equation that estimates the NEL bed days count

    # Define this to help fit everything on one line:
    c = (yrs*lambda_factor)**(1.0/NEL_coeffs[3])
    # Final count:
    Count = -np.log((1.0 + c)**(-1.0))
    return Count


def find_lp_NEL_Count(age, sex, mrs, lg_mean_ages, NEL_coeffs, NEL_mRS):
    """
    Linear predictor for NEL bed days count.

    Returns:
    NEL_lp - float.
    """
    # calculates the normalized age
    age_norm = age - lg_mean_ages[mrs]
    # calculates the linear predictor for NEL bed days
    NEL_lp = (
        NEL_coeffs[0] +
        (NEL_coeffs[1]*age_norm) +
        (NEL_coeffs[2]*sex) +
        NEL_mRS[mrs]
    )
    return NEL_lp


def find_EL_Count(EL_lp, EL_coeffs, yrs):
    """
    This section predicts the cumulative EL bed days count for
    a given individual and a given number of years

    Inputs:
    yrs   - float. Number of years since discharge.

    Returns:
    Count - float. Number of elective bed days over the input years.
    """
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(-EL_lp)
    # equation that estimates the EL bed days count
    # Define this to help fit everything on one line:
    c = (yrs*lambda_factor)**(1.0/EL_coeffs[3])
    # Final count:
    Count = -np.log((1.0 + c)**(-1.0))
    return Count


def find_lp_EL_Count(age, sex, mrs, lg_mean_ages, EL_coeffs, EL_mRS):
    """
    Linear predictor for EL bed days count.

    Returns:
    EL_lp - float.
    """
    # calculates the normalized age
    age_norm = age - lg_mean_ages[mrs]
    # calculates the linear predictor for EL bed days
    EL_lp = (
        EL_coeffs[0] +
        (EL_coeffs[1]*age_norm) +
        (EL_coeffs[2]*sex) +
        EL_mRS[mrs]
    )
    return EL_lp


def find_residential_care_average_time(average_care_year, yrs):
    """
    Find the average number of years spent in residential care
    over a time period of "yrs" since discharge.

    Keep this as a function for more easily calculating lots of years.

    Inputs:
    average_care_year - float. Average amount of time spent in care per
                        year for someone of this mRS score.
    yrs               - float. Number of years since discharge.

    Returns:
    years_in_care - float. Number of years spent in residential care
                    over the input number of years.
    """
    years_in_care = average_care_year * yrs
    return years_in_care


def find_average_care_year_per_mRS(
        age,
        perc_care_home_over70,
        perc_care_home_not_over70
        ):
    """
    Find the average care year per mRS for a patient of the input age.

    This is moved into a function in models.py because the
    calculation of percentage in a care home depends on whether
    we're using the individual mRS or dichotomous model.

    Inputs:
    age - float. Age of this patient.

    Returns:
    average_care_year_per_mRS - np.array. Average number of years
                                spent in residential care. One value
                                for each mRS.
    """
    if age > 70:
        perc_care_home = perc_care_home_over70
    else:
        perc_care_home = perc_care_home_not_over70
    # Define the "Average care (Years)" from Resource_Use sheet.
    average_care_year_per_mRS = 0.95 * perc_care_home
    return average_care_year_per_mRS
