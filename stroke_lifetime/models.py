"""
This script contains functions for the risk and resource use models.

These were adapted from the following R script:
  test.harnes.R, received 17/NOV/2022 from Peter McMeekin.
"""
# Imports:
import numpy as np


# #####################################################################
# ############################ Mortality ##############################
# #####################################################################

def find_lpDeath_year1(
        age: int,
        sex: int,
        mrs: int,
        lg_mean_ages: np.array,
        lg_coeffs: np.array
        ):
    """
    Calculate the linear predictor (lp) for death during year 1.

    This linear predictor is for the logistic (lg) model.

    Inputs:
    -------
    age          - float or int. Patient's age.
    sex          - int. Patient's sex, 0 for female and 1 for male.
    mrs          - int. Patient's mRS score from 0 to 5.
    lg_mean_ages - list or np.array. Mean age coefficients for the
                   logistic model.
    lg_coeffs    - np.array. Other coefficients for the logistic model.

    Returns:
    --------
    float. The value of the linear predictor.
    """
    # The irrelevant mRS constants from lg_coeffs will be multiplied
    # by zero, but the one we want will be multiplied by one.
    mrss = [0, 0, 0, 0, 0, 0]
    mrss[mrs] = 1

    # Create the multiplication factors for the logistic coefficients.
    # The ivs array ends up with the same number of values in it as
    # are in lg_coeffs.
    ivs = np.array([
        1,
        age - lg_mean_ages[mrs],
        sex,
        *mrss
        ])

    # Multiply the coefficients by the scale factors and take the sum.
    lp = np.sum(lg_coeffs * ivs)
    return lp


def find_pDeath_year1(lp: float):
    """
    Calculates probability of death in year 1 from a linear predictor.

    This is for the logistic model.

    Inputs:
    -------
    lp - float. Value of the linear predictor for the logistic model.

    Returns:
    --------
    float. Probability of death in year one.
    """
    # Logistic formula for probability:
    p = 1.0 / (1.0 + np.exp(-lp))
    return p


def find_lpDeath_yearn(
        age: int,
        sex: int,
        mrs: int,
        gz_mean_age: float,
        gz_coeffs: np.array
        ):
    """
    Calculate the linear predictor (lp) for death after year 1.

    This linear predictor is for the Gompertz (gz) model.

    Inputs:
    -------
    age          - float or int. Patient's age.
    sex          - int. Patient's sex, 0 for female and 1 for male.
    mrs          - int. Patient's mRS score from 0 to 5.
    gz_mean_age  - float. Mean age coefficients for the
                   Gompertz model.
    gz_coeffs    - np.array. Other coefficients for the Gompertz model.

    Returns:
    --------
    float. The value of the linear predictor.
    """
    # The irrelevant mRS constants from gz_coeffs will be multiplied
    # by zero, but the one we want will be multiplied by one.
    mrss = np.array([0, 0, 0, 0, 0, 0])
    mrss[mrs] = 1

    # Create the multiplication factors for the Gompertz coefficients.
    # The ivs array ends up with the same number of values in it as
    # are in gz_coeffs.
    ivs = np.array([
        1,
        age - gz_mean_age,
        (age**2.0) - gz_mean_age**2.0,
        sex,
        *mrss * (age - gz_mean_age),
        *mrss
        ])

    # Multiply the coefficients by the scale factors and take the sum.
    lp = np.sum(gz_coeffs * ivs)
    return lp


