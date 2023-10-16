"""
This contains everything in the Resources and Costs section.
"""
import streamlit as st
import numpy as np
import pandas as pd

# For writing formulae in the "Details" sections:
import utilities_lifetime.latex_equations as eqn


def main(
        df: pd.DataFrame,
        mRS_input: int,
        fixed_params: dict,
        table_discounted_cost: np.array,
        model_input_str: str
        ):
    """
    Main function for drawing everything under the "Resources" tab.

    This setup of picking bits out of dictionaries is inherited
    from the older version of this container that had all results
    stored in separate variable names. Maybe one day I'll tidy this.

    Inputs:
    -------
    df                    - pd.DataFrame. Contains all of the calculated
                            results for all mRS scores.
    mrs_input             - int. The mRS score to highlight in areas
                            that only show one score's results.
    fixed_params          - dict. Contains fixed parameters independent
                            of the model results.
    table_discounted_cost - np.array. The table of discounted cost by
                            change in outcome, ready to print.
    model_type_used       - str. Whether this is the separate "mRS" or
                            "Dichotomous" model. Used to change the
                            formatting in the app for model type.
    """
    # Pick bits out of the dataframe for all mRS:
    ae_count_list = df['ae_count']
    nel_count_list = df['nel_count']
    el_count_list = df['el_count']
    care_years_list = df['care_years']
    ae_discounted_cost = df['ae_discounted_cost']
    nel_discounted_cost = df['nel_discounted_cost']
    el_discounted_cost = df['el_discounted_cost']
    care_years_discounted_cost = df['care_years_discounted_cost']
    total_discounted_cost = df['total_discounted_cost'].tolist()

    # Get the results for just the selected mRS:
    results_dict = df.loc[mRS_input].to_dict()
    variables_dict = dict(**results_dict, **fixed_params)

    # Resource use
    # |__Mortality__ |__QALYs__ |__Resources__ |__Cost__
    #
    # +-------------------+
    # | v Details:        |
    # +-------------------+
    # | v Example:        |
    # +-------------------+

    st.write('### Resource use')
    st.markdown(''.join([
        'Acute hospital attendances are modelled using ',
        'a Weibull distribution. ',
        'Non-elective bed days and elective bed days are both ',
        'modelled using a log-logistic distribution.'
        ]))

    tabs = st.tabs([
        'A&E Admissions',
        'Non-elective bed days',
        'Elective bed days',
        'Time in residential care'
        ])

    with tabs[0]:
        # A&E admissions:
        with st.expander('Details: A&E Resource use'):
            write_details_ae_admissions(variables_dict, model_input_str)
        with st.expander('Example: A&E Resource use'):
            write_example_ae_admissions(variables_dict)
    with tabs[1]:
        # NEL admissions:
        with st.expander('Details: NEL Resource use'):
            write_details_nel_admissions(variables_dict, model_input_str)
        with st.expander('Example: NEL Resource use'):
            write_example_nel_admissions(variables_dict)
    with tabs[2]:
        # EL admissions:
        with st.expander('Details: EL Resource use'):
            write_details_el_admissions(variables_dict, model_input_str)
        with st.expander('Example: EL Resource use'):
            write_example_el_admissions(variables_dict)
    with tabs[3]:
        # Time in care:
        with st.expander('Details: Time in care Resource use'):
            write_details_time_in_care(variables_dict, model_input_str)
        with st.expander('Example: Time in care Resource use'):
            write_example_time_in_care(variables_dict)

    # Table:
    #     +-----+----------+---------+--------------+
    #     | A&E | NEL days | EL days | Time in care |
    # +---+-----+----------+---------+--------------+
    # | 0 |     |          |         |              |
    # | 1 |     |          |         |              |
    # | 2 |     |          |         |              |
    # | 3 |     |          |         |              |
    # | 4 |     |          |         |              |
    # | 5 |     |          |         |              |
    # +---+-----+----------+---------+--------------+
    #
    # Check which model we're using and draw a table:
    if model_input_str == 'mRS':
        write_table_resource_use(
            ae_count_list, nel_count_list, el_count_list, care_years_list)
    else:
        write_table_resource_use_dicho(
            ae_count_list, nel_count_list, el_count_list, care_years_list)

    # Discounted cost of resource use
    # +-------------------+
    # | v Details:        |
    # +-------------------+
    # | v Example:        |
    # +-------------------+
    #
    #     +-----+----------+---------+--------------+------------+
    #     | A&E | NEL days | EL days | Time in care | Total cost |
    # +---+-----+----------+---------+--------------+------------+
    # | 0 |     |          |         |              |            |
    # | 1 |     |          |         |              |            |
    # | 2 |     |          |         |              |            |
    # | 3 |     |          |         |              |            |
    # | 4 |     |          |         |              |            |
    # | 5 |     |          |         |              |            |
    # +---+-----+----------+---------+--------------+------------+
    #
    st.write('### Discounted Cost of Resource use')
    with st.expander('Details: Discounted resource use'):
        write_details_discounted_resource_use(variables_dict)
    with st.expander('Example: Discounted resource use'):
        write_example_discounted_resource_use(variables_dict)

    # Check which model we're using and draw a table:
    if model_input_str == 'mRS':
        write_table_discounted_resource_use(
            ae_discounted_cost,
            nel_discounted_cost,
            el_discounted_cost,
            care_years_discounted_cost,
            total_discounted_cost
            )
    else:
        write_table_discounted_resource_use_dicho(
            ae_discounted_cost,
            nel_discounted_cost,
            el_discounted_cost,
            care_years_discounted_cost,
            total_discounted_cost
            )

    # Discounted total costs by change in outcome
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
    st.write('### Discounted total costs by change in outcome')

    st.markdown(''.join([
        'The change in total costs between two mRS scores ',
        'is simply the difference between their total cost values ',
        'in the table above.'
    ]))
    # Check which model we're using and draw a bespoke table:
    if model_input_str == 'mRS':
        st.markdown(''.join([
            'For example, the change from ',
            'an outcome of mRS=1 to mRS=2 gives a difference of: ',
        ]))
        st.latex(''.join([
            r'''\begin{equation*}''',
            f'£{total_discounted_cost[2]:.2f}-',
            f'£{total_discounted_cost[1]:.2f}=',
            f'£{total_discounted_cost[2]-total_discounted_cost[1]:.2f}',
            r'''\end{equation*}'''
        ]))
        write_table_discounted_change(table_discounted_cost)
    else:
        write_table_discounted_change_dicho(total_discounted_cost)


