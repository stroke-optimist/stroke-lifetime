"""
This contains everything in the QALYs section.
"""
import streamlit as st
import numpy as np
import pandas as pd

# For writing formulae in the "Details" sections:
import utilities_lifetime.latex_equations
# Import constants:
import utilities_lifetime.fixed_params


def main(
        survival_times,
        qalys,
        qaly_list,
        qaly_raw_list,
        qalys_table,
        variables_dict
        ):
    """

    qalys      - array or list. Contains six floats, one for each
                 mRS, that are the QALY values. This is just used for
                 printing the example val1 - val2 = diff in table.
    """
    st.markdown('### Discounted QALYs')
    with st.expander('Details: Discounted QALYs'):
        write_details_discounted_qalys(variables_dict)
    with st.expander('Example: Discounted QALYs'):
        write_example_discounted_qalys(
            qaly_list, qaly_raw_list, variables_dict, survival_times[:, 0]
            )

    # Check which model we're using and draw a bespoke table:
    if st.session_state['lifetime_model_type'] == 'mRS':
        write_table_discounted_qalys(survival_times, qalys)
    else:
        write_table_discounted_qalys_dicho(survival_times, qalys)

    st.markdown('### Discounted QALYs by change in outcome')
    st.markdown(''.join([
        'The change in QALYs between two mRS scores ',
        'is simply the difference between their QALY values ',
        'in the table above.'
    ]))
    # Check which model we're using and draw a bespoke table:
    if st.session_state['lifetime_model_type'] == 'mRS':
        st.markdown(''.join([
            'For example, the change from ',
            'an outcome of mRS=1 to mRS=2 gives a difference of:'
        ]))
        diff_str = f'{qalys[1]:.2f}-{qalys[2]:.2f}={qalys[1]-qalys[2]:.2f}'
        st.latex(diff_str)
        write_table_discounted_qalys_outcome(qalys_table)
        st.caption('Change in outcome from column value to row value.')
    else:
        write_table_discounted_qalys_outcome_dicho(qalys)

    # Notes from the Excel FrontSheet:
    st.write('Stroke. 2018;49:965-971')
    st.write(
        'Note: QALY shorfalls compared to lifetime QALYs can be ',
        'weighted 85%-95% shortfall valued @ 120%, ',
        '95% shortfall valued @ 170%')
    st.write('**** NICE health technology evaluations: the manual (Jan 2022)')


def write_table_discounted_qalys(survival_times, qalys):
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
            utilities_lifetime.fixed_params.utility_list[i],
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


def write_table_discounted_qalys_dicho(survival_times, qalys):
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
            utilities_lifetime.fixed_params.utility_list[i],
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


def write_details_discounted_qalys(vd):
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
        markdown_table_qaly_coeffs = utilities_lifetime.\
            latex_equations.table_qaly_coeffs(vd)
        st.markdown(markdown_table_qaly_coeffs)
    with cols_coeffs[1]:
        # Mean age coefficients.
        # Check the model type to decide which table to show.
        model_type_used = st.session_state['lifetime_model_type']
        if model_type_used == 'mRS':
            markdown_table_mean_age_coeffs = utilities_lifetime.\
                latex_equations.table_mean_age_coeffs(vd)
        else:
            markdown_table_mean_age_coeffs = utilities_lifetime.\
                latex_equations.table_mean_age_coeffs_dicho(vd)
        st.markdown(markdown_table_mean_age_coeffs)

    # ----- Raw qalys -----
    st.markdown(''.join([
        'The raw QALYs $Q_{y,\mathrm{raw}}$ are calculated ',
        'for each year $y$ until ',
        'the end of the median survival years $m$. ',
        'Each raw QALY is calculated as: '
    ]))
    latex_discounted_raw_qalys_generic = utilities_lifetime.latex_equations.\
        discounted_raw_qalys_generic()
    st.latex(latex_discounted_raw_qalys_generic)
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
    latex_discounted_qalys_generic = utilities_lifetime.latex_equations.\
        discounted_qalys_generic()
    st.latex(latex_discounted_qalys_generic)
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
    latex_discounted_qalys_total_generic = utilities_lifetime.\
        latex_equations.discounted_qalys_total_generic()
    st.latex(latex_discounted_qalys_total_generic)


def write_example_discounted_qalys(
        qaly_list,
        qaly_raw_list,
        vd,
        med_survival_yrs_list
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
        table_qalys = utilities_lifetime.latex_equations.\
            build_table_str_qalys(
                qaly_raw_list, qaly_list, np.sum(qaly_list)
                )
        st.markdown(table_qalys)
        # st.caption('caption_str')

    with cols[1]:
        # ----- Example calculation of discounted resource -----
        # st.markdown(''.join([
        #     'Example of the calculation of the discounted QALY ',
        #     'for a chosen year:'
        # ]))

        # ----- Input number of years -----
        # Give this slider a key or streamlit throws warnings
        # about multiple identical sliders.
        time_input_yr = st.slider(
            'Choose number of years for this example',
            min_value=1,
            max_value=len(qaly_list),
            value=2,
            key='TimeforQALYS'
            )
        for year in [time_input_yr]:
            latex_discounted_raw_qalys = utilities_lifetime.latex_equations.\
                discounted_raw_qalys(
                    vd,
                    year,
                    qaly_raw_list[year-1]
                    )
            st.latex(latex_discounted_raw_qalys)
            st.markdown(''.join([
                '$^{*}$ This value is 0 for female patients ',
                'and 1 for male.'
                ]))

            # Check if this is the final year.
            # If it is, add an extra string to explain that we reduce
            # the value to match the fraction of the year that is lived in.
            med_survival_yrs = med_survival_yrs_list[vd["mrs"]]
            if year > med_survival_yrs:
                # Get just the bit after the decimal place:
                frac = med_survival_yrs % int(med_survival_yrs)
                if frac == 0.0:
                    frac = 1.0
            else:
                frac = 0.0

            latex_discounted_qaly = \
                utilities_lifetime.latex_equations.discounted_qalys(
                    vd,
                    qaly_raw_list[year-1],
                    year,
                    qaly_list[year-1],
                    frac
                    )
            st.latex(latex_discounted_qaly)
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
    latex_discounted_qalys_generic = utilities_lifetime.latex_equations.\
        discounted_qalys_generic()
    st.latex(latex_discounted_qalys_generic)
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
    latex_discounted_qalys = utilities_lifetime.latex_equations.\
        discounted_qalys(vd)
    st.latex(latex_discounted_qalys)