def find_FDeath_yearn(
        year: int,
        gz_gamma: float,
        p1: float,
        lp_yearn: float
        ):
    """
    Calculate the cumulative hazard after year one.

    Calculate the cumulative hazard at time t (H_t).
    Also, combine this hazard with the prob of death in year one to
    calculate the cumulative probability of death by time t (F_t).

    Uses the Gompertz model.

    Inputs:
    -------
    year       - float or int. The chosen year.
    gz_gamma   - float. Gompertz gamma coefficient.
    p1         - float. Probability of death in year one.
    lp_yearn   - float. Linear predictor for probability of death
                 after year 1.

    Returns:
    --------
    hazard         - float. The cumulative hazard in the chosen year.
    cum_prob_death - float. The cumulative probability of death in the
                     chosen year.
    """
    # Convert input years to days:
    days = (year - 1.0) * 365.0
    # ^ AL changed this definition of days to match the Excel
    # Calculations sheet.

    # Cumulative hazard at time t:
    hazard = (np.exp(lp_yearn) * (np.exp(days*gz_gamma) - 1.0) /
              gz_gamma)

    # Also calculate the adjustment for year 1.
    # Cumulative probability of death by time t:
    cum_prob_death = 1.0 - ((1.0 - hazard)*(1.0 - p1))
    return hazard, cum_prob_death


def find_iDeath(
        year: int,
        gz_gamma: float,
        lp_yearn: float = None,
        pDeath_year1: float = None
        ):
    """
    Calculate the probability of death in a given year.

    If year>1, use cumulative probability of death in this year
    minus the cumulative probability of death in the previous year.

    Input:
    ------
    year         - float or int, the year in question.
    gz_gamma     - float. Gompertz gamma coefficient.
    lp_yearn     - float. The value of the linear predictor for death
                   after year 1. Needed for year > 1.
    pDeath_year1 - float. The probability of death in year 1.
                   Needed for year=1, 2.

    Returns:
    --------
    iDeath - float. The probability of death in the chosen year.
    """
    # rVal = 0.0

    # Death in year 1:
    # Find linear predictor:

    if year == 1:
        # AL changed the above from original "if(year==0)".
        # Just use the existing value for probability in year 1:
        iDeath = pDeath_year1
    elif year == 2:
        # AL changed the above from original
        # "else if (rVal == 1)".
        # Calculate probability of death by year 2...
        hazard0, p0 = find_FDeath_yearn(
            year, gz_gamma, pDeath_year1, lp_yearn
            )
        # ... and combine with the probability of death in year 1:
        iDeath = 1.0 - np.exp(pDeath_year1 - p0)
    else:
        # Calculate the probability of death by this year...
        hazard0, p0 = find_FDeath_yearn(year, gz_gamma, pDeath_year1, lp_yearn)
        # ... and by the previous year...
        hazard1, p1 = find_FDeath_yearn(
            year-1.0, gz_gamma, pDeath_year1, lp_yearn)
        # ... and combine to get the probability of death in this year.
        iDeath = 1.0 - np.exp(p1 - p0)
    return iDeath


def find_time_for_this_hazard(
        gz_gamma: float,
        p_death_year1: float,
        lp_yearn: float,
        hazard_prob: float = 1.0
        ):
    """
    Find the time when hazard reaches some value.

    Use this to find when survival first reaches zero.

    Inputs:
    -------
    gz_gamma      - float. Gompertz gamma coefficient.
    p_death_year1 - float. Probability of death in year 1.
    lp_yearn      - float. Linear predictor for probability of death
                    after year 1.
    hazard_prob   - float. Chosen hazard value.
                    Survival is zero when this prob is 1.0.

    Returns:
    --------
    years_to_hazard - float. Years from discharge until the input
                      probability of death is reached.
    """
    if p_death_year1 < hazard_prob:
        # AL has changed the following line from R:
        # prob_prime = ((1.0 + prob)/(1.0 + pd1)) - 1.0
        # ... because using the following line instead
        # gives the expected result for the survival-time graph.
        prob_prime = hazard_prob
        # Invert the pDeath_yearn formula to get time:
        # Define "x" to shorten the "days = " line.
        x = (gz_gamma * prob_prime * np.exp(-lp_yearn)) + 1.0
        days = np.log(x) / gz_gamma
        # Convert days to years:
        years_to_hazard = (days/365) + 1
    else:
        # AL - is the following correct?
        years_to_hazard = (
            np.log(hazard_prob) /
            (np.log(1.0 - p_death_year1)/365.0)
            / 365.0
        )
    return years_to_hazard