def write_table_resource_use(
        ae_count_list, nel_count_list,
        el_count_list, care_years_list
        ):
    """
    Write a table of the resource use for each mRS.

    Use the non-removable index column as the mRS column.

    Inputs:
    Each of these is a list of six floats, one for each mRS.
    ae_count_list  - Number of A&E admissions.
    nel_count_list  - Number of non-elective bed days.
    el_count_list   - Number of elective bed days.
    care_years_list - Number of years in residential care.
    """
    headings = [
        # 'mRS',
        'A&E',
        'NEL Days',
        'EL Days',
        'Average time in residential care (years)'
    ]
    # Combine lists into a grid
    table = np.transpose(np.vstack((
        ae_count_list,
        nel_count_list,
        el_count_list,
        care_years_list
        )))
    # Change into a dataframe with column headings:
    df_table = pd.DataFrame(table, columns=headings)

    # Write to streamlit:
    st.table(df_table.style.format("{:4.2f}"))


def write_table_resource_use_dicho(
        ae_count_list, nel_count_list,
        el_count_list, care_years_list
        ):
    """
    Write a table of the resource use for each outcome.

    This uses the first and final rows of the individual mRS table
    with re-labelled rows and column headings.

    Inputs:
    Each of these is a list of six floats, one for each mRS.
    ae_count_list  - Number of A&E admissions.
    nel_count_list  - Number of non-elective bed days.
    el_count_list   - Number of elective bed days.
    care_years_list - Number of years in residential care.
    """
    headings = [
        '',  # Heading for outcome column
        'A&E',
        'NEL Days',
        'EL Days',
        'Average time in residential care (years)'
    ]
    # Combine lists into a grid
    table = np.transpose(np.vstack((
        ae_count_list,
        nel_count_list,
        el_count_list,
        care_years_list
        )))
    # Only keep the first and last rows:
    table = table[[0, -1], :]
    # Add a new column for the outcome labels:
    table = np.hstack((
        np.array(['Independent', 'Dependent'], dtype=object).reshape(2, 1),
        table
    ))
    # Change into a dataframe with column headings:
    df_table = pd.DataFrame(table, columns=headings)

    # Make a format dictionary for precision printing:
    format_dict = {
        headings[1]: '{:4.2f}',
        headings[2]: '{:4.2f}',
        headings[3]: '{:4.2f}',
        headings[4]: '{:4.2f}',
    }
    # Write to streamlit:
    st.table(df_table.style.format(format_dict))


