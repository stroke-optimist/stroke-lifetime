"""
Define constants that will be used in multiple places throughout the
script but that only need to be defined once.

There are now two sets of parameters, one each for:
+ individual mRS levels
+ dichotomised outcome
The equivalent parameters have the same name in both cases.
There's a check in these dictionary-building for which set to use
depending on the user selection of model type. These functions are
run every time the app is re-run so that the parameters used
always match the selected model type.

This script contains multiple functions that build up a single
dictionary of fixed parameters. The dictionary values are defined
as variables in the functions and then at the end added to the
dictionary. This layout is used instead of just making a dictionary
at the start and adding values as they're defined because this way
is better for including very many comments about where exactly
all of the numbers came from. It's also better for the values that
are calculated every time, and in case one day we change the dicts
to another format but need to keep the same data.
"""
import numpy as np


def get_fixed_params(model_input_str: str):
    """
    Main function for collecting parameters for chosen model type.

    Runs two functions in this script. The first collects the
    parameters that are shared between model types. The second looks
    at the input chosen model type and collects the remaining
    parameters that are specific to that model type.

    Inputs:
    -------
    model_input_str - str. Either "mRS" or "Dichotomous". "mRS" has
                      separate parameters for each mRS score, and
                      "dichotomous" has shared parameters for mRS
                      0, 1, 2 and for mRS 3, 4, 5.

    Returns:
    --------
    fixed_params - dict. The dictionary of fixed parameters. Keys:
        time_max_post_discharge_year        - int.
        qaly_age_coeff                      - float.
        qaly_age2_coeff                     - float.
        qaly_sex_coeff                      - float.
        discount_factor_QALYs_perc          - float.
        discount_factor_costs_perc          - float.
        wtp_qaly_gpb                        - float.
        cost_ae_gbp                         - float.
        cost_elective_bed_day_gbp           - float.
        cost_non_elective_bed_day_gbp       - float.
        cost_residential_day_gbp            - float.
        n_patients_care_home                - np.array.
        n_patients_not_care_home            - np.array.
        n_patients_care_home_over70         - np.array.
        n_patients_not_care_home_over70     - np.array.
        n_patients_care_home_not_over70     - np.array.
        n_patients_not_care_home_not_over70 - np.array.
        perc_care_home_all_ages             - float.
        perc_care_home_over70               - float.
        perc_care_home_not_over70           - float.
        utility_list                        - list.
        lg_coeffs                           - np.array.
        lg_mean_ages                        - np.array.
        gz_coeffs                           - np.array.
        gz_gamma                            - float.
        gz_mean_age                         - float.
        ae_coeffs                           - np.array.
        ae_mRS                              - np.array.
        nel_coeffs                          - np.array.
        nel_mRS                             - np.array.
        el_coeffs                           - np.array.
        el_mRS                              - np.array.
    """
    # Start with parameters that are shared for all model types:
    fixed_params_shared = make_fixed_params_shared()

    # Get parameters for the selected model type:
    if model_input_str == 'mRS':
        fixed_params_model = make_fixed_params_mrs_model(fixed_params_shared)
    elif model_input_str == 'Dichotomous':
        fixed_params_model = make_fixed_params_dicho_model(
            fixed_params_shared)

    # Combine the separate dictionaries into one:
    fixed_params = dict(**fixed_params_shared, **fixed_params_model)

    return fixed_params