def find_survival_time_for_pDeath(
        pDeath: float,
        pDeath_year1: float,
        lpDeath_yearn: float,
        gz_gamma: float
        ):
    """
    Calculate the time when the probability of death = chosen value.

    From Calculations sheet in Excel v7.

    Inputs:
    -------
    pDeath        - float. Chosen probability of death. e.g. for
                    median, use pDeath=0.5. For lower IQR value,
                    use pDeath=0.25.
    pDeath_year1  - float. Probability of death in year 1.
    lpDeath_year1 - float. Linear predictor for death in year 1.
    gz_gamma      - float. Gompertz gamma coefficient.

    Returns:
    --------
    survival_time  - float. The survival time in years.
    survival_years - float. Case 1 survival time.
    time_log       - float. Case 2 survival time.
    eqperc         - float. Adjusted input probability to account for
                     the chance of death during year one. a.k.a. P`.
    """
    # ----- Case 1: -----
    # Use this if input probability is greater than the probability
    # of death in year one.
    # Cells named "eq 50%", "eq 25%", "eq 75%":
    # This is called P`, prob prime, in the paper:
    eqperc = ((1.0 + pDeath)/(1.0 + pDeath_year1)) - 1.0

    # Cells named "med years":
    if eqperc <= 0:
        survival_years = -1.0
    else:
        # Define "x" to shorten the "survival_years = ..." line.
        x = eqperc * gz_gamma / np.exp(lpDeath_yearn)
        survival_years = np.log(x + 1.0) / (gz_gamma*365.0)
        # Note: one year added to median survival years as they
        # survive the first year.
        survival_years += 1.0

    # ----- Case 2: -----
    # Use this if input probability is less than or equal to the
    # probability of death in year one.
    # Cells named "time log":
    # AL - this needs an extra comment to explain why two 365s.
    # The result does match the Excel output.
    time_log_days = (
        np.log(1.0 - pDeath) /
        (np.log(1 - pDeath_year1)/365.0)
    )
    time_log = time_log_days / 365.0

    # Choose which case to use:
    survival_time = survival_years if survival_years > 1.0 else time_log

    # Return all of the options anyway:
    return survival_time, survival_years, time_log, eqperc


# #####################################################################
# ############################## QALYs ################################
# #####################################################################

def calculate_qaly(
        util: float,
        med_survival_years: float,
        age: float,
        sex: int,
        average_age: float,
        qaly_age_coeff: float,
        qaly_age2_coeff: float,
        qaly_sex_coeff: float,
        dfq: float = 0.035
        ):
    """
    Calculate the number of QALYs up until the median survival time.

    Inputs:
    -------
    util               - float. Utility for this person's mRS score.
    med_survival_years - float. Median survival time in years.
    age                - float. Patient's age in years.
    sex                - int. 0 for female, 1 for male.
    average_age        - float. Average age coefficient.
    qaly_age_coeff     - float. QALY age coefficient.
    qaly_age2_coeff    - float. QALY age^2 coefficient.
    qaly_sex_coeff     - float. QALY sex coefficient.
    dfq                - float. Discount Factor QALYs, e.g. 3.5%.

    Returns:
    --------
    total_qaly       - float. Calculated number of QALYs.
    qaly_by_year     - list. The discounted QALY for each year.
    qaly_raw_by_year - list. The raw QALY for each year.
    """
    # Store the raw QALY for each year in here:
    # (store this for printing a details table later).
    qaly_raw_by_year = []
    # Store discounted QALY for each year in here:
    qaly_by_year = []
    for year in np.arange(0, med_survival_years):
        # Calculate raw QALY
        raw_qaly = (
            util -
            ((age+year) - average_age) * qaly_age_coeff -
            ((age+year)**2.0 - average_age**2.0) * qaly_age2_coeff +
            sex * qaly_sex_coeff
        )
        raw_qaly = 1 if raw_qaly > 1 else raw_qaly
        qaly_raw_by_year.append(raw_qaly)

        # Calculate discounted QALY:
        qaly = raw_qaly * (1.0 + dfq)**(-year)

        if (year + age + 1) < (med_survival_years + age):
            # If this is *not* the final year:
            scale_factor = 1
        elif (year + age + 1) < (med_survival_years + age + 1):
            # If this *is* the final year, scale down the QALY
            # to match the amount of the year that the patient
            # lives during.
            if year == 0:
                # Modulus of zero raises an error.
                # When this condition is reached, med_survival_years
                # is less than one anyway so just use that value:
                scale_factor = med_survival_years
            else:
                # Find just the digits after the decimal place
                # of the median survival in years:
                scale_factor = med_survival_years % int(med_survival_years)
        else:
            # This shouldn't happen.
            scale_factor = 0

        # Multiply the discounted QALY by the scale factor:
        qaly *= scale_factor

        # Add this discounted QALY to the list:
        qaly_by_year.append(qaly)

    # Sum up all of the values in the list:
    total_qaly = np.sum(qaly_by_year)
    return total_qaly, qaly_by_year, qaly_raw_by_year