def write_table_discounted_resource_use(
        ae_discounted_cost,
        nel_discounted_cost,
        el_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        ):
    """
    Write a table of the discounted resource use for each mRS.

    Use the non-removable index column as the mRS column.

    Inputs:
    Each of these is a np.array of six values, one for each mRS.
                                  cost x discounted number of...
    ae_discounted_cost        -  ... A&E admissions.
    nel_discounted_cost        -  ... non-elective bed days.
    el_discounted_cost         -  ... elective bed days.
    care_years_discounted_cost -  ... years in care.
    total_discounted_cost      -  sum of these four ^ values.
    """
    headings = [
        # 'mRS',
        'A&E',
        'NEL Days',
        'EL Days',
        'Cost of residental care',
        'Total cost'
    ]

    # Combine lists into a grid
    table = np.transpose(np.vstack((
        ae_discounted_cost,
        nel_discounted_cost,
        el_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        )))

    # Ready to delete (15th Dec 2022):
    # # Round pounds up (away from zero if -ve) to match Excel.
    # table_round = np.zeros_like(table)
    # inds_neg = np.where(table < 0.0)
    # inds_pos = np.where(table >= 0.0)
    # table_round[inds_neg] = np.floor(table[inds_neg])
    # table_round[inds_pos] = np.ceil(table[inds_pos])
    # table_round = table

    # Change into a dataframe with column headings:
    df_table = pd.DataFrame(table, columns=headings)

    # Write to streamlit:
    st.table(df_table.style.format('£{:.0f}'))


def write_table_discounted_resource_use_dicho(
        ae_discounted_cost,
        nel_discounted_cost,
        el_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        ):
    """
    Write a table of the discounted resource use for each outcome.

    This uses the first and final rows of the individual mRS table
    with re-labelled rows and column headings.

    Inputs:
    Each of these is a np.array of six values, one for each mRS.
                                  cost x discounted number of...
    ae_discounted_cost        -  ... A&E admissions.
    nel_discounted_cost        -  ... non-elective bed days.
    el_discounted_cost         -  ... elective bed days.
    care_years_discounted_cost -  ... years in care.
    total_discounted_cost      -  sum of these four ^ values.
    """
    headings = [
        '',  # Heading for outcome label column
        'A&E',
        'NEL Days',
        'EL Days',
        'Cost of residental care',
        'Total cost'
    ]

    # Combine lists into a grid
    table = np.transpose(np.vstack((
        ae_discounted_cost,
        nel_discounted_cost,
        el_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        )))

    # Only keep the first and final rows:
    table = table[[0, -1], :]
    # Add a first column with the outcome labels:
    table = np.hstack((
        np.array(['Independent', 'Dependent'], dtype=object).reshape(2, 1),
        table
    ))

    # Change into a dataframe with column headings:
    df_table = pd.DataFrame(table, columns=headings)

    # Make a format dictionary for precision printing:
    format_dict = {
        headings[1]: '£{:.0f}',
        headings[2]: '£{:.0f}',
        headings[3]: '£{:.0f}',
        headings[4]: '£{:.0f}',
        headings[5]: '£{:.0f}',
    }
    # Write to streamlit:
    st.table(df_table.style.format(format_dict))


