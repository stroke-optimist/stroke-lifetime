"""
Define constants that will be used in multiple places throughout the
script but that only need to be defined once.
"""
import streamlit as st
import numpy as np


def page_setup():
    # The following options set up the display in the tab in your
    # browser.
    # Set page to widescreen must be first call to st.
    st.set_page_config(
        page_title='Stroke risk model',
        page_icon=':hospital:',
        # layout='wide'
        )


# Calculate survival and risk up to and including this year:
time_max_post_discharge_yr = 50

# Colour scheme to match Excel risk chart:
colours_excel = [
    '#ffc000',   # mRS 0
    '#ed7d31',   # mRS 1
    '#a5a5a5',   # mRS 2
    '#b4c7e7',   # mRS 3
    '#5b9bd5',   # mRS 4
    '#70ad47',   # mRS 5
]


# ----- From the Excel FrontSheet -----
# File: Excel NHCT v7.0
#   perc = percentage
#   GBP = GB pounds
# Inputs column 2:
discount_factor_QALYs_perc = 3.50
discount_factor_costs_perc = 3.50
WTP_QALY_gpb = 20000
# Inputs column 3:
cost_ae_gbp = 170.46
cost_elective_bed_day_gbp = 443.80
cost_non_elective_bed_day_gbp = 532.56
cost_residential_day_gbp = 102.71
# QALYs:
# for mRS = [0,    1,    2,    3,    4,    5   ]
utilities = [0.95, 0.93, 0.83, 0.62, 0.42, 0.11]


# ----- From the R script -----
# (test.harnes.R, received 17/NOV/2022 from Peter McMeekin)
#   lg = logistic (mortality model)
#   gz = Gompertz (mortality model)

# regression coefficents
# const, adjage, male, mrs1, mrs2, mrs3, mrs4, mrs5
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
# Note: There are related numbers in Excel NHCT v7.0 Coefficients sheet
# that go unused in the R script. These are labelled:
# Coef. | Std. | Err. | z | P>z | [95% Conf. Interval]
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

# const, adjage, adjage2, male,
# mrs1*adjage, mrs2*adjage, mrs3*adjage, mrs4*adjage, mrs5*adjage,
# mrs1, mrs2, mrs3, mrs4, mrs5
gz_coeffs = np.array([
    -9.066997,     # constant
    0.0072893,     # adjage (adjusted age)
    0.0005922,     # adjage^2
    0.1782744,     # male
    0.0,           # mRS0 - needed for python zero-indexing later
    -0.0203561,    # mrs1 * adjage
    -0.0258925,    # mrs2 * adjage
    -0.0256267,    # mrs3 * adjage
    -0.0312966,    # mrs4 * adjage
    -0.138619,     # mrs5 * adjage
    0.0,           # mRS0 - needed for python zero-indexing later
    0.2300774,     # mrs1
    0.4113532,     # mrs2
    0.6846613,     # mrs3
    0.8534541,     # mrs4
    1.776318       # mrs5
    ])
# Note: There are related numbers in Excel NHCT v7.0 Coefficients sheet
# that go unused in the R script. These are labelled:
# Obs | Mean | Std. | Dev. | Min | Max
# The values in the list used here are from the Mean column.

gz_gamma = 0.0002183

# mrs1, mrs2, mrs3, mrs4, mrs5
gz_mean_age = 73.7324


# A&E
# A&E coefficients:
A_E_coeffs = np.array([
    -0.0691459,     # constant
    -0.0049821,     # age
    0.0791412,      # sex
    0.8167258       # gamma
    ])
A_E_mRS = np.array([
    0,              # mrs0
    0.1534326,      # mrs1
    -0.1125641,     # mrs2
    -0.4519718,     # mrs3
    -0.3794212,     # mrs4
    -0.3181142      # mrs5
    ])

# Non-elective bed days:
NEL_coeffs = np.array([
    -1.334001,      # constant
    -0.0248403,     # age
    0.2965771,      # sex
    0.1616682       # gamma
    ])
NEL_mRS = np.array([
    0,              # mrs0
    -0.0467482,     # mrs1
    -0.4899248,     # mrs2
    -1.152301,      # mrs3
    -1.298562,      # mrs4
    -0.6243521      # mrs5
    ])

# Elective bed days:
EL_coeffs = np.array([
    1.273549,       # constant
    -0.0081321,     # age
    -0.0773456,     # sex
    0.8516285       # gamma
    ])
EL_mRS = np.array([
    0,              # mrs0
    -0.7987555,     # mrs1
    -0.8763055,     # mrs2
    -0.1613053,     # mrs3
    0.1961125,      # mrs4
    -1.72541        # mrs5
    ])


# ----- Discharge destinations: -----
# Number of people "n" in each category.
# mRS 0, 1, 2, 3, 4, 5
n_care_home = np.array([1, 3, 3, 32, 109, 26])
n_Home = np.array([120, 276, 269, 158, 77, 10])
n_Somewhere_else = np.array([3, 5, 10, 25, 39, 4])
n_Transfer_inpatient = np.array([0, 2, 4, 3, 3, 0])
n_Transfer_community_team = np.array([2, 17, 41, 95, 7, 0])
n_Transfer_community_team_not_SSNAP = np.array([0, 2, 0, 2, 0, 0])
n_Transfer_inpatient_not_SSNAP = np.array([0, 0, 1, 2, 4, 1])

n_not_care_home = np.sum([
    n_Home,
    n_Somewhere_else,
    n_Transfer_inpatient,
    n_Transfer_community_team,
    n_Transfer_community_team_not_SSNAP,
    n_Transfer_inpatient_not_SSNAP
    ], axis=0
    )

# Combine these counts into percentage rates:
perc_care_home_all_ages = n_care_home / (n_care_home + n_not_care_home)

# Separate conditions for mRS>=3.
# Numbers for age > 70...
n_care_home_over70 = np.array([28, 94, 24])
n_not_care_home_over70 = np.array([245, 190, 34])
# ... and for age <= 70.
n_care_home_not_over70 = np.array([4, 15, 2])
n_not_care_home_not_over70 = np.array([72, 49, 7])

# Combine into percentage rates:
perc_care_home_over70 = np.append(
    perc_care_home_all_ages[:3],
    n_care_home_over70/n_not_care_home_over70
    )
perc_care_home_not_over70 = np.append(
    perc_care_home_all_ages[:3],
    n_care_home_not_over70/n_not_care_home_not_over70
    )