def calculate_qaly_v7(
        util: float,
        med_survival_years: float,
        dfq: float = 0.035
        ):
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

def find_ae_count(
        ae_lp: float,
        ae_coeffs: np.array,
        years: float
        ):
    """
    Calculate the cumulative ae admissions count after some years.

    The patient details (age, sex, mRS) have been used to calculate
    the linear predictor (lp).

    Inputs:
    -------
    ae_lp     - float. Value of linear predictor for A&E admissions.
    ae_coeffs - np.array. A&E coefficients.
    years     - float. Number of years since discharge.

    Returns:
    --------
    ae_count - float. Number of admissions to A&E over input years.
    """
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(-ae_coeffs[3] * ae_lp)
    # equation that estimates the ae admissions count
    # Define this to help fit everything on one line:
    c = (-lambda_factor) * (years**ae_coeffs[3])
    # Final count:
    # (Presumably the redundant log(exp()) is inherited from the
    # Excel spreadsheet or the R script?)
    ae_count = -np.log(np.exp(c))
    return ae_count


def find_lp_ae_count(
        age: float,
        sex: int,
        mrs: int,
        lg_mean_ages: np.array,
        ae_coeffs: np.array,
        ae_mRS: np.array
        ):
    """
    Calculate the linear predictor (lp) for A&E admissions count.

    Inputs:
    -------
    age          - float or int. Patient's age.
    sex          - int. Patient's sex, 0 for female and 1 for male.
    mrs          - int. Patient's mRS score from 0 to 5.
    lg_mean_ages - list or np.array. Mean age coefficients for the
                   logistic model.
    ae_coeffs    - np.array. Coefficients for the A&E model.
    ae_mRS       - np.array. mRS coefficients for the A&E model.

    Returns:
    --------
    ae_lp - float. The value of the linear predictor.
    """
    # calculates the normalized age
    age_norm = age - lg_mean_ages[mrs]
    # calculates the linear predictor for ae
    ae_lp = (
        ae_coeffs[0] +
        (ae_coeffs[1]*age_norm) +
        (ae_coeffs[2]*sex) +
        ae_mRS[mrs]
    )
    return ae_lp


def find_nel_count(
        nel_lp: float,
        nel_coeffs: np.array,
        years: float
        ):
    """
    Calculate cumulative NEL bed days count after some years.

    The patient details (age, sex, mRS) have been used to calculate
    the linear predictor (lp).

    Inputs:
    -------
    nel_lp     - float. Value of the linear predictor for NEL days.
    nel_coeffs - np.array. Coefficients for the NEL days model.
    years      - float. Number of years since discharge.

    Returns:
    --------
    count - float. Number of non-elective bed days over input years.
    """
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(-nel_lp)
    # equation that estimates the NEL bed days count

    # Define this to help fit everything on one line:
    c = (years * lambda_factor)**(1.0 / nel_coeffs[3])
    # Final count:
    count = -np.log((1.0 + c)**(-1.0))
    return count