def write_table_discounted_change(table_discounted_cost):
    """
    Write a table of the discounted resource use for each mRS.

    Use the non-removable index column as the mRS column.
    Use the unicode characters to add empty space before a '-'
    to fake the right-alignment.

    Inputs:
    Each of these is a np.array of six values, one for each mRS.
                                  cost x discounted number of...
    ae_discounted_cost        -  ... A&E admissions.
    nel_discounted_cost        -  ... non-elective bed days.
    el_discounted_cost         -  ... elective bed days.
    care_years_discounted_cost -  ... years in care.
    total_discounted_cost      -  sum of these four ^ values.
    """
    # Use this function to colour values in the table:
    def color_negative_red(val):
        colour = None
        if len(val) > 0:
            if val[0] == '-' and val[-1] != '-':
                # Also check final character to check it's not a
                # string of one character, '-'.
                colour = 'red'
        return f'color: {colour}'

    # Change the table values to formatted strings:
    table = []
    for row in range(6):
        row_vals = []
        for column in range(6):
            diff_val = table_discounted_cost[row][column]
            if type(diff_val) == np.float64:
                # Either add a minus sign or a bit of empty space.
                sign = '-' if diff_val < 0 else '\U00002004'
                # Ready to delete (15th Dec 2022):
                # Round pounds up (away from zero if -ve) to match Excel.
                # diff = sign+f'£{np.ceil(np.abs(diff_val)):.0f}'
                diff = sign+f'£{np.abs(diff_val):.0f}'
                # Add extra spaces at the start for right-alignment
                # cheat:
                extra_spaces = 10 - len(diff)
                diff = (
                    diff.split('£')[0] + '£' +
                    extra_spaces * '\U00002002' +
                    diff.split('£')[1]
                )
                row_vals.append(diff)
            elif column == row:
                # Show only a dash on the right-hand-side of the cell.
                row_vals.append(9*'\U00002002' + '-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table)

    df_table = pd.DataFrame(table)

    # Write to streamlit:
    st.table(df_table.style.applymap(color_negative_red))
    st.caption(''.join([
        'Changes in outcome from column value to row value. ',
        'Numbers in red are increased costs to the NHS, ',
        'numbers in black represent savings to the NHS'
        ]))


def write_table_discounted_change_dicho(total_discounted_cost):
    """
    Write a table of the discounted resource use for each outcome.

    This uses the first and final rows of the individual mRS table
    with re-labelled rows and column headings.
    Use the unicode characters to add empty space before a '-'
    to fake the right-alignment.

    Inputs:
    Each of these is a np.array of six values, one for each mRS.
                                  cost x discounted number of...
    ae_discounted_cost        -  ... A&E admissions.
    nel_discounted_cost        -  ... non-elective bed days.
    el_discounted_cost         -  ... elective bed days.
    care_years_discounted_cost -  ... years in care.
    total_discounted_cost      -  sum of these four ^ values.
    """
    # Use this function to colour values in the table:
    def color_negative_red(val):
        colour = None
        if len(val) > 0:
            if val[0] == '-' and val[-1] != '-':
                # Also check final character to check it's not a
                # string of one character, '-'.
                colour = 'red'
        return f'color: {colour}'

    diff_val = total_discounted_cost[-1]-total_discounted_cost[0]
    # Either add a minus sign or a bit of empty space.
    sign = '-' if diff_val < 0 else '\U00002004'
    # Ready to delete (15th Dec 2022):
    # Round pounds up (away from zero if -ve) to match Excel.
    # diff = sign+f'£{np.ceil(np.abs(diff_val)):.0f}'
    diff = sign+f'£{np.abs(diff_val):.0f}'
    # Add extra spaces at the start for right-alignment
    # cheat:
    extra_spaces = 10 - len(diff)
    diff = (
        diff.split('£')[0] + '£' +
        extra_spaces * '\U00002002' +
        diff.split('£')[1]
    )

    table = [
        ['Independent', 9*'\U00002002' + '-', ''],
        ['Dependent', diff, 9*'\U00002002' + '-']
    ]
    table = np.array(table)

    df_table = pd.DataFrame(table, columns=['', 'Independent', 'Dependent'])

    # Write to streamlit:
    st.table(df_table.style.applymap(color_negative_red))
    st.caption(''.join([
        'Changes in outcome from column value to row value. ',
        'Numbers in red are increased costs to the NHS, ',
        'numbers in black represent savings to the NHS'
        ]))


def write_details_ae_admissions(vd, model_input_str):
    """
    Write method for calculating number of A&E admissions.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the number of ',
        'admissions to A&E.'
        ]))
    ae_coeff_cols = st.columns(2)
    with ae_coeff_cols[0]:
        st.markdown(eqn.table_ae_coeffs(vd))

    with ae_coeff_cols[1]:
        # Check which model we're using and draw a bespoke table:
        if model_input_str == 'mRS':
            st.markdown(eqn.table_ae_mrs_coeffs(vd))
        else:
            st.markdown(eqn.table_ae_mrs_coeffs_dicho(vd))

    # ----- Formula -----
    st.markdown(''.join([
        'The A&E admissions model is a Weibull distribution. ',
        'The number of admissions over $\mathrm{yrs}$, ',
        'a number of years, is given by: '
        ]))
    latex_ae_count_generic = eqn.\
        ae_count_generic()
    st.latex(latex_ae_count_generic)

    # ----- linear predictor -----
    st.markdown('and with linear predictor: ')
    st.latex(eqn.ae_lp_generic())
    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (e.g. age, sex, and mRS).'
        ]))


def write_example_ae_admissions(vd):
    """
    Write example for calculating number of A&E admissions.

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
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    st.latex(eqn.ae_lp(vd))
    st.write('$^{*}$ This value is 0 for female patients and 1 for male.')

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    st.latex(eqn.median_survival_display(vd))

    # ----- Calculation for count -----
    st.markdown('The final count:')
    st.latex(eqn.ae_count(vd))


def write_details_nel_admissions(vd, model_input_str):
    """
    Write method for calculating number of NEL bed-days.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the number of ',
        'non-elective bed days.'
        ]))
    nel_coeff_cols = st.columns(2)
    with nel_coeff_cols[0]:
        st.markdown(eqn.table_nel_coeffs(vd))

    with nel_coeff_cols[1]:
        # Check which model we're using and draw a bespoke table:
        if model_input_str == 'mRS':
            st.markdown(eqn.table_nel_mrs_coeffs(vd))
        else:
            st.markdown(eqn.table_nel_mrs_coeffs_dicho(vd))

    # ----- Formula -----
    st.markdown(''.join([
        'The non-elective bed day model is a log-logistic distribution. ',
        'The number of bed days over $\mathrm{yrs}$, ',
        'a number of years, is given by: '
        ]))
    st.latex(eqn.nel_bed_days_generic())

    # ----- linear predictor -----
    st.markdown('and with linear predictor: ')
    st.latex(eqn.nel_lp_generic())
    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (e.g. age, sex, and mRS).'
        ]))


def write_example_nel_admissions(vd):
    """
    Write example for calculating number of NEL bed-days.

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
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    st.latex(eqn.nel_lp(vd))
    st.write('$^{*}$ This value is 0 for female patients and 1 for male.')

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    st.latex(eqn.median_survival_display(vd))

    # ----- Calculation for count -----
    st.markdown('The final count:')
    st.latex(eqn.nel_bed_days(vd))


def write_details_el_admissions(vd, model_input_str):
    """
    Write method for calculating number of EL bed-days.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the number of ',
        'elective bed days.'
        ]))
    el_coeff_cols = st.columns(2)
    with el_coeff_cols[0]:
        st.markdown(eqn.table_el_coeffs(vd))

    with el_coeff_cols[1]:
        # Check which model we're using and draw a bespoke table:
        if model_input_str == 'mRS':
            st.markdown(eqn.table_el_mrs_coeffs(vd))
        else:
            st.markdown(eqn.table_el_mrs_coeffs_dicho(vd))

    # ----- Formula -----
    st.markdown(''.join([
        'The elective bed day model is a log-logistic distribution. ',
        'The number of bed days over $\mathrm{yrs}$, ',
        'a number of years, is given by: '
        ]))
    st.latex(eqn.el_bed_days_generic())

    # ----- linear predictor -----
    st.markdown('and with linear predictor: ')
    st.latex(eqn.el_lp_generic())
    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (e.g. age, sex, and mRS).'
        ]))


def write_example_el_admissions(vd):
    """
    Write example for calculating number of EL bed-days.

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
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    st.latex(eqn.el_lp(vd))
    st.write('$^{*}$ This value is 0 for female patients and 1 for male.')

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    st.latex(eqn.median_survival_display(vd))

    # ----- Calculation for count -----
    st.markdown('The final count:')
    st.latex(eqn.el_bed_days(vd))


def write_details_time_in_care(vd, model_input_str):
    """
    Write method for calculating time spent in care.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the number of ',
        'days spent in residential care. ',
        'They represent the proportion of people in each mRS ',
        'category who are discharged into a residential care home, ',
        'and different proportions are considered for patients over ',
        'the age of 70.'
        ]))

    # Check which model we're using and draw a bespoke table:
    if model_input_str == 'mRS':
        st.markdown(eqn.table_time_in_care_coeffs(vd))
    else:
        st.markdown(eqn.table_time_in_care_coeffs_dicho(vd))

    st.markdown(''.join([
        'The number of years spent in residential care ',
        'is estimated from the mRS score at discharge ',
        'and the average number of years spent in care ',
        'for people with that mRS score. ',
        'The average time spent in care per mRS is 95\% of ',
        'each value in the table above. '
    ]))
    # ----- Formula -----
    st.markdown('The number of years spent in residential care is: ')
    st.latex(eqn.tic_generic())
    st.markdown(''.join([
        'for $c$, the value from the table.'
    ]))


def write_example_time_in_care(vd):
    """
    Write example for calculating time spent in care.

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
        'on the patient details.'
        ]))

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    st.latex(eqn.median_survival_display(vd))

    # ----- Calculation for linear predictor -----
    st.markdown('The number of years spent in residential care is:')
    st.latex(eqn.tic(vd))


