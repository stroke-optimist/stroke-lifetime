"""
This contains everything in the QALYs section.
"""
import streamlit as st
import numpy as np
import pandas as pd

# For writing formulae in the "Details" sections:
import utilities_lifetime.latex_equations as eqn


def main(
        df: pd.DataFrame,
        mrs_input: int,
        fixed_params: dict,
        qalys_table: np.array,
        model_input_str: str
        ):
    """
    Main function for drawing everything under the "QALYs" tab.

    This setup of picking bits out of dictionaries is inherited
    from the older version of this container that had all results
    stored in separate variable names. Maybe one day I'll tidy this.

    Inputs:
    -------
    df              - pd.DataFrame. Contains all of the calculated
                      results for all mRS scores.
    mrs_input       - int. The mRS score to highlight in areas
                      that only show one score's results.
    fixed_params    - dict. Contains fixed parameters independent
                      of the model results.
    qalys_table     - np.array. The table of discounted QALYs by
                      change in outcome, ready to print.
    model_input_str - str. Whether this is the separate "mRS" or
                      "Dichotomous" model. Used to change the
                      formatting in the app for model type.
    """

    # Pick bits out of the dataframe for all mRS:

    survival_median_years = df['survival_median_years']
    survival_lower_quartile_years = df['survival_lower_quartile_years']
    survival_upper_quartile_years = df['survival_upper_quartile_years']
    life_expectancy = df['life_expectancy']

    all_survival_times = np.array([
        survival_median_years,
        survival_lower_quartile_years,
        survival_upper_quartile_years,
        life_expectancy
    ]).T
    qalys_all_mrs = df['qalys_total'].tolist()

    # Get the results for just the selected mRS:
    results_dict = df.loc[mrs_input].to_dict()
    variables_dict = dict(**results_dict, **fixed_params)

    # Pick bits out of the results for just the selected mRS:
    survival_times = [
        variables_dict['survival_median_years'],
        variables_dict['survival_lower_quartile_years'],
        variables_dict['survival_upper_quartile_years'],
        variables_dict['life_expectancy']
    ]
    # qalys = variables_dict['qalys']
    qalys_by_year = variables_dict['qalys_by_year']
    raw_qalys_by_year = variables_dict['raw_qalys_by_year']

    # Discounted QALYS
    # +-------------------+
    # | v Details:        |
    # +-------------------+
    # | v Example:        |
    # +-------------------+
    #
    #     +---------+-----------------+-----------+-----------+-------+
    #     | Utility | Median survival | Lower IQR | Upper IQR | QALYs |
    # +---+---------+-----------------+-----------+-----------+-------+
    # | 0 |         |                 |           |           |       |
    # | 1 |         |                 |           |           |       |
    # | 2 |         |                 |           |           |       |
    # | 3 |         |                 |           |           |       |
    # | 4 |         |                 |           |           |       |
    # | 5 |         |                 |           |           |       |
    # +---+---------+-----------------+-----------+-----------+-------+
    #
    st.markdown('### Discounted QALYs')
    with st.expander('Details: Discounted QALYs'):
        write_details_discounted_qalys(variables_dict, model_input_str)
    with st.expander('Example: Discounted QALYs'):
        write_example_discounted_qalys(
            qalys_by_year, raw_qalys_by_year, variables_dict, survival_times[0]
            )

    # Check which model we're using and draw a bespoke table:
    if model_input_str == 'mRS':
        write_table_discounted_qalys(
            all_survival_times, qalys_all_mrs, fixed_params)
    else:
        write_table_discounted_qalys_dicho(
            all_survival_times, qalys_all_mrs, fixed_params)

    # Discounted QALYS by change in outcome
    #     +---+---+---+---+---+---+
    #     | 0 | 1 | 2 | 3 | 4 | 5 |
    # +---+---+---+---+---+---+---+
    # | 0 |   |   |   |   |   |   |
    # | 1 |   |   |   |   |   |   |
    # | 2 |   |   |   |   |   |   |
    # | 3 |   |   |   |   |   |   |
    # | 4 |   |   |   |   |   |   |
    # | 5 |   |   |   |   |   |   |
    # +---+---+---+---+---+---+---+
    #
    st.markdown('### Discounted QALYs by change in outcome')
    st.markdown(''.join([
        'The change in QALYs between two mRS scores ',
        'is simply the difference between their QALY values ',
        'in the table above.'
    ]))
    # Check which model we're using and draw a bespoke table:
    if model_input_str == 'mRS':
        st.markdown(''.join([
            'For example, the change from ',
            'an outcome of mRS=1 to mRS=2 gives a difference of:'
        ]))
        diff_str = (
            f'{qalys_all_mrs[1]:.2f}-{qalys_all_mrs[2]:.2f}=' +
            f'{qalys_all_mrs[1]-qalys_all_mrs[2]:.2f}'
            )
        st.latex(diff_str)
        write_table_discounted_qalys_outcome(qalys_table)
        st.caption('Change in outcome from column value to row value.')
    else:
        write_table_discounted_qalys_outcome_dicho(qalys_all_mrs)

    # Notes from the Excel FrontSheet:
    st.write('Stroke. 2018;49:965-971')
    st.write(
        'Note: QALY shorfalls compared to lifetime QALYs can be ',
        'weighted 85%-95% shortfall valued @ 120%, ',
        '95% shortfall valued @ 170%')
    st.write('**** NICE health technology evaluations: the manual (Jan 2022)')


