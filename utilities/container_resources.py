"""
This contains everything in the Resources and Costs section.
"""
import streamlit as st
import numpy as np
import pandas as pd
import utilities.latex_equations


def main(
        A_E_count_list, NEL_count_list, EL_count_list, care_years_list,
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost,
        table_discounted_cost,
        variables_dict
        ):
    
    st.write('### Resource use')
    with st.expander('Details: Resource use'):
        write_details_resource_use(variables_dict)
    write_table_resource_use(
        A_E_count_list, NEL_count_list,
        EL_count_list, care_years_list
        )
    
    st.write('### Discounted Cost of Resource use')
    with st.expander('Details: Discounted resource use'):
        write_details_discounted_resource_use(variables_dict)
    write_table_discounted_resource_use(
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        )

    st.write('### Discounted total costs by change in outcome')
    write_table_discounted_change(
        table_discounted_cost, total_discounted_cost)


def write_table_resource_use(
        A_E_count_list, NEL_count_list,
        EL_count_list, care_years_list
        ):
    headings = [
        # 'mRS',
        'A&E',
        'NEL Days',
        'EL Days',
        'Average time in residential care (years)'
    ]
    # Combine lists into a grid
    table = np.transpose(np.vstack((
        A_E_count_list,
        NEL_count_list,
        EL_count_list,
        care_years_list
        )))
    # Change into a dataframe with column headings:
    df_table = pd.DataFrame(table, columns=headings)

    # Write to streamlit:
    st.table(df_table.style.format("{:4.2f}"))


def write_table_discounted_resource_use(
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        ):
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
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        )))

    # # Round pounds up (away from zero if -ve) to match Excel.
    # table_round = np.zeros_like(table)
    # inds_neg = np.where(table < 0.0)
    # inds_pos = np.where(table >= 0.0)
    # table_round[inds_neg] = np.floor(table[inds_neg])
    # table_round[inds_pos] = np.ceil(table[inds_pos])
    table_round = table

    # Change into a dataframe with column headings:
    df_table = pd.DataFrame(table_round, columns=headings)

    # Write to streamlit:
    st.table(df_table.style.format('£{:.0f}'))


def write_table_discounted_change(
        table_discounted_cost, total_discounted_cost):
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
    st.markdown(''.join([
        'The change in total costs between two mRS scores ',
        'is simply the difference between their total cost values ',
        'in the table above. For example, the change from ',
        'an outcome of mRS=1 to mRS=2 gives a difference of: ',
    ]))
    st.latex(''.join([
        r'''\begin{equation*}''',
        f'£{total_discounted_cost[1]:.2f}-',
        f'£{total_discounted_cost[2]:.2f}=',
        f'£{total_discounted_cost[2]-total_discounted_cost[1]:.2f}',
        r'''\end{equation*}'''
    ]))
    st.table(df_table.style.applymap(color_negative_red))
    st.write('Changes in outcome from column value to row value.')
    st.write('Numbers in red are increased costs to the NHS, ',
             'numbers in black represent savings to the NHS')


def write_details_resource_use(vd):
    tabs = st.tabs([
        'A&E Admissions',
        'Non-elective bed days',
        'Elective bed days',
        'Time in residential care'
        ])

    with tabs[0]:
        # A&E admissions:
        write_details_ae_admissions(vd)
    with tabs[1]:
        # A&E admissions:
        write_details_nel_admissions(vd)
    with tabs[2]:
        # A&E admissions:
        write_details_el_admissions(vd)
    with tabs[3]:
        # A&E admissions:
        write_details_time_in_care(vd)