def write_details_discounted_resource_use(vd):
    """
    Write method for calculating the discounted resource
    use and cost.

    The method is the same for all resources so the example code is
    in a function and used by all four resources.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ----- Formula for one year -----
    st.markdown(''.join([
        'The formulae used previously to find the number of ',
        'A&E admissions [Equation 14], non-elective bed days ',
        '[Equation 16], elective bed days [Equation 18], ',
        'and years in care [Equation 20] all count the ',
        'cumulative number of entries over several years. '
    ]))
    st.markdown(''.join([
        'To find $\mathrm{Count}_i$, ',
        'the number of entries in a given year $i$, ',
        'we use the same formulae to find the difference between ',
        'the entries up to and including year $i$ ',
        'and the entries up to and including year $i-1$:'
    ]))
    st.latex(eqn.count_yeari_generic())
    st.markdown(''.join([
        'For a resource that totals $\mathrm{Count}_i$ entries ',
        'in year $i$, the discounted resource $D_i$ is given as:'
    ]))
    st.latex(eqn.discounted_resource_generic(vd))

    # ----- Sum over all years -----
    st.markdown(''.join([
        'Then the discounted resource cost $D$ over all years '
        'is the sum of ',
        'these values up to the median survival year, $m$, ',
        'multiplied by a cost factor $c$: '
    ]))
    st.latex(eqn.discounted_resource_total_generic())

    # ----- Convert to costs -----
    st.markdown(''.join([
        'The following cost factors are used: '
    ]))
    cols_cost = st.columns(2)
    with cols_cost[0]:
        st.markdown(eqn.table_cost_factors_1(vd))
    with cols_cost[1]:
        st.markdown(eqn.table_cost_factors_2(vd))

    # ----- State where total costs column comes from -----
    st.markdown(''.join([
        'The "Total cost" column gives the sum of the discounted ',
        'resource costs across the four categories.'
    ]))


def write_example_discounted_resource_use(vd):
    """
    Write example for calculating the discounted resource
    use and cost.

    The method is the same for all resources so the example code is
    in a function and used by all four resources.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details ',
        'and values in ',
        'pink change with the chosen year.'
        ]))

    # ----- Show median survival years for this patient -----
    # vd["survival_meds_IQRs"][vd["mrs"], 0]
    st.markdown('For the median survival years: ')
    st.latex(eqn.median_survival_display(vd))

    # Tabs for each category:
    tabs = st.tabs([
        'A&E Admissions',
        'Non-elective bed days',
        'Elective bed days',
        'Time in residential care'
        ])

    with tabs[0]:
        # A&E admissions:
        caption_str = ''.join([
            '$\mathrm{Count}(\mathrm{yrs})$ is from Equation [16] ',
            'and "Discounted use" is from Equation [24].'
            ])
        write_details_discounted_resource(
            vd, "ae_counts_by_year", "discounted_list_ae",
            "cost_ae_gbp", "ae_discounted_cost", caption_str)
    with tabs[1]:
        # NEL bed days:
        caption_str = ''.join([
            '$\mathrm{Count}(\mathrm{yrs})$ is from Equation [18] ',
            'and "Discounted use" is from Equation [24].'
            ])
        write_details_discounted_resource(
            vd, "nel_counts_by_year", "discounted_list_nel",
            "cost_non_elective_bed_day_gbp", "nel_discounted_cost",
            caption_str)
    with tabs[2]:
        # EL bed days:
        caption_str = ''.join([
            '$\mathrm{Count}(\mathrm{yrs})$ is from Equation [20] ',
            'and "Discounted use" is from Equation [24].'
            ])
        write_details_discounted_resource(
            vd, "el_counts_by_year", "discounted_list_el",
            "cost_elective_bed_day_gbp", "el_discounted_cost",
            caption_str)
    with tabs[3]:
        # Time in care:
        caption_str = ''.join([
            '$\mathrm{Count}(\mathrm{yrs})$ is from Equation [22] ',
            'and "Discounted use" is from Equation [24].'
            ])
        write_details_discounted_resource(
            vd, "care_years_by_year", "discounted_list_care",
            "cost_residential_day_gbp", "care_years_discounted_cost",
            caption_str, care=1)


