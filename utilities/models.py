"""
This script contains functions for the risk and resource use models.
These were adapted from the following R script:
  test.harnes.R, received 17/NOV/2022 from Peter McMeekin.
"""
# Imports:
import numpy as np

from utilities.fixed_params import \
    lg_coeffs, lg_mean_ages, \
    gz_coeffs, gz_mean_age, gz_gamma, \
    A_E_coeffs, A_E_mRS, \
    NEL_coeffs, NEL_mRS, \
    EL_coeffs, EL_mRS


def find_lpDeath_yr1(age, sex, mrs):
    """The linear predictor for logit year 1"""

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


def find_pDeath_yr1(age, sex, mrs):
    """Gets probability in year 1"""

    lp = find_lpDeath_yr1(age, sex, mrs)
    p = 1.0 / (1.0 + np.exp(-lp))

    return p


def find_lpDeath_yrn(age, sex, mrs):
    """linear predictor for Gompertz"""

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


def find_pDeath_yrn(age, sex, mrs, yr, p1=None):
    """Cumm hazard Gompertz"""

    lp = find_lpDeath_yrn(age, sex, mrs)
    days = (yr - 1.0)*365.0
    # ^ AL changed this definition of days to match the Excel
    # Calculations sheet.
    p_orig = np.exp(lp)*(np.exp(days*gz_gamma)-1.0) / gz_gamma

    # Also calculate the adjustment for year 1.
    # (comment this better - why do we bother with two different p?)
    if p1 is None:
        # Calculate the prob in year 1 if it's not given:
        p1 = find_pDeath_yr1(age, sex, mrs)
    p = 1.0 - ((1.0 - p_orig)*(1.0 - p1))
    return p_orig, p


def find_iDeath(age, sex, mrs, yr):
    """prob of death in year n"""
    # rVal = 0.0
    if yr == 1:
        # AL changed the above from original "if(yr==0)".
        rVal = find_pDeath_yr1(age, sex, mrs)
    elif yr == 2:
        # AL changed the above from original
        # "else if (rVal == 1)"
        p0_orig, p0 = find_pDeath_yrn(age, sex, mrs, yr)
        p1 = find_pDeath_yr1(age, sex, mrs)
        rVal = 1.0 - np.exp(p1 - p0)
    else:
        p0_orig, p0 = find_pDeath_yrn(age, sex, mrs, yr)
        p1_orig, p1 = find_pDeath_yrn(age, sex, mrs, yr-1.0)
        rVal = 1.0 - np.exp(p1 - p0)
    return rVal


def find_tDeath(age, sex, mrs, prob):
    """
    Time of death based on probability, need to check year zero
    Think it is fixed

    "years_to_death" was called "rVal" in the R function.
    """
    # Probability of death in year one:
    pd1 = find_pDeath_yr1(age, sex, mrs)
    if pd1 < prob:
        # AL has changed the following line from R:
        # prob_prime = ((1.0 + prob)/(1.0 + pd1)) - 1.0
        # ... because using the following line instead
        # gives the expected result for the survival-time graph.
        prob_prime = prob
        # Linear predictor for death in year n:
        glp = find_lpDeath_yrn(age, sex, mrs)
        # Invert the pDeath_yrn formula to get time:
        days = np.log((gz_gamma * prob_prime * np.exp(-glp)) + 1.0) / gz_gamma
        # Convert days to years:
        years_to_death = (days/365) + 1
    else:
        # AL - is the following correct?
        years_to_death = np.log(prob) / -(-(np.log(1.0 - pd1))/365.0) / 365.0

    return years_to_death


def find_survival_time_for_pDeath(pDeath, pDeath_yr1, lpDeath_yrn):
    """
    From Calculations sheet.
    """
    # Cells named "eq 50%", "eq 25%", "eq 75%":
    eqperc = ((1.0 + pDeath)/(1.0 + pDeath_yr1)) - 1.0

    # Cells named "med yrs":
    if eqperc <= 0:
        survival_yrs = -1.0
    else:
        survival_yrs = (
            np.log(
                (eqperc * gz_gamma / np.exp(lpDeath_yrn)) + 1.0
            )
            / (gz_gamma*365.0)
        )
        # Note: one year added to median survival years as they
        # survive the first year.
        survival_yrs += 1.0

    # Cells named "time log":
    # AL - This derivation doesn't look correct.
    # Is the initial "1-" in there by accident? It disappears.
    #
    # Note when first year survuval is less than pDeath %, the median
    # survival is calculate from the logit function from the formula:
    #      1 - (1 - pDeath_yr1)^x = (1 - pdeath)
    # -->  log(1 - pdeath) = log[(1 - pDeath_yr1)^x]
    # -->  log(1 - pdeath) = x log(1 - pDeath_yr1)
    # -->  x = log(1 - pdeath) / log(1 - pDeath_yr1)
    #
    # AL - this needs an extra comment to explain why two 365s.
    # The result does match the Excel output.
    time_log = (
        np.log(1.0 - pDeath) /
        -(
            -np.log(1 - pDeath_yr1)/365.0
        )/365.0
    )

    # Choose which to use:
    survival_time = survival_yrs if survival_yrs > 1.0 else time_log

    return survival_time, survival_yrs, time_log, eqperc


def calculate_qaly(util, med_survival_years, dfq=0.035):
    # DFQ = discount factor QALYs, e.g. 3.5%.
    qaly = (
        util +
        util *
        ((1.0 + dfq)**(-1.0)) *
        (1.0 - (1 + dfq)**(-(med_survival_years - 1.0))) /
        (1.0 - (1 + dfq)**(-1.0))
        )
    return qaly


def find_A_E_Count(age, sex, mrs, yrs):
    """
    This section predicts the cumulative A_E admissions count for
    a given individual and a given number of years
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
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(A_E_coeffs[3] * A_E_lp)
    # equation that estimates the A_E admissions count
    Count = (
        -np.log(
            np.exp(
                (-lambda_factor) * (yrs**A_E_coeffs[3])
            )
        )
    )
    return Count


def find_NEL_Count(age, sex, mrs, yrs):
    """
    This section predicts the cumulative NEL bed days count for
    a given individual and a given number of years
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
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(-NEL_lp)
    # equation that estimates the NEL bed days count
    Count = (
        -np.log(
            (
                1.0 + (yrs*lambda_factor)**(1.0/NEL_coeffs[3])
            )**(-1.0)
        )
    )
    return Count


def find_EL_Count(age, sex, mrs, yrs):
    """
    This section predicts the cumulative EL bed days count for
    a given individual and a given number of years
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
    # creates the lambda function for the equation
    # AL - for python, changed this to a variable:
    lambda_factor = np.exp(-EL_lp)
    # equation that estimates the EL bed days count
    Count = (
        -np.log(
            (
                1.0 + (yrs*lambda_factor)**(1.0/EL_coeffs[3])
            )**(-1.0)
        )
    )
    return Count


def find_residential_care_average_time(mRS, average_care_year_per_mRS, yrs):
    """
    Keep this as a function for more easily calculating lots of years.
    """
    years_in_care = average_care_year_per_mRS[mRS] * yrs
    return years_in_care