def write_details_ae_admissions(vd):

    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the number of ',
        'admissions to A&E.'
        ]))
    ae_coeff_cols = st.columns(2)
    with ae_coeff_cols[0]:
        markdown_ae_coeffs = utilities.latex_equations.table_ae_coeffs(vd)
        st.markdown(markdown_ae_coeffs)

    with ae_coeff_cols[1]:
        markdown_ae_mrs_coeffs = utilities.latex_equations.\
            table_ae_mrs_coeffs(vd)
        st.markdown(markdown_ae_mrs_coeffs)

    # ----- Formula -----
    st.markdown(''.join([
        'The A&E admissions model is a Weibull distribution. ',
        'The number of admissions over $\mathrm{yrs}$, ',
        'a number of years, is given by: '
        ]))
    latex_ae_count_generic = utilities.latex_equations.\
        ae_count_generic()
    st.latex(latex_ae_count_generic)

    # # ----- Lambda function -----
    # st.markdown('with Lambda function $\Lambda_\mathrm{AE}$: ')
    # latex_ae_lambda_generic = utilities.latex_equations.\
    #     ae_lambda_generic()
    # st.latex(latex_ae_lambda_generic)

    # ----- linear predictor -----
    st.markdown('and with linear predictor: ')
    latex_ae_lp_generic = utilities.latex_equations.\
        ae_lp_generic()
    st.latex(latex_ae_lp_generic)
    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (e.g. age, sex, and mRS).'
        ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    latex_ae_lp = utilities.latex_equations.ae_lp(vd)
    st.latex(latex_ae_lp)
    st.write('$^{*}$ This value is 0 for female patients and 1 for male.')

    # # ----- Calculation for Lambda -----
    # st.markdown('The Lambda function:')
    # latex_ae_lambda = utilities.latex_equations.ae_lambda(vd)
    # st.latex(latex_ae_lambda)

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    latex_median_survival_display = utilities.latex_equations.\
        median_survival_display(vd)
    st.latex(latex_median_survival_display)

    # ----- Calculation for count -----
    st.markdown('The final count:')
    latex_ae_count = utilities.latex_equations.ae_count(vd)
    st.latex(latex_ae_count)


def write_details_nel_admissions(vd):

    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the number of ',
        'non-elective bed days.'
        ]))
    nel_coeff_cols = st.columns(2)
    with nel_coeff_cols[0]:
        markdown_nel_coeffs = utilities.latex_equations.table_nel_coeffs(vd)
        st.markdown(markdown_nel_coeffs)

    with nel_coeff_cols[1]:
        markdown_nel_mrs_coeffs = utilities.latex_equations.\
            table_nel_mrs_coeffs(vd)
        st.markdown(markdown_nel_mrs_coeffs)

    # ----- Formula -----
    st.markdown(''.join([
        'The non-elective bed day model is a log-logistic distribution. ',
        'The number of bed days over $\mathrm{yrs}$, ',
        'a number of years, is given by: '
        ]))
    latex_nel_bed_days_generic = utilities.latex_equations.\
        nel_bed_days_generic()
    st.latex(latex_nel_bed_days_generic)

    # # ----- Lambda function -----
    # st.markdown('with Lambda function $\Lambda_\mathrm{AE}$: ')
    # latex_ae_lambda_generic = utilities.latex_equations.\
    #     ae_lambda_generic()
    # st.latex(latex_ae_lambda_generic)

    # ----- linear predictor -----
    st.markdown('and with linear predictor: ')
    latex_nel_lp_generic = utilities.latex_equations.\
        nel_lp_generic()
    st.latex(latex_nel_lp_generic)
    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (e.g. age, sex, and mRS).'
        ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    latex_nel_lp = utilities.latex_equations.nel_lp(vd)
    st.latex(latex_nel_lp)
    st.write('$^{*}$ This value is 0 for female patients and 1 for male.')

    # # ----- Calculation for Lambda -----
    # st.markdown('The Lambda function:')
    # latex_ae_lambda = utilities.latex_equations.ae_lambda(vd)
    # st.latex(latex_ae_lambda)

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    latex_median_survival_display = utilities.latex_equations.\
        median_survival_display(vd)
    st.latex(latex_median_survival_display)

    # ----- Calculation for count -----
    st.markdown('The final count:')
    latex_nel_bed_days = utilities.latex_equations.nel_bed_days(vd)
    st.latex(latex_nel_bed_days)


