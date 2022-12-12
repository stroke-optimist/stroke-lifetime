"""
This contains everything in the QALYs section.
"""
import streamlit as st
import numpy as np
import pandas as pd
import utilities.latex_equations

from utilities.fixed_params import utility_list


def main(survival_times, qalys, qalys_table, variables_dict):
    st.markdown('### Discounted QALYs')
    with st.expander('Details: Discounted QALYs'):
        write_details_discounted_qalys(variables_dict)
    write_table_discounted_qalys(survival_times, qalys)

    st.markdown('### Discounted QALYs by change in outcome')
    write_table_discounted_qalys_outcome(qalys_table, qalys)


def write_table_discounted_qalys(survival_times, qalys):
    """
    Use the non-removable index column as the mRS column.
    """
    qaly_table = []
    for i, mRS in enumerate(range(6)):
        qaly_table.append([
            utility_list[i],
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


def write_table_discounted_qalys_outcome(qaly_table, qalys):

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
                row_vals.append(3*'\U00002002' + '-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table)

    df_table = pd.DataFrame(table)

    # Write to streamlit:
    st.markdown(''.join([
        'The change in QALYs between two mRS scores ',
        'is simply the difference between their QALY values ',
        'in the table above. For example, the change from ',
        'an outcome of mRS=1 to mRS=2 gives a difference of ',
        f'{qalys[1]:.2f}$-${qalys[2]:.2f}$=${qalys[1]-qalys[2]:.2f}.'
    ]))
    st.write('Change in outcome from column value to row value.')
    st.table(df_table)
    # Notes from the Excel FrontSheet:
    st.write('Stroke. 2018;49:965-971')
    st.write(
        'Note: QALY shorfalls compared to lifetime QALYs can be ',
        'weighted 85%-95% shortfall valued @ 120%, ',
        '95% shortfall valued @ 170%')
    st.write('**** NICE health technology evaluations: the manual (Jan 2022)')
    return


def write_details_discounted_qalys(vd):
    st.markdown(''.join([
        'The discounted QALYs, $Q$, are calculated as: '
    ]))
    # ----- Formula ----
    latex_discounted_qalys_generic = utilities.latex_equations.\
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

    # ----- Show median survival years for this patient -----
    st.markdown('For the median survival years: ')
    # latex_median_survival_display = utilities.latex_equations.\
    #     median_survival_display(vd)
    # st.latex(latex_median_survival_display)
    # ^ don't bother showing it - it's in the table right there.

    # ----- Calculate QALYs -----
    # st.markdown('For the median survival years: ')
    latex_discounted_qalys = utilities.latex_equations.\
        discounted_qalys(vd)
    st.latex(latex_discounted_qalys)