def make_fixed_params_shared():
    """
    Make dictionary for fixed parameters for all model types.

    Returns:
    --------
    dict. The dictionary of fixed parameters. Keys:
        time_max_post_discharge_year        - int.
        qaly_age_coeff                      - float.
        qaly_age2_coeff                     - float.
        qaly_sex_coeff                      - float.
        discount_factor_QALYs_perc          - float.
        discount_factor_costs_perc          - float.
        wtp_qaly_gpb                        - float.
        cost_ae_gbp                         - float.
        cost_elective_bed_day_gbp           - float.
        cost_non_elective_bed_day_gbp       - float.
        cost_residential_day_gbp            - float.
        n_patients_care_home                - np.array.
        n_patients_not_care_home            - np.array.
        n_patients_care_home_over70         - np.array.
        n_patients_not_care_home_over70     - np.array.
        n_patients_care_home_not_over70     - np.array.
        n_patients_not_care_home_not_over70 - np.array.
    """

    # Calculate survival and hazard up to and including this year:
    time_max_post_discharge_year = 50

    # ----- QALYs -----
    qaly_age_coeff = 0.0002587
    qaly_age2_coeff = 0.0000332
    qaly_sex_coeff = 0.0212126

    # ----- From the Excel FrontSheet -----
    # File: Excel NHCT v7.4
    #   perc = percentage
    #   GBP = GB pounds
    # Inputs column 2:
    discount_factor_QALYs_perc = 3.50       # %
    discount_factor_costs_perc = 3.50       # %
    wtp_qaly_gpb = 20000                    # £
    # Inputs column 3:
    cost_ae_gbp = 170.46                    # £
    cost_elective_bed_day_gbp = 443.80      # £
    cost_non_elective_bed_day_gbp = 532.56  # £
    cost_residential_day_gbp = 102.71       # £

    # ----- Discharge destinations: -----
    # From the Excel NHCT v7.4 "Discharge_Dest" sheet.
    # Number of people "n" in each category.
    # mRS 0, 1, 2, 3, 4, 5
    n_patients_care_home = np.array([1, 3, 3, 32, 109, 26])
    n_Home = np.array([120, 276, 269, 158, 77, 10])
    n_Somewhere_else = np.array([3, 5, 10, 25, 39, 4])
    n_Transfer_inpatient = np.array([0, 2, 4, 3, 3, 0])
    n_Transfer_community_team = np.array([2, 17, 41, 95, 7, 0])
    n_Transfer_community_team_not_SSNAP = np.array([0, 2, 0, 2, 0, 0])
    n_Transfer_inpatient_not_SSNAP = np.array([0, 0, 1, 2, 4, 1])

    # Get a list of the number of people not in a care home,
    # one value per mRS like in the lists above.
    n_patients_not_care_home = np.sum([
        n_Home,
        n_Somewhere_else,
        n_Transfer_inpatient,
        n_Transfer_community_team,
        n_Transfer_community_team_not_SSNAP,
        n_Transfer_inpatient_not_SSNAP
        ], axis=0
        )
    # Only store the "care home" and "not care home" values
    # and discard the separate non-care-home destination values.

    # Separate conditions for mRS>=3.
    # Numbers for age > 70...
    n_patients_care_home_over70 = np.array([28, 94, 24])
    n_patients_not_care_home_over70 = np.array([245, 190, 34])
    # ... and for age <= 70.
    n_patients_care_home_not_over70 = np.array([4, 15, 2])
    n_patients_not_care_home_not_over70 = np.array([72, 49, 7])

    # Place into a dictionary:
    return dict(
        time_max_post_discharge_year=time_max_post_discharge_year,
        qaly_age_coeff=qaly_age_coeff,
        qaly_age2_coeff=qaly_age2_coeff,
        qaly_sex_coeff=qaly_sex_coeff,
        discount_factor_QALYs_perc=discount_factor_QALYs_perc,
        discount_factor_costs_perc=discount_factor_costs_perc,
        wtp_qaly_gpb=wtp_qaly_gpb,
        cost_ae_gbp=cost_ae_gbp,
        cost_elective_bed_day_gbp=cost_elective_bed_day_gbp,
        cost_non_elective_bed_day_gbp=cost_non_elective_bed_day_gbp,
        cost_residential_day_gbp=cost_residential_day_gbp,
        n_patients_care_home=n_patients_care_home,
        n_patients_not_care_home=n_patients_not_care_home,
        n_patients_care_home_over70=n_patients_care_home_over70,
        n_patients_not_care_home_over70=n_patients_not_care_home_over70,
        n_patients_care_home_not_over70=n_patients_care_home_not_over70,
        n_patients_not_care_home_not_over70=n_patients_not_care_home_not_over70
    )