def write_details_discounted_resource(
        vd, count_str, discount_str, cost_str,
        discounted_cost_str, caption_str='', care=0):
    """
    Write example for calculating discounted resource use and cost for
    any of the four resources.

    The input variables pull out the relevant values from the dict.

    Inputs:
    vd                  - dict. vd is short for variables_dict from
                          main_calculations. It contains lots of
                          useful constants and variables.
    count_str           - str. Name of list of resource use in each
                          year.
    discount_str        - str. Name of list of discounted resouce use
                          in each year.
    cost_str            - str. Name of the cost conversion string
                          (fixed parameter).
    discounted_cost_str - str. Name of the calculated discounted cost
                          value.
    caption_str         - str. Optional caption to be written under
                          the big table with all the counts.
    care                - int. 1 if this is the residential care case,
                          else 0. If care=1, then include x365 in
                          formula to convert cost per day to cost per
                          year.
    """
    # Counts in each year:
    counts_i = vd[count_str]
    # Discounted use:
    discounted_i = vd[discount_str]
    # Cumulative counts:
    counts_yrs = np.cumsum(counts_i)
    # Total discounted use:
    discounted_sum = np.sum(discounted_i)

    cols = st.columns([0.45, 0.3])
    with cols[0]:
        # ----- Write table with the values -----
        st.markdown(eqn.build_table_str_resource_count(
                counts_yrs, counts_i, discounted_i, discounted_sum))
        st.caption(caption_str)

    with cols[-1]:
        # ----- Example calculation of discounted resource -----
        st.markdown(''.join([
            'Example of the calculation of the discounted resource ',
            'for a chosen year:'
        ]))

        # ----- Input number of years -----
        # Give this slider a key or streamlit throws warnings
        # about multiple identical sliders.
        time_input_yr = st.slider(
            'Choose number of years for this example',
            min_value=1,
            max_value=len(counts_i),
            value=2,
            key='TimeForDiscountTable' + cost_str
            )
        for year in [time_input_yr]:
            st.latex(eqn.discounted_resource(
                vd, counts_i[year-1], year, discounted_i[year-1]))

    # ----- Calculate discounted cost -----
    st.markdown(''.join([
        'The total discounted cost is then: '
    ]))
    st.latex(eqn.discounted_cost(
        vd, discounted_sum, cost_str, discounted_cost_str, care))