def write_table_discounted_qalys(survival_times, qalys, fixed_params):
    """
    Write a table of the discounted QALY values for each mRS. It also
    includes the median and IQR survival times.

    Use the non-removable index column as the mRS column.

    Inputs:
    survival_times - array or list. Array of six lists, one for each
                     mRS, where each contains [median, IQR lower, IQR
                     upper, life expectancy].
    qalys          - array or list. Contains six floats, one for each
                     mRS, that are the QALY values.
    """
    qaly_table = []
    for i, mRS in enumerate(range(6)):
        qaly_table.append([
            fixed_params['utility_list'][i],
            # mRS,
            survival_times[i][0],
            survival_times[i][1],
            survival_times[i][2],
            qalys[i]
        ])

    # Convert to a pandas dataframe so we can label the columns:
    qaly_table = np.array(qaly_table)
    df_table = pd.DataFrame(
        qaly_table,
        columns=(
            'Utility',
            # 'mRS',
            'Median survival (years)',
            'Lower IQR (years)',
            'Upper IQR (years)',
            'QALYs'
            )
    )
    format_dict = {
        'Utility': '{:4.2f}',
        # 'mRS': '{:1.0f}',
        'Median survival (years)': '{:4.2f}',
        'Lower IQR (years)': '{:4.2f}',
        'Upper IQR (years)': '{:4.2f}',
        'QALYs': '{:4.2f}'
        }
    # Write to streamlit:
    st.table(df_table.style.format(format_dict))


def write_table_discounted_qalys_dicho(survival_times, qalys, fixed_params):
    """
    Write a table of the discounted QALY values for each mRS. It also
    includes the median and IQR survival times.

    This is a variation of the individual mRS table with rows and
    column headers re-labelled.

    Inputs:
    survival_times - array or list. Array of six lists, one for each
                     mRS, where each contains [median, IQR lower, IQR
                     upper, life expectancy].
    qalys          - array or list. Contains six floats, one for each
                     mRS, that are the QALY values.
    """
    # New column for the outcome names:
    outcome_labels = ['Independent', 'Dependent']
    qaly_table = []
    # Only keep the first and final rows of the individual mRS table:
    for i in [0, -1]:
        qaly_table.append([
            outcome_labels[i],
            fixed_params['utility_list'][i],
            # mRS,
            survival_times[i][0],
            survival_times[i][1],
            survival_times[i][2],
            qalys[i]
        ])

    # Convert to a pandas dataframe so we can label the columns:
    qaly_table = np.array(qaly_table, dtype=object)
    df_table = pd.DataFrame(
        qaly_table,
        columns=(
            ' ',  # Outcome label header
            'Utility',
            # 'mRS',
            'Median survival (years)',
            'Lower IQR (years)',
            'Upper IQR (years)',
            'QALYs'
            )
    )
    format_dict = {
        'Utility': '{:4.2f}',
        # 'mRS': '{:1.0f}',
        'Median survival (years)': '{:4.2f}',
        'Lower IQR (years)': '{:4.2f}',
        'Upper IQR (years)': '{:4.2f}',
        'QALYs': '{:4.2f}'
        }
    # Write to streamlit:
    st.table(df_table.style.format(format_dict))