def make_fixed_params_mrs_model(fixed_params):
    """
    Calculates and collects parameters for the separate-mRS model.

    Inputs:
    -------
    fixed_params - dict. Contains the discharge destination numbers
                   that are used here to calculate percentage of
                   patients going to a care home.

    Returns:
    --------
    dict. The dictionary of fixed parameters. Keys:
        perc_care_home_all_ages       - float.
        perc_care_home_over70         - float.
        perc_care_home_not_over70     - float.
        utility_list                  - list.
        lg_coeffs                     - np.array.
        lg_mean_ages                  - np.array.
        gz_coeffs                     - np.array.
        gz_gamma                      - float.
        gz_mean_age                   - float.
        ae_coeffs                     - np.array.
        ae_mRS                        - np.array.
        nel_coeffs                    - np.array.
        nel_mRS                       - np.array.
        el_coeffs                     - np.array.
        el_mRS                        - np.array.
    """
    # ----- Discharge destinations -----

    # Combine these counts into percentage rates:
    perc_care_home_all_ages = (
        fixed_params['n_patients_care_home'] /
        (fixed_params['n_patients_care_home'] +
         fixed_params['n_patients_not_care_home'])
        )

    perc_care_home_over70 = np.append(
        perc_care_home_all_ages[:3],
        fixed_params['n_patients_care_home_over70'] /
        fixed_params['n_patients_not_care_home_over70']
        )
    perc_care_home_not_over70 = np.append(
        perc_care_home_all_ages[:3],
        fixed_params['n_patients_care_home_not_over70'] /
        fixed_params['n_patients_not_care_home_not_over70']
        )

    # From Excel "Coefficients" sheet, "QALYs" table
    # File: Excel NHCT v7.4
    # QALYs:
    # for mRS    = [0,    1,    2,    3,    4,    5   ]
    utility_list = [0.95, 0.93, 0.83, 0.62, 0.42, 0.11]

    # ----- Mortality -----
    # From the Excel "stata_year1" sheet
    # File: Excel NHCT v7.4

    # -- Year one: --
    # lg for logistic
    # regression coefficents
    lg_coeffs = np.array([
        -4.235428,    # constant
        0.0663151,    # adjage (adjusted age)
        0.2757525,    # male
        0.0,          # mRS0 - needed for python zero-indexing later
        0.9538716,    # mrs1
        1.259014,     # mrs2
        2.477345,     # mrs3
        3.739959,     # mrs4
        4.944438      # mrs5
        ])
    # Note: There are related numbers in Excel NHCT v7.4 Coefficients sheet
    # that go unused in the R script. These are labelled:
    # Coef. | Std. Err. | z | P>z | [95% Conf. Interval] x 2
    # The values in the list used here are from the Coef. column.

    # mrs1, mrs2, mrs3, mrs4, mrs5
    lg_mean_ages = np.array([
        67.09161,     # mrs0
        67.98058,     # mrs1
        72.85753,     # mrs2
        76.48837,     # mrs3
        78.56029,     # mrs4
        80.91837      # mrs5
        ])

    # -- Year >1 --
    # gz for Gompertz
    # From the Excel "stata_extrap" sheet, results set 2 (cells J11:J25).
    # File: Excel NHCT v7.4
    gz_coeffs = np.array([
        -9.317337,     # constant
        0.0533406,     # adjage (adjusted age)
        0.0002026,     # adjage^2
        0.0873645,     # male
        0.0,           # mRS0 - needed for python zero-indexing later
        -0.004399,     # mrs1 * adjage
        -0.001777,     # mrs2 * adjage
        0.0058719,     # mrs3 * adjage
        0.0033625,     # mrs4 * adjage
        -0.124118,     # mrs5 * adjage
        0.0,           # mRS0 - needed for python zero-indexing later
        0.1234595,     # mrs1
        0.537909,      # mrs2
        1.01626,       # mrs3
        1.302992,      # mrs4
        2.513704       # mrs5
        ])
    gz_gamma = 0.0001832
    # Note: There are related numbers in Excel NHCT v7.4 Coefficients sheet
    # that go unused in the R script. These are labelled:
    # Obs | Mean | Std. | Dev. | Min | Max
    # The values in the list used here are from the Mean column.

    # From Excel "Coefficients" sheet, cell C16 in NHCT v7.4.
    gz_mean_age = 73.7324

    # ----- Resource use -----
    # From the Excel NHCT v7.4 "Resource_Use" sheet.
    # A&E
    ae_coeffs = np.array([
        -0.0691459,     # constant
        -0.0049821,     # age
        0.0791412,      # sex
        0.8167258       # gamma
        ])
    ae_mRS = np.array([
        0,              # mrs0
        0.1534326,      # mrs1
        -0.1125641,     # mrs2
        -0.4519718,     # mrs3
        -0.3794212,     # mrs4
        -0.3181142      # mrs5
        ])

    # Non-elective bed days:
    nel_coeffs = np.array([
        -1.334001,      # constant
        -0.0248403,     # age
        0.2965771,      # sex
        0.1616682       # gamma
        ])
    nel_mRS = np.array([
        0,              # mrs0
        -0.0467482,     # mrs1
        -0.4899248,     # mrs2
        -1.152301,      # mrs3
        -1.298562,      # mrs4
        -0.6243521      # mrs5
        ])

    # Elective bed days:
    el_coeffs = np.array([
        1.273549,       # constant
        -0.0081321,     # age
        -0.0773456,     # sex
        0.8516285       # gamma
        ])
    el_mRS = np.array([
        0,              # mrs0
        -0.7987555,     # mrs1
        -0.8763055,     # mrs2
        -0.1613053,     # mrs3
        0.1961125,      # mrs4
        -1.72541        # mrs5
        ])

    # Put all of this into a dictionary:
    return dict(
        perc_care_home_all_ages=perc_care_home_all_ages,
        perc_care_home_over70=perc_care_home_over70,
        perc_care_home_not_over70=perc_care_home_not_over70,
        utility_list=utility_list,
        lg_coeffs=lg_coeffs,
        lg_mean_ages=lg_mean_ages,
        gz_coeffs=gz_coeffs,
        gz_gamma=gz_gamma,
        gz_mean_age=gz_mean_age,
        ae_coeffs=ae_coeffs,
        ae_mRS=ae_mRS,
        nel_coeffs=nel_coeffs,
        nel_mRS=nel_mRS,
        el_coeffs=el_coeffs,
        el_mRS=el_mRS
    )