def find_lp_nel_count(
        age: float,
        sex: int,
        mrs: int,
        lg_mean_ages: np.array,
        nel_coeffs: np.array,
        nel_mRS: np.array
        ):
    """
    Calculate the linear predictor (lp) for NEL bed days count.

    Inputs:
    -------
    age          - float or int. Patient's age.
    sex          - int. Patient's sex, 0 for female and 1 for male.
    mrs          - int. Patient's mRS score from 0 to 5.
    lg_mean_ages - list or np.array. Mean age coefficients for the
                   logistic model.
    nel_coeffs   - np.array. Coefficients for the NEL days model.
    nel_mRS      - np.array. mRS coefficients for the NEL days model.

    Returns:
    --------
    ae_lp - float. The value of the linear predictor.
    """
    # calculates the normalized age
    age_norm = age - lg_mean_ages[mrs]
    # calculates the linear predictor for NEL bed days
    nel_lp = (
        nel_coeffs[0] +
        (nel_coeffs[1] * age_norm) +
        (nel_coeffs[2] * sex) +
        nel_mRS[mrs]
    )
    return nel_lp


def find_el_count(
        el_lp: float,
        el_coeffs: np.array,
        years: float
        ):
    """
    Calculate cumulative EL bed days count after some years.

    The patient details (age, sex, mRS) have been used to calculate
    the linear predictor (lp).

    Inputs:
    -------
    el_lp     - float. Value of the linear predictor for EL days.
    el_coeffs - np.array. Coefficients for the EL days model.
    years     - float. Number of years since discharge.

    Returns:
    --------
    count - float. Number of elective bed days over input years.
    """
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(-el_lp)
    # equation that estimates the EL bed days count
    # Define this to help fit everything on one line:
    c = (years * lambda_factor)**(1.0 / el_coeffs[3])
    # Final count:
    count = -np.log((1.0 + c)**(-1.0))
    return count


def find_lp_el_count(
        age: float,
        sex: int,
        mrs: int,
        lg_mean_ages: np.array,
        el_coeffs: np.array,
        el_mRS: np.array
        ):
    """
    Calculate the linear predictor (lp) for EL bed days count.

    Inputs:
    -------
    age          - float or int. Patient's age.
    sex          - int. Patient's sex, 0 for female and 1 for male.
    mrs          - int. Patient's mRS score from 0 to 5.
    lg_mean_ages - list or np.array. Mean age coefficients for the
                   logistic model.
    el_coeffs    - np.array. Coefficients for the EL days model.
    el_mRS       - np.array. mRS coefficients for the EL days model.

    Returns:
    --------
    el_lp - float. The value of the linear predictor.
    """
    # calculates the normalized age
    age_norm = age - lg_mean_ages[mrs]
    # calculates the linear predictor for EL bed days
    el_lp = (
        el_coeffs[0] +
        (el_coeffs[1] * age_norm) +
        (el_coeffs[2] * sex) +
        el_mRS[mrs]
    )
    return el_lp


def find_residential_care_average_time(
        average_care_year: float,
        years: float or np.array
        ):
    """
    Find the average number of years spent in residential care
    over a time period of "years" since discharge.

    Keep this as a function for more easily calculating lots of years.

    Inputs:
    -------
    average_care_year - float. Average amount of time spent in care per
                        year for someone of this mRS score.
    years             - float or np.array. Number of years since
                        discharge or array of years.

    Returns:
    --------
    years_in_care - float. Number of years spent in residential care
                    over the input number of years.
    """
    years_in_care = average_care_year * years
    return years_in_care


def find_average_care_year_per_mRS(
        age: float,
        perc_care_home_over70: float,
        perc_care_home_not_over70: float
        ):
    """
    Find the average care year per mRS for a patient of the input age.

    This is moved into a function in models.py because the
    calculation of percentage in a care home depends on whether
    we're using the individual mRS or dichotomous model.

    Inputs:
    age                       - float. Age of this patient.
    perc_care_home_over70     - float. Percentage of patients aged
                                over 70 who are discharged to a
                                care home.
    perc_care_home_not_over70 - float. Percentage of patients aged
                                over 70 who are discharged to a
                                care home.

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