def write_table_discounted_qalys_outcome(qaly_table):
    """
    Write a table of the change in discounted QALY values for each
    change in mRS outcome.

    Use the non-removable index column as the mRS column. Don't label
    the columns so the default 0, 1, ... 5 can be mRS as well.

    Inputs:
    qaly_table - 2D array. 6 rows by 6 columns. Each cell contains the
                 difference in QALYs between mRS=column value and mRS=
                 row value.
    """
    # Change the table values to formatted strings:
    table = []
    for row in range(6):
        row_vals = []
        for column in range(6):
            val = qaly_table[row][column]
            if type(val) == np.float64:
                # Format the number as a nice string:
                row_vals.append(f'{val:4.2f}')
            elif column == row:
                # Show only a dash on the right-hand-side of the cell.
                # Use unicode character to add extra spaces and so
                # fake the right-alignment.
                row_vals.append(3*'\U00002002' + '-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table)

    df_table = pd.DataFrame(table)

    # Write to streamlit:
    st.table(df_table)


def write_table_discounted_qalys_outcome_dicho(qalys):
    """
    Write a table of the change in discounted QALY values for each
    change in mRS outcome.

    Inputs:
    qalys      - array or list. Contains six floats, one for each
                 mRS, that are the QALY values. This is just used for
                 printing the example val1 - val2 = diff in table.
    """
    outcome_labels = ['Independent', 'Dependent']
    # When there's no change,
    # show only a dash on the right-hand-side of the cell.
    # Use unicode character to add extra spaces and so
    # fake the right-alignment.
    table = [
        ['Independent', 3*'\U00002002' + '-', ''],
        ['Dependent', f'{qalys[0]-qalys[-1]:4.2f}', 3*'\U00002002' + '-']
        ]
    table = np.array(table, dtype=object)

    df_table = pd.DataFrame(table, columns=[''] + outcome_labels)

    # Write to streamlit:
    st.write('Change in outcome from column value to row value.')
    st.table(df_table)


def write_details_discounted_qalys(vd, model_input_str):
    """
    Write method for calculating QALYs from utility, years,
    patient details, and fixed coefficients.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ----- Tables of coefficients -----
    st.markdown(''.join([
        'The following constants are used to calculate QALYs. ',
        ]))
    cols_coeffs = st.columns(2)
    with cols_coeffs[0]:
        # QALY coefficients.
        st.markdown(eqn.table_qaly_coeffs(vd))
    with cols_coeffs[1]:
        # Mean age coefficients.
        # Check the model type to decide which table to show.
        if model_input_str == 'mRS':
            st.markdown(eqn.table_mean_age_coeffs(vd))
        else:
            st.markdown(eqn.table_mean_age_coeffs_dicho(vd))

    # ----- Raw qalys -----
    st.markdown(''.join([
        'The raw QALYs $Q_{y,\mathrm{raw}}$ are calculated ',
        'for each year $y$ until ',
        'the end of the median survival years $m$. ',
        'Each raw QALY is calculated as: '
    ]))
    st.latex(eqn.discounted_raw_qalys_generic())
    st.markdown(''.join([
        'where $u$ is the utility score for the patient mRS, ',
        r'''$\beta_Q$''', ' are constants and ',
        '$X$ are values of the patient details (i.e. age, ',
        'age in each year $y$, and sex). '
        'If $Q_{\mathrm{raw}}$ is greater than 1, the value is reset to ',
        '$Q_{\mathrm{raw}}=1$.'
    ]))

    # ----- Discounted QALY per year -----
    st.markdown(''.join([
        'These are converted to discounted QALYs $Q_{y}$ ',
        'for each year $y$ using the following: '
    ]))
    st.latex(eqn.discounted_qalys_generic())
    st.markdown(''.join([
        'where $d$ is the discount factor of ',
        f'{vd["discount_factor_QALYs_perc"]:.2f}' + '%. '
        'For the final year, $y>m$ and so the QALY is multiplied by ',
        'a scale factor to only include the fraction of the year ',
        'when the patient was alive.'
    ]))

    # ----- Sum for total QALY -----
    st.markdown(''.join([
        'The $Q_y$ values are summed up over all $y$ ',
        'to give the final QALY value, $Q$:'
    ]))
    st.latex(eqn.discounted_qalys_total_generic())


def write_example_discounted_qalys(
        qalys_by_year,
        raw_qalys_by_year,
        vd,
        med_survival_yrs
        ):
    """
    Write example for calculating QALYs from utility, years,
    patient details, and fixed coefficients.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details '
        'or change depending on the year chosen.'
        ]))

    cols = st.columns([0.3, 0.7])
    with cols[0]:
        # ----- Write table with the values -----
        st.markdown(eqn.build_table_str_qalys(
            raw_qalys_by_year, qalys_by_year, np.sum(qalys_by_year)
            ))

    with cols[1]:
        # ----- Example calculation of discounted resource -----
        # st.markdown(''.join([
        #     'Example of the calculation of the discounted QALY ',
        #     'for a chosen year:'
        # ]))

        # ----- Input number of years -----
        # Give this slider a key or streamlit throws warnings
        # about multiple identical sliders.
        if len(qalys_by_year) > 1:
            time_input_yr = st.slider(
                'Choose number of years for this example',
                min_value=1,
                max_value=len(qalys_by_year),
                value=1,
                key='TimeforQALYS'
                )
        else:
            st.markdown(
                '''
                The median survival is below one year so only the
                first year can be shown.

                Number of years for this example: 1
                '''
                )
            time_input_yr = 1
            
        for year in [time_input_yr]:
            st.latex(eqn.discounted_raw_qalys(
                    vd,
                    year,
                    raw_qalys_by_year[year-1]
                    ))
            st.markdown(''.join([
                '$^{*}$ This value is 0 for female patients ',
                'and 1 for male.'
                ]))

            # Check if this is the final year.
            # If it is, add an extra string to explain that we reduce
            # the value to match the fraction of the year that is lived in.
            if year > med_survival_yrs:
                if med_survival_yrs >= 1:
                    # Get just the bit after the decimal place:
                    frac = med_survival_yrs % int(med_survival_yrs)
                else:
                    # Can't take modulus of zero, so just use the
                    # existing number which is 0.something:
                    frac = med_survival_yrs
                if frac == 0.0:
                    frac = 1.0
            else:
                frac = 0.0

            st.latex(eqn.discounted_qalys(
                vd,
                raw_qalys_by_year[year-1],
                year,
                qalys_by_year[year-1],
                frac
                ))
            if frac > 0:
                # If the user-selected year is the final year,
                # write an extra line to explain the scale factor.
                st.markdown(''.join([
                    f'The scale factor of {frac:.2f} accounts for this ',
                    'being the final year of survival. ',
                    'It comes from the median survival of ',
                    f'{med_survival_yrs:.2f} years minus {year-1} years, ',
                    'the number of years survived in full.'
                ]))


def write_details_discounted_qalys_v7(vd):
    """
    Write method and example for calculating QALYs from utility, years,
    and the discount factor.

    This was used for an older version of the Excel spreadsheet,
    NHCT v7.0. It currently goes unused in the Streamlit app.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    st.markdown(''.join([
        'The discounted QALYs, $Q$, are calculated as: '
    ]))
    # ----- Formula ----
    st.latex(eqn.discounted_qalys_generic())
    st.markdown(''.join([
        'where $u$ is the utility score for this mRS, ',
        '$d$ is the discount factor of ',
        f'{vd["discount_factor_QALYs_perc"]:.2f}' + '%, ',
        'and $\mathrm{yrs}$ is the median survival years for this patient.'
    ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the table below depending ',
        'on the patient details.'
        ]))

    # ----- Calculate QALYs -----
    st.markdown('For the median survival years: ')
    st.latex(eqn.discounted_qalys(vd))