def make_fixed_params_dicho_model(fixed_params):
    """
    Calculates and collects parameters for the dichotomous model.

    Inputs:
    -------
    fixed_params - dict. Contains the discharge destination numbers
                   that are used here to calculate percentage of
                   patients going to a care home.

    Returns:
    --------
    dict. The dictionary of fixed parameters. Keys:
        perc_care_home_all_ages   - float.
        perc_care_home_over70     - float.
        perc_care_home_not_over70 - float.
        utility_list              - list.
        lg_coeffs                 - np.array.
        lg_mean_ages              - np.array.
        gz_coeffs                 - np.array.
        gz_gamma                  - float.
        gz_mean_age               - float.
        ae_coeffs                 - np.array.
        ae_mRS                    - np.array.
        nel_coeffs                - np.array.
        nel_mRS                   - np.array.
        el_coeffs                 - np.array.
        el_mRS                    - np.array.
    """
    # ----- Discharge destinations -----

    # Combine these counts into percentage rates:
    perc_care_home_all_ages_independent = (
        np.sum(fixed_params['n_patients_care_home'][:3]) /
        np.sum(fixed_params['n_patients_care_home'][:3] +
               fixed_params['n_patients_not_care_home'][:3])
        )
    perc_care_home_all_ages_dependent = (
        np.sum(fixed_params['n_patients_care_home'][3:]) /
        np.sum(fixed_params['n_patients_care_home'][3:] +
               fixed_params['n_patients_not_care_home'][3:])
        )
    perc_care_home_all_ages = np.array(
        [perc_care_home_all_ages_independent] * 3 +
        [perc_care_home_all_ages_dependent] * 3
    )

    perc_care_home_over70_dependent = (
        np.sum(fixed_params['n_patients_care_home_over70']) /
        (np.sum(fixed_params['n_patients_care_home_over70']) +
         np.sum(fixed_params['n_patients_not_care_home_over70']))
        )

    perc_care_home_not_over70_dependent = (
        np.sum(fixed_params['n_patients_care_home_not_over70']) /
        (np.sum(fixed_params['n_patients_care_home_not_over70']) +
         np.sum(fixed_params['n_patients_not_care_home_not_over70']))
        )

    perc_care_home_over70 = np.append(
        perc_care_home_all_ages[:3],
        [perc_care_home_over70_dependent] * 3
        )
    perc_care_home_not_over70 = np.append(
        perc_care_home_all_ages[:3],
        [perc_care_home_not_over70_dependent] * 3
        )

    # From Excel "Coefficients" sheet, "QALYs" table
    # File: Excel NHCT v7.4
    # QALYs:
    # for [Independent, Dependent]
    utility_list = [0.86, 0.86, 0.86, 0.43, 0.43, 0.43]

    # ----- Mortality -----
    # From the Excel "stata_year1" sheet
    # File: Excel NHCT v7.4

    # -- Year one: --
    # lg for logistic
    # regression coefficents
    lg_coeffs = np.array([
        -3.172763,    # constant
        0.068276,     # adjage (adjusted age)
        0.1344353,    # male
        0.0,          # mRS0 - needed for python zero-indexing later
        0.0,          # mrs1
        0.0,          # mrs2
        2.202913,     # mrs3
        2.202913,     # mrs4
        2.202913      # mrs5
        ])
    # Note: There are related numbers in Excel NHCT v7.4 Coefficients sheet
    # that go unused in the R script. These are labelled:
    # Coef. | Std. Err. | z | P>z | [95% Conf. Interval] x 2
    # The values in the list used here are from the Coef. column.

    lg_mean_ages = np.array([
        70.06683,  # Independent
        70.06683,  # Independent
        70.06683,  # Independent
        78.21609,  # Dependent
        78.21609,  # Dependent
        78.21609   # Dependent
        ])

    # -- Year >1 --
    # gz for Gompertz
    # From the Excel "stata_extrap" sheet, results set 4 (cells J31:J45).
    # File: Excel NHCT v7.4
    gz_coeffs = np.array([
        -8.720822,     # constant
        -0.013376,     # adjage (adjusted age)
        0.0006541,     # adjage^2
        0.0944971,     # male
        0.0,           # mRS0 - needed for python zero-indexing later
        0.0,           # mrs1 * adjage
        0.0,           # mrs2 * adjage
        0.0027337,     # mrs3 * adjage
        0.0027337,     # mrs4 * adjage
        0.0027337,     # mrs5 * adjage
        0.0,           # mRS0 - needed for python zero-indexing later
        0.0,           # mrs1
        0.0,           # mrs2
        0.3514468,     # mrs3
        0.3514468,     # mrs4
        0.3514468      # mrs5
        ])
    gz_gamma = 0.000164
    # Note: There are related numbers in Excel NHCT v7.4 Coefficients sheet
    # that go unused in the R script. These are labelled:
    # Obs | Mean | Std. | Dev. | Min | Max
    # The values in the list used here are from the Mean column.

    # From Excel "Coefficients" sheet, cell C16 in NHCT v7.4.
    gz_mean_age = 73.7324

    # ----- Resource use -----
    # From the Excel NHCT v7.4 "Resource_Use" sheet.
    # A&E
    ae_coeffs = np.array([
        -0.0642146,     # constant
        -0.0049919,     # age
        0.0857713,      # sex
        0.8160829       # gamma
        ])
    ae_mRS = np.array([
        0.0,            # Independent
        0.0,            # Independent
        0.0,            # Independent
        -0.4333583,     # Dependent
        -0.4333583,     # Dependent
        -0.4333583,     # Dependent
        ])

    # Non-elective bed days:
    nel_coeffs = np.array([
        -1.611057,      # constant
        -0.0249443,     # age
        0.293765,       # sex
        0.1624848       # gamma
        ])
    nel_mRS = np.array([
        0.0,            # Independent
        0.0,            # Independent
        0.0,            # Independent
        -0.9156318,     # Dependent
        -0.9156318,     # Dependent
        -0.9156318      # Dependent
        ])

    # Elective bed days:
    el_coeffs = np.array([
        0.5616489,      # constant
        -0.0071193,     # age
        -0.0930076,     # sex
        0.8694792       # gamma
        ])
    el_mRS = np.array([
        0.0,            # Independent
        0.0,            # Independent
        0.0,            # Independent
        0.6038344,      # Dependent
        0.6038344,      # Dependent
        0.6038344       # Dependent
        ])
    # Put all of this into a dictionary:
    return dict(
        perc_care_home_all_ages=perc_care_home_all_ages,
        perc_care_home_over70=perc_care_home_over70,
        perc_care_home_not_over70=perc_care_home_not_over70,
        utility_list=utility_list,
        lg_coeffs=lg_coeffs,
        lg_mean_ages=lg_mean_ages,
        gz_coeffs=gz_coeffs,
        gz_gamma=gz_gamma,
        gz_mean_age=gz_mean_age,
        ae_coeffs=ae_coeffs,
        ae_mRS=ae_mRS,
        nel_coeffs=nel_coeffs,
        nel_mRS=nel_mRS,
        el_coeffs=el_coeffs,
        el_mRS=el_mRS
    )