def write_details_el_admissions(vd):

    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the number of ',
        'elective bed days.'
        ]))
    el_coeff_cols = st.columns(2)
    with el_coeff_cols[0]:
        markdown_el_coeffs = utilities.latex_equations.table_el_coeffs(vd)
        st.markdown(markdown_el_coeffs)

    with el_coeff_cols[1]:
        markdown_el_mrs_coeffs = utilities.latex_equations.\
            table_el_mrs_coeffs(vd)
        st.markdown(markdown_el_mrs_coeffs)

    # ----- Formula -----
    st.markdown(''.join([
        'The elective bed day model is a log-logistic distribution. ',
        'The number of bed days over $\mathrm{yrs}$, ',
        'a number of years, is given by: '
        ]))
    latex_el_bed_days_generic = utilities.latex_equations.\
        el_bed_days_generic()
    st.latex(latex_el_bed_days_generic)

    # # ----- Lambda function -----
    # st.markdown('with Lambda function $\Lambda_\mathrm{AE}$: ')
    # latex_ae_lambda_generic = utilities.latex_equations.\
    #     ae_lambda_generic()
    # st.latex(latex_ae_lambda_generic)

    # ----- linear predictor -----
    st.markdown('and with linear predictor: ')
    latex_el_lp_generic = utilities.latex_equations.\
        el_lp_generic()
    st.latex(latex_el_lp_generic)
    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (e.g. age, sex, and mRS).'
        ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    latex_el_lp = utilities.latex_equations.el_lp(vd)
    st.latex(latex_el_lp)
    st.write('$^{*}$ This value is 0 for female patients and 1 for male.')

    # # ----- Calculation for Lambda -----
    # st.markdown('The Lambda function:')
    # latex_ae_lambda = utilities.latex_equations.ae_lambda(vd)
    # st.latex(latex_ae_lambda)

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    latex_median_survival_display = utilities.latex_equations.\
        median_survival_display(vd)
    st.latex(latex_median_survival_display)

    # ----- Calculation for count -----
    st.markdown('The final count:')
    latex_el_bed_days = utilities.latex_equations.el_bed_days(vd)
    st.latex(latex_el_bed_days)


def write_details_time_in_care(vd):

    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the number of ',
        'days spent in residential care. ',
        'They represent the proportion of people in each mRS ',
        'category who are discharged into a residential care home, ',
        'and different proportions are considered for patients over ',
        'the age of 70.'
        ]))
    markdown_tic_coeffs = utilities.latex_equations.\
        table_time_in_care_coeffs(vd)
    st.markdown(markdown_tic_coeffs)

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
    latex_tic_generic = utilities.latex_equations.\
        tic_generic()
    st.latex(latex_tic_generic)
    st.markdown(''.join([
        'for $c$, the value from the table.'
    ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details.'
        ]))

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    latex_median_survival_display = utilities.latex_equations.\
        median_survival_display(vd)
    st.latex(latex_median_survival_display)

    # ----- Calculation for linear predictor -----
    st.markdown('The number of years spent in residential care is:')
    latex_tic = utilities.latex_equations.tic(vd)
    st.latex(latex_tic)


def write_details_discounted_resource_use(vd):
    tabs = st.tabs([
        'A&E Admissions',
        'Non-elective bed days',
        'Elective bed days',
        'Time in residential care'
        ])

    with tabs[0]:
        # A&E admissions:
        write_details_discounted_ae(vd)
    with tabs[1]:
        # A&E admissions:
        write_details_discounted_nel(vd)
    with tabs[2]:
        # A&E admissions:
        write_details_discounted_el(vd)
    with tabs[3]:
        # A&E admissions:
        write_details_discounted_care(vd)


def write_details_discounted_ae(vd):
    pass 

def write_details_discounted_nel(vd):
    pass 

def write_details_discounted_el(vd):
    pass 

def write_details_discounted_care(vd):
    pass